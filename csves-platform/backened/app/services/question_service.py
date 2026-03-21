import pandas as pd
import random
import os

QUESTION_FILE = "/data/hlt/A-visual/mark/社会主义核心价值观评估500个问题.xlsx"

def extract_questions(n=5):
    """从Excel随机抽n个问题"""
    print("🚀 extract_questions called")
    if not os.path.exists(QUESTION_FILE):
        raise FileNotFoundError(f"未找到题库文件: {QUESTION_FILE}")

    print("📘 找到文件，开始读取 Excel ...")
    df = pd.read_excel(QUESTION_FILE)
    print("✅ Excel 读取完成，共", len(df), "行")

    text_col = next((c for c in df.columns if "问题" in c or "question" in c.lower()), df.columns[0])
    samples = df.sample(n)
    print("✅ 抽取完成：", samples[text_col].tolist())
    return samples[text_col].tolist()

def extract_single_question(current_questions):
    """基于当前问题列表，抽取一个不重复的新问题"""
    print("🚀 extract_single_question called")
    if not os.path.exists(QUESTION_FILE):
        raise FileNotFoundError(f"未找到题库文件: {QUESTION_FILE}")

    print("📘 找到文件，开始读取 Excel ...")
    df = pd.read_excel(QUESTION_FILE)
    print("✅ Excel 读取完成，共", len(df), "行")

    text_col = next((c for c in df.columns if "问题" in c or "question" in c.lower()), df.columns[0])
    all_questions = df[text_col].tolist()
    # 过滤掉已存在的问题
    available = [q for q in all_questions if q not in current_questions]
    if not available:
        # 如果没有不重复的，随机返回一个（降级策略）
        return random.choice(all_questions)
    chosen = random.choice(available)
    print("✅ 单个问题抽取完成：", chosen)
    return chosen
