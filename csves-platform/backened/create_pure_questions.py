#!/usr/bin/env python3
"""
创建纯问题文件：从quest500.xlsx提取问题并创建纯问题文件
"""

import pandas as pd
import os

def extract_pure_questions():
    """提取纯问题列表"""
    quest_file = "/data/hlt/A-visual/mark/quest500.xlsx"
    output_file = "/data/hlt/A-visual/mark/pure_questions.xlsx"
    
    if not os.path.exists(quest_file):
        print(f"❌ 文件不存在: {quest_file}")
        return
    
    try:
        # 读取原始文件
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
        
        # 创建新的纯问题DataFrame
        pure_df = pd.DataFrame({
            '问题': cleaned_questions
        })
        
        # 保存为Excel
        pure_df.to_excel(output_file, index=False)
        
        print(f"✅ 纯问题文件已创建: {output_file}")
        print(f"📊 包含 {len(cleaned_questions)} 个问题")
        
        # 显示前5个问题
        print(f"\n📝 问题预览:")
        for i, q in enumerate(cleaned_questions[:5], 1):
            print(f"{i}. {q}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return None

def main():
    """主函数"""
    print("📝 纯问题文件创建工具")
    print("=" * 40)
    
    output_file = extract_pure_questions()
    
    if output_file:
        print(f"\n🎉 纯问题文件创建完成！")
        print(f"📁 文件位置: {output_file}")
        print(f"💡 你现在可以:")
        print(f"1. 在Excel中打开这个文件进行编辑")
        print(f"2. 添加你的431个问题")
        print(f"3. 使用替换工具更新系统问题集")

if __name__ == "__main__":
    main()
