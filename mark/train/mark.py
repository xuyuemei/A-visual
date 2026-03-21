import os
import torch
import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ======= 输入与输出文件路径 =======
INPUT_NEWS = "/data/hlt/A-visual/mark/train/2024.12_2025.9.xlsx"   
OUTPUT_SCORE = "/data/hlt/A-visual/mark/train/12-9.xlsx"

# ======= 模型路径配置 =======
MODEL_PATH = "/data/hlt/A-visual/mark/Qwen_model.pt"
BASE_MODEL = "/data/hlt/A-visual/mark/Qwen/Qwen/Qwen2.5-0.5B-Instruct"

# ======= 12 维度 =======
DIMENSIONS = ["爱国","敬业","诚信","友善","法治","公正",
              "自由","平等","文明","和谐","民主","富强"]

# ======= 加载模型 =======
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL, 
        trust_remote_code=True,
        local_files_only=True
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=12,
        trust_remote_code=True,
        local_files_only=True
    )
    state_dict = torch.load(MODEL_PATH, map_location="cpu")
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    return tokenizer, model

# ======= 熵 =======
def entropy(p):
    p = np.maximum(p, 1e-12)
    return -np.sum(p * np.log(p))

# ======= 分类难度 =======
def classify_difficulty(ent):
    if ent < 0.3: return "Easy"
    elif ent < 0.8: return "Medium"
    else: return "Hard"

# ======= 主程序 =======
def main():
    df = pd.read_excel(INPUT_NEWS)
    df["标题"] = df["标题"].astype(str)
    df["内容"] = df["内容"].astype(str)

    tokenizer, model = load_model()

    all_scores = []
    ent_list = []
    diff_list = []

    for i, row in df.iterrows():

        # ★★★ 输入文本结构：标题 + 内容 ★★★
        text = row["标题"] + "\n" + row["内容"]

        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        with torch.no_grad():
            logits = model(**inputs).logits
            probs = torch.softmax(logits, dim=1).numpy()[0]

        # 低于阈值的记为 0
        probs = np.where(probs < 0.001, 0, probs)

        all_scores.append(probs)

        # 熵 & 难度
        ent = entropy(probs)
        ent_list.append(ent)
        diff_list.append(classify_difficulty(ent))

        if (i+1) % 1000 == 0:
            print(f"已完成 {i+1}/{len(df)}")

    # ======= 结果写入 =======
    all_scores = np.array(all_scores)
    for idx, dim in enumerate(DIMENSIONS):
        df[dim] = all_scores[:, idx]

    df["entropy"] = ent_list
    df["difficulty"] = diff_list

    df.to_excel(OUTPUT_SCORE, index=False)
    print("评分完成！已生成：", OUTPUT_SCORE)


if __name__ == "__main__":
    main()
