# 只负责评分，并输出熵与难度等级
# 不做排序、不过滤、不分类
# 分数<0.001 记为 0

import os
import torch
import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

INPUT_QA = "/data/hlt/A-visual/mark/deepseek_answers.xlsx"
OUTPUT_SCORE = "/data/hlt/A-visual/mark/conflict_results.xlsx"

MODEL_PATH = "/data/hlt/A-visual/mark/Qwen_model.pt"
BASE_MODEL = "/data/hlt/A-visual/mark/Qwen/Qwen/Qwen2.5-0.5B-Instruct"

DIMENSIONS = ["爱国","敬业","诚信","友善","法治","公正","自由","平等","文明","和谐","民主","富强"]

def load_model():
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(BASE_MODEL,
                                                               num_labels=12,
                                                               trust_remote_code=True,
                                                               local_files_only=True)
    state_dict = torch.load(MODEL_PATH, map_location="cpu")
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    return tokenizer, model

def entropy(p):
    p = np.maximum(p, 1e-12)
    return -np.sum(p * np.log(p))

def classify_difficulty(ent):
    if ent < 0.3: return "Easy"
    elif ent < 0.8: return "Medium"
    else: return "Hard"

def main():
    df = pd.read_excel(INPUT_QA)
    df["question"] = df["question"].astype(str)
    df["answer"] = df["answer"].astype(str)

    tokenizer, model = load_model()

    all_scores = []
    ent_list = []
    diff_list = []

    for i, row in df.iterrows():
        text = row["question"] + "\n" + row["answer"]
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            logits = model(**inputs).logits
            probs = torch.softmax(logits, dim=1).numpy()[0]

        probs = np.where(probs < 0.001, 0, probs)

        all_scores.append(probs)

        ent = entropy(probs)
        ent_list.append(ent)
        diff_list.append(classify_difficulty(ent))

        if (i+1) % 50 == 0:
            print(f"已完成 {i+1}/{len(df)}")

    all_scores = np.array(all_scores)
    for idx, dim in enumerate(DIMENSIONS):
        df[dim] = all_scores[:, idx]

    df["entropy"] = ent_list
    df["difficulty"] = diff_list

    df.to_excel(OUTPUT_SCORE, index=False)
    print("评分完成，包含熵和难度标签。")

if __name__ == "__main__":
    main()
