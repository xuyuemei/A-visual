import { create } from "zustand";
import { persist } from "zustand/middleware";

// ---------------------- 核心价值观分析结果类型 (统一在这里定义并导出) ----------------------
export interface AnalysisResult {
  core_value_analysis: {
    identified_values: string[];
    interpretability_analysis: string;
    // ✅ 关键修复：改成可选，兼容 ModelAnalysis 返回缺字段的情况
    sociological_significance?: string;
  };
}
// ------------------------------------------------------------------------------------------

// 问答对的接口 (已更新)
export interface QAItem {
  question: string;
  answer: string;
  // ✅ 新增：可选的分析结果字段
  analysis?: AnalysisResult;
}

// 记录类型枚举
export type RecordType = 'model' | 'text' | 'video';

// 历史记录的接口 (支持多类型)
export interface HistoryRecord {
  id: string;
  timestamp: string;
  type: RecordType; // 记录类型

  // 模型评估专用字段
  modelInfos?: Array<{
    name: string; // 技术名
    displayName: string; // 展示名
  }>;

  // 按模型展示名存储问答列表 (Key: displayName) - 模型评估专用
  qaByModel?: Record<string, QAItem[]>;

  // 按模型展示名存储分数 (Key: displayName) - 模型评估和视频分析都用
  scoresByModel?: Record<string, Record<string, number>>;

  // 文本评分专用字段
  textContent?: string;
  textAnalysis?: string;

  // 视频分析专用字段
  videoInfo?: {
    filename: string;
    duration: number;
    resolution: string;
    fps: number;
  };
  transcript?: string;
  processingSummary?: {
    total_frames: number;
    analyzed_frames: number;
    audio_segments: number;
    has_audio: boolean;
  };
}

interface HistoryStore {
  records: HistoryRecord[];
  maxRecords: number;
  addRecord: (record: Omit<HistoryRecord, "id" | "timestamp">) => void;
  removeRecord: (id: string) => void;
  clearHistory: () => void;
}

export const useHistoryStore = create<HistoryStore>()(
  persist(
    (set, get) => ({
      records: [],
      maxRecords: 10,

      addRecord: (recordData) => {
        const newRecord: HistoryRecord = {
          ...recordData,
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
        };

        set((state) => ({
          records: [newRecord, ...state.records].slice(0, state.maxRecords),
        }));
      },

      removeRecord: (id: string) => {
        set((state) => ({
          records: state.records.filter((record) => record.id !== id),
        }));
      },

      clearHistory: () => {
        set({ records: [] });
      },
    }),
    {
      name: "multi-type-history-v1",
    }
  )
);
