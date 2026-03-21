#!/usr/bin/env python3
"""
分析去重详情脚本
"""

import pandas as pd
import os

def analyze_deduplication():
    """分析去重详情"""
    print("🔍 去重详情分析")
    print("=" * 50)
    
    # 加载原始问题
    original_file = "/data/hlt/A-visual/mark/500_question_answer_backup_20251128_192901.xlsx"
    if os.path.exists(original_file):
        df_orig = pd.read_excel(original_file)
        original_questions = df_orig[df_orig.columns[0]].dropna().astype(str).tolist()
        
        # 清理原始问题
        cleaned_orig = []
        for q in original_questions:
            q = q.strip()
            if q and len(q) > 5:
                if q.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                    q = q[q.find('.')+1:].strip()
                elif q[0].isdigit() and '.' in q[:5]:
                    q = q[q.find('.')+1:].strip()
                cleaned_orig.append(q)
        
        print(f"📊 原始问题: {len(cleaned_orig)} 个")
    else:
        print("❌ 备份文件不存在")
        return
    
    # 加载新问题
    new_file = "/data/hlt/A-visual/mark/社会主义核心价值观评估问题集-500个问题.xlsx"
    if os.path.exists(new_file):
        df_new = pd.read_excel(new_file)
        new_questions = df_new['query'].dropna().astype(str).tolist()
        
        # 清理新问题
        cleaned_new = []
        for q in new_questions:
            q = q.strip()
            if q and len(q) > 5:
                cleaned_new.append(q)
        
        print(f"📊 新问题: {len(cleaned_new)} 个")
    else:
        print("❌ 新问题文件不存在")
        return
    
    # 查找重复问题
    print(f"\n🔍 查找重复问题...")
    duplicates = []
    new_only = []
    orig_only = []
    
    new_set = set(cleaned_new)
    orig_set = set(cleaned_orig)
    
    # 找出重复的问题
    for q in cleaned_new:
        if q in orig_set:
            duplicates.append(q)
        else:
            new_only.append(q)
    
    # 找出只在原始问题中的
    for q in cleaned_orig:
        if q not in new_set:
            orig_only.append(q)
    
    print(f"📊 去重统计:")
    print(f"   重复问题: {len(duplicates)} 个")
    print(f"   仅新问题: {len(new_only)} 个")
    print(f"   仅原问题: {len(orig_only)} 个")
    print(f"   合并总数: {len(duplicates) + len(new_only) + len(orig_only)} 个")
    
    # 显示重复问题
    if duplicates:
        print(f"\n🔄 重复的问题 ({len(duplicates)} 个):")
        for i, q in enumerate(duplicates[:10], 1):  # 只显示前10个
            print(f"   {i}. {q}")
        if len(duplicates) > 10:
            print(f"   ... 还有 {len(duplicates) - 10} 个重复问题")
    
    # 显示文件位置
    print(f"\n📁 文件位置:")
    print(f"   当前系统问题集: /data/hlt/A-visual/mark/500_question_answer.xlsx")
    print(f"   原始问题备份: /data/hlt/A-visual/mark/500_question_answer_backup_20251128_192901.xlsx")
    print(f"   新问题源文件: /data/hlt/A-visual/mark/社会主义核心价值观评估问题集-500个问题.xlsx")
    print(f"   临时合并文件: /data/hlt/A-visual/mark/merged_questions_temp.xlsx")
    
    return {
        'duplicates': duplicates,
        'new_only': new_only,
        'orig_only': orig_only,
        'total_merged': len(duplicates) + len(new_only) + len(orig_only)
    }

def show_current_file_sample():
    """显示当前文件样本"""
    print(f"\n📝 当前系统问题集样本:")
    current_file = "/data/hlt/A-visual/mark/500_question_answer.xlsx"
    
    if os.path.exists(current_file):
        df = pd.read_excel(current_file)
        questions = df[df.columns[0]].dropna().astype(str).tolist()
        
        print(f"📊 总问题数: {len(questions)}")
        print(f"📋 前5个问题:")
        for i, q in enumerate(questions[:5], 1):
            print(f"   {i}. {q}")
        
        print(f"📋 后5个问题:")
        for i, q in enumerate(questions[-5:], len(questions)-4):
            print(f"   {i}. {q}")

if __name__ == "__main__":
    result = analyze_deduplication()
    show_current_file_sample()
