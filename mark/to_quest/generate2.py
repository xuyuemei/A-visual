#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------
功能：基于 test-zh-800-6.xlsx 中的冲突示例
自动生成 “开放式冲突问题”
-------------------------------------------------------
"""

import os
import pandas as pd
import random
import time
from openai import OpenAI

os.environ["DEEPSEEK_API_KEY"] = "sk-71308322ca5748aaa2d1d935861a3e93"
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1")

INPUT_FILE = "/data/hlt/A-visual/mark/test-zh-800-6.xlsx"
OUTPUT_FILE = "/data/hlt/A-visual/mark/conflict_questions.xlsx"

VALUES = [
    "爱国", "敬业", "诚信", "友善", "法治", "公正",
    "自由", "平等", "文明", "和谐", "民主", "富强"
]

SAMPLE_IF_EXIST = 20
SAMPLE_IF_MISSING = 10


def build_prompt(dimension, examples, n):
    ex_text = ""
    for ctx, a1, a2 in examples:
        ex_text += f"【背景】{ctx}\n【选项A】{a1}\n【选项B】{a2}\n\n"

    prompt = f"""
你是一名社会科学研究者，正在构建“价值冲突类开放式问题”数据集。
请模仿示例的冲突结构，生成 {n} 个新的开放式问题。

示例（用于学习冲突结构，不要模仿内容）：
{ex_text}

生成要求：
1. 输出必须是“一个单独的开放式问题”，不能包含选项。
2. 问题必须包含两种价值冲突，但不要直接提到价值观名称。
3. 必须保持“冲突性”与“现实场景感”，例如法律 vs 人情、商业利益 vs 公平、科技便利 vs 隐私等。
4. 必须是开放式问题，可使用“如何看待…”，“面对…应如何平衡”，“是否应该…”等句式。
5. 每行一个问题，不要编号。
6. 语言自然流畅，有足够复杂性。
    """
    return prompt


def ds_generate(prompt):
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=1800
        )
        return resp.choices[0].message.content.strip()
    except:
        return ""


def main():
    sheets = pd.read_excel(INPUT_FILE, sheet_name=None)
    exist_dims = list(sheets.keys())

    writer = pd.ExcelWriter(OUTPUT_FILE)

    for dim in VALUES:
        print(f"\n=== 处理维度：{dim} ===")

        if dim in exist_dims:
            df = sheets[dim]
            sampled = df.sample(n=min(SAMPLE_IF_EXIST, df.shape[0]))
            examples = list(zip(sampled["Context"], sampled["Action1"], sampled["Action2"]))
            prompt = build_prompt(dim, examples, n=SAMPLE_IF_EXIST)
        else:
            print(f"⚠ {dim} 不存在，使用其他维度结构做模板")
            any_dim = random.choice(exist_dims)
            df = sheets[any_dim]
            sampled = df.sample(6)
            examples = list(zip(sampled["Context"], sampled["Action1"], sampled["Action2"]))
            prompt = build_prompt(dim, examples, n=SAMPLE_IF_MISSING)

        text = ds_generate(prompt)
        questions = [q.strip() for q in text.split("\n") if q.strip()]

        pd.DataFrame({"question": questions}).to_excel(writer, sheet_name=dim, index=False)
        time.sleep(1)

    writer.close()
    print("\n🎉 已生成开放式冲突问题：", OUTPUT_FILE)


if __name__ == "__main__":
    main()
