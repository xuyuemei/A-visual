#!/usr/bin/env python3
"""
替换问题集脚本：将431个新问题替换到现有问题文件中
"""

import pandas as pd
import os
from datetime import datetime

def backup_current_file():
    """备份当前问题文件"""
    current_file = "/data/hlt/A-visual/mark/500_question_answer.xlsx"
    backup_file = f"/data/hlt/A-visual/mark/500_question_answer_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    if os.path.exists(current_file):
        df = pd.read_excel(current_file)
        df.to_excel(backup_file, index=False)
        print(f"✅ 当前文件已备份到: {backup_file}")
        return True
    else:
        print("❌ 当前问题文件不存在")
        return False

def create_new_question_file(new_questions, output_file):
    """创建新的问题文件"""
    # 创建新的DataFrame，只包含问题列
    new_df = pd.DataFrame({
        'Unnamed: 0': new_questions,
        # 添加空的回答列，保持原有格式
        'deepseekr1': [''] * len(new_questions),
        'glm4': [''] * len(new_questions),
        'qwen2.5-72b-instruct': [''] * len(new_questions),
        'gpt4': [''] * len(new_questions),
        'claude-3-opus': [''] * len(new_questions),
        'llama3.1-8b': [''] * len(new_questions),
        'DeepSeek-R1-Distill-Llama-8B': [''] * len(new_questions),
        'llama3.1-70b': [''] * len(new_questions),
    })
    
    new_df.to_excel(output_file, index=False)
    print(f"✅ 新问题文件已创建: {output_file}")
    print(f"📊 包含 {len(new_questions)} 个问题")

def load_quest500_questions():
    """从quest500.xlsx加载问题"""
    quest_file = "/data/hlt/A-visual/mark/quest500.xlsx"
    
    if not os.path.exists(quest_file):
        print(f"❌ 文件不存在: {quest_file}")
        return []
    
    try:
        df = pd.read_excel(quest_file)
        questions = df['infer_result'].dropna().astype(str).tolist()
        
        # 清理问题
        cleaned_questions = []
        for i, q in enumerate(questions):
            q = q.strip()
            if q and len(q) > 5:
                cleaned_questions.append(q)
            else:
                print(f"⚠️ 跳过无效问题 {i+1}: {q}")
        
        print(f"✅ 从 quest500.xlsx 加载了 {len(cleaned_questions)} 个问题")
        return cleaned_questions
        
    except Exception as e:
        print(f"❌ 读取 quest500.xlsx 失败: {e}")
        return []

def main():
    """主函数"""
    print("🔄 问题集替换工具")
    print("=" * 50)
    
    # 1. 备份当前文件
    if not backup_current_file():
        return
    
    # 2. 加载quest500的问题
    quest_questions = load_quest500_questions()
    if not quest_questions:
        print("❌ 无法加载问题，退出")
        return
    
    # 3. 创建新文件
    output_file = "/data/hlt/A-visual/mark/500_question_answer.xlsx"
    create_new_question_file(quest_questions, output_file)
    
    print(f"\n🎉 问题集替换完成！")
    print(f"📊 从 {len(quest_questions)} 个问题替换到系统文件")
    print(f"📍 系统现在将使用这 {len(quest_questions)} 个问题进行抽取")
    
    # 4. 显示前5个问题预览
    print(f"\n📝 新问题集预览:")
    for i, q in enumerate(quest_questions[:5], 1):
        print(f"{i}. {q}")
    
    print(f"\n💡 提示:")
    print(f"1. 重启后端服务以使用新问题集")
    print(f"2. 在前端点击'重新抽取'测试新问题")
    print(f"3. 原文件已备份，如需恢复可使用备份文件")

if __name__ == "__main__":
    main()
