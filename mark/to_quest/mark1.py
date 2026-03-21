#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对 conflict 样本执行社会主义核心价值观 12 维评分
字段格式适配：
Context | Action1 | Action2 | A_support | B_support | explanation
"""

import os
import torch
import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

INPUT_QA = "/data/hlt/A-visual/mark/conflict_parts/a.xlsx"
OUTPUT_SCORE = "/data/hlt/A-visual/mark/conflict_parts/a_scored.xlsx"

MODEL_PATH = "/data/hlt/A-visual/mark/Qwen_model.pt"
BASE_MODEL = "/data/hlt/A-visual/mark/Qwen/Qwen/Qwen2.5-0.5B-Instruct"

DIMENSIONS = ["爱国","敬业","诚信","友善","法治","公正","自由","平等","文明","和谐","民主","富强"]


# ----------------- 加载模型 -----------------
def load_model():
    print("📌 加载模型中...")
    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL, trust_remote_code=True, local_files_only=True
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL, num_labels=12, trust_remote_code=True, local_files_only=True
    )
    state_dict = torch.load(MODEL_PATH, map_location="cpu")
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    print("✅ 模型加载完成")
    return tokenizer, model


# ----------------- 熵函数 -----------------
def entropy(p):
    p = np.maximum(p, 1e-12)
    return -np.sum(p * np.log(p))


def classify_difficulty(ent):
    if ent < 0.3: return "Easy"
    elif ent < 0.8: return "Medium"
    else: return "Hard"


# ----------------- 主流程 -----------------
def main():
    print(f"📄 正在读取：{INPUT_QA}")
    df = pd.read_excel(INPUT_QA)

    # 检查列是否齐全
    required_cols = ["Context", "Action1", "Action2", "explanation"]
    for c in required_cols:
        if c not in df.columns:
            raise ValueError(f"❌ 缺少必要字段：{c}")

    tokenizer, model = load_model()

    all_scores = []
    ent_list = []
    diff_list = []

    print(f"🧠 正在为 {len(df)} 条样本评分...")

    for i, row in df.iterrows():
        # 🔥 ⭐ 新输入构造（最关键的修改）
        text = (
            "Context: " + str(row["Context"]) + "\n" +
            "Action A: " + str(row["Action1"]) + "\n" +
            "Action B: " + str(row["Action2"]) + "\n" +
            "Model Explanation: " + str(row["explanation"])
        )

        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

        with torch.no_grad():
            logits = model(**inputs).logits
            probs = torch.softmax(logits, dim=1).numpy()[0]

        # 分数 <0.001 → 0
        probs = np.where(probs < 0.001, 0, probs)

        all_scores.append(probs)

        # 熵
        ent = entropy(probs)
        ent_list.append(ent)
        diff_list.append(classify_difficulty(ent))

        if (i+1) % 50 == 0:
            print(f"  → 已完成 {i+1}/{len(df)}")

    # 写入 12 维度
    all_scores = np.array(all_scores)
    for idx, dim in enumerate(DIMENSIONS):
        df[dim] = all_scores[:, idx]

    df["entropy"] = ent_list
    df["difficulty"] = diff_list

    df.to_excel(OUTPUT_SCORE, index=False)

    print(f"\n🎉 完成评分！输出文件：{OUTPUT_SCORE}")


if __name__ == "__main__":
    main()
