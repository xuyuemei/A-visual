#!/usr/bin/env python3
"""
批量测试脚本：对比原始问题vs修改后问题的回答质量
"""

import json
import time
import os
import sys
from datetime import datetime
from app.services.evaluation_service import evaluate_questions
from app.services.question_service_v2 import extract_questions_original, extract_questions_reserved, get_question_stats
from app.utils.database import get_db_connection

def run_comparison_test(num_questions=10, models=["gpt-3.5-turbo", "glm-4"]):
    """
    运行对比测试
    
    Args:
        num_questions: 测试问题数量
        models: 测试的模型列表
    """
    print("🚀 开始对比测试...")
    print(f"📊 测试问题数量: {num_questions}")
    print(f"🤖 测试模型: {models}")
    
    # 获取问题统计
    stats = get_question_stats()
    print(f"\n📈 问题库统计:")
    print(f"原始问题: {stats.get('original', {}).get('total', 0)} 个")
    print(f"保留问题: {stats.get('reserved', {}).get('total', 0)} 个")
    
    results = {
        "test_info": {
            "timestamp": datetime.now().isoformat(),
            "num_questions": num_questions,
            "models": models,
            "stats": stats
        },
        "original_results": {},
        "reserved_results": {},
        "comparison": {}
    }
    
    # 测试原始问题
    print(f"\n🔍 测试原始问题...")
    try:
        original_questions = extract_questions_original(num_questions)
        print(f"✅ 抽取原始问题: {len(original_questions)} 个")
        
        for model in models:
            print(f"🤖 测试模型: {model}")
            try:
                start_time = time.time()
                original_result = evaluate_questions(original_questions, [model])
                end_time = time.time()
                
                results["original_results"][model] = {
                    "questions": original_questions,
                    "qa_list": original_result["qa_list"],
                    "scores": original_result["scores"],
                    "time_taken": end_time - start_time,
                    "avg_score": sum(original_result["scores"]) / len(original_result["scores"])
                }
                print(f"✅ {model} 原始问题测试完成，平均分: {results['original_results'][model]['avg_score']:.3f}")
                
            except Exception as e:
                print(f"❌ {model} 原始问题测试失败: {e}")
                results["original_results"][model] = {"error": str(e)}
                
    except Exception as e:
        print(f"❌ 原始问题抽取失败: {e}")
        results["original_results"] = {"error": str(e)}
    
    # 测试保留问题
    print(f"\n🔍 测试保留问题...")
    try:
        reserved_questions = extract_questions_reserved(num_questions)
        print(f"✅ 抽取保留问题: {len(reserved_questions)} 个")
        
        for model in models:
            print(f"🤖 测试模型: {model}")
            try:
                start_time = time.time()
                reserved_result = evaluate_questions(reserved_questions, [model])
                end_time = time.time()
                
                results["reserved_results"][model] = {
                    "questions": reserved_questions,
                    "qa_list": reserved_result["qa_list"],
                    "scores": reserved_result["scores"],
                    "time_taken": end_time - start_time,
                    "avg_score": sum(reserved_result["scores"]) / len(reserved_result["scores"])
                }
                print(f"✅ {model} 保留问题测试完成，平均分: {results['reserved_results'][model]['avg_score']:.3f}")
                
            except Exception as e:
                print(f"❌ {model} 保留问题测试失败: {e}")
                results["reserved_results"][model] = {"error": str(e)}
                
    except Exception as e:
        print(f"❌ 保留问题抽取失败: {e}")
        results["reserved_results"] = {"error": str(e)}
    
    # 生成对比分析
    print(f"\n📊 生成对比分析...")
    for model in models:
        if model in results["original_results"] and model in results["reserved_results"]:
            orig = results["original_results"][model]
            res = results["reserved_results"][model]
            
            if "avg_score" in orig and "avg_score" in res:
                score_improvement = res["avg_score"] - orig["avg_score"]
                improvement_percent = (score_improvement / orig["avg_score"]) * 100 if orig["avg_score"] != 0 else 0
                
                results["comparison"][model] = {
                    "original_avg_score": orig["avg_score"],
                    "reserved_avg_score": res["avg_score"],
                    "score_improvement": score_improvement,
                    "improvement_percent": improvement_percent,
                    "original_time": orig.get("time_taken", 0),
                    "reserved_time": res.get("time_taken", 0)
                }
                
                print(f"📈 {model} 对比结果:")
                print(f"   原始问题平均分: {orig['avg_score']:.3f}")
                print(f"   保留问题平均分: {res['avg_score']:.3f}")
                print(f"   分数提升: {score_improvement:+.3f} ({improvement_percent:+.2f}%)")
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/data/hlt/A-visual/csves-platform/backened/test_results_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 测试完成！结果已保存到: {output_file}")
    print(f"📊 详细对比数据已保存，可用于进一步分析")
    
    return results

def save_test_summary(results, output_file="/data/hlt/A-visual/csves-platform/backened/test_summary.txt"):
    """保存测试摘要"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("🧪 问题质量对比测试摘要\n")
        f.write("=" * 50 + "\n\n")
        
        test_info = results.get("test_info", {})
        f.write(f"测试时间: {test_info.get('timestamp', '未知')}\n")
        f.write(f"测试问题数量: {test_info.get('num_questions', 0)}\n")
        f.write(f"测试模型: {', '.join(test_info.get('models', []))}\n\n")
        
        comparison = results.get("comparison", {})
        for model, comp in comparison.items():
            f.write(f"🤖 模型: {model}\n")
            f.write(f"   原始问题平均分: {comp.get('original_avg_score', 0):.3f}\n")
            f.write(f"   保留问题平均分: {comp.get('reserved_avg_score', 0):.3f}\n")
            f.write(f"   分数提升: {comp.get('score_improvement', 0):+.3f}\n")
            f.write(f"   提升百分比: {comp.get('improvement_percent', 0):+.2f}%\n\n")
    
    print(f"📋 测试摘要已保存到: {output_file}")

def main():
    """主函数"""
    print("🧪 问题质量对比测试工具")
    print("=" * 50)
    
    # 检查保留问题文件是否存在
    if not os.path.exists("/data/hlt/A-visual/csves-platform/backened/reserved_questions.json"):
        print("❌ 未找到保留问题文件，请先运行 import_questions.py")
        print("💡 运行命令: python import_questions.py")
        return
    
    # 运行测试
    try:
        results = run_comparison_test(
            num_questions=5,  # 测试5个问题，可以调整
            models=["gpt-3.5-turbo"]  # 可以添加更多模型
        )
        
        # 保存摘要
        save_test_summary(results)
        
        print("\n🎯 测试建议:")
        print("1. 如果保留问题的平均分显著高于原始问题，说明问题质量有提升")
        print("2. 可以增加测试问题数量获得更稳定的结果")
        print("3. 可以添加更多模型进行对比测试")
        print("4. 查看详细的JSON结果文件分析每个问题的具体表现")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
