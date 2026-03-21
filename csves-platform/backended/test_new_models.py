#!/usr/bin/env python3
"""
测试新模型：Qwen2.5-72B-Instruct和Qwen2.5-32B-Instruct
然后和之前的Excel数据合并
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

def run_new_models_test():
    """运行新模型测试"""
    print("🧪 开始新模型测试")
    print("=" * 80)
    print("🤖 针对2个新模型：Qwen2.5-72B-Instruct、Qwen2.5-32B-Instruct")
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
    
    # 新的2个模型
    models = ["Qwen 2.5 32B", "Qwen 2.5 72B"]
    
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

def merge_with_existing_data(new_results):
    """和之前的数据合并"""
    print(f"\n🔄 合并新旧数据...")
    
    # 读取之前的数据
    existing_batch_file = "/data/hlt/A-visual/mark/batch_volatility_analysis.xlsx"
    existing_model_file = "/data/hlt/A-visual/mark/model_batch_volatility.xlsx"
    
    # 读取现有的批次波动值数据
    if os.path.exists(existing_batch_file):
        orig_volatility = pd.read_excel(existing_batch_file, sheet_name='原始问题波动值')
        final_volatility = pd.read_excel(existing_batch_file, sheet_name='最终问题波动值')
    else:
        print("❌ 找不到现有的批次波动值文件")
        return
    
    # 读取现有的模型批次波动值数据
    if os.path.exists(existing_model_file):
        orig_model_volatility = pd.read_excel(existing_model_file, sheet_name='原始问题模型波动')
        final_model_volatility = pd.read_excel(existing_model_file, sheet_name='最终问题模型波动')
        comparison_df = pd.read_excel(existing_model_file, sheet_name='模型波动对比')
    else:
        print("❌ 找不到现有的模型波动值文件")
        return
    
    # 计算新模型的波动值数据
    dimensions = ['富强', '民主', '文明', '和谐', '自由', '平等', '公正', '法治', '爱国', '敬业', '诚信', '友善']
    
    # 计算新模型的批次波动值
    new_orig_volatility = []
    new_final_volatility = []
    
    for model in new_results["original_results"].keys():
        # 原始问题波动值
        for dim in dimensions:
            orig_scores = [qa['scores'].get(dim, 0) for qa in new_results["original_results"][model]]
            final_scores = [qa['scores'].get(dim, 0) for qa in new_results["final_results"][model]]
            
            if len(orig_scores) >= 2:
                orig_vol = calculate_volatility(orig_scores)
                new_orig_volatility.append({
                    '问题类型': '原始问题',
                    '模型': model,
                    '维度': dim,
                    '批次数量': len(orig_scores),
                    '均分': round(np.mean(orig_scores), 4),
                    '标准差': orig_vol['std'],
                    '方差': orig_vol['variance'],
                    '变异系数': orig_vol['cv'],
                    '极差': orig_vol['range'],
                    '最小值': orig_vol['min'] if 'min' in orig_vol else round(np.min(orig_scores), 4),
                    '最大值': orig_vol['max'] if 'max' in orig_vol else round(np.max(orig_scores), 4)
                })
            
            if len(final_scores) >= 2:
                final_vol = calculate_volatility(final_scores)
                new_final_volatility.append({
                    '问题类型': '最终问题',
                    '模型': model,
                    '维度': dim,
                    '批次数量': len(final_scores),
                    '均分': round(np.mean(final_scores), 4),
                    '标准差': final_vol['std'],
                    '方差': final_vol['variance'],
                    '变异系数': final_vol['cv'],
                    '极差': final_vol['range'],
                    '最小值': final_vol['min'] if 'min' in final_vol else round(np.min(final_scores), 4),
                    '最大值': final_vol['max'] if 'max' in final_vol else round(np.max(final_scores), 4)
                })
    
    # 计算新模型的模型批次波动值
    new_orig_model_volatility = []
    new_final_model_volatility = []
    new_comparison = []
    
    for model in new_results["original_results"].keys():
        # 原始问题模型批次波动值
        orig_model_data = new_results["original_results"][model]
        batch_scores = []
        for batch in sorted(set(qa['batch'] for qa in orig_model_data)):
            batch_data = [qa for qa in orig_model_data if qa['batch'] == batch]
            avg_total_score = np.mean([sum(qa['scores'].values()) / len(qa['scores']) for qa in batch_data])
            batch_scores.append(avg_total_score)
        
        if len(batch_scores) >= 2:
            orig_model_vol = calculate_volatility(batch_scores)
            new_orig_model_volatility.append({
                '问题类型': '原始问题',
                '模型': model,
                '批次数量': len(batch_scores),
                '批次均分': [round(score, 4) for score in batch_scores],
                '平均分': round(np.mean(batch_scores), 4),
                '标准差': orig_model_vol['std'],
                '方差': orig_model_vol['variance'],
                '变异系数': orig_model_vol['cv'],
                '极差': orig_model_vol['range'],
                '最小值': orig_model_vol['min'] if 'min' in orig_model_vol else round(np.min(batch_scores), 4),
                '最大值': orig_model_vol['max'] if 'max' in orig_model_vol else round(np.max(batch_scores), 4)
            })
        
        # 最终问题模型批次波动值
        final_model_data = new_results["final_results"][model]
        batch_scores = []
        for batch in sorted(set(qa['batch'] for qa in final_model_data)):
            batch_data = [qa for qa in final_model_data if qa['batch'] == batch]
            avg_total_score = np.mean([sum(qa['scores'].values()) / len(qa['scores']) for qa in batch_data])
            batch_scores.append(avg_total_score)
        
        if len(batch_scores) >= 2:
            final_model_vol = calculate_volatility(batch_scores)
            new_final_model_volatility.append({
                '问题类型': '最终问题',
                '模型': model,
                '批次数量': len(batch_scores),
                '批次均分': [round(score, 4) for score in batch_scores],
                '平均分': round(np.mean(batch_scores), 4),
                '标准差': final_model_vol['std'],
                '方差': final_model_vol['variance'],
                '变异系数': final_model_vol['cv'],
                '极差': final_model_vol['range'],
                '最小值': final_model_vol['min'] if 'min' in final_model_vol else round(np.min(batch_scores), 4),
                '最大值': final_model_vol['max'] if 'max' in final_model_vol else round(np.max(batch_scores), 4)
            })
        
        # 对比分析
        if len(new_orig_model_volatility) > 0 and len(new_final_model_volatility) > 0:
            orig_row = new_orig_model_volatility[-1]
            final_row = new_final_model_volatility[-1]
            
            new_comparison.append({
                '模型': model,
                '原始问题批次均分': orig_row['批次均分'],
                '最终问题批次均分': final_row['批次均分'],
                '原始问题平均分': orig_row['平均分'],
                '最终问题平均分': final_row['平均分'],
                '原始问题标准差': orig_row['标准差'],
                '最终问题标准差': final_row['标准差'],
                '标准差变化': round(final_row['标准差'] - orig_row['标准差'], 4),
                '原始问题变异系数': orig_row['变异系数'],
                '最终问题变异系数': final_row['变异系数'],
                '变异系数变化': round(final_row['变异系数'] - orig_row['变异系数'], 4),
                '波动性改善': 'stable' if final_row['标准差'] <= orig_row['标准差'] else 'more_volatile'
            })
    
    # 合并数据
    merged_orig_volatility = pd.concat([orig_volatility, pd.DataFrame(new_orig_volatility)], ignore_index=True)
    merged_final_volatility = pd.concat([final_volatility, pd.DataFrame(new_final_volatility)], ignore_index=True)
    merged_orig_model_volatility = pd.concat([orig_model_volatility, pd.DataFrame(new_orig_model_volatility)], ignore_index=True)
    merged_final_model_volatility = pd.concat([final_model_volatility, pd.DataFrame(new_final_model_volatility)], ignore_index=True)
    merged_comparison = pd.concat([comparison_df, pd.DataFrame(new_comparison)], ignore_index=True)
    
    # 保存合并后的数据
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_batch_file = f"/data/hlt/A-visual/mark/merged_batch_volatility_{timestamp}.xlsx"
    merged_model_file = f"/data/hlt/A-visual/mark/merged_model_volatility_{timestamp}.xlsx"
    
    with pd.ExcelWriter(merged_batch_file, engine='openpyxl') as writer:
        merged_orig_volatility.to_excel(writer, sheet_name='原始问题波动值', index=False)
        merged_final_volatility.to_excel(writer, sheet_name='最终问题波动值', index=False)
    
    with pd.ExcelWriter(merged_model_file, engine='openpyxl') as writer:
        merged_orig_model_volatility.to_excel(writer, sheet_name='原始问题模型波动', index=False)
        merged_final_model_volatility.to_excel(writer, sheet_name='最终问题模型波动', index=False)
        merged_comparison.to_excel(writer, sheet_name='模型波动对比', index=False)
    
    print(f"✅ 数据合并完成！")
    print(f"📊 合并后的批次波动值: {merged_batch_file}")
    print(f"📊 合并后的模型波动值: {merged_model_file}")
    
    return merged_batch_file, merged_model_file

def main():
    """主函数"""
    print("🧪 新模型测试工具")
    print("=" * 80)
    print("🤖 针对2个新模型：Qwen2.5-72B-Instruct、Qwen2.5-32B-Instruct")
    print("📊 每次4个问题，共4组（16个问题）")
    print("📈 分别评估500个问题组和91个问题组")
    print("📋 计算每个维度的波动值")
    print("🔄 和之前的数据合并")
    print("⚠️  使用前端现成接口，获取真实数据")
    print()
    
    # 运行测试
    results = run_new_models_test()
    
    if results:
        # 合并数据
        merged_files = merge_with_existing_data(results)
        
        if merged_files:
            print(f"\n🎉 新模型测试和数据合并完成！")
            
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
                print(f"\n🎉 新模型测试完成，数据已合并！")
                print(f"📈 包含详细的波动性分析（标准差、方差、变异系数等）")
            else:
                print(f"\n⚠️  API调用失败，无法获取真实评分")
    
    else:
        print("❌ 测试失败")

if __name__ == "__main__":
    main()
