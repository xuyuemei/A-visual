import React, { useEffect, useMemo, useState } from "react";
import { Card, Button } from "antd";
import { PlusOutlined, CloseOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import ModelSelectModal, { ModelOption } from "../ModelSelectModal/ModelSelectModal";
import styles from "./ComparePool.module.css";

interface ComparePoolProps {
  max?: number;
  onModelsChange?: (models: ModelOption[]) => void;
}

const ComparePool: React.FC<ComparePoolProps> = ({ max = 4, onModelsChange }) => {
  const { t } = useTranslation();
  const [boxes, setBoxes] = useState<(ModelOption | null)[]>(Array(max).fill(null));
  const [open, setOpen] = useState(false);

  // ✅ max 变化时同步 boxes 长度，并尽量保留已有选择
  useEffect(() => {
    setBoxes((prev) => {
      if (prev.length === max) return prev;

      if (prev.length > max) {
        const next = prev.slice(0, max);
        onModelsChange?.(next.filter((b) => b !== null) as ModelOption[]);
        return next;
      }

      return [...prev, ...Array(max - prev.length).fill(null)];
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [max]);

  const selectedModels = useMemo(
    () => boxes.filter((b) => b !== null) as ModelOption[],
    [boxes]
  );

  const handleAddClick = () => {
    setOpen(true);
  };

  const handleSubmitFromModal = (selected: ModelOption[]) => {
    const next: (ModelOption | null)[] = Array(max).fill(null);
    for (let i = 0; i < max; i++) next[i] = selected[i] || null;

    setBoxes(next);
    onModelsChange?.(selected);
    setOpen(false);
  };

  const handleRemove = (index: number) => {
    const next = [...boxes];
    next[index] = null;
    setBoxes(next);
    onModelsChange?.(next.filter((b) => b !== null) as ModelOption[]);
  };

  const clearAll = () => {
    const next = Array(max).fill(null);
    setBoxes(next);
    onModelsChange?.([]);
  };

  return (
    <div className={styles.poolWrapper}>
      {/* Header */}
      <div className={styles.poolHeader}>
        <div className={styles.poolTitleBlock}>
          <div className={styles.poolTitle}>{t('evaluate.comparePool.title')}</div>
          <div className={styles.poolSubtitle}>
            {t('evaluate.comparePool.subtitle', { max })}
          </div>
        </div>

        <div className={styles.poolActions}>
          <button
            className={styles.ghostBtn}
            onClick={handleAddClick}
            type="button"
            title={t('evaluate.comparePool.selectModels')}
          >
            <PlusOutlined />
            {t('evaluate.comparePool.selectModels')}
          </button>

          <button
            className={styles.ghostBtn}
            onClick={clearAll}
            type="button"
            disabled={selectedModels.length === 0}
            title={t('evaluate.comparePool.clear')}
          >
            {t('evaluate.comparePool.clear')}
          </button>
        </div>
      </div>

      {/* Selected tags */}
      {selectedModels.length > 0 && (
        <div className={styles.selectedBar}>
          {selectedModels.map((m, idx) => {
            const key =
              (m as any).id ??
              (m as any).value ??
              (m as any).model ??
              `${m.displayName}-${m.source}-${idx}`;

            return (
              <span key={key} className={styles.tag}>
                {m.displayName}
                <span className={styles.tagDot}>·</span>
                {m.source}
              </span>
            );
          })}
        </div>
      )}

      {/* Grid */}
      <div className={styles.grid}>
        {boxes.slice(0, max).map((model, idx) => (
          <Card
            key={idx}
            className={`${styles.box} ${model ? styles.boxFilled : styles.boxEmpty}`}
            variant="borderless"
            onClick={() => !model && handleAddClick()}
            styles={{ body: { padding: 0, height: "100%" } }}
          >
            {model ? (
              <div className={styles.modelCard}>
                <div className={styles.cardTop}>
                  <div className={styles.modelText}>
                    <div className={styles.modelName} title={model.displayName}>
                      {model.displayName}
                    </div>
                    <div className={styles.modelMeta} title={model.source}>
                      {model.source}
                    </div>
                  </div>

                  <Button
                    size="small"
                    type="text"
                    icon={<CloseOutlined />}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemove(idx);
                    }}
                    className={styles.closeBtn}
                    aria-label="remove"
                  />
                </div>

                <div className={styles.cardBottom}>
                  <span className={styles.badge}>{t('evaluate.comparePool.selected')}</span>
                </div>
              </div>
            ) : (
              <div className={styles.addBox}>
                <div className={styles.addIcon}>
                  <PlusOutlined />
                </div>
                <div className={styles.addText}>{t('evaluate.comparePool.addModel')}</div>
                <div className={styles.addHint}>{t('evaluate.comparePool.clickToSelect')}</div>
              </div>
            )}
          </Card>
        ))}
      </div>

      {/* Footer hint */}
      <div className={styles.tipRow}>
        <div className={styles.tipText}>
          {t('evaluate.comparePool.currentSelection', { current: selectedModels.length, max })}
        </div>
      </div>

      <ModelSelectModal
        open={open}
        onClose={() => setOpen(false)}
        onSubmit={handleSubmitFromModal}
        max={max}
        initialSelected={selectedModels}
      />
    </div>
  );
};

export default ComparePool;
