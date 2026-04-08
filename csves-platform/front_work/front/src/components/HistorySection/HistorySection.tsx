import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useTranslation } from "react-i18next";
import styles from "./HistorySection.module.css";
import RadarChart from "../Graph/RadarChart";
import DimensionTable from "../DimensionTable/DimensionTable";
import { useHistoryStore, HistoryRecord, RecordType } from "../history/historyStore"; // 引入 HistoryRecord 和 RecordType

const HistorySection: React.FC = () => {
  const { t } = useTranslation();
  const { records, removeRecord, clearHistory } = useHistoryStore();

  // 获取记录类型的显示名称
  const getRecordTypeLabel = (type: RecordType) => {
    switch (type) {
      case 'model': return '模型评测';
      case 'text': return '图文评测';
      case 'video': return '视频评测';
      default: return '未知类型';
    }
  };

  // 检查记录是否有评分数据
  const hasScores = (record: HistoryRecord) => {
    return record.scoresByModel && Object.keys(record.scoresByModel).length > 0;
  };

  // 状态管理
  const [activeTab, setActiveTab] = useState<"radar" | "table">("radar");
  const [expandedRecord, setExpandedRecord] = useState<string | null>(null);
  
  // 当前查看的问题索引（翻页用）
  const [currentQAIndex, setCurrentQAIndex] = useState(0);
  
  // 当前正在查看回答的模型（Key: displayName）
  const [activeAnswerModel, setActiveAnswerModel] = useState<string | null>(null);

  // 切换记录展开/收起
  const toggleExpand = (record: HistoryRecord) => {
    if (expandedRecord === record.id) {
      setExpandedRecord(null);
      setActiveAnswerModel(null);
    } else {
      setExpandedRecord(record.id);
      setCurrentQAIndex(0);
      const qaModelNames = Object.keys(record.qaByModel || {});
      // 根据记录类型设置默认模型
      if (record.type === 'model' && record.modelInfos && record.modelInfos.length > 0) {
        setActiveAnswerModel(record.modelInfos[0].displayName);
      } else if (record.type === 'text' && record.scoresByModel) {
        setActiveAnswerModel(Object.keys(record.scoresByModel)[0]);
      } else if (record.type === 'video' && record.scoresByModel) {
        setActiveAnswerModel(Object.keys(record.scoresByModel)[0]);
      } else if (qaModelNames.length > 0) {
        setActiveAnswerModel(qaModelNames[0]);
      } else {
        setActiveAnswerModel(null);
      }
    }
  };

  // 格式化日期
  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) return "未知时间";
    return new Intl.DateTimeFormat("zh-CN", {
      year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
    }).format(date);
  };

  // 翻页逻辑
  const goToPage = (index: number) => setCurrentQAIndex(index);
  const nextPage = () => {
    if (!activeAnswerModel) return;
    const record = records.find(r => r.id === expandedRecord);
    if (!record) return;
    
    let activeList: any[] = [];
    if (record.type === 'model' && record.qaByModel) {
      activeList = record.qaByModel[activeAnswerModel] || [];
    }
    // 文本和视频评测没有问答列表，不需要翻页
    
    if (currentQAIndex < activeList.length - 1) setCurrentQAIndex(currentQAIndex + 1);
  };
  const prevPage = () => {
    if (currentQAIndex > 0) setCurrentQAIndex(currentQAIndex - 1);
  };

  const getQAArrayLength = (record: HistoryRecord, modelName: string | null): number => {
    if (!modelName || !record.qaByModel) return 0;
    return record.qaByModel[modelName]?.length || 0;
  };

  if (records.length === 0) {
    return (
      <div className={styles.emptyState}>
        <h3>历史记录</h3>
        <p>暂无历史记录，完成一次模型评测后将会显示在这里</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h3>评估历史记录</h3>
        <button className={styles.clearButton} onClick={clearHistory} disabled={records.length === 0}>
          清空历史
        </button>
      </div>

      <div className={styles.historyList}>
        {records.map((record, index) => (
          (() => {
            const modelInfos = record.modelInfos ?? [];
            const qaByModel = record.qaByModel ?? {};
            const activeQaList = activeAnswerModel ? (qaByModel[activeAnswerModel] ?? []) : [];
            const fallbackQuestion = record.type === 'text' ? '文本评分内容' : record.type === 'video' ? '视频评测内容' : '暂无问题';

            return (
          <motion.div
            key={record.id}
            className={styles.historyCard}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            {/* 卡片头部：显示模型概览 */}
            <div className={styles.cardHeader}>
              <div className={styles.recordInfo}>
                <div className={styles.modelTagList}>
                  {/* 显示参与评估的模型标签 */}
                  {modelInfos.length > 0 ? (
                    modelInfos.map((m, i) => (
                      <span key={i} className={styles.modelTag}>{m.displayName}</span>
                    ))
                  ) : (
                    <span className={styles.modelTag}>{getRecordTypeLabel(record.type)}</span>
                  )}
                </div>
                <span className={styles.timestamp}>{formatDate(record.timestamp)}</span>
              </div>
              <div className={styles.cardActions}>
                <button className={styles.toggleButton} onClick={() => toggleExpand(record)}>
                  {expandedRecord === record.id ? "收起" : "查看详情"}
                </button>
                <button className={styles.deleteButton} onClick={() => removeRecord(record.id)}>
                  删除
                </button>
              </div>
            </div>

            {/* 展开内容 */}
            <AnimatePresence>
              {expandedRecord === record.id && activeAnswerModel && (
                <motion.div
                  className={styles.cardContent}
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  {/* 1. 视图切换 Tab (价值罗盘 / 维度表格) */}
                  <div className={styles.viewToggle}>
                    <button
                      className={`${styles.viewToggleButton} ${activeTab === "radar" ? styles.activeToggle : ""}`}
                      onClick={() => setActiveTab("radar")}
                    >
                      {t('common.valueCompass')}
                    </button>
                    <button
                      className={`${styles.viewToggleButton} ${activeTab === "table" ? styles.activeToggle : ""}`}
                      onClick={() => setActiveTab("table")}
                    >
                      {t('common.dimensionTable')}
                    </button>
                  </div>

                  {/* 2. 可视化图表 (传入所有模型的数据) */}
                  <div className={styles.visualization}>
                    <AnimatePresence mode="wait">
                      {activeTab === "radar" ? (
                        <motion.div key="radar" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                          {/* 传递 scoresByModel 进行多模型对比展示 */}
                          <RadarChart scoresByModel={record.scoresByModel || {}} /> 
                        </motion.div>
                      ) : (
                        <motion.div key="table" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                          <DimensionTable scoresByModel={record.scoresByModel || {}} />
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>

                  {/* 3. 问答展示卡片 (带多模型切换和内部滚动) */}
                  <div className={styles.cardContainer}>
                    <div className={styles.cardWithArrows}>
                      
                      {/* 左翻页箭头 */}
                      <button 
                        className={styles.arrow} 
                        onClick={() => prevPage()}
                      >
                        <svg width="54" height="58" viewBox="0 0 24 24" fill="none">
                          <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </button>

                      {/* 问答主卡片 */}
                      <div className={styles.qaCard}>
                        {/* A. 问题区域 (固定) */}
                        <div className={styles.questionSection}>
                          <div className={styles.questionHeader}>
                            <span className={styles.questionNumber}>Q{currentQAIndex + 1}</span>
                            <h3 className={styles.questionText}>
                              {/* 确保当前模型和问题索引有效 */}
                              {activeQaList[currentQAIndex]?.question || fallbackQuestion}
                            </h3>
                          </div>
                          
                          {/* 模型切换 Tabs (胶囊按钮) */}
                          <div className={styles.logToggleGroup}>
                            {modelInfos.map((info) => (
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

                        {/* B. 回答区域 */}
                        <div className={styles.answerSection}>
                          {/* Markdown 回答内容 (内部滚动) */}
                          <div className={styles.answerContentMain}>
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {activeQaList[currentQAIndex]?.answer || "该模型在当前问题下暂无回答"}
                            </ReactMarkdown>
                          </div>

                          {/* 底部进度条 */}
                          <div className={styles.lineCounter}>
                            {activeQaList.map((_, i) => (
                              <button
                                key={i}
                                onClick={() => goToPage(i)}
                                className={`${styles.line} ${i === currentQAIndex ? styles.activeLine : ""}`}
                              />
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* 右翻页箭头 */}
                      <button 
                        className={styles.arrow} 
                        onClick={() => nextPage()}
                      >
                        <svg width="54" height="58" viewBox="0 0 24 24" fill="none">
                          <path d="M9 18L15 12L9 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </button>
                    </div>
                  </div>

                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
            );
          })()
        ))}
      </div>
    </div>
  );
};

export default HistorySection;