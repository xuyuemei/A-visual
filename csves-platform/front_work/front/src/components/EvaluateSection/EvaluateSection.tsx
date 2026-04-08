import React, { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useTranslation } from "react-i18next";
import styles from "./EvaluateSection.module.css";
import RadarChart from "../Graph/RadarChart";
import DimensionTable from "../DimensionTable/DimensionTable";

// ✅ 关键修复：从 historyStore 统一导入类型，EvaluateSection 不再自己声明 QAItem/AnalysisResult
import { useHistoryStore, QAItem, AnalysisResult } from "../history/historyStore";

// 引入 ModelAnalysis 组件
import ModelAnalysis from "../ModelAnalysis/ModelAnalysis";

// ====================== 类型定义（只保留 ModelItem / Props）======================
interface ModelItem {
  name: string; // 后端使用的技术名
  displayName?: string; // 前端展示名
  source?: string; // 提供方名称
}

interface EvalLogItem {
  id: string;
  text: string;
}

interface Props {
  selectedModels: (string | ModelItem)[];
}

// ====================== 主组件 ======================
const EvaluateSection: React.FC<Props> = ({ selectedModels }) => {
  const { t } = useTranslation();
  const [qaByModel, setQaByModel] = useState<Record<string, QAItem[]>>({});
  const [scoresByModel, setScoresByModel] = useState<Record<string, Record<string, number>>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [currentPage, setCurrentPage] = useState(0);
  const [activeAnswerModel, setActiveAnswerModel] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<"qa" | "radar">("qa");

  const [extractedQuestions, setExtractedQuestions] = useState<string[]>([]);
  const [awaitingConfirm, setAwaitingConfirm] = useState(false);

  const [showEvalLog, setShowEvalLog] = useState(false);
  const [evalLogItems, setEvalLogItems] = useState<EvalLogItem[]>([]);
  const logTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [analysisExpanded, setAnalysisExpanded] = useState(false);
  const [activeEvidenceDim, setActiveEvidenceDim] = useState<string | null>(null);
  const [showDebug, setShowDebug] = useState(false);


  const sectionRef = useRef<HTMLDivElement>(null);

  const { addRecord } = useHistoryStore();

  // ✅ 核心修复：适配后端嵌套结构 visual_evidence[dim].tokens
  const renderHighlightedText = (text: string, evidence: any) => {
    if (!text) return "";
    if (!evidence) return text;

    // 自动兼容后端新结构：visual_evidence -> { "维度": { "tokens": [...] } }
    let evidenceArray: any[] = [];
    const firstDimData = Object.values(evidence)[0] as any;
    
    if (firstDimData && Array.isArray(firstDimData.tokens)) {
      evidenceArray = firstDimData.tokens; // 适配新版
    } else if (Array.isArray(firstDimData)) {
      evidenceArray = firstDimData; // 兼容旧版
    } else if (Array.isArray(evidence)) {
      evidenceArray = evidence;
    }

    if (evidenceArray.length === 0) return text;

    let highlighted = text;
    // 降序排列，防止短词替换破坏长词结构
    const sorted = [...evidenceArray].sort((a, b) => ((b.t || b.token)?.length || 0) - ((a.t || a.token)?.length || 0));

    sorted.forEach((item) => {
      // 适配点：兼容后端缩写 t 和 s
      const token = item.t || item.token;
      const score = item.s || item.score;
      if (!token) return;

      // 清洗 Token 前缀 (Ġ, ▂, \n)
      const cleanToken = token.replace(/[Ġ\s\u2581\n]/g, '').trim();
      if (!cleanToken) return;

      if (text.includes(cleanToken)) {
        // 后端已做 0.8 次方，这里映射到视觉
        const alpha = Math.min(Math.max(Math.abs(score) * 0.8, 0.1), 0.6);
        const color = `rgba(255, 235, 59, ${alpha})`;
        const escaped = cleanToken.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`(${escaped})`, 'gu');
        highlighted = highlighted.replace(regex, `<span style="background-color: ${color}; border-radius: 2px; padding: 0 2px;">$1</span>`);
      }
    });
    return highlighted;
  };

  // ✅ 用 ref 持有最新 scores，避免 setState 异步导致保存时取到旧值
  const scoresRef = useRef(scoresByModel);
  useEffect(() => {
    scoresRef.current = scoresByModel;
  }, [scoresByModel]);

  // ✅ 统一获取当前选中模型列表（按技术名去重）
  const getSelectedModelInfos = () => {
    const map = new Map<string, { key: string; displayName: string; technicalName: string }>();
    selectedModels.forEach((m) => {
      if (typeof m === "string") {
        if (!map.has(m)) {
          map.set(m, { key: m, displayName: m, technicalName: m });
        }
      } else {
        const technicalName = m.name;
        const displayName = m.displayName || m.name;
        if (!map.has(technicalName)) {
          map.set(technicalName, { key: displayName, displayName, technicalName });
        }
      }
    });
    return Array.from(map.values());
  };

  const saveToHistory = (
    qaSnapshot?: Record<string, QAItem[]>,
    scoresSnapshot?: Record<string, Record<string, number>>
  ) => {
    const qaByModelAll = qaSnapshot ?? qaByModel;
    const scoresByModelAll = scoresSnapshot ?? scoresByModel;

    const infos = getSelectedModelInfos();
    if (infos.length === 0) return;

    const firstDisplayName = infos[0].displayName;
    if (!qaByModelAll[firstDisplayName] || qaByModelAll[firstDisplayName].length === 0) return;

    addRecord({
      type: 'model',
      modelInfos: infos.map((info) => ({
        name: info.technicalName,
        displayName: info.displayName,
      })),
      qaByModel: qaByModelAll,
      scoresByModel: scoresByModelAll,
    });

    console.log("💾 多模型评测结果（可能包含分析）已保存到历史记录");
  };

  // ✅ 将 ModelAnalysis 结果保存到对应 QAItem，并触发历史记录保存
  const updateAnalysisResult = (modelDisplayName: string, pageIndex: number, analysis: AnalysisResult) => {
    setQaByModel((prev) => {
      const list = prev[modelDisplayName];
      if (!list || !list[pageIndex]) return prev;

      // 只有当分析结果确实变化才更新
      if (JSON.stringify(list[pageIndex].analysis) === JSON.stringify(analysis)) return prev;

      const nextList = list.map((it, idx) => (idx === pageIndex ? { ...it, analysis } : it));
      const next = { ...prev, [modelDisplayName]: nextList };

      // ✅ 用 microtask 确保 next 已生成后保存；scores 用 ref 取最新
      queueMicrotask(() => saveToHistory(next, scoresRef.current));
      return next;
    });
  };

  // ✅ 步骤一：仅抽取问题
  // ✅ 单个问题重抽（临时模拟，后续对接后端）
  const reshuffleQuestion = async (index: number) => {
    try {
      const res = await axios.post("/api/extract_single", {
        current_questions: extractedQuestions,
      });
      const newQuestion = res.data?.question;
      if (newQuestion) {
        setExtractedQuestions((prev) => {
          const next = [...prev];
          next[index] = newQuestion;
          return next;
        });
      } else {
        setError(t('evaluate.errors.questionReshuffleFailed'));
      }
    } catch (err: any) {
      console.error("❌ 重抽问题失败：", err);
      setError(err?.response?.data?.error || t('evaluate.errors.questionReshuffleRetry'));
    }
  };

  const fetchQuestions = async () => {
    setLoading(true);
    setError(null);
    setCurrentPage(0);
    setAwaitingConfirm(false);
    setQaByModel({});
    setScoresByModel({});
    setEvalLogItems([]);
    setAnalysisExpanded(false);

    try {
      const qRes = await axios.get("/api/extract");
      const questions: string[] = qRes.data?.questions || [];
      if (questions.length === 0) {
        setError("未从后端获取到问题，请检查 Flask 输出。");
        return;
      }
      setExtractedQuestions(questions);
      setAwaitingConfirm(true);
    } catch (err: any) {
      console.error("❌ 抽取问题失败：", err);
      setError("抽取问题失败，请检查后端服务。");
    } finally {
      setLoading(false);
    }
  };

  // ✅ 步骤二：确认后开始评估
  const runEvaluation = async (questions: string[]) => {
    if (!questions || questions.length === 0) return;
    const modelInfos = getSelectedModelInfos();
    if (modelInfos.length === 0) return;

    setLoading(true);
    setError(null);
    setCurrentPage(0);

    setEvalLogItems([{ id: `init-${Date.now()}`, text: "开始评估" }]);
    setShowEvalLog(true);

    try {
      const qaByModelAcc: Record<string, QAItem[]> = {};
      const scoresByModelAcc: Record<string, Record<string, number>> = {};

      for (const info of modelInfos) {
        const displayName = info.displayName;
        const technicalName = info.technicalName;
        const qa_acc: QAItem[] = [];

        setEvalLogItems((prev) => [
          ...prev,
          { id: `start-${displayName}-${Date.now()}`, text: `开始评估模型 ${displayName} ...` },
        ]);

        for (let i = 0; i < Math.min(5, questions.length); i++) {
          const q = questions[i];
          const short = q.slice(0, 30);

          setEvalLogItems((prev) => [
            ...prev,
            { id: `q-${displayName}-${i}-${Date.now()}`, text: `正在调用模型 ${displayName} 回答问题： ${short}...` },
          ]);

          const singleRes = await axios.post("/api/evaluate", { models: [technicalName], questions: [q] });

          let single = singleRes.data;
          if (typeof single === "string") {
            try { single = JSON.parse(single); } catch { single = null; }
          }

          const item = single?.qa_list?.[0];

          if (item && item.question) {
            console.log(`[Backend Data Check] Model: ${displayName}`, item);

            qa_acc.push({ 
              question: item.question, 
              answer: item.answer || "",
              // 关键适配：确保 visual_evidence 能够正确传到前端
              visualEvidence: item.visual_evidence || item 
            });
          } else {
            console.warn(`[Backend Warning] Model: ${displayName} returned empty item`);
            qa_acc.push({ question: q, answer: "(无有效返回)", visualEvidence: undefined });
          }

          qaByModelAcc[displayName] = [...qa_acc];
          setQaByModel((prev) => ({ ...prev, [displayName]: [...qa_acc] }));
        }

        // 最终评分（完整问题集）
        const scoreRes = await axios.post("/api/evaluate", { models: [technicalName], questions });

        let scorePayload = scoreRes.data;
        if (typeof scorePayload === "string") {
          try {
            scorePayload = JSON.parse(scorePayload);
          } catch {
            scorePayload = null;
          }
        }

        const scoresObj = scorePayload?.scores || {};
        scoresByModelAcc[displayName] = scoresObj;
        setScoresByModel((prev) => ({ ...prev, [displayName]: scoresObj }));
      }

      setAwaitingConfirm(false);
      setEvalLogItems((prev) => [...prev, { id: `done-${Date.now()}`, text: "评估完成，正在渲染结果..." }]);
      setTimeout(() => setShowEvalLog(false), 800);

      setActiveAnswerModel(modelInfos[0].displayName);

      // ✅ 用累积快照保存，避免 setState 异步导致历史为空
      saveToHistory(qaByModelAcc, scoresByModelAcc);
    } catch (err: any) {
      console.error("评估失败：", err);
      setError("评估失败，请检查后端服务或网络。");
      if (logTimerRef.current) {
        clearTimeout(logTimerRef.current);
        logTimerRef.current = null;
      }
    } finally {
      setLoading(false);
    }
  };

  const scrollToTop = () => {
    if (sectionRef.current) {
      sectionRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  const nextPage = () => {
    const activeList = activeAnswerModel ? qaByModel[activeAnswerModel] || [] : [];
    if (activeList.length === 0) return;
    const next = currentPage === activeList.length - 1 ? 0 : currentPage + 1;
    setCurrentPage(next);
    setAnalysisExpanded(false);
    setTimeout(scrollToTop, 100);
  };

  const prevPage = () => {
    const activeList = activeAnswerModel ? qaByModel[activeAnswerModel] || [] : [];
    if (activeList.length === 0) return;
    const prev = currentPage === 0 ? activeList.length - 1 : currentPage - 1;
    setCurrentPage(prev);
    setAnalysisExpanded(false);
    setTimeout(scrollToTop, 100);
  };

  const goToPage = (page: number) => {
    const activeList = activeAnswerModel ? qaByModel[activeAnswerModel] || [] : [];
    if (page >= 0 && page < activeList.length) {
      setCurrentPage(page);
      setAnalysisExpanded(false);
      setTimeout(scrollToTop, 100);
    }
  };

  // ✅ 当模型选择变化时触发
  useEffect(() => {
    if (selectedModels.length > 0) {
      fetchQuestions();
    } else {
      setQaByModel({});
      setScoresByModel({});
      setCurrentPage(0);
      setAwaitingConfirm(false);
      setExtractedQuestions([]);
      setAnalysisExpanded(false);
      if (logTimerRef.current) {
        clearTimeout(logTimerRef.current);
        logTimerRef.current = null;
      }
      setShowEvalLog(false);
      setEvalLogItems([]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedModels]);

  // ====================== 组件渲染 ======================
useEffect(() => {
  const evidence = activeAnswerModel
    ? (qaByModel[activeAnswerModel]?.[currentPage]?.visualEvidence as Record<string, any> | null)
    : null;

  if (!evidence) {
    setActiveEvidenceDim(null);
    return;
  }

  const dims = Object.keys(evidence).filter((dim) => {
    const topSents = evidence[dim]?.top_sentences;
    return Array.isArray(topSents) && topSents.length > 0;
  });

  if (dims.length === 0) {
    setActiveEvidenceDim(null);
    return;
  }

  if (!activeEvidenceDim || !dims.includes(activeEvidenceDim)) {
    setActiveEvidenceDim(dims[0]);
  }
}, [activeAnswerModel, currentPage, qaByModel, activeEvidenceDim]);

useEffect(() => {
  setShowDebug(false);
}, [activeAnswerModel, currentPage]);

  const modelInfosForView = getSelectedModelInfos();
  const currentQaList = activeAnswerModel ? qaByModel[activeAnswerModel] || [] : [];
  const currentQuestion = currentQaList[currentPage];
  const currentActiveModelInfo =
    modelInfosForView.find((info) => info.displayName === activeAnswerModel) || null;

  return (
    <div className={styles.container} ref={sectionRef}>
      {/* 视图切换：模型回答 / 价值罗盘 */}
      {!loading && !error && !awaitingConfirm && Object.keys(qaByModel).length > 0 && (
        <div className={styles.viewToolbar}>
          <div className={styles.viewToggle}>
            <button
              className={`${styles.toggleButton} ${activeView === "qa" ? styles.activeToggle : ""}`}
              onClick={() => setActiveView("qa")}
            >
              大模型回答与分析
            </button>
            <button
              className={`${styles.toggleButton} ${activeView === "radar" ? styles.activeToggle : ""}`}
              onClick={() => setActiveView("radar")}
            >
              价值罗盘与评分表
            </button>
          </div>
        </div>
      )}

      {loading && !showEvalLog && <p className={styles.loading}>{t('common.processing')}</p>}
      {error && <p className={styles.error}>{error}</p>}

      {!loading && Object.keys(qaByModel).length === 0 && !error && selectedModels.length === 0 && (
        <p className={styles.empty}>{t('evaluate.comparePool.noDataHint')}</p>
      )}

      {/* 日志面板 */}
      {loading && showEvalLog && (
        <div className={styles.cardContainer}>
          <div className={styles.card}>
            <div className={styles.answerSection}>
              <div className={styles.answerContent}>
                {evalLogItems.map((item) => (
                  <div key={item.id} className={styles.logItem}>
                    <div className={styles.logItemHeader}>
                      <span className={styles.logItemArrow}>•</span>
                      <span className={styles.logItemSummary}>{item.text}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 抽题确认 */}
            {!loading && awaitingConfirm && extractedQuestions.length > 0 && (
        <div className={styles.cardContainer}>
          <div className={styles.card}>
            <div className={styles.questionSection}>
              <div className={styles.questionHeader}>
                <div>
                  <p className={styles.sectionEyebrow}>Question Review</p>
                  <h3 className={styles.questionText}>{t("evaluate.questions.extracted")}</h3>
                </div>
              </div>
            </div>

            <div className={styles.answerSection}>
              <div className={styles.answerContent}>
                <div className={styles.questionList}>
                  {extractedQuestions.slice(0, 5).map((q, i) => (
                    <div key={i} className={styles.questionItem}>
                      <div className={styles.questionItemMain}>
                        <span className={styles.questionTag}>{`Q${i + 1}`}</span>
                        <span className={styles.questionItemText}>{q}</span>
                      </div>

                      <button
                        onClick={() => reshuffleQuestion(i)}
                        className={styles.ghostButton}
                        title={t("evaluate.buttons.reshuffle")}
                      >
                        {t("evaluate.buttons.reshuffle")}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className={styles.actionBar}>
              <button className={styles.primaryAction} onClick={() => runEvaluation(extractedQuestions)}>
                {t("evaluate.buttons.confirmEvaluation")}
              </button>
              <button className={styles.secondaryAction} onClick={fetchQuestions}>
                {t("evaluate.buttons.reshuffleAll")}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 问答翻页 */}
      {activeView === "qa" && !loading && !error && !awaitingConfirm && Object.keys(qaByModel).length > 0 && (
        <div className={styles.cardContainer}>
          <div className={styles.cardWithArrows}>
            {/* 左箭头 */}
            <button className={`${styles.arrow} ${styles.arrowLeft}`} onClick={prevPage}>
              <svg width="54" height="58" viewBox="0 0 24 24" fill="none">
                <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>

            <AnimatePresence mode="wait">
              <motion.div
                key={currentPage}
                className={`${styles.card} ${styles.cardFull}`}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.3 }}
              >
                <div className={styles.questionSection}>
  <div className={styles.questionHeader} style={{ alignItems: 'baseline' }}>
    <span className={styles.questionTag} style={{ fontSize: '20px' }}>Q{currentPage + 1}</span>
    <h3 className={styles.questionText} style={{ fontSize: '20px' }}>{currentQuestion?.question || ""}</h3>
  </div>
  <div className={styles.logToggleGroup} style={{ marginTop: '16px' }}>
    {modelInfosForView.map((info) => (
      <button
        key={info.displayName}
        className={`${styles.logToggle} ${
          activeAnswerModel === info.displayName ? styles.logToggleActive : ""
        }`}
        onClick={() => setActiveAnswerModel(info.displayName)}
      >
        {info.displayName}
      </button>
    ))}
  </div>
</div>

<div className={styles.answerSection}>
  <div className={styles.answerRow}>
    <div className={styles.answerColumn}>
      <div className={styles.answerContentMain}>
  <div className={styles.markdownBody}>
    <ReactMarkdown remarkPlugins={[remarkGfm]}>
      {(activeAnswerModel && qaByModel[activeAnswerModel]?.[currentPage]?.answer) || ""}
    </ReactMarkdown>
  </div>
</div>
    </div>

    <div className={styles.analysisColumn}>
      {activeAnswerModel && qaByModel[activeAnswerModel]?.[currentPage] && (
        <div className={styles.sidePanelSection}>
          {(() => {
            const evidence = activeAnswerModel
              ? (qaByModel[activeAnswerModel]?.[currentPage]?.visualEvidence as Record<string, any> | null)
              : null;

            if (!evidence) {
              return <div className={styles.evidenceEmpty}>暂无可展示的证据</div>;
            }

            const dimNames = Object.keys(evidence).filter((dim) => {
              const topSents = evidence[dim]?.top_sentences;
              return Array.isArray(topSents) && topSents.length > 0;
            });

            if (dimNames.length === 0) {
              return <div className={styles.evidenceEmpty}>暂无可展示的证据</div>;
            }

            const currentDim = activeEvidenceDim && dimNames.includes(activeEvidenceDim)
              ? activeEvidenceDim
              : dimNames[0];

            const currentDimData = evidence[currentDim];
            const currentTopSents = currentDimData?.top_sentences || [];

            return (
              <>
                <div className={styles.evidenceTabs}>
                  {dimNames.map((dim) => (
                    <button
                      key={dim}
                      type="button"
                      className={`${styles.evidenceTab} ${
                        currentDim === dim ? styles.evidenceTabActive : ""
                      }`}
                      onClick={() => setActiveEvidenceDim(dim)}
                    >
                      {dim}
                    </button>
                  ))}
                </div>

                <div className={styles.evidenceGrid}>
                  <div className={styles.evidenceCard}>
                    <div className={styles.evidenceCardHeader}>
                      <span className={styles.evidenceBadge}>{currentDim}</span>
                      <span className={styles.evidenceTitle}>核心证据提取</span>
                    </div>

                    <div className={styles.evidenceList}>
                      {currentTopSents.map((s: any, idx: number) => (
                        <div key={idx} className={styles.evidenceQuote}>
                          “{s.text}”
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </>
            );
          })()}
        </div>
      )}

      {activeAnswerModel && qaByModel[activeAnswerModel]?.[currentPage] && (
        <div className={styles.sidePanelSection}>


          <div className={analysisExpanded ? styles.analysisSection : styles.analysisSectionCollapsed}>
            <ModelAnalysis
              key={`${activeAnswerModel}-${currentPage}`}
              question={qaByModel[activeAnswerModel][currentPage].question}
              modelAnswer={qaByModel[activeAnswerModel][currentPage].answer}
              modelName={activeAnswerModel}
              scores={scoresByModel[activeAnswerModel] || {}}
              showDetails={analysisExpanded}
              onAnalysisComplete={(analysis) => {
                updateAnalysisResult(activeAnswerModel, currentPage, analysis as AnalysisResult);
                setAnalysisExpanded(true);
              }}
            />
          </div>
        </div>
      )}
    </div>
  </div>
</div>

                <div className={styles.lineCounter}>
  {Array.from({
    length: (activeAnswerModel && qaByModel[activeAnswerModel]?.length) || 0,
  }).map((_, index) => {
    const disabled =
      !activeAnswerModel || index >= (qaByModel[activeAnswerModel]?.length || 0);
    const active = index === currentPage;

    return (
      <button
        key={index}
        type="button"
        onClick={() => goToPage(index)}
        disabled={disabled}
        className={`${styles.pagePill} ${active ? styles.pagePillActive : ""} ${
          disabled ? styles.pagePillDisabled : ""
        }`}
        title={`跳转到第 ${index + 1} 题`}
      >
        <span className={styles.pagePillLabel}>Q{index + 1}</span>
      </button>
    );
  })}
</div>
              </motion.div>
            </AnimatePresence>

            {/* 右箭头 */}
            <button className={`${styles.arrow} ${styles.arrowRight}`} onClick={nextPage}>
              <svg width="60" height="88" viewBox="0 0 24 24" fill="none">
                <path d="M9 18L15 12L9 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* 可视化区域 */}
      {!loading && !error && Object.keys(scoresByModel).length > 0 && activeView !== "qa" && (
        <motion.div
          className={styles.visualizationSection}
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
        >
          {activeView === "radar" ? (
            <>
              <RadarChart scoresByModel={scoresByModel} />
              <DimensionTable scoresByModel={scoresByModel} />
            </>
          ) : null}
        </motion.div>
      )}
    </div>
  );
};

export default EvaluateSection;