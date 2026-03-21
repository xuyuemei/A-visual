import React, { useState } from "react";
import { Modal, Input, List, Typography } from "antd";

export interface ModelOption {
  key: string;
  name: string;
  description: string;
}

interface Props {
  open: boolean;
  onClose: () => void;
  onSubmit: (selected: ModelOption | null) => void; // ✅ 单选
}

const ModelSelectModal: React.FC<Props> = ({ open, onClose, onSubmit }) => {
  // ✅ 固定模型列表（你可以后续换成后端接口）
  const modelList: ModelOption[] = [
    { key: "qwen-2.5-0.5B", name: "Qwen 2.5 0.5B", description: "阿里通义轻量模型" },
    { key: "llama-3.2-1B", name: "LLaMA 3.2 1B", description: "Meta 1B参数模型" },
    { key: "deepseek-r1", name: "DeepSeek-R1", description: "DeepSeek 推理优化模型" },
    { key: "glm-4", name: "GLM-4", description: "智谱AI 通用模型" },
    { key: "chatgpt-4o-mini", name: "ChatGPT-4o-mini", description: "OpenAI 轻量视觉语言模型" },
    { key: "mistral-7B", name: "Mistral 7B", description: "法系高效开源模型" },
  ];

  const [searchText, setSearchText] = useState("");
  const [selected, setSelected] = useState<ModelOption | null>(null);

  // ✅ 搜索过滤（忽略大小写）
  const filteredModels = modelList.filter(
    (m) =>
      m.name.toLowerCase().includes(searchText.toLowerCase()) ||
      m.description.toLowerCase().includes(searchText.toLowerCase())
  );

  // ✅ 点击选中模型
  const handleSelect = (model: ModelOption) => {
    setSelected(model);
  };

  // ✅ 提交按钮逻辑
  const handleSubmit = () => {
    if (selected) {
      onSubmit(selected); // 将选中的模型传回父组件
    } else {
      onSubmit(null); // 如果没选则传 null
    }
    setSelected(null); // 清空选中状态
    setSearchText(""); // 清空搜索框
    onClose(); // ✅ 关闭弹窗
  };

  return (
    <Modal
      title="选择要对比的大语言模型"
      open={open}
      onCancel={onClose}
      onOk={handleSubmit}
      okText="Submit"
      cancelText="Cancel"
    >
      {/* 搜索框 */}
      <Input
        placeholder="搜索模型..."
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}
        style={{ marginBottom: 12 }}
      />

      {/* 模型列表 */}
      <List
        dataSource={filteredModels}
        renderItem={(model) => (
          <List.Item
            onClick={() => handleSelect(model)}
            style={{
              cursor: "pointer",
              padding: "10px 14px",
              background:
                selected?.key === model.key ? "#e6f4ff" : "transparent",
              transition: "background 0.2s",
            }}
            onMouseEnter={(e) => {
              if (selected?.key !== model.key)
                (e.currentTarget.style.background = "#f9f9f9");
            }}
            onMouseLeave={(e) => {
              if (selected?.key !== model.key)
                (e.currentTarget.style.background = "transparent");
            }}
          >
            <Typography.Text strong>{model.name}</Typography.Text> —{" "}
            <span style={{ color: "#666" }}>{model.description}</span>
          </List.Item>
        )}
      />
    </Modal>
  );
};

export default ModelSelectModal;
