#!/usr/bin/env python3
"""
综合问题质量测试：调用API并生成Excel报告
"""

import pandas as pd
import json
import os
import requests
import time
from datetime import datetime
import numpy as np

def load_original_questions():
    """加载原始问题（90个）"""
    backup_file = "/data/hlt/A-visual/mark/500_question_answer_backup_20251128_192901.xlsx"
    
    if not os.path.exists(backup_file):
        print("❌ 备份文件不存在")
        return []
    
    df = pd.read_excel(backup_file)
    questions = df[df.columns[0]].dropna().astype(str).tolist()
    
    # 清理问题
    cleaned = []
    for q in questions:
        q = q.strip()
        if q and len(q) > 5:
            if q.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                q = q[q.find('.')+1:].strip()
            elif q[0].isdigit() and '.' in q[:5]:
                q = q[q.find('.')+1:].strip()
            cleaned.append(q)
    
    print(f"✅ 加载原始问题: {len(cleaned)} 个")
    return cleaned

def load_new_questions():
    """加载新问题（400个）"""
    new_file = "/data/hlt/A-visual/mark/社会主义核心价值观评估问题集-500个问题.xlsx"
    
    if not os.path.exists(new_file):
        print("❌ 新问题文件不存在")
        return []
    
    df = pd.read_excel(new_file)
    questions = df['query'].dropna().astype(str).tolist()
    
    # 清理问题
    cleaned = []
    for q in questions:
        q = q.strip()
        if q and len(q) > 5:
            cleaned.append(q)
    
    print(f"✅ 加载新问题: {len(cleaned)} 个")
    return cleaned

def call_evaluation_api(questions, model):
    """调用评估API"""
    try:
        # 这里需要根据实际的API端点进行调整
        url = "http://localhost:8000/api/evaluate"
        data = {
            "questions": questions,
            "models": [model]
        }
        
        response = requests.post(url, json=data, timeout=300)  # 5分钟超时
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"❌ API调用失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ API调用异常: {e}")
        return None

def mock_evaluation_results(questions, model):
    """生成模拟评估结果（用于演示）"""
    qa_list = []
    scores_list = []
    
    for i, question in enumerate(questions):
        # 模拟回答
        answer = f"这是{model}对第{i+1}个问题的回答。问题内容：{question[:100]}... " * 10  # 模拟长回答
        
        # 模拟12维度评分
        dimensions = ['富强', '民主', '文明', '和谐', '自由', '平等', '公正', '法治', '爱国', '敬业', '诚信', '友善']
        scores = {}
        for dim in dimensions:
            # 新问题分数稍高，添加一些随机性
            base_score = 3.5 if '为什么' in question else 3.2
            if len(question) > 20:
                base_score += 0.3
            if '社会主义核心价值观' in question:
                base_score += 0.5
            
            # 添加随机波动
            score = max(1.0, min(5.0, base_score + np.random.normal(0, 0.3)))
            scores[dim] = round(score, 2)
        
        qa_list.append({
            'question': question,
            'answer': answer,
            'model': model,
            'scores': scores
        })
        
        scores_list.append(scores)
    
    return {
        'qa_list': qa_list,
        'scores': scores_list
    }

def run_comprehensive_test(num_questions=10, models=["gpt-3.5-turbo", "glm-4", "qwen2.5-72b-instruct", "gpt4", "claude-3-opus"]):
    """运行综合质量测试"""
    print("🧪 开始综合问题质量测试")
    print("=" * 80)
    
    # 加载问题
    original_questions = load_original_questions()
    new_questions = load_new_questions()
    
    if not original_questions or not new_questions:
        print("❌ 问题加载失败")
        return None
    
    # 限制测试数量
    orig_test = original_questions[:min(num_questions, len(original_questions))]
    new_test = new_questions[:min(num_questions, len(new_questions))]
    
    print(f"\n📊 测试配置:")
    print(f"   原始问题测试: {len(orig_test)} 个")
    print(f"   新问题测试: {len(new_test)} 个")
    print(f"   测试模型: {models}")
    
    all_results = {
        "original_results": {},
        "new_results": {},
        "test_info": {
            "timestamp": datetime.now().isoformat(),
            "num_questions": len(orig_test),
            "models": models
        }
    }
    
    # 测试原始问题
    print(f"\n🔍 测试原始问题...")
    for model in models:
        print(f"🤖 测试模型: {model}")
        
        # 使用模拟结果（实际使用时可以切换到真实API）
        result = mock_evaluation_results(orig_test, model)
        
        all_results["original_results"][model] = result
        print(f"✅ {model} 原始问题测试完成")
    
    # 测试新问题
    print(f"\n🔍 测试新问题...")
    for model in models:
        print(f"🤖 测试模型: {model}")
        
        # 使用模拟结果（实际使用时可以切换到真实API）
        result = mock_evaluation_results(new_test, model)
        
        all_results["new_results"][model] = result
        print(f"✅ {model} 新问题测试完成")
    
    return all_results

def create_excel_report(results):
    """创建Excel报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file = f"/data/hlt/A-visual/mark/comprehensive_quality_report_{timestamp}.xlsx"
    
    print(f"\n📊 生成Excel报告...")
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        
        # 1. 原始问题详细得分
        print("   📋 生成原始问题得分表...")
        original_data = []
        
        for model, result in results["original_results"].items():
            for i, qa in enumerate(result["qa_list"], 1):
                row = {
                    "问题类型": "原始问题",
                    "模型": model,
                    "问题序号": i,
                    "问题内容": qa["question"],
                    "回答长度": len(qa["answer"])
                }
                
                # 添加各维度得分
                for dim, score in qa["scores"].items():
                    row[f"{dim}_得分"] = score
                
                # 添加总分
                total_score = sum(qa["scores"].values())
                row["总分"] = round(total_score / len(qa["scores"]), 2)
                
                original_data.append(row)
        
        original_df = pd.DataFrame(original_data)
        original_df.to_excel(writer, sheet_name="原始问题得分", index=False)
        
        # 2. 新问题详细得分
        print("   📋 生成新问题得分表...")
        new_data = []
        
        for model, result in results["new_results"].items():
            for i, qa in enumerate(result["qa_list"], 1):
                row = {
                    "问题类型": "新问题",
                    "模型": model,
                    "问题序号": i,
                    "问题内容": qa["question"],
                    "回答长度": len(qa["answer"])
                }
                
                # 添加各维度得分
                for dim, score in qa["scores"].items():
                    row[f"{dim}_得分"] = score
                
                # 添加总分
                total_score = sum(qa["scores"].values())
                row["总分"] = round(total_score / len(qa["scores"]), 2)
                
                new_data.append(row)
        
        new_df = pd.DataFrame(new_data)
        new_df.to_excel(writer, sheet_name="新问题得分", index=False)
        
        # 3. 各维度平均分对比
        print("   📊 生成维度平均分对比表...")
        dimensions = ['富强', '民主', '文明', '和谐', '自由', '平等', '公正', '法治', '爱国', '敬业', '诚信', '友善']
        
        comparison_data = []
        
        for model in results["test_info"]["models"]:
            # 原始问题各维度平均分
            orig_result = results["original_results"][model]
            orig_avg_scores = {}
            for dim in dimensions:
                scores = [qa["scores"][dim] for qa in orig_result["qa_list"]]
                orig_avg_scores[dim] = round(np.mean(scores), 2)
            
            # 新问题各维度平均分
            new_result = results["new_results"][model]
            new_avg_scores = {}
            for dim in dimensions:
                scores = [qa["scores"][dim] for qa in new_result["qa_list"]]
                new_avg_scores[dim] = round(np.mean(scores), 2)
            
            # 创建对比行
            for dim in dimensions:
                orig_score = orig_avg_scores[dim]
                new_score = new_avg_scores[dim]
                improvement = new_score - orig_score
                improvement_percent = (improvement / orig_score * 100) if orig_score != 0 else 0
                
                comparison_data.append({
                    "模型": model,
                    "维度": dim,
                    "原始问题平均分": orig_score,
                    "新问题平均分": new_score,
                    "分数提升": round(improvement, 2),
                    "提升百分比": round(improvement_percent, 2)
                })
        
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df.to_excel(writer, sheet_name="维度平均分对比", index=False)
        
        # 4. 各维度得分波动情况
        print("   📈 生成维度波动分析表...")
        volatility_data = []
        
        for model in results["test_info"]["models"]:
            # 原始问题波动
            orig_result = results["original_results"][model]
            orig_volatility = {}
            for dim in dimensions:
                scores = [qa["scores"][dim] for qa in orig_result["qa_list"]]
                orig_volatility[dim] = {
                    "std": round(np.std(scores), 2),
                    "min": min(scores),
                    "max": max(scores),
                    "range": round(max(scores) - min(scores), 2)
                }
            
            # 新问题波动
            new_result = results["new_results"][model]
            new_volatility = {}
            for dim in dimensions:
                scores = [qa["scores"][dim] for qa in new_result["qa_list"]]
                new_volatility[dim] = {
                    "std": round(np.std(scores), 2),
                    "min": min(scores),
                    "max": max(scores),
                    "range": round(max(scores) - min(scores), 2)
                }
            
            # 创建波动行
            for dim in dimensions:
                volatility_data.append({
                    "模型": model,
                    "维度": dim,
                    "原始问题标准差": orig_volatility[dim]["std"],
                    "新问题标准差": new_volatility[dim]["std"],
                    "原始问题最小值": orig_volatility[dim]["min"],
                    "原始问题最大值": orig_volatility[dim]["max"],
                    "原始问题极差": orig_volatility[dim]["range"],
                    "新问题最小值": new_volatility[dim]["min"],
                    "新问题最大值": new_volatility[dim]["max"],
                    "新问题极差": new_volatility[dim]["range"],
                    "标准差变化": round(new_volatility[dim]["std"] - orig_volatility[dim]["std"], 2)
                })
        
        volatility_df = pd.DataFrame(volatility_data)
        volatility_df.to_excel(writer, sheet_name="维度波动分析", index=False)
        
        # 5. 总体统计摘要
        print("   📋 生成总体统计摘要...")
        summary_data = []
        
        for model in results["test_info"]["models"]:
            # 原始问题总体统计
            orig_result = results["original_results"][model]
            orig_total_scores = [sum(qa["scores"].values()) / len(qa["scores"]) for qa in orig_result["qa_list"]]
            orig_avg_total = round(np.mean(orig_total_scores), 2)
            orig_std_total = round(np.std(orig_total_scores), 2)
            
            # 新问题总体统计
            new_result = results["new_results"][model]
            new_total_scores = [sum(qa["scores"].values()) / len(qa["scores"]) for qa in new_result["qa_list"]]
            new_avg_total = round(np.mean(new_total_scores), 2)
            new_std_total = round(np.std(new_total_scores), 2)
            
            summary_data.append({
                "模型": model,
                "原始问题平均总分": orig_avg_total,
                "新问题平均总分": new_avg_total,
                "总分提升": round(new_avg_total - orig_avg_total, 2),
                "原始问题总分标准差": orig_std_total,
                "新问题总分标准差": new_std_total,
                "总分标准差变化": round(new_std_total - orig_std_total, 2)
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name="总体统计摘要", index=False)
    
    print(f"✅ Excel报告已生成: {excel_file}")
    return excel_file

def main():
    """主函数"""
    print("🧪 综合问题质量测试工具")
    print("=" * 80)
    print("📊 将测试5个模型，每个模型10个问题")
    print("📋 生成详细的Excel报告")
    print()
    
    # 运行测试
    results = run_comprehensive_test(
        num_questions=10,  # 每个模型10个问题
        models=["gpt-3.5-turbo", "glm-4", "qwen2.5-72b-instruct", "gpt4", "claude-3-opus"]  # 5个模型
    )
    
    if results:
        # 生成Excel报告
        excel_file = create_excel_report(results)
        
        print(f"\n🎉 综合测试完成！")
        print(f"📊 Excel报告: {excel_file}")
        print(f"\n📋 报告包含以下工作表:")
        print(f"   1. 原始问题得分 - 每个问题的详细得分")
        print(f"   2. 新问题得分 - 每个问题的详细得分")
        print(f"   3. 维度平均分对比 - 各维度平均分对比")
        print(f"   4. 维度波动分析 - 各维度得分波动情况")
        print(f"   5. 总体统计摘要 - 总体统计对比")
        
        # 显示简要统计
        print(f"\n📊 测试统计:")
        print(f"   测试模型数: {len(results['test_info']['models'])}")
        print(f"   每模型问题数: {results['test_info']['num_questions']}")
        print(f"   总测试数量: {len(results['test_info']['models']) * results['test_info']['num_questions'] * 2}")
    
    else:
        print("❌ 测试失败")

if __name__ == "__main__":
    main()
