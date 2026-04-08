#!/usr/bin/env python3
"""
导入标注了"保留"的问题到评估系统
"""

import pandas as pd
import json
import os
from pathlib import Path

def load_reserved_questions(file_path):
    """
    从Excel文件中加载问题（当前格式：第一列是问题，其他列是模型回答）
    
    Args:
        file_path: Excel文件路径
        
    Returns:
        list: 问题列表
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    print(f"📖 正在读取文件: {file_path}")
    df = pd.read_excel(file_path)
    print(f"✅ 文件读取完成，共 {len(df)} 行")
    print(f"📋 列名: {df.columns.tolist()}")
    
    # 第一列是问题
    question_col = df.columns[0]
    print(f"📍 问题列: {question_col}")
    
    # 获取所有问题
    questions = df[question_col].dropna().astype(str).tolist()
    
    # 清理问题文本
    cleaned_questions = []
    for i, q in enumerate(questions):
        q = q.strip()
        if q and len(q) > 5:  # 过滤太短的问题
            # 移除可能的序号前缀
            if q.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                q = q[q.find('.')+1:].strip()
            elif q[0].isdigit() and '.' in q[:5]:
                q = q[q.find('.')+1:].strip()
            
            cleaned_questions.append(q)
        else:
            print(f"⚠️ 跳过无效问题 {i+1}: {q}")
    
    print(f"🎯 最终有效问题数量: {len(cleaned_questions)}")
    return cleaned_questions

def save_questions_to_json(questions, output_path):
    """保存问题到JSON文件"""
    data = {
        "questions": questions,
        "count": len(questions),
        "source": "马院修改版500问题集",
        "status": "保留"
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 问题已保存到: {output_path}")

def main():
    """主函数"""
    # 输入文件路径 - 你需要提供标注了保留/删除的Excel文件
    input_file = "/data/hlt/A-visual/mark/500_question_answer.xlsx"  # 请替换为实际文件路径
    
    # 输出JSON文件路径
    output_file = "/data/hlt/A-visual/csves-platform/backened/reserved_questions.json"
    
    try:
        # 加载保留的问题
        questions = load_reserved_questions(input_file)
        
        # 保存到JSON文件
        save_questions_to_json(questions, output_file)
        
        print("\n🎉 问题导入完成！")
        print(f"📊 总共导入了 {len(questions)} 个保留的问题")
        print(f"📁 问题文件保存在: {output_file}")
        
        # 显示前5个问题作为预览
        print("\n📝 问题预览:")
        for i, q in enumerate(questions[:5], 1):
            print(f"{i}. {q[:100]}...")
            
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        print("请检查文件路径和格式是否正确")

if __name__ == "__main__":
    main()
