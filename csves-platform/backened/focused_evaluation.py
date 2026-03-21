#!/usr/bin/env python3
"""
专注评估：针对3个指定模型，每次4个问题，共4组
计算500个问题组和91个问题组的评分和波动值
"""

import pandas as pd
import numpy as np
import requests
import json
import time
from datetime import datetime
import sys
import os

# 添加路径以导入后端模块
sys.path.append('/data/hlt/A-visual/bishework/backened')

def load_original_questions():
    """加载原始问题（91个）"""
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

def load_final_questions():
    """加载最终问题集（500个）"""
    final_file = "/data/hlt/A-visual/mark/社会主义核心价值观评估500个问题.xlsx"
    
    if not os.path.exists(final_file):
        print("❌ 最终问题文件不存在")
        return []
    
    try:
        df = pd.read_excel(final_file)
        first_col = df.columns[0]
        questions = df[first_col].dropna().astype(str).tolist()
        
        # 清理问题
        cleaned = []
        for q in questions:
            q = q.strip()
            if q and len(q) > 5:
                cleaned.append(q)
        
        print(f"✅ 加载最终问题: {len(cleaned)} 个")
        return cleaned
    except Exception as e:
        print(f"❌ 加载最终问题失败: {e}")
        return []

def call_frontend_evaluate_api(questions, models):
    """直接调用前端现成的/api/evaluate接口"""
    try:
        url = "http://localhost:8000/api/evaluate"
        
        # 构造请求数据（完全按照前端格式）
        data = {
            "questions": questions,
            "models": models
        }
        
        print(f"🤖 调用前端评估API...")
        print(f"   问题数量: {len(questions)}")
        print(f"   模型: {models}")
        print(f"   示例问题: {questions[0][:50]}...")
        
        response = requests.post(url, json=data, timeout=600)  # 10分钟超时
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ API调用成功")
                return result
            except json.JSONDecodeError:
                print(f"⚠️ 返回非JSON格式")
                print(f"   响应内容: {response.text[:200]}...")
                return None
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"   响应内容: {response.text[:300]}...")
            return None
            
    except Exception as e:
        print(f"❌ API调用异常: {e}")
        return None

def calculate_volatility(scores_list):
    """计算波动性指标"""
    if not scores_list or len(scores_list) < 2:
        return {
            'variance': 0,
            'std': 0,
            'cv': 0,
            'range': 0,
            'median': 0
        }
    
    scores_array = np.array(scores_list)
    variance = np.var(scores_array)
    std = np.std(scores_array)
    mean = np.mean(scores_array)
    cv = (std / mean) if mean != 0 else 0
    range_val = np.max(scores_array) - np.min(scores_array)
    median = np.median(scores_array)
    
    return {
        'variance': round(variance, 4),
        'std': round(std, 4),
        'cv': round(cv, 4),
        'range': round(range_val, 4),
        'median': round(median, 4)
    }

def run_focused_evaluation():
    """运行专注评估"""
    print("🧪 开始专注评估")
    print("=" * 80)
    print("🤖 针对5个指定模型：DeepSeek、GPT-4o、Qwen 2.5 7B、Qwen 2.5 32B、Qwen 2.5 72B")
    print("📊 每次4个问题，共4组（16个问题）")
    print("📈 分别评估500个问题组和91个问题组")
    print("📋 计算每个维度的波动值")
    print()
    
    # 加载问题
    original_questions = load_original_questions()
    final_questions = load_final_questions()
    
    if not original_questions or not final_questions:
        print("❌ 问题加载失败")
        return None
    
    # 指定的5个模型（使用前端实际名称）
    models = ["DeepSeek", "GPT-4o", "Qwen 2.5 7B", "Qwen 2.5 32B", "Qwen 2.5 72B"]
    
    # 每次处理4个问题，共4组（16个问题）
    questions_per_batch = 4
    num_batches = 4
    total_questions = questions_per_batch * num_batches
    
    # 确保有足够的问题
    orig_questions = original_questions[:min(total_questions, len(original_questions))]
    final_questions = final_questions[:min(total_questions, len(final_questions))]
    
    print(f"\n📊 测试配置:")
    print(f"   原始问题集: {len(original_questions)} 个问题")
    print(f"   最终问题集: {len(final_questions)} 个问题")
    print(f"   测试模型: {models}")
    print(f"   每批问题数: {questions_per_batch}")
    print(f"   批次数: {num_batches}")
    print(f"   总测试问题数: {total_questions}")
    print(f"   🔍 使用前端现成接口，获取真实数据...")
    
    dimensions = ['富强', '民主', '文明', '和谐', '自由', '平等', '公正', '法治', '爱国', '敬业', '诚信', '友善']
    
    all_results = {
        "original_results": {model: [] for model in models},
        "final_results": {model: [] for model in models},
        "volatility_analysis": {},
        "test_info": {
            "timestamp": datetime.now().isoformat(),
            "questions_per_batch": questions_per_batch,
            "num_batches": num_batches,
            "models": models,
            "original_total": len(original_questions),
            "final_total": len(final_questions)
        }
    }
    
    # 测试原始问题（91个问题组）
    print(f"\n🔍 测试原始问题（91个问题组）...")
    
    for batch_idx in range(num_batches):
        start_idx = batch_idx * questions_per_batch
        end_idx = start_idx + questions_per_batch
        batch_questions = orig_questions[start_idx:end_idx]
        
        print(f"\n📦 批次 {batch_idx + 1}/{num_batches} - 原始问题:")
        print(f"   问题范围: {start_idx + 1}-{end_idx}")
        print(f"   问题: {[q[:30] + '...' for q in batch_questions]}")
        
        for model in models:
            print(f"\n🤖 测试模型 {model} - 批次 {batch_idx + 1}:")
            
            # 调用前端API
            result = call_frontend_evaluate_api(batch_questions, [model])
            if result and 'qa_list' in result and 'scores' in result:
                qa_list = result['qa_list']
                scores = result['scores']
                
                # 存储结果
                for i, qa in enumerate(qa_list):
                    if i < len(batch_questions):
                        all_results["original_results"][model].append({
                            'batch': batch_idx + 1,
                            'question': batch_questions[i],
                            'model': model,
                            'answer': qa.get('answer', ''),
                            'scores': scores.copy()  # 所有问题使用相同的评分
                        })
                
                print(f"✅ 模型 {model} 批次 {batch_idx + 1} 完成，评分: {scores}")
            else:
                print(f"❌ 模型 {model} 批次 {batch_idx + 1} 失败")
            
            # 避免请求过快
            time.sleep(2)
    
    # 测试最终问题（500个问题组）
    print(f"\n🔍 测试最终问题（500个问题组）...")
    
    for batch_idx in range(num_batches):
        start_idx = batch_idx * questions_per_batch
        end_idx = start_idx + questions_per_batch
        batch_questions = final_questions[start_idx:end_idx]
        
        print(f"\n📦 批次 {batch_idx + 1}/{num_batches} - 最终问题:")
        print(f"   问题范围: {start_idx + 1}-{end_idx}")
        print(f"   问题: {[q[:30] + '...' for q in batch_questions]}")
        
        for model in models:
            print(f"\n🤖 测试模型 {model} - 批次 {batch_idx + 1}:")
            
            # 调用前端API
            result = call_frontend_evaluate_api(batch_questions, [model])
            if result and 'qa_list' in result and 'scores' in result:
                qa_list = result['qa_list']
                scores = result['scores']
                
                # 存储结果
                for i, qa in enumerate(qa_list):
                    if i < len(batch_questions):
                        all_results["final_results"][model].append({
                            'batch': batch_idx + 1,
                            'question': batch_questions[i],
                            'model': model,
                            'answer': qa.get('answer', ''),
                            'scores': scores.copy()  # 所有问题使用相同的评分
                        })
                
                print(f"✅ 模型 {model} 批次 {batch_idx + 1} 完成，评分: {scores}")
            else:
                print(f"❌ 模型 {model} 批次 {batch_idx + 1} 失败")
            
            # 避免请求过快
            time.sleep(2)
    
    # 计算波动性分析
    print(f"\n📈 计算波动性分析...")
    
    for model in models:
        orig_results = all_results["original_results"][model]
        final_results = all_results["final_results"][model]
        
        model_volatility = {}
        
        for dim in dimensions:
            # 原始问题该维度的所有评分
            orig_scores = [qa['scores'].get(dim, 0) for qa in orig_results]
            final_scores = [qa['scores'].get(dim, 0) for qa in final_results]
            
            # 计算波动性
            orig_vol = calculate_volatility(orig_scores)
            final_vol = calculate_volatility(final_scores)
            
            model_volatility[dim] = {
                'original': orig_vol,
                'final': final_vol,
                'volatility_change': round(final_vol['std'] - orig_vol['std'], 4),
                'volatility_improvement': 'stable' if final_vol['std'] <= orig_vol['std'] else 'more_volatile'
            }
        
        all_results["volatility_analysis"][model] = model_volatility
    
    return all_results

def create_focused_excel_report(results):
    """创建专注评估的Excel报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file = f"/data/hlt/A-visual/mark/focused_evaluation_report_{timestamp}.xlsx"
    
    print(f"\n📊 生成专注评估Excel报告: {excel_file}")
    
    dimensions = ['富强', '民主', '文明', '和谐', '自由', '平等', '公正', '法治', '爱国', '敬业', '诚信', '友善']
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        
        # 1. 原始问题详细得分（91个问题组）
        print("   📋 生成原始问题得分表（91个问题组）...")
        original_data = []
        
        for model, qa_list in results["original_results"].items():
            for i, qa in enumerate(qa_list, 1):
                row = {
                    "问题类型": "原始问题(91个)",
                    "模型": model,
                    "批次": qa["batch"],
                    "问题序号": i,
                    "问题内容": qa["question"],
                    "回答长度": len(qa["answer"]) if "answer" in qa else 0
                }
                
                # 添加各维度得分
                for dim in dimensions:
                    row[f"{dim}_得分"] = qa["scores"].get(dim, 0)
                
                # 添加总分
                total_score = sum(qa["scores"].values())
                row["总分"] = round(total_score / len(qa["scores"]), 2) if qa["scores"] else 0
                
                original_data.append(row)
        
        original_df = pd.DataFrame(original_data)
        original_df.to_excel(writer, sheet_name="原始问题得分_91组", index=False)
        
        # 2. 最终问题详细得分（500个问题组）
        print("   📋 生成最终问题得分表（500个问题组）...")
        final_data = []
        
        for model, qa_list in results["final_results"].items():
            for i, qa in enumerate(qa_list, 1):
                row = {
                    "问题类型": "最终问题(500个)",
                    "模型": model,
                    "批次": qa["batch"],
                    "问题序号": i,
                    "问题内容": qa["question"],
                    "回答长度": len(qa["answer"]) if "answer" in qa else 0
                }
                
                # 添加各维度得分
                for dim in dimensions:
                    row[f"{dim}_得分"] = qa["scores"].get(dim, 0)
                
                # 添加总分
                total_score = sum(qa["scores"].values())
                row["总分"] = round(total_score / len(qa["scores"]), 2) if qa["scores"] else 0
                
                final_data.append(row)
        
        final_df = pd.DataFrame(final_data)
        final_df.to_excel(writer, sheet_name="最终问题得分_500组", index=False)
        
        # 3. 各维度平均分对比
        print("   📊 生成维度平均分对比表...")
        comparison_data = []
        
        for model in results["original_results"].keys():
            # 原始问题各维度平均分
            orig_qa_list = results["original_results"][model]
            orig_avg_scores = {}
            for dim in dimensions:
                scores = [qa["scores"].get(dim, 0) for qa in orig_qa_list if qa["scores"]]
                orig_avg_scores[dim] = round(np.mean(scores), 2) if scores else 0
            
            # 最终问题各维度平均分
            final_qa_list = results["final_results"][model]
            final_avg_scores = {}
            for dim in dimensions:
                scores = [qa["scores"].get(dim, 0) for qa in final_qa_list if qa["scores"]]
                final_avg_scores[dim] = round(np.mean(scores), 2) if scores else 0
            
            # 创建对比行
            for dim in dimensions:
                orig_score = orig_avg_scores[dim]
                final_score = final_avg_scores[dim]
                improvement = final_score - orig_score
                improvement_percent = (improvement / orig_score * 100) if orig_score != 0 else 0
                
                comparison_data.append({
                    "模型": model,
                    "维度": dim,
                    "原始问题平均分": orig_score,
                    "最终问题平均分": final_score,
                    "分数提升": round(improvement, 2),
                    "提升百分比": round(improvement_percent, 2)
                })
        
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df.to_excel(writer, sheet_name="维度平均分对比", index=False)
        
        # 4. 波动性分析（重点！）
        print("   📈 生成波动性分析表...")
        volatility_data = []
        
        for model, model_vol in results["volatility_analysis"].items():
            for dim, vol_data in model_vol.items():
                orig_vol = vol_data['original']
                final_vol = vol_data['final']
                
                volatility_data.append({
                    "模型": model,
                    "维度": dim,
                    "原始问题标准差": orig_vol['std'],
                    "最终问题标准差": final_vol['std'],
                    "标准差变化": vol_data['volatility_change'],
                    "波动性改善": vol_data['volatility_improvement'],
                    "原始问题方差": orig_vol['variance'],
                    "最终问题方差": final_vol['variance'],
                    "原始问题变异系数": orig_vol['cv'],
                    "最终问题变异系数": final_vol['cv'],
                    "原始问题极差": orig_vol['range'],
                    "最终问题极差": final_vol['range']
                })
        
        volatility_df = pd.DataFrame(volatility_data)
        volatility_df.to_excel(writer, sheet_name="波动性分析", index=False)
        
        # 5. 批次分析
        print("   📦 生成批次分析表...")
        batch_data = []
        
        for model in results["original_results"].keys():
            # 按批次统计原始问题
            orig_batches = {}
            for qa in results["original_results"][model]:
                batch = qa["batch"]
                if batch not in orig_batches:
                    orig_batches[batch] = []
                total_score = sum(qa["scores"].values()) / len(qa["scores"]) if qa["scores"] else 0
                orig_batches[batch].append(total_score)
            
            # 按批次统计最终问题
            final_batches = {}
            for qa in results["final_results"][model]:
                batch = qa["batch"]
                if batch not in final_batches:
                    final_batches[batch] = []
                total_score = sum(qa["scores"].values()) / len(qa["scores"]) if qa["scores"] else 0
                final_batches[batch].append(total_score)
            
            # 创建批次统计
            for batch in range(1, 5):
                orig_scores = orig_batches.get(batch, [])
                final_scores = final_batches.get(batch, [])
                
                orig_avg = round(np.mean(orig_scores), 2) if orig_scores else 0
                final_avg = round(np.mean(final_scores), 2) if final_scores else 0
                
                batch_data.append({
                    "模型": model,
                    "批次": batch,
                    "原始问题平均总分": orig_avg,
                    "最终问题平均总分": final_avg,
                    "批次提升": round(final_avg - orig_avg, 2),
                    "原始问题数量": len(orig_scores),
                    "最终问题数量": len(final_scores)
                })
        
        batch_df = pd.DataFrame(batch_data)
        batch_df.to_excel(writer, sheet_name="批次分析", index=False)
        
        # 6. 总体统计摘要
        print("   📋 生成总体统计摘要...")
        summary_data = []
        
        for model in results["original_results"].keys():
            # 原始问题总体统计
            orig_qa_list = results["original_results"][model]
            orig_total_scores = [sum(qa["scores"].values()) / len(qa["scores"]) for qa in orig_qa_list if qa["scores"]]
            orig_avg_total = round(np.mean(orig_total_scores), 2) if orig_total_scores else 0
            orig_std_total = round(np.std(orig_total_scores), 2) if len(orig_total_scores) > 1 else 0
            
            # 最终问题总体统计
            final_qa_list = results["final_results"][model]
            final_total_scores = [sum(qa["scores"].values()) / len(qa["scores"]) for qa in final_qa_list if qa["scores"]]
            final_avg_total = round(np.mean(final_total_scores), 2) if final_total_scores else 0
            final_std_total = round(np.std(final_total_scores), 2) if len(final_total_scores) > 1 else 0
            
            summary_data.append({
                "模型": model,
                "原始问题平均总分": orig_avg_total,
                "最终问题平均总分": final_avg_total,
                "总分提升": round(final_avg_total - orig_avg_total, 2),
                "总分提升百分比": round((final_avg_total - orig_avg_total) / orig_avg_total * 100, 2) if orig_avg_total != 0 else 0,
                "原始问题总分标准差": orig_std_total,
                "最终问题总分标准差": final_std_total,
                "总分标准差变化": round(final_std_total - orig_std_total, 2),
                "原始问题总数": results["test_info"]["original_total"],
                "最终问题总数": results["test_info"]["final_total"],
                "实际测试原始问题": len(orig_qa_list),
                "实际测试最终问题": len(final_qa_list)
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name="总体统计摘要", index=False)
    
    print(f"✅ 专注评估Excel报告已生成: {excel_file}")
    return excel_file

def main():
    """主函数"""
    print("🧪 专注评估工具")
    print("=" * 80)
    print("🤖 针对5个指定模型：DeepSeek、GPT-4o、Qwen 2.5 7B、Qwen 2.5 32B、Qwen 2.5 72B")
    print("📊 每次4个问题，共4组（16个问题）")
    print("📈 分别评估500个问题组和91个问题组")
    print("📋 计算每个维度的波动值")
    print("⚠️  使用前端现成接口，获取真实数据")
    print()
    
    # 运行测试
    results = run_focused_evaluation()
    
    if results:
        # 生成Excel报告
        excel_file = create_focused_excel_report(results)
        
        print(f"\n🎉 专注评估完成！")
        print(f"📊 Excel报告: {excel_file}")
        print(f"\n📋 报告包含以下工作表:")
        print(f"   1. 原始问题得分_91组 - 91个问题组的真实API评估得分")
        print(f"   2. 最终问题得分_500组 - 500个问题组的真实API评估得分")
        print(f"   3. 维度平均分对比 - 各维度平均分对比")
        print(f"   4. 波动性分析 - 重点！标准差、方差、变异系数等波动指标")
        print(f"   5. 批次分析 - 每批次的详细分析")
        print(f"   6. 总体统计摘要 - 总体统计对比")
        
        # 显示简要统计
        test_info = results["test_info"]
        print(f"\n📊 测试统计:")
        print(f"   原始问题集: {test_info['original_total']} 个问题")
        print(f"   最终问题集: {test_info['final_total']} 个问题")
        print(f"   测试模型数: {len(test_info['models'])}")
        print(f"   每批问题数: {test_info['questions_per_batch']}")
        print(f"   批次数: {test_info['num_batches']}")
        print(f"   总测试数量: {len(test_info['models']) * test_info['questions_per_batch'] * test_info['num_batches'] * 2}")
        
        # 显示成功评估数量
        total_original = sum(len(qa_list) for qa_list in results["original_results"].values())
        total_final = sum(len(qa_list) for qa_list in results["final_results"].values())
        print(f"\n✅ 成功评估统计:")
        print(f"   原始问题成功评估: {total_original} 个")
        print(f"   最终问题成功评估: {total_final} 个")
        print(f"   总计成功评估: {total_original + total_final} 个")
        
        if total_original + total_final > 0:
            print(f"\n🎉 使用前端现成接口，获取真实模型回答和评分！")
            print(f"📈 包含详细的波动性分析（标准差、方差、变异系数等）")
            print(f"📦 包含批次分析，可以观察不同批次的表现")
        else:
            print(f"\n⚠️  API调用失败，无法获取真实评分")
    
    else:
        print("❌ 测试失败")

if __name__ == "__main__":
    main()
