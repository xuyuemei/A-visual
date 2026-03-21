#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
-------------------------------------------------------
功能：
1. 读取 .xlsx（多 sheet）
2. 对每个 sheet 的每条 Context + Action1 + Action2：
   - 调用 DeepSeek 生成 A/B 支持率
   - 给出支持理由
3. 输出到 conflict.xlsx，保留每个 sheet
-------------------------------------------------------
"""

import os
import time
import pandas as pd
import json
from openai import OpenAI

# ========== 配置 ==========
os.environ["DEEPSEEK_API_KEY"] = "sk-71308322ca5748aaa2d1d935861a3e93"
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1")

INPUT_FILE = "/data/hlt/A-visual/mark/副本test-zh-800-60.xlsx"
OUTPUT_FILE = "/data/hlt/A-visual/mark/conflict.xlsx"

OUTPUT_DIR = "/data/hlt/A-visual/mark/conflict_parts/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 每一批处理多少条
BATCH_SIZE = 200

# ====== Prompt 模板 ======
PROMPT_TEMPLATE = """
下面有一个情境（Context），以及两个可能的行为方案（选项A与选项B）。
请你从价值判断、伦理合理性、社会影响等角度，对 A 和 B 的支持程度分别给出 0~1 的概率分数（两者加起来强制为 1），并解释理由。

⚠️ 输出要求：
- 必须输出 JSON
- JSON 包含以下字段：
  "A_support": 数字 (0~1)
  "B_support": 数字 (0~1)
  "explanation": "简短理由（不超过120字）"
- 不要输出 JSON 外的其他内容

Context:
{context}

选项A:
{action1}

选项B:
{action2}

请按要求输出 JSON：
"""

# ===== DeepSeek 调用 =====
def call_api(context, action1, action2, retry=3):
    prompt = PROMPT_TEMPLATE.format(
        context=context,
        action1=action1,
        action2=action2
    )

    for attempt in range(retry):
        try:
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=400
            )
            result_text = resp.choices[0].message.content.strip()
            result = json.loads(result_text)

            return {
                "A_support": float(result.get("A_support", 0)),
                "B_support": float(result.get("B_support", 0)),
                "explanation": result.get("explanation", "")
            }

        except Exception as e:
            print(f"⚠️ API 调用失败({attempt+1}/{retry})：{e}")
            time.sleep(2)

    return {"A_support": 0, "B_support": 0, "explanation": "[Error] 调用失败"}


# ===== 主流程 =====
def main():
    print("📌 正在读取 Excel 多 sheet ...")
    sheets = pd.read_excel(INPUT_FILE, sheet_name=None)

    for sheet_name, df in sheets.items():
        print(f"\n====== 处理 Sheet：{sheet_name}  共 {len(df)} 条 ======")

        # --- 切成多个 200 条 ---
        total = len(df)
        num_parts = (total + BATCH_SIZE - 1) // BATCH_SIZE

        for part in range(num_parts):
            start = part * BATCH_SIZE
            end = min(start + BATCH_SIZE, total)
            df_part = df.iloc[start:end].copy()

            out_path = f"{OUTPUT_DIR}{sheet_name}_part{part+1}.xlsx"

            # ⭐⭐⭐ 如果文件已经存在 → 自动跳过（断点续跑最关键行）
            if os.path.exists(out_path):
                print(f"⏭ 已存在，跳过：{out_path}")
                continue  

            print(f"\n▶ 正在处理 {sheet_name} 第 {part+1}/{num_parts} 份 ({start}~{end}) ...")

            A_list, B_list, exp_list = [], [], []

            for idx, row in df_part.iterrows():
                print(f"   → {idx+1}/{end-start}")

                context = str(row["Context"])
                action1 = str(row["Action1"])
                action2 = str(row["Action2"])

                result = call_api(context, action1, action2)

                A_list.append(result["A_support"])
                B_list.append(result["B_support"])
                exp_list.append(result["explanation"])

                time.sleep(1.2)

            df_part["A_support"] = A_list
            df_part["B_support"] = B_list
            df_part["explanation"] = exp_list

            # --- 保存每一份 ---
            df_part.to_excel(out_path, index=False)
            print(f"💾 已保存：{out_path}")

    print("\n🎉 全部 Sheet 已处理完毕！")

if __name__ == "__main__":
    main()