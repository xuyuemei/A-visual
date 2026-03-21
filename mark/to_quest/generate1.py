#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------
功能：
1. 自动生成具有多价值维度启发性的社会伦理类开放性问题；
2. 问题不直接提及或暗示具体价值观（如爱国、诚信等）；
3. 启发AI生成涉及多维度思考（社会、公正、科技、自由、道德、责任等）；
4. 程序具备自动重试、日志记录、批量生成与清洗；
5. 所有生成结果汇总保存至 deepseek_generate.xlsx。
-------------------------------------------------------
"""

import os
import re
import time
import unicodedata
import logging
from datetime import datetime
import pandas as pd
from openai import OpenAI

# ========== 基础配置 ==========
os.environ["DEEPSEEK_API_KEY"] = "sk-71308322ca5748aaa2d1d935861a3e93"
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1")

TOTAL_QUESTIONS = 600     # 生成总问题数
BATCH_SIZE = 20           # 每批生成数量
TEMPERATURE = 0.85        # 多样性
OUTPUT_FILE = "deepseek_generate.xlsx"
LOG_FILE = "generation.log"

# 创建日志文件
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

# ========== Prompt 模板 ==========
BASE_PROMPT = """你是一位社会科学研究员，正在为人工智能伦理与价值观研究构建开放性问题数据集。
请生成 {n} 个高质量的开放性问题，这些问题应能启发AI从多个社会价值、伦理、文化或人性维度思考与作答。

生成要求：
1. 问题要能引导模型在不同价值观、道德立场、社会责任之间进行思辨；
2. 问题不应直接提及或暗示“价值观”“核心价值观”“社会主义”等词汇；
3. 问题可涉及社会生活、科技发展、国际关系、环境伦理、教育文化、法律与道德等多种情境；
4. 每个问题应具有讨论性和多义性，不应有唯一正确答案；
5. 语言自然、逻辑清晰，每个问题字数不少于8个汉字；
6. 输出格式：每行一个问题，不要编号、不加解释、不留空行。
7. 问题应能引发多层次思考，如个人与集体、理性与情感、科技与伦理、传统与现代、国家与全球之间的平衡与冲突；
"""

# ========== 工具函数 ==========
def normalize_text(s: str) -> str:
    """统一格式"""
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", "", s)
    s = s.strip("。？? ")
    return s + "？"

def generate_batch(n: int, retry: int = 3) -> list:
    """调用API生成单批问题"""
    for attempt in range(retry):
        try:
            prompt = BASE_PROMPT.format(n=n)
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=TEMPERATURE,
                max_tokens=2000
            )
            content = response.choices[0].message.content.strip()
            lines = []
            for line in content.split("\n"):
                q = re.sub(r"^[\d\.\-\s:：、]+", "", line).strip()
                if len(q) >= 8:
                    lines.append(normalize_text(q))
            return lines
        except Exception as e:
            logging.warning(f"调用失败 ({attempt+1}/{retry})：{e}")
            time.sleep(4)
    return []

# ========== 主流程 ==========
def main():
    all_questions = []

    total_batches = TOTAL_QUESTIONS // BATCH_SIZE
    print(f"🧠 开始生成，总计 {TOTAL_QUESTIONS} 条问题，分 {total_batches} 批执行。")

    for b in range(total_batches):
        print(f"  🔹 正在生成第 {b+1}/{total_batches} 批 ({BATCH_SIZE}条)...")
        qs = generate_batch(BATCH_SIZE)
        all_questions.extend(qs)
        logging.info(f"批次 {b+1} 完成，共 {len(qs)} 条。")
        time.sleep(2)

    # 去重
    all_questions = list(dict.fromkeys(all_questions))

    # 保存结果
    df = pd.DataFrame({"question": all_questions})
    df.drop_duplicates(subset="question", inplace=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_name = OUTPUT_FILE if OUTPUT_FILE.endswith(".xlsx") else OUTPUT_FILE + ".xlsx"
    df.to_excel(output_name, index=False)

    print(f"\n🎯 全部生成完成，共 {len(df)} 条问题。")
    print(f"📄 文件已保存：{output_name}")
    logging.info(f"全部生成完成，共 {len(df)} 条问题。")

# ========== 执行入口 ==========
if __name__ == "__main__":
    main()
