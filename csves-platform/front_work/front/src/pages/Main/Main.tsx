import React, { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useSearchParams } from "react-router-dom";
import { BarChartOutlined, ApartmentOutlined, RadarChartOutlined } from "@ant-design/icons";
import styles from "./Main.module.css";

// 组件导入
import ComparePool from "../../components/ComparePool/ComparePool";
import EvaluateSection from "../../components/EvaluateSection/EvaluateSection";
import TextScoreSection from "../../components/TextScoreSection/TextScoreSection";
import VideoUploadSection from "../../components/VideoUploadSection/VideoUploadSection";
import LeaderboardSection from "../../components/LeaderboardSection/LeaderboardSection";

type ActiveTab = "evaluate" | "history" | "text" | "model" | "video";
type EvalPanelTab = "leaderboard" | "realtime";

const VALID_TABS: ActiveTab[] = ["evaluate", "history", "text", "model", "video"];

const isValidTab = (value: string | null): value is ActiveTab => {
  return !!value && VALID_TABS.includes(value as ActiveTab);
};

interface HeroBlockProps {
  title: string;
  subtitle: string;
  descriptions: string[];
  highlights?: Array<{ value: React.ReactNode; label?: string }>;
  imageAlt?: string;
}

const HeroBlock: React.FC<HeroBlockProps> = ({
  title,
  subtitle,
  descriptions,
  highlights,
  imageAlt = "价值罗盘主视觉",
}) => {
  const visibleDescriptions = descriptions.filter((text) => text.trim().length > 0);

  return (
    <div className={styles.heroLayout}>
      <div className={styles.heroTextColumn}>
        <div className={styles.heroTextInner}>
          <h2 className={styles.sectionTitle}>{title}</h2>
          <p className={styles.sectionSubtitleMain}>{subtitle}</p>

          {highlights && highlights.length > 0 && (
            <div className={styles.heroInsightRow}>
              {highlights.map((item, index) => (
                <div key={`insight-${index}`} className={styles.heroInsightItem}>
                  <div className={styles.heroInsightValue}>{item.value}</div>
                  {item.label && <div className={styles.heroInsightLabel}>{item.label}</div>}
                </div>
              ))}
            </div>
          )}

          {visibleDescriptions.map((text, index) => (
            <p key={`${title}-desc-${index}`} className={styles.sectionIntro}>
              {text}
            </p>
          ))}
        </div>
      </div>

      <div className={styles.heroImageColumn}>
        <div className={styles.heroImageShell}>
          <img src="/logo.png" alt={imageAlt} className={styles.heroImage} />
        </div>
      </div>
    </div>
  );
};

const Main: React.FC = () => {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const [selectedModels, setSelectedModels] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<ActiveTab>("evaluate");
  const [evalPanelTab, setEvalPanelTab] = useState<EvalPanelTab>("leaderboard");

  useEffect(() => {
    const tabParam = searchParams.get("tab");
    if (isValidTab(tabParam)) {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  const handleModelsChange = (models: any[]) => {
    setSelectedModels(models);
  };

  const renderEvalWorkspace = () => {
    return (
      <>
        <div className={styles.evalSwitchBar}>
          <button
            type="button"
            className={`${styles.evalSwitchTab} ${
              evalPanelTab === "leaderboard" ? styles.evalSwitchTabActive : ""
            }`}
            onClick={() => setEvalPanelTab("leaderboard")}
          >
            评测榜单
          </button>
          <button
            type="button"
            className={`${styles.evalSwitchTab} ${
              evalPanelTab === "realtime" ? styles.evalSwitchTabActive : ""
            }`}
            onClick={() => setEvalPanelTab("realtime")}
          >
            实时评测
          </button>
        </div>

        {evalPanelTab === "realtime" ? (
          <>
            <div className={styles.poolWrapper}>
              <ComparePool onModelsChange={handleModelsChange} />
            </div>
            <EvaluateSection selectedModels={selectedModels} />
          </>
        ) : (
          <LeaderboardSection />
        )}
      </>
    );
  };

  const homeDescriptions = useMemo(() => [], []);

  const homeHighlights = useMemo(
    () => [
      { value: "30", label: "可选模型" },
      { value: <ApartmentOutlined />, label: "模型对比" },
      { value: <RadarChartOutlined />, label: "价值观罗盘" },
      { value: <BarChartOutlined />, label: "结果分析" },
    ],
    []
  );

  const textDescriptions = useMemo(
    () => [
      t("textScoring.description1"),
      t("textScoring.description2"),
      t("textScoring.description3"),
    ],
    [t]
  );

  const modelDescriptions = useMemo(() => [], []);

  const videoDescriptions = useMemo(
    () => [t("videoEvaluation.description1"), t("videoEvaluation.description2")],
    [t]
  );

  return (
    <div className={styles.container}>
      <div
        className={`${styles.scrollContainer} ${
          activeTab === "evaluate" || activeTab === "model" ? styles.noOuterFrame : ""
        }`}
      >
        {activeTab === "evaluate" ? (
          <section className={styles.topSection}>
            <HeroBlock
              title={t("home.title")}
              subtitle={t("home.subtitle")}
              descriptions={homeDescriptions}
              highlights={homeHighlights}
            />
            {renderEvalWorkspace()}
          </section>
        ) : activeTab === "text" ? (
          <section className={styles.textScoreSection}>
            <HeroBlock
              title={t("textScoring.title")}
              subtitle={t("textScoring.subtitle")}
              descriptions={textDescriptions}
            />
            <TextScoreSection />
          </section>
        ) : activeTab === "model" ? (
          <section className={styles.modelEvaluationSection}>
            <HeroBlock
              title={t("modelEvaluation.title")}
              subtitle={t("modelEvaluation.subtitle")}
              descriptions={modelDescriptions}
            />
            {renderEvalWorkspace()}
          </section>
        ) : activeTab === "video" ? (
          <section className={styles.videoEvaluationSection}>
            <HeroBlock
              title={t("videoEvaluation.title")}
              subtitle={t("videoEvaluation.subtitle")}
              descriptions={videoDescriptions}
            />
            <VideoUploadSection />
          </section>
        ) : activeTab === "history" ? (
          <section className={styles.historySection}>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>{t("navigation.history")}</h2>
              <p className={styles.sectionSubtitle}>各主流大语言模型基于社会主义核心价值观的评测排行</p>
            </div>
            <LeaderboardSection />
          </section>
        ) : null}
      </div>
    </div>
  );
};

export default Main;