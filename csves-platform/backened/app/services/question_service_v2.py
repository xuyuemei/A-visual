import pandas as pd
import random
import os
import json

# 原始问题文件
ORIGINAL_QUESTION_FILE = "/data/hlt/A-visual/mark/500_question_answer.xlsx"

# 新的保留问题文件
RESERVED_QUESTIONS_FILE = "/data/hlt/A-visual/csves-platform/backened/reserved_questions.json"

def extract_questions_original(n=5):
    """从原始Excel随机抽n个问题（用于对比测试）"""
    print("🚀 extract_questions_original called")
    if not os.path.exists(ORIGINAL_QUESTION_FILE):
        raise FileNotFoundError(f"未找到原始题库文件: {ORIGINAL_QUESTION_FILE}")

    print("📘 找到原始文件，开始读取 Excel ...")
    df = pd.read_excel(ORIGINAL_QUESTION_FILE)
    print("✅ Excel 读取完成，共", len(df), "行")

    text_col = next((c for c in df.columns if "问题" in c or "question" in c.lower()), df.columns[0])
    samples = df.sample(n)
    print("✅ 原始问题抽取完成：", samples[text_col].tolist())
    return samples[text_col].tolist()

def extract_questions_reserved(n=5):
    """从保留问题JSON文件随机抽n个问题（用于测试修改后的问题）"""
    print("🚀 extract_questions_reserved called")
    if not os.path.exists(RESERVED_QUESTIONS_FILE):
        raise FileNotFoundError(f"未找到保留问题文件: {RESERVED_QUESTIONS_FILE}，请先运行 import_questions.py")

    print("📘 找到保留问题文件，开始读取 JSON ...")
    with open(RESERVED_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    print(f"✅ JSON 读取完成，共 {len(questions)} 个保留问题")

    if len(questions) < n:
        print(f"⚠️ 保留问题数量不足，当前只有 {len(questions)} 个，全部返回")
        samples = questions
    else:
        samples = random.sample(questions, n)
    
    print("✅ 保留问题抽取完成：", samples)
    return samples

def extract_questions(n=5, use_original=False):
    """
    统一的问题抽取接口
    
    Args:
        n: 抽取问题数量
        use_original: 是否使用原始问题（False表示使用保留问题）
    
    Returns:
        list: 问题列表
    """
    if use_original:
        return extract_questions_original(n)
    else:
        return extract_questions_reserved(n)

def get_question_stats():
    """获取问题统计信息"""
    stats = {}
    
    # 原始问题统计
    if os.path.exists(ORIGINAL_QUESTION_FILE):
        try:
            df = pd.read_excel(ORIGINAL_QUESTION_FILE)
            stats['original'] = {
                'total': len(df),
                'file': ORIGINAL_QUESTION_FILE
            }
        except Exception as e:
            stats['original'] = {'error': str(e)}
    else:
        stats['original'] = {'error': '文件不存在'}
    
    # 保留问题统计
    if os.path.exists(RESERVED_QUESTIONS_FILE):
        try:
            with open(RESERVED_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            stats['reserved'] = {
                'total': len(data.get('questions', [])),
                'source': data.get('source', '未知'),
                'file': RESERVED_QUESTIONS_FILE
            }
        except Exception as e:
            stats['reserved'] = {'error': str(e)}
    else:
        stats['reserved'] = {'error': '文件不存在，请先运行 import_questions.py'}
    
    return stats

if __name__ == "__main__":
    # 测试代码
    print("📊 问题库统计信息:")
    stats = get_question_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n🧪 测试抽取保留问题:")
    try:
        questions = extract_questions_reserved(3)
        print(f"成功抽取 {len(questions)} 个问题")
    except Exception as e:
        print(f"抽取失败: {e}")
