#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------
功能：
1. 从 .xlsx 读取问题（单张表）
2. 选择前 N 条问题
3. 调用 DeepSeek API 生成回答
4. 保存到 deepseek_answers.xlsx
-------------------------------------------------------
"""

import os
import time
import pandas as pd
from openai import OpenAI

# ===================== 配置区域 =====================
os.environ["DEEPSEEK_API_KEY"] = "sk-71308322ca5748aaa2d1d935861a3e93"
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com/v1")

INPUT_FILE = "/data/hlt/A-visual/mark/conflict.xlsx"   
OUTPUT_FILE = "/data/hlt/A-visual/mark/deepseek_answers.xlsx"      
TOP_N = 50                                 # 生成前 N 条回答
SLEEP_TIME = 1.2                            # 避免限流
MODEL = "deepseek-chat"
TEMPERATURE = 0.8


# ===================== 调用 DeepSeek API =====================
def ask_deepseek(question, retry=3):
    """向 DeepSeek 发送问题，返回回答"""
    for attempt in range(retry):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": question}],
                temperature=TEMPERATURE,
                max_tokens=900
            )
            return resp.choices[0].message.content.strip()

        except Exception as e:
            print(f"⚠️ 生成失败({attempt+1}/{retry})：{e}")
            time.sleep(2)

    return "[Error] 无法生成回答"


# ===================== 主流程 =====================
def main():
    print("📄 正在读取 .xlsx ...")
    df = pd.read_excel(INPUT_FILE)

    # 自动检测列名
    if "question" not in df.columns:
        raise ValueError("❌ 文件中未找到 'question' 列，请检查文件格式。")

    df = df.dropna(subset=["question"])

    print(f"📌 文件共 {len(df)} 条问题，将生成前 {TOP_N} 条回答。")

    # 选取前 TOP_N 条
    df = df.iloc[:TOP_N].copy()

    # 存储结果
    answers = []

    for i, q in enumerate(df["question"], 1):
        print(f"🧠 正在生成回答：{i}/{TOP_N}")
        ans = ask_deepseek(q)
        answers.append(ans)
        time.sleep(SLEEP_TIME)

    df["answer"] = answers

    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\n🎉 成功生成回答，已保存至：{OUTPUT_FILE}")


if __name__ == "__main__":
    main()
