import React, { useEffect, useMemo, useRef, useState } from 'react';
import styles from './ModelAnalysis.module.css';

interface AnalysisResult {
  core_value_analysis: {
    identified_values: string[];
    interpretability_analysis: string;
  };
}

interface AnalysisProps {
  question: string;
  modelAnswer: string;
  modelName: string;
  scores: Record<string, number>;
  onAnalysisComplete?: (analysis: AnalysisResult) => void;
  showDetails?: boolean;
}

const PREVIEW_LENGTH = 260;

const ModelAnalysis: React.FC<AnalysisProps> = ({
  question,
  modelAnswer,
  modelName,
  scores,
  onAnalysisComplete,
  showDetails = true,
}) => {
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [hasAnalyzed, setHasAnalyzed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  const abortControllerRef = useRef<AbortController | null>(null);
  const requestIdRef = useRef(0);

  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  const normalizedQuestion = useMemo(() => question?.trim() || '', [question]);
  const normalizedAnswer = useMemo(() => modelAnswer?.trim() || '', [modelAnswer]);
  const normalizedModelName = useMemo(() => modelName?.trim() || '', [modelName]);

  const scoreValidation = useMemo(() => {
    if (!scores || typeof scores !== 'object') {
      return { valid: false, message: '评分数据缺失' };
    }

    const entries = Object.entries(scores);
    if (entries.length === 0) {
      return { valid: false, message: '评分数据为空' };
    }

    for (const [key, value] of entries) {
      if (!key?.trim()) {
        return { valid: false, message: '存在空的评分维度名称' };
      }
      if (typeof value !== 'number' || Number.isNaN(value)) {
        return { valid: false, message: `维度“${key}”的评分不是有效数字` };
      }
      if (value < 0 || value > 1) {
        return { valid: false, message: `维度“${key}”的评分必须在 0 到 1 之间` };
      }
    }

    return { valid: true, message: '' };
  }, [scores]);

  const canAnalyze =
    !loading &&
    !!normalizedQuestion &&
    !!normalizedAnswer &&
    scoreValidation.valid;

  const getFriendlyErrorMessage = (message: string) => {
    if (!message) return '分析失败，请重试';
    if (message.includes('Failed to fetch')) return '网络连接失败，请检查网络后重试';
    if (message.includes('AbortError')) return '分析请求已取消';
    if (message.includes('超时')) return '分析服务响应超时，请稍后重试';
    return message;
  };

  const analyzeAnswer = async () => {
    if (!normalizedAnswer) {
      setError('没有回答内容可供分析');
      return;
    }

    if (!normalizedQuestion) {
      setError('问题内容为空');
      return;
    }

    if (!scoreValidation.valid) {
      setError(scoreValidation.message || '评分数据不合法');
      return;
    }

    // 取消上一次请求
    abortControllerRef.current?.abort();

    const controller = new AbortController();
    abortControllerRef.current = controller;

    const currentRequestId = ++requestIdRef.current;

    setLoading(true);
    setError(null);
    setHasAnalyzed(true);
    setExpandedSections(new Set());

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
        body: JSON.stringify({
          question: normalizedQuestion,
          modelAnswer: normalizedAnswer,
          modelName: normalizedModelName,
          scores,
        }),
      });

      const responseText = await response.text();

      let data: any;
      try {
        data = JSON.parse(responseText);
      } catch {
        throw new Error('服务器返回的不是合法 JSON');
      }

      if (!response.ok) {
        const errorMessage =
          data?.error ||
          data?.message ||
          `请求失败: ${response.status}`;
        throw new Error(errorMessage);
      }

      if (data?.error) {
        throw new Error(data.error);
      }

      if (!data?.core_value_analysis) {
        throw new Error('响应数据格式不正确：缺少 core_value_analysis');
      }

      if (
        !Array.isArray(data.core_value_analysis.identified_values) ||
        data.core_value_analysis.identified_values.length === 0
      ) {
        throw new Error('响应数据格式不正确：identified_values 缺失');
      }

      if (
        typeof data.core_value_analysis.interpretability_analysis !== 'string' ||
        !data.core_value_analysis.interpretability_analysis.trim()
      ) {
        throw new Error('响应数据格式不正确：interpretability_analysis 缺失');
      }

      // 只处理最新的一次请求，避免旧请求覆盖新请求
      if (currentRequestId !== requestIdRef.current) {
        return;
      }

      setAnalysis(data);
      onAnalysisComplete?.(data);
    } catch (err: unknown) {
      if (controller.signal.aborted) {
        return;
      }

      const message =
        err instanceof Error
          ? err.message
          : '分析失败，请重试';

      setError(getFriendlyErrorMessage(message));
    } finally {
      if (currentRequestId === requestIdRef.current) {
        setLoading(false);
      }
    }
  };

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
  };

  const renderDetailedContent = (content: string, section: string) => {
    const isExpanded = expandedSections.has(section);
    const shouldTruncate = content.length > PREVIEW_LENGTH;
    const displayContent =
      isExpanded || !shouldTruncate
        ? content
        : `${content.slice(0, PREVIEW_LENGTH)}...`;

    const paragraphs = displayContent
      .split(/\n+/)
      .map((item) => item.trim())
      .filter(Boolean);

    return (
      <div className={styles.detailedContent}>
        <div className={styles.paragraphGroup}>
          {paragraphs.map((paragraph, index) => (
            <p key={`${section}-${index}`}>{paragraph}</p>
          ))}
        </div>

        {shouldTruncate && (
          <button
            type="button"
            className={styles.expandButton}
            onClick={() => toggleSection(section)}
            aria-expanded={isExpanded}
            aria-controls={`${section}-content`}
          >
            {isExpanded ? '收起' : '展开详细分析'}
          </button>
        )}
      </div>
    );
  };

  const identifiedValues = analysis?.core_value_analysis?.identified_values || [];
  const interpretabilityText =
    analysis?.core_value_analysis?.interpretability_analysis || '';

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <button
          type="button"
          onClick={analyzeAnswer}
          disabled={!canAnalyze}
          className={styles.analyzeButton}
        >
          {loading
            ? analysis
              ? '重新分析中...'
              : '深度分析中...'
            : analysis
            ? '重新生成核心价值观分析'
            : '开始核心价值观可解释性分析'}
        </button>

        {!scoreValidation.valid && (
          <span className={styles.inlineHint}>{scoreValidation.message}</span>
        )}
      </div>

      {error && (
        <div className={styles.error} role="alert">
          <strong>分析失败：</strong>
          <span>{error}</span>
        </div>
      )}

      {!hasAnalyzed && !analysis && !loading && !error && (
        <div className={styles.analysisResult}>
          <div className={styles.emptyState}>
            <h3>核心价值观可解释性分析</h3>
            <p>点击上方按钮开始分析</p>
          </div>
        </div>
      )}

      {loading && !analysis && (
        <div className={styles.analysisResult}>
          <div className={styles.loadingState}>
            <div className={styles.loadingSpinner} />
            <p>正在生成可解释性分析，请稍候...</p>
          </div>
        </div>
      )}

      {analysis && showDetails && (
        <div className={styles.analysisResult}>
          {loading && (
            <div className={styles.refreshingBanner}>
              正在基于最新内容重新分析，当前先保留上一版结果
            </div>
          )}

          <div className={styles.valueTagsSection}>
            <h4>识别的核心价值观</h4>
            <div className={styles.valueTags}>
              {identifiedValues.map((value, index) => (
                <span key={`${value}-${index}`} className={styles.valueTag}>
                  {value}
                </span>
              ))}
            </div>
          </div>

          <div className={styles.dimensionCard}>
            <button
              type="button"
              className={styles.dimensionHeader}
              onClick={() => toggleSection('interpretability')}
              aria-expanded={expandedSections.has('interpretability')}
              aria-controls="interpretability-content"
            >
              <h5>可解释性分析</h5>
              <span className={styles.expandIcon}>
                {expandedSections.has('interpretability') ? '▲' : '▼'}
              </span>
            </button>

            <div id="interpretability-content">
              {renderDetailedContent(interpretabilityText, 'interpretability')}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelAnalysis;