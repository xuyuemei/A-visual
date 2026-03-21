import React, { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useSearchParams } from "react-router-dom";
import styles from "./Main.module.css";

// 组件导入
import ComparePool from "../../components/ComparePool/ComparePool";
import EvaluateSection from "../../components/EvaluateSection/EvaluateSection";
import HistorySection from "../../components/HistorySection/HistorySection";
import TextScoreSection from "../../components/TextScoreSection/TextScoreSection";
import VideoUploadSection from "../../components/VideoUploadSection/VideoUploadSection";

type ActiveTab = "evaluate" | "history" | "text" | "model" | "video";

const VALID_TABS: ActiveTab[] = ["evaluate", "history", "text", "model", "video"];

const isValidTab = (value: string | null): value is ActiveTab => {
  return !!value && VALID_TABS.includes(value as ActiveTab);
};

interface HeroBlockProps {
  eyebrow: string;
  title: string;
  subtitle: string;
  descriptions: string[];
  chips: string[];
  imageAlt?: string;
}

const HeroBlock: React.FC<HeroBlockProps> = ({
  eyebrow,
  title,
  subtitle,
  descriptions,
  chips,
  imageAlt = "价值罗盘主视觉",
}) => {
  return (
    <div className={styles.heroLayout}>
      <div className={styles.heroTextColumn}>
        <div className={styles.heroTextInner}>
          <div className={styles.heroEyebrow}>{eyebrow}</div>

          <h2 className={styles.sectionTitle}>{title}</h2>
          <p className={styles.sectionSubtitleMain}>{subtitle}</p>

          <div className={styles.heroChipRow}>
            {chips.map((chip, index) => (
              <span key={`${chip}-${index}`} className={styles.heroChip}>
                {chip}
              </span>
            ))}
          </div>

          {descriptions.map((text, index) => (
            <p key={`${title}-desc-${index}`} className={styles.sectionIntro}>
              {text}
            </p>
          ))}
        </div>
      </div>

      <div className={styles.heroImageColumn}>
        <div className={styles.heroImageShell}>
          <div className={styles.heroImageTopBar}>
            <span className={styles.heroDot} />
            <span className={styles.heroDot} />
            <span className={styles.heroDot} />
            <span className={styles.heroTopLabel}>VALUE COMPASS / SYSTEM PANEL</span>
          </div>

          <div className={styles.heroImageFrame}>
            <img src="/logo.png" alt={imageAlt} className={styles.heroImage} />
          </div>
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

  useEffect(() => {
    const tabParam = searchParams.get("tab");
    if (isValidTab(tabParam)) {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  const handleModelsChange = (models: any[]) => {
    setSelectedModels(models);
  };

  const homeDescriptions = useMemo(
    () => [t("home.description1"), t("home.description2")],
    [t]
  );

  const textDescriptions = useMemo(
    () => [
      t("textScoring.description1"),
      t("textScoring.description2"),
      t("textScoring.description3"),
    ],
    [t]
  );

  const modelDescriptions = useMemo(
    () => [t("modelEvaluation.description1"), t("modelEvaluation.description2")],
    [t]
  );

  const videoDescriptions = useMemo(
    () => [t("videoEvaluation.description1"), t("videoEvaluation.description2")],
    [t]
  );

  return (
    <div className={styles.container}>
      <div className={styles.scrollContainer}>
        {activeTab === "evaluate" ? (
          <section className={styles.topSection}>
            <HeroBlock
              eyebrow="AI VALUE ALIGNMENT PLATFORM"
              title={t("home.title")}
              subtitle={t("home.subtitle")}
              descriptions={homeDescriptions}
              chips={["Explainability", "Model Comparison", "Structured Evaluation"]}
            />
            <div className={styles.poolWrapper}>
              <ComparePool onModelsChange={handleModelsChange} />
            </div>
            <EvaluateSection selectedModels={selectedModels} />
          </section>
        ) : activeTab === "text" ? (
          <section className={styles.textScoreSection}>
            <HeroBlock
              eyebrow="TEXT SCORING ENGINE"
              title={t("textScoring.title")}
              subtitle={t("textScoring.subtitle")}
              descriptions={textDescriptions}
              chips={["Semantic Scoring", "Core Values", "Evidence Driven"]}
            />
            <TextScoreSection />
          </section>
        ) : activeTab === "model" ? (
          <section className={styles.modelEvaluationSection}>
            <HeroBlock
              eyebrow="MODEL EVALUATION WORKSPACE"
              title={t("modelEvaluation.title")}
              subtitle={t("modelEvaluation.subtitle")}
              descriptions={modelDescriptions}
              chips={["Benchmark View", "Value Analysis", "Comparative Review"]}
            />
            <div className={styles.poolWrapper}>
              <ComparePool onModelsChange={handleModelsChange} />
            </div>
            <EvaluateSection selectedModels={selectedModels} />
          </section>
        ) : activeTab === "video" ? (
          <section className={styles.videoEvaluationSection}>
            <HeroBlock
              eyebrow="MULTIMODAL VIDEO ANALYSIS"
              title={t("videoEvaluation.title")}
              subtitle={t("videoEvaluation.subtitle")}
              descriptions={videoDescriptions}
              chips={["Video Upload", "Scene Understanding", "Multimodal Review"]}
            />
            <VideoUploadSection />
          </section>
        ) : activeTab === "history" ? (
          <section className={styles.historySection}>
            <div className={styles.sectionHeader}>
              <div className={styles.heroEyebrow}>RECORDS / TRACE / REVIEW</div>
              <h2 className={styles.sectionTitle}>{t("history.title")}</h2>
              <p className={styles.sectionSubtitle}>{t("history.subtitle")}</p>
            </div>
            <HistorySection />
          </section>
        ) : null}
      </div>
    </div>
  );
};

export default Main;