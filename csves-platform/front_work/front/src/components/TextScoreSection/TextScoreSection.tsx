import React, { useMemo, useState } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import RadarChart from "../Graph/RadarChart";
import TextDimensionTable from "../DimensionTable/TextDimensionTable";
import styles from "./TextScoreSection.module.css";

// ✅ 新增：弹窗组件
import VoiceInputModal from "../VoiceInputModal/VoiceInputModal";
// ✅ 新增：历史记录
import { useHistoryStore } from "../history/historyStore";

type Scores = Record<string, number>;
type ScoresByModel = Record<string, Scores>;

type LowDimension = { dimension: string; score: number };
type SentenceRisk = {
  index: number;
  text: string;
  start_char: number;
  end_char: number;
  low_dimensions: LowDimension[];
  risk_level: "high" | "medium" | "normal" | "unknown";
};

type KeywordLocalization = {
  keyword: string;
  matched_text?: string;
  category: string;
  start_char: number;
  end_char: number;
  window_text: string;
  risk_level: "high" | "medium" | "normal" | "unknown";
  low_dimensions: LowDimension[];
};

type LocalizationSummary = {
  sentence_count: number;
  keyword_hit_count: number;
  high_risk_sentence_count: number;
  medium_risk_sentence_count: number;
  overall_risk_level: "high" | "medium" | "normal" | "unknown";
};

type TextLocalizationResult = {
  sentence_risks: SentenceRisk[];
  keyword_localizations: KeywordLocalization[];
  summary: LocalizationSummary;
};

type TextLocalizationItem = {
  index: number;
  text: string;
  localization: TextLocalizationResult;
};

type ImageLocalizationBlock = {
  id: string;
  bbox: { x1: number; y1: number; x2: number; y2: number };
  description: string;
  overall_risk_level: "high" | "medium" | "normal" | "unknown";
  overall_low_dimensions: LowDimension[];
  risk_reason?: string;
};

type ImageLocalizationItem = {
  filename: string;
  previewUrl: string;
  width: number;
  height: number;
  blocks: ImageLocalizationBlock[];
};

const TextScoreSection: React.FC = () => {
  const { t } = useTranslation();
  const { addRecord } = useHistoryStore();
  const [currentText, setCurrentText] = useState("");
  const [texts, setTexts] = useState<string[]>([]);

  // 用于触发隐藏的文件选择
  const fileInputRef = React.useRef<HTMLInputElement | null>(null);

  const [scoresByModel, setScoresByModel] = useState<ScoresByModel>({});
  const [singleScores, setSingleScores] = useState<Scores | null>(null);
  const [localizationResults, setLocalizationResults] = useState<TextLocalizationItem[]>([]);
  const [imageLocalizations, setImageLocalizations] = useState<ImageLocalizationItem[]>([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeResultView, setActiveResultView] = useState<"compass" | "positioning">("compass");

  // ✅ 控制弹窗打开/关闭
  const [voiceOpen, setVoiceOpen] = useState(false);

  const hasResult = Object.keys(scoresByModel).length > 0;
  const totalCount = useMemo(() => texts.length, [texts]);

  const normalizeMarkdownText = (raw: string) => {
    return (raw || "")
      .replace(/^\s*图片内容分析[:：]\s*/u, "")
      .replace(/\r/g, "")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  };

  const buildBlockReason = (block: ImageLocalizationBlock) => {
    const explicitReason = (block.risk_reason || "").trim();
    if (explicitReason) {
      return explicitReason;
    }
    if (block.overall_risk_level === "high") {
      return "该区域综合评估为高风险，建议优先进行人工复核与处置。";
    }
    if (block.overall_risk_level === "medium") {
      return "该区域综合评估为中等风险，建议持续关注并结合上下文复核。";
    }
    return "该区域存在潜在风险信号，建议人工复核。";
  };

  const extractRiskWords = (text: string) => {
    const source = (text || "").toLowerCase();
    if (!source) return [] as string[];

    const lexicon = [
      "暴力",
      "血腥",
      "打斗",
      "武器",
      "刀",
      "枪",
      "仇恨",
      "辱骂",
      "歧视",
      "煽动",
      "极端",
      "毒品",
      "吸毒",
      "赌博",
      "诈骗",
      "色情",
      "裸露",
      "低俗",
      "自残",
      "自杀",
      "违法",
      "违规",
      "攻击",
      "威胁",
      "危险",
      "未成年人",
      "欺凌",
      "恐怖",
      "爆炸",
      "酒驾",
      "谣言",
    ];

    return lexicon.filter((word) => source.includes(word)).slice(0, 6);
  };

  const onConfirmAdd = () => {
    setError(null);
    const textContent = currentText.trim();
    if (!textContent) {
      setError("当前文本为空，无法添加。");
      return;
    }
    setTexts((prev) => [...prev, textContent]);
    setCurrentText("");
  };

  const removeText = (idx: number) => {
    setTexts((prev) => prev.filter((_, i) => i !== idx));
  };

  const clearAll = () => {
    setCurrentText("");
    setTexts([]);
    setScoresByModel({});
    setSingleScores(null);
    setLocalizationResults([]);
    setImageLocalizations([]);
    setActiveResultView("compass");
    setError(null);
  };

  // 处理文件上传，支持 txt、doc/docx 以及图片文件
  const onFileChange: React.ChangeEventHandler<HTMLInputElement> = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);

    const name = file.name.toLowerCase();
    const isTxt = name.endsWith(".txt") || file.type.startsWith("text");
    const isDoc = name.endsWith(".doc") || name.endsWith(".docx");
    const isImage = file.type.startsWith("image/");

    // 1）txt：前端直接读取整个文件内容作为一个词条
    if (isTxt) {
      const reader = new FileReader();
      reader.onload = () => {
        const content = (reader.result ?? "").toString().trim();
        if (!content) {
          setError("文件内容为空，无法添加。");
          return;
        }

        // 将整个文件内容作为一个词条，而不是按行拆分
        const fullText = content.replace(/\r?\n/g, ' ').trim();
        
        if (!fullText) {
          setError("文件内容为空，无法添加。");
          return;
        }

        setTexts((prev) => [...prev, fullText]);
        if (e.target) {
          e.target.value = "";
        }
      };

      reader.onerror = () => {
        setError("读取文件失败，请重试或检查文件格式。");
      };

      reader.readAsText(file, "utf-8");
      return;
    }

    // 2）图片：前端读取并调用 AI 视觉分析接口
    if (isImage) {
      const reader = new FileReader();
      reader.onload = () => {
        const imageData = reader.result as string;
        if (!imageData) {
          setError("图片读取失败，无法添加。");
          return;
        }

        // 调用 AI 视觉分析接口
        setLoading(true);
        
        // 将 base64 数据转换为文件对象
        const base64Data = imageData.split(',')[1];
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const imageBlob = new Blob([byteArray], { type: file.type });
        
        const formData = new FormData();
        formData.append("image", imageBlob, file.name);
        formData.append("filename", file.name);

        axios
          .post("/api/analyze_image", formData, {
            headers: { "Content-Type": "multipart/form-data" },
          })
          .then((res) => {
            const analysisResult = res.data?.analysis || res.data?.description || "";
            const localizationBlocks = (res.data?.localization || []) as ImageLocalizationBlock[];
            const width = Number(res.data?.details?.width || 0);
            const height = Number(res.data?.details?.height || 0);
            if (!analysisResult) {
              setError("图片分析结果为空，无法添加。");
              return;
            }
            
            // 保留模型返回的 Markdown 结构，避免前缀破坏标题层级
            const imageDescription = normalizeMarkdownText(analysisResult);
            
            setTexts((prev) => [...prev, imageDescription]);

            setImageLocalizations((prev) => [
              ...prev,
              {
                filename: file.name,
                previewUrl: imageData,
                width,
                height,
                blocks: Array.isArray(localizationBlocks) ? localizationBlocks : [],
              },
            ]);
          })
          .catch((err) => {
            console.error("图片分析失败:", err);
            // 如果 AI 分析失败，降级到文件信息描述
            const fallbackDescription = `图片文件：${file.name}，类型：${file.type}，大小：${(file.size / 1024).toFixed(2)}KB。请根据图片内容进行社会主义核心价值观12维度评估。`;
            setTexts((prev) => [...prev, fallbackDescription]);
          })
          .finally(() => {
            setLoading(false);
            if (e.target) {
              e.target.value = "";
            }
          });
      };

      reader.onerror = () => {
        setError("图片读取失败，请重试或检查图片格式。");
      };

      reader.readAsDataURL(file);
      return;
    }

    // 2）doc/docx：上传给后端解析，将整个文档内容作为一个词条
    if (isDoc) {
      const formData = new FormData();
      formData.append("file", file);

      setLoading(true);
      axios
        .post("/api/parse_doc_text", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        })
        .then((res) => {
          const textsFromDoc = (res.data && (res.data.texts as string[])) || [];
          if (!Array.isArray(textsFromDoc) || textsFromDoc.length === 0) {
            setError("文档解析结果为空，无法添加。");
            return;
          }
          
          // 将所有段落合并为一个完整的文本作为一个词条
          const fullDocText = textsFromDoc.join(' ').trim();
          
          if (!fullDocText) {
            setError("文档解析结果为空，无法添加。");
            return;
          }
          
          setTexts((prev) => [...prev, fullDocText]);
        })
        .catch((err) => {
          setError(
            err?.response?.data?.error ||
              "文档解析失败，请检查后端 /api/parse_doc_text 是否正常。",
          );
        })
        .finally(() => {
          setLoading(false);
          if (e.target) {
            e.target.value = "";
          }
        });

      return;
    }

    setError("仅支持上传 .txt、.doc 或 .docx 文件。");
    e.target.value = "";
  };

  const onScore = async () => {
    setError(null);
    setScoresByModel({});
    setSingleScores(null);
    setLocalizationResults([]);

    if (texts.length === 0) {
      setError("请先输入文本并点击“确认添加”，再开始评分。");
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post("/api/score_text_batch", { texts });
      const scores = res.data?.scores as Scores | undefined;

      if (!scores) {
        setError("后端未返回 scores 字段，请检查 /api/score_text_batch。");
        return;
      }

      setScoresByModel({ 评分: scores });
      setSingleScores(scores);
      setActiveResultView("compass");

      try {
        const locateRes = await axios.post("/api/score_text_localize_batch", { texts });
        const locItems = (locateRes.data?.results || []) as Array<any>;
        setLocalizationResults(
          locItems.map((item, i) => ({
            index: Number.isFinite(item?.index) ? item.index : i,
            text: item?.text || texts[i] || "",
            localization: item?.localization || {
              sentence_risks: [],
              keyword_localizations: [],
              summary: {
                sentence_count: 0,
                keyword_hit_count: 0,
                high_risk_sentence_count: 0,
                medium_risk_sentence_count: 0,
                overall_risk_level: "unknown",
              },
            },
          }))
        );
      } catch (locErr) {
        console.warn("批量文本定位失败，降级逐条定位：", locErr);
        const fallback: TextLocalizationItem[] = [];
        for (let i = 0; i < texts.length; i += 1) {
          try {
            const r = await axios.post("/api/score_text_localize", { text: texts[i] });
            fallback.push({
              index: i,
              text: texts[i],
              localization: {
                sentence_risks: r.data?.sentence_risks || [],
                keyword_localizations: r.data?.keyword_localizations || [],
                summary: r.data?.summary || {
                  sentence_count: 0,
                  keyword_hit_count: 0,
                  high_risk_sentence_count: 0,
                  medium_risk_sentence_count: 0,
                  overall_risk_level: "unknown",
                },
              },
            });
          } catch {
            fallback.push({
              index: i,
              text: texts[i],
              localization: {
                sentence_risks: [],
                keyword_localizations: [],
                summary: {
                  sentence_count: 0,
                  keyword_hit_count: 0,
                  high_risk_sentence_count: 0,
                  medium_risk_sentence_count: 0,
                  overall_risk_level: "unknown",
                },
              },
            });
          }
        }
        setLocalizationResults(fallback);
      }
      
      // ✅ 保存到历史记录
      addRecord({
        type: 'text',
        textContent: texts.join('\n\n'),
        textAnalysis: JSON.stringify(scores, null, 2),
        scoresByModel: { 评分: scores },
      });
      
      console.log("💾 文本评分结果已保存到历史记录");
    } catch (e: any) {
      setError(e?.response?.data?.error || "评分失败，请检查后端是否启动或接口路径是否正确。");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h2 className={styles.title}>文本价值观 12 维度评分</h2>

        <textarea
          className={styles.textarea}
          value={currentText}
          onChange={(e) => setCurrentText(e.target.value)}
          placeholder="请输入一段文本... 或使用语音输入"
        />

        <div className={styles.actions}>
          <button className={styles.secondary} onClick={onConfirmAdd} disabled={loading}>
            确认添加
          </button>

          {/* ✅ 点击打开弹窗 */}
          <button
            className={styles.secondary}
            onClick={() => setVoiceOpen(true)}
            disabled={loading}
            title="需要浏览器麦克风权限"
          >
            语音输入
          </button>

          {/* 文件上传按钮：点击触发隐藏的 file input */}
          <button
            className={styles.secondary}
            type="button"
            disabled={loading}
            onClick={() => {
              setError(null);
              fileInputRef.current?.click();
            }}
            title="上传文本文件或图片文件（支持AI视觉分析），自动添加到列表"
          >
            上传文件
          </button>

          <button className={styles.primary} onClick={onScore} disabled={loading || texts.length === 0}>
            {loading ? "评分中..." : "开始评分"}
          </button>

          <button className={styles.secondary} onClick={clearAll} disabled={loading}>
            清空全部
          </button>
        </div>

        {/* 隐藏的文件选择框，仅用于触发系统文件选择 */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,text/plain,.docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/*"
          style={{ display: "none" }}
          onChange={onFileChange}
          disabled={loading}
        />

        {error && <div className={styles.error}>{error}</div>}

        {/* ✅ 已添加文本列表：替换掉 inline style，改成 class 版 */}
        {texts.length > 0 && (
          <div className={styles.listCard}>
            <div className={styles.listHeader}>
              <div className={styles.listTitle}>
                已添加文本
                <span className={styles.listCount}>{texts.length}</span>
              </div>
              <div className={styles.listHint}>将参与评分（可删除）</div>
            </div>

            <div className={styles.listBody}>
              {texts.map((t, idx) => (
                <div key={idx} className={styles.listItem}>
                  <div className={styles.listBadge}>文本{idx + 1}</div>

                  <div className={styles.listText}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{normalizeMarkdownText(t)}</ReactMarkdown>
                  </div>

                  <div className={styles.listActions}>
                    <button
                      type="button"
                      className={styles.deleteBtn}
                      onClick={() => removeText(idx)}
                      disabled={loading}
                      title="删除这条"
                      aria-label={`删除文本${idx + 1}`}
                    >
                      删除
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className={styles.countHint}>
          当前待评分文本数量：<strong>{totalCount}</strong>
        </div>
      </div>

      {hasResult && (
        <div className={styles.result}>
          <div className={styles.resultToggleContainer}>
            <button
              className={`${styles.resultToggleButton} ${activeResultView === "compass" ? styles.resultActiveToggle : ""}`}
              onClick={() => setActiveResultView("compass")}
            >
              价值罗盘
            </button>
            <button
              className={`${styles.resultToggleButton} ${activeResultView === "positioning" ? styles.resultActiveToggle : ""}`}
              onClick={() => setActiveResultView("positioning")}
            >
              定位分析
            </button>
          </div>

          {activeResultView === "compass" && (
            <>
              <RadarChart scoresByModel={scoresByModel} />
              {singleScores && (
                <TextDimensionTable
                  scores={singleScores}
                  title={`社会主义核心价值观维度评分表（共 ${texts.length} 段文本，总评分）`}
                />
              )}
            </>
          )}

          {activeResultView === "positioning" && imageLocalizations.length === 0 && (
            <div className={styles.imageLocHint}>当前暂无图片低分区域定位结果，请先上传图片并完成分析。</div>
          )}

          {activeResultView === "positioning" && imageLocalizations.length > 0 && (
            <div className={styles.imageLocCard}>
              <h3 className={styles.imageLocTitle}>图片低分区域定位</h3>
              {imageLocalizations.map((item, idx) => (
                <div key={`${item.filename}-${idx}`} className={styles.imageLocGroup}>
                  <div className={styles.imageLocFile}>图片：{item.filename}</div>

                  {(() => {
                    const riskBlocks = item.blocks.filter(
                      (b) => b.overall_risk_level === "high" || b.overall_risk_level === "medium"
                    );

                    return (
                      <>
                        <div className={styles.imageCanvasWrap}>
                          <img src={item.previewUrl} alt={item.filename} className={styles.imagePreview} />
                          {riskBlocks.map((block, riskIdx) => {
                            const riskClass =
                              block.overall_risk_level === "high" ? styles.riskBoxHigh : styles.riskBoxMedium;
                            const riskLabelClass =
                              block.overall_risk_level === "high" ? styles.riskLabelHigh : styles.riskLabelMedium;
                            const w = item.width || 1;
                            const h = item.height || 1;
                            const leftPct = (block.bbox.x1 / w) * 100;
                            const topPct = (block.bbox.y1 / h) * 100;
                            const widthPct = ((block.bbox.x2 - block.bbox.x1) / w) * 100;
                            const heightPct = ((block.bbox.y2 - block.bbox.y1) / h) * 100;

                            return (
                              <div
                                key={`box-${item.filename}-${block.id}`}
                                className={`${styles.riskBox} ${riskClass}`}
                                style={{
                                  left: `${leftPct}%`,
                                  top: `${topPct}%`,
                                  width: `${widthPct}%`,
                                  height: `${heightPct}%`,
                                }}
                                title={`区域${riskIdx + 1} - ${block.overall_risk_level}`}
                              >
                                <span className={`${styles.riskLabel} ${riskLabelClass}`}>{riskIdx + 1}</span>
                              </div>
                            );
                          })}
                        </div>

                        {item.blocks.length === 0 && (
                          <div className={styles.imageLocHint}>当前图片暂无可定位的风险区域（仅显示预览图）。</div>
                        )}

                        {riskBlocks.map((block, riskIdx) => (
                          <div key={block.id} className={styles.imageLocItem}>
                            <div className={styles.imageLocHeader}>
                              <span className={styles.riskIndexTag}>区域 {riskIdx + 1}</span>
                              <span>
                                风险等级：
                                <span
                                  className={`${styles.riskLevelTag} ${
                                    block.overall_risk_level === "high" ? styles.riskLevelHigh : styles.riskLevelMedium
                                  }`}
                                >
                                  {block.overall_risk_level === "high" ? "高" : "中等"}
                                </span>
                              </span>
                              <span>
                                坐标：({block.bbox.x1},{block.bbox.y1})-({block.bbox.x2},{block.bbox.y2})
                              </span>
                            </div>
                            <div className={styles.imageLocDims}>
                              低分维度：
                              {block.overall_low_dimensions?.length
                                ? block.overall_low_dimensions
                                    .slice(0, 4)
                                    .map((d) => `${d.dimension}(${d.score.toFixed(2)})`)
                                    .join("、")
                                : "无"}
                            </div>
                            <div className={styles.imageLocDesc}>区域描述：{block.description || "无"}</div>
                            <div className={styles.imageLocReason}>
                              风险原因：{buildBlockReason(block)}
                            </div>
                            <div className={styles.imageLocReason}>
                              风险词：
                              {extractRiskWords(block.description || "").length
                                ? extractRiskWords(block.description || "").join("、")
                                : "未检出明显风险词"}
                            </div>
                          </div>
                        ))}
                      </>
                    );
                  })()}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ✅ 语音弹窗 */}
      <VoiceInputModal
        open={voiceOpen}
        onClose={() => setVoiceOpen(false)}
        onConfirm={(txt) => {
          setCurrentText((prev) => {
            const base = prev.trim();
            const add = (txt || "").trim();
            if (!add) return prev;
            return base ? base + " " + add : add;
          });
        }}
        lang="zh-CN"
      />
    </div>
  );
};

export default TextScoreSection;
