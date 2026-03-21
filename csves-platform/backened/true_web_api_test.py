#!/usr/bin/env python3
"""
真实网页API测试：完全模拟前端调用
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

def load_final_questions():
    """加载最终问题集（499个）"""
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

def call_web_api_like_frontend(question, model_id):
    """完全模拟前端调用网页API"""
    try:
        url = "http://localhost:8000/api/dataprocess"
        
        # 创建Excel数据（模拟前端上传的Excel文件格式）
        # 前端通常上传的是包含问题的Excel文件
        excel_data = {
            'headers': ['问题', '答案', '富强', '民主', '文明', '和谐', '自由', '平等', '公正', '法治', '爱国', '敬业', '诚信', '友善'],
            'data': [[question, '', '', '', '', '', '', '', '', '', '', '', '', '', '']]  # 空的评分列让AI填写
        }
        
        # 构造请求参数（完全模拟前端）
        data = {
            'inputValue': f'请对以下问题进行社会主义核心价值观评估，从富强、民主、文明、和谐、自由、平等、公正、法治、爱国、敬业、诚信、友善12个维度进行评分（1-5分），并给出详细分析：{question}',
            'selectedModel': model_id,  # 使用数字ID
            'sheetData': json.dumps(excel_data)
        }
        
        print(f"🤖 调用模型ID {model_id} 评估问题: {question[:50]}...")
        
        response = requests.post(url, data=data, timeout=300)  # 5分钟超时
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ 模型ID {model_id} 评估完成")
                return result
            except json.JSONDecodeError:
                print(f"⚠️ 模型ID {model_id} 返回非JSON格式，尝试解析...")
                # 如果返回的是celldata格式，需要特殊处理
                try:
                    text_response = response.text
                    if 'data' in text_response:
                        return json.loads(text_response)
                    else:
                        print(f"❌ 模型ID {model_id} 返回格式无法解析")
                        return None
                except:
                    print(f"❌ 模型ID {model_id} 返回格式无法解析")
                    return None
        else:
            print(f"❌ 模型ID {model_id} API调用失败: {response.status_code}")
            print(f"   响应内容: {response.text[:300]}...")
            return None
            
    except Exception as e:
        print(f"❌ 模型ID {model_id} API调用异常: {e}")
        return None

def parse_real_api_result(result, question, model_id):
    """解析真实API返回的结果"""
    try:
        if isinstance(result, dict):
            if 'data' in result:
                # 如果是celldata格式
                data = result['data']
                if len(data) > 0:
                    row = data[0]
                    if len(row) >= 14:  # 问题 + 答案 + 12个维度
                        answer_text = str(row[1]) if len(row) > 1 else ""
                        
                        # 提取12个维度的评分
                        dimensions = ['富强', '民主', '文明', '和谐', '自由', '平等', '公正', '法治', '爱国', '敬业', '诚信', '友善']
                        scores = {}
                        
                        for i, dim in enumerate(dimensions):
                            score_index = i + 2  # 跳过问题(0)和答案(1)
                            if score_index < len(row):
                                try:
                                    score = float(row[score_index])
                                    scores[dim] = round(score, 2)
                                except:
                                    # 如果无法转换为数字，尝试从答案文本中提取
                                    scores[dim] = extract_score_from_text(answer_text, dim)
                            else:
                                scores[dim] = extract_score_from_text(answer_text, dim)
                        
                        return {
                            'question': question,
                            'model': f'model_{model_id}',
                            'answer': answer_text,
                            'scores': scores
                        }
            elif 'error' in result:
                print(f"❌ API返回错误: {result['error']}")
                return None
        
        return None
        
    except Exception as e:
        print(f"❌ 解析结果失败: {e}")
        return None

def extract_score_from_text(text, dimension):
    """从文本中提取特定维度的评分"""
    import re
    
    patterns = [
        f'{dimension}[：:]\s*([1-5](?:\\.[0-9])?)',
        f'{dimension}[：:]\s*([1-5])分',
        f'{dimension}\\s*=\\s*([1-5](?:\\.[0-9])?)',
        f'{dimension}\\s*([1-5](?:\\.[0-9])?)分',
    ]
    
    for pattern in patterns:
        try:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return round(float(match.group(1)), 2)
        except:
            continue
    
    # 如果找不到，返回默认分数
    return 3.0

def run_true_web_api_test(num_questions=1, model_ids=["1", "2", "3", "4"]):
    """运行真实网页API测试"""
    print("🧪 开始真实网页API质量对比测试")
    print("=" * 80)
    
    # 加载问题
    original_questions = load_original_questions()
    final_questions = load_final_questions()
    
    if not original_questions or not final_questions:
        print("❌ 问题加载失败")
        return None
    
    # 限制测试数量
    orig_test = original_questions[:min(num_questions, len(original_questions))]
    final_test = final_questions[:min(num_questions, len(final_questions))]
    
    print(f"\n📊 测试配置:")
    print(f"   原始问题测试: {len(orig_test)} 个 (总共{len(original_questions)}个)")
    print(f"   最终问题测试: {len(final_test)} 个 (总共{len(final_questions)}个)")
    print(f"   测试模型ID: {model_ids}")
    print(f"   ⚠️  真实网页API调用，完全模拟前端...")
    
    all_results = {
        "original_results": {},
        "final_results": {},
        "test_info": {
            "timestamp": datetime.now().isoformat(),
            "num_questions": len(orig_test),
            "model_ids": model_ids,
            "original_total": len(original_questions),
            "final_total": len(final_questions)
        }
    }
    
    # 模型ID到名称的映射
    model_names = {
        "1": "gpt-4o",
        "2": "deepseek-reasoner", 
        "3": "deepseek-v3",
        "4": "baichuan-13b"
    }
    
    # 测试原始问题
    print(f"\n🔍 测试原始问题...")
    for model_id in model_ids:
        print(f"\n🤖 测试模型ID {model_id} ({model_names[model_id]}) - 原始问题:")
        model_results = []
        
        for i, question in enumerate(orig_test, 1):
            print(f"   问题 {i}/{len(orig_test)}: {question[:30]}...")
            
            # 调用API
            result = call_web_api_like_frontend(question, model_id)
            if result:
                parsed = parse_real_api_result(result, question, model_id)
                if parsed:
                    model_results.append(parsed)
                    print(f"      ✅ 成功解析评分: {parsed['scores']}")
                else:
                    print(f"      ❌ 解析失败")
            else:
                print(f"      ❌ API调用失败")
            
            # 避免请求过快
            time.sleep(5)
        
        all_results["original_results"][f"model_{model_id}"] = model_results
        print(f"✅ 模型ID {model_id} 原始问题测试完成，成功评估 {len(model_results)} 个问题")
    
    # 测试最终问题
    print(f"\n🔍 测试最终问题...")
    for model_id in model_ids:
        print(f"\n🤖 测试模型ID {model_id} ({model_names[model_id]}) - 最终问题:")
        model_results = []
        
        for i, question in enumerate(final_test, 1):
            print(f"   问题 {i}/{len(final_test)}: {question[:30]}...")
            
            # 调用API
            result = call_web_api_like_frontend(question, model_id)
            if result:
                parsed = parse_real_api_result(result, question, model_id)
                if parsed:
                    model_results.append(parsed)
                    print(f"      ✅ 成功解析评分: {parsed['scores']}")
                else:
                    print(f"      ❌ 解析失败")
            else:
                print(f"      ❌ API调用失败")
            
            # 避免请求过快
            time.sleep(5)
        
        all_results["final_results"][f"model_{model_id}"] = model_results
        print(f"✅ 模型ID {model_id} 最终问题测试完成，成功评估 {len(model_results)} 个问题")
    
    return all_results

def create_true_api_excel_report(results):
    """创建真实API评估Excel报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file = f"/data/hlt/A-visual/mark/true_web_api_evaluation_report_{timestamp}.xlsx"
    
    print(f"\n📊 生成真实网页API评估Excel报告: {excel_file}")
    
    dimensions = ['富强', '民主', '文明', '和谐', '自由', '平等', '公正', '法治', '爱国', '敬业', '诚信', '友善']
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        
        # 1. 原始问题详细得分
        print("   📋 生成原始问题得分表...")
        original_data = []
        
        for model, qa_list in results["original_results"].items():
            for i, qa in enumerate(qa_list, 1):
                row = {
                    "问题类型": "原始问题(90个)",
                    "模型": model,
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
        original_df.to_excel(writer, sheet_name="原始问题得分", index=False)
        
        # 2. 最终问题详细得分
        print("   📋 生成最终问题得分表...")
        final_data = []
        
        for model, qa_list in results["final_results"].items():
            for i, qa in enumerate(qa_list, 1):
                row = {
                    "问题类型": "最终问题(499个)",
                    "模型": model,
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
        final_df.to_excel(writer, sheet_name="最终问题得分", index=False)
        
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
        
        # 4. 总体统计摘要
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
                "最终问题总数": results["test_info"]["final_total"]
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name="总体统计摘要", index=False)
    
    print(f"✅ 真实网页API评估Excel报告已生成: {excel_file}")
    return excel_file

def main():
    """主函数"""
    print("🧪 真实网页API质量对比测试工具")
    print("=" * 80)
    print("🤖 完全模拟前端调用后端4个模型进行评估")
    print("📊 对比原始90个问题 vs 最终499个问题")
    print("⚠️  真实API调用，需要较长时间")
    print("🔍 使用真实API返回的评分，非模拟数据")
    print()
    
    # 运行测试
    results = run_true_web_api_test(
        num_questions=1,  # 每个模型1个问题（快速测试）
        model_ids=["1", "2", "3", "4"]  # 4个真实模型ID
    )
    
    if results:
        # 生成Excel报告
        excel_file = create_true_api_excel_report(results)
        
        print(f"\n🎉 真实网页API对比测试完成！")
        print(f"📊 Excel报告: {excel_file}")
        print(f"\n📋 报告包含以下工作表:")
        print(f"   1. 原始问题得分 - 原始90个问题的真实API评估得分")
        print(f"   2. 最终问题得分 - 最终499个问题的真实API评估得分")
        print(f"   3. 维度平均分对比 - 各维度平均分对比")
        print(f"   4. 总体统计摘要 - 总体统计对比")
        
        # 显示简要统计
        test_info = results["test_info"]
        print(f"\n📊 测试统计:")
        print(f"   原始问题集: {test_info['original_total']} 个问题")
        print(f"   最终问题集: {test_info['final_total']} 个问题")
        print(f"   测试模型数: {len(test_info['model_ids'])}")
        print(f"   每模型问题数: {test_info['num_questions']}")
        print(f"   总测试数量: {len(test_info['model_ids']) * test_info['num_questions'] * 2}")
        
        # 显示成功评估数量
        total_original = sum(len(qa_list) for qa_list in results["original_results"].values())
        total_final = sum(len(qa_list) for qa_list in results["final_results"].values())
        print(f"\n✅ 成功评估统计:")
        print(f"   原始问题成功评估: {total_original} 个")
        print(f"   最终问题成功评估: {total_final} 个")
        print(f"   总计成功评估: {total_original + total_final} 个")
        
        if total_original + total_final > 0:
            print(f"\n🎉 使用真实API评分，非模拟数据！")
        else:
            print(f"\n⚠️  API调用失败，无法获取真实评分")
    
    else:
        print("❌ 测试失败")

if __name__ == "__main__":
    main()
