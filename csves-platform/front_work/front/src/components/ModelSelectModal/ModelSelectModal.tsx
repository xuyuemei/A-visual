import React, { useState, useEffect } from "react";
import { Modal, Checkbox, Button, Spin, message } from "antd";
import { useTranslation } from "react-i18next";
import styles from "./ModelSelectModal.module.css";

export interface ModelOption {
  name: string;        // 后端使用的模型键（必须与 llm_api.py 一致）
  displayName: string; // 前端展示用名称，例如 GPT4o-Instruct、Qwen2.5-7B-Instruct
  source: string;      // 展示来源小字，例如 OpenAI / deepseek / Alibaba Qwen Team
}

interface ModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (selected: ModelOption[]) => void;
  max: number;
  initialSelected?: ModelOption[];
}

const ModelSelectModal: React.FC<ModalProps> = ({ open, onClose, onSubmit, max, initialSelected }) => {
  const { t } = useTranslation();
  // ✅ 模型列表（name 与后端键匹配，displayName/ source 仅用于展示）
  const [models] = useState<ModelOption[]>([
    {
      name: "DeepSeek",
      displayName: "DeepSeek-R1",
      source: "deepseek",
    },
    {
      name: "GPT-4o",
      displayName: "GPT4o-Instruct",
      source: "OpenAI",
    },
    // 千问系列（与后端 API_MODELS 对应）
    {
      name: "Qwen 2.5 7B",
      displayName: "Qwen2.5-7B-Instruct",
      source: "Alibaba Qwen Team",
    },
    {
      name: "Qwen 2.5 32B",
      displayName: "Qwen2.5-32B-Instruct",
      source: "Alibaba Qwen Team",
    },
    {
      name: "Qwen 2.5 72B",
      displayName: "Qwen2.5-72B-Instruct",
      source: "Alibaba Qwen Team",
    },
  ]);

  const [selected, setSelected] = useState<ModelOption[]>(initialSelected || []);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      setSelected(initialSelected || []);
    }
  }, [open, initialSelected]);

  const handleChange = (model: ModelOption) => {
    setSelected((prev) => {
      const exists = prev.some((m) => m.name === model.name);
      if (exists) {
        return prev.filter((m) => m.name !== model.name);
      }
      if (prev.length >= max) {
        return prev;
      }
      return [...prev, model];
    });
  };

  const handleConfirm = () => {
    if (!selected || selected.length === 0) {
      message.warning("请至少选择一个模型！");
      return;
    }
    onSubmit(selected);
    message.success(`已选择 ${selected.length} 个模型`);
    onClose();
  };

  return (
    <Modal
      open={open}
      title={t('modal.selectModel')}
      onCancel={onClose}
      footer={null}
      centered
      width={600}
    >
      {loading ? (
        <div className={styles.loadingContainer}>
          <Spin tip="正在加载模型..." />
        </div>
      ) : models.length === 0 ? (
        <p className={styles.empty}>暂无模型，请稍后再试。</p>
      ) : (
        <div className={styles.modelList}>
          {models.map((model) => (
            (() => {
              const checked = selected.some((m) => m.name === model.name);
              const disabled = !checked && selected.length >= max;
              return (
              <Checkbox
                key={model.name}
                checked={checked}
                disabled={disabled}
                onChange={() => handleChange(model)}
                className={`${styles.checkboxItem} ${disabled ? styles.disabled : ""}`}
              >
                <div className={styles.modelInfo}>
                  {/* 大字：展示模型名，例如 GPT4o-Instruct / Qwen2.5-7B-Instruct */}
                  <strong>{model.displayName}</strong>
                  {/* 小字：来源，如 OpenAI / deepseek / Alibaba Qwen Team */}
                  <span className={styles.source}>{model.source}</span>
                </div>
              </Checkbox>
              );
            })()
          ))}
        </div>
      )}

      <div className={styles.footer}>
        <Button onClick={onClose}>{t('modal.cancel')}</Button>
        <Button type="primary" onClick={handleConfirm} disabled={!selected || selected.length === 0}>
          {t('modal.confirm')}
        </Button>
      </div>
    </Modal>
  );
};

export default ModelSelectModal;
