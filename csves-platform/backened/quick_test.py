#!/usr/bin/env python3
"""
快速对比测试脚本：直接测试原问题vs新问题
"""

import sys
import os
sys.path.append('/data/hlt/A-visual/bishework/backened')

from complete_migration_plan import QuestionMigrationManager

def quick_test():
    """快速测试"""
    print("⚡ 快速对比测试")
    print("=" * 40)
    
    manager = QuestionMigrationManager()
    
    # 检查文件
    if not os.path.exists(manager.original_file):
        print(f"❌ 原始问题文件不存在: {manager.original_file}")
        return
    
    if not os.path.exists(manager.new_file):
        print(f"❌ 新问题文件不存在: {manager.new_file}")
        return
    
    print("✅ 文件检查通过")
    
    # 加载问题
    orig_questions = manager.load_original_questions()
    new_questions = manager.load_new_questions()
    
    print(f"📊 原始问题: {len(orig_questions)} 个")
    print(f"📊 新问题: {len(new_questions)} 个")
    
    # 运行测试
    print("\n🧪 开始对比测试...")
    results = manager.run_comparison_test(
        num_questions=3,  # 快速测试3个问题
        models=["gpt-3.5-turbo"]
    )
    
    if results:
        # 保存结果
        result_file = manager.save_results(results, "quick_test_results.json")
        summary_file = manager.generate_summary_report(results)
        
        print(f"\n🎉 快速测试完成！")
        print(f"📋 查看摘要: {summary_file}")
        
        # 显示简要结果
        comparison = results.get("comparison", {})
        for model, comp in comparison.items():
            improvement = comp.get('improvement_percent', 0)
            print(f"\n📈 {model} 测试结果:")
            print(f"   分数提升: {comp.get('score_improvement', 0):+.3f}")
            print(f"   提升百分比: {improvement:+.2f}%")
            
            if improvement > 5:
                print("   ✅ 新问题质量显著提升！")
            elif improvement > 0:
                print("   📈 新问题质量有所提升")
            else:
                print("   ⚠️ 新问题质量无明显提升")
    else:
        print("❌ 测试失败")

if __name__ == "__main__":
    quick_test()
