#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------
功能：
从“无回答问题集”中删除那些已在“有回答问题集”中出现的问题。
特点：
1. 自动处理全角/半角、中文/英文引号、问号等差异
2. 更稳健：避免字符串精度误差，保留真正不同的问题
3. 输出去重后的新文件
-------------------------------------------------------
结果：
从500条中只找到了8条非重复问题
"""

import pandas as pd
import unicodedata
import re

# ========== 文件路径 ==========
NO_ANS_FILE = "/data/hlt/A-visual/mark/quest500.xlsx"     # 无回答问题
ANS_FILE = "/data/hlt/A-visual/mark/ans500.xlsx"          # 有回答问题
OUTPUT_FILE = "/data/hlt/A-visual/mark/quest500_clean.xlsx"  # 输出去重后文件


def normalize_text(s: str) -> str:
    """
    对中文问句做标准化处理（防止符号差异造成匹配失败）
    """
    if pd.isna(s):
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKC", s)  # 全角转半角
    s = re.sub(r"\s+", "", s)             # 去掉所有空格
    s = s.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")
    s = s.replace("？", "?").replace("!", "！")
    s = s.strip()
    return s


def deduplicate_questions(no_ans_path, ans_path, output_path):
    # === 读取数据 ===
    df_no = pd.read_excel(no_ans_path)
    df_yes = pd.read_excel(ans_path)

    # === 提取问题列 ===
    no_q = df_no["infer_result"].astype(str).map(normalize_text)
    yes_q = df_yes["query"].astype(str).map(normalize_text)

    # === 去重逻辑 ===
    answered_set = set(yes_q)
    mask_keep = ~no_q.isin(answered_set)

    df_clean = df_no[mask_keep].copy()
    before, after = len(df_no), len(df_clean)

    # === 保存 ===
    df_clean.to_excel(output_path, index=False)
    print(f"✅ 去重完成：从 {before} 条减少到 {after} 条。")
    print(f"📄 新文件已保存：{output_path}")


if __name__ == "__main__":
    deduplicate_questions(NO_ANS_FILE, ANS_FILE, OUTPUT_FILE)
