#!/usr/bin/env python3
"""
完整的问题迁移和对比测试方案
"""

import pandas as pd
import json
import os
import time
from datetime import datetime
from app.services.evaluation_service import evaluate_questions

class QuestionMigrationManager:
    def __init__(self):
        self.original_file = "/data/hlt/A-visual/mark/500_question_answer.xlsx"
        self.new_file = "/data/hlt/A-visual/mark/社会主义核心价值观评估问题集-500个问题.xlsx"
        self.backup_dir = "/data/hlt/A-visual/mark/backups"
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def backup_original_questions(self):
        """备份原始问题"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{self.backup_dir}/original_questions_{timestamp}.xlsx"
        
        if os.path.exists(self.original_file):
            df = pd.read_excel(self.original_file)
            df.to_excel(backup_file, index=False)
            print(f"✅ 原始问题已备份: {backup_file}")
            return backup_file
        else:
            print("❌ 原始问题文件不存在")
            return None
    
    def load_original_questions(self):
        """加载原始问题"""
        try:
            df = pd.read_excel(self.original_file)
            questions = df[df.columns[0]].dropna().astype(str).tolist()
            
            # 清理问题
            cleaned = []
            for q in questions:
                q = q.strip()
                if q and len(q) > 5:
                    # 移除序号前缀
                    if q.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                        q = q[q.find('.')+1:].strip()
                    elif q[0].isdigit() and '.' in q[:5]:
                        q = q[q.find('.')+1:].strip()
                    cleaned.append(q)
            
            print(f"✅ 加载原始问题: {len(cleaned)} 个")
            return cleaned
        except Exception as e:
            print(f"❌ 加载原始问题失败: {e}")
            return []
    
    def load_new_questions(self):
        """加载新的431个问题"""
        try:
            df = pd.read_excel(self.new_file)
            questions = df['query'].dropna().astype(str).tolist()
            
            # 清理问题
            cleaned = []
            for i, q in enumerate(questions):
                q = q.strip()
                if q and len(q) > 5:
                    cleaned.append(q)
                else:
                    print(f"⚠️ 跳过无效问题 {i+1}: {q}")
            
            print(f"✅ 加载新问题: {len(cleaned)} 个")
            return cleaned
        except Exception as e:
            print(f"❌ 加载新问题失败: {e}")
            return []
    
    def create_new_question_file(self, questions, output_path):
        """创建新的系统问题文件"""
        # 保持与原文件相同的格式
        new_df = pd.DataFrame({
            'Unnamed: 0': questions,
            'deepseekr1': [''] * len(questions),
            'glm4': [''] * len(questions),
            'qwen2.5-72b-instruct': [''] * len(questions),
            'gpt4': [''] * len(questions),
            'claude-3-opus': [''] * len(questions),
            'llama3.1-8b': [''] * len(questions),
            'DeepSeek-R1-Distill-Llama-8B': [''] * len(questions),
            'llama3.1-70b': [''] * len(questions),
        })
        
        new_df.to_excel(output_path, index=False)
        print(f"✅ 新系统问题文件已创建: {output_path}")
        print(f"📊 包含 {len(questions)} 个问题")
    
    def switch_to_original_questions(self):
        """切换到原始问题"""
        backup_file = f"{self.backup_dir}/original_questions_for_switch.xlsx"
        if os.path.exists(self.original_file):
            df = pd.read_excel(self.original_file)
            df.to_excel(backup_file, index=False)
            print(f"✅ 已切换到原始问题")
            return True
        return False
    
    def switch_to_new_questions(self):
        """切换到新问题"""
        new_system_file = f"{self.backup_dir}/new_questions_system.xlsx"
        if os.path.exists(new_system_file):
            df = pd.read_excel(new_system_file)
            df.to_excel(self.original_file, index=False)
            print(f"✅ 已切换到新问题（431个）")
            return True
        return False
    
    def run_comparison_test(self, num_questions=10, models=["gpt-3.5-turbo"]):
        """运行对比测试"""
        print("🚀 开始对比测试...")
        
        # 加载问题
        original_questions = self.load_original_questions()
        new_questions = self.load_new_questions()
        
        if not original_questions or not new_questions:
            print("❌ 问题加载失败")
            return None
        
        # 限制测试问题数量
        orig_test = original_questions[:min(num_questions, len(original_questions))]
        new_test = new_questions[:min(num_questions, len(new_questions))]
        
        results = {
            "test_info": {
                "timestamp": datetime.now().isoformat(),
                "num_questions": len(orig_test),
                "models": models,
                "original_count": len(original_questions),
                "new_count": len(new_questions)
            },
            "original_results": {},
            "new_results": {},
            "comparison": {}
        }
        
        # 测试原始问题
        print(f"\n🔍 测试原始问题...")
        for model in models:
            try:
                start_time = time.time()
                orig_result = evaluate_questions(orig_test, [model])
                end_time = time.time()
                
                results["original_results"][model] = {
                    "questions": orig_test,
                    "qa_list": orig_result["qa_list"],
                    "scores": orig_result["scores"],
                    "time_taken": end_time - start_time,
                    "avg_score": sum(orig_result["scores"]) / len(orig_result["scores"])
                }
                print(f"✅ {model} 原始问题测试完成，平均分: {results['original_results'][model]['avg_score']:.3f}")
                
            except Exception as e:
                print(f"❌ {model} 原始问题测试失败: {e}")
                results["original_results"][model] = {"error": str(e)}
        
        # 测试新问题
        print(f"\n🔍 测试新问题...")
        for model in models:
            try:
                start_time = time.time()
                new_result = evaluate_questions(new_test, [model])
                end_time = time.time()
                
                results["new_results"][model] = {
                    "questions": new_test,
                    "qa_list": new_result["qa_list"],
                    "scores": new_result["scores"],
                    "time_taken": end_time - start_time,
                    "avg_score": sum(new_result["scores"]) / len(new_result["scores"])
                }
                print(f"✅ {model} 新问题测试完成，平均分: {results['new_results'][model]['avg_score']:.3f}")
                
            except Exception as e:
                print(f"❌ {model} 新问题测试失败: {e}")
                results["new_results"][model] = {"error": str(e)}
        
        # 生成对比分析
        print(f"\n📊 生成对比分析...")
        for model in models:
            if model in results["original_results"] and model in results["new_results"]:
                orig = results["original_results"][model]
                new = results["new_results"][model]
                
                if "avg_score" in orig and "avg_score" in new:
                    score_improvement = new["avg_score"] - orig["avg_score"]
                    improvement_percent = (score_improvement / orig["avg_score"]) * 100 if orig["avg_score"] != 0 else 0
                    
                    results["comparison"][model] = {
                        "original_avg_score": orig["avg_score"],
                        "new_avg_score": new["avg_score"],
                        "score_improvement": score_improvement,
                        "improvement_percent": improvement_percent,
                        "original_time": orig.get("time_taken", 0),
                        "new_time": new.get("time_taken", 0)
                    }
                    
                    print(f"📈 {model} 对比结果:")
                    print(f"   原始问题平均分: {orig['avg_score']:.3f}")
                    print(f"   新问题平均分: {new['avg_score']:.3f}")
                    print(f"   分数提升: {score_improvement:+.3f} ({improvement_percent:+.2f}%)")
        
        return results
    
    def save_results(self, results, filename=None):
        """保存测试结果"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comparison_results_{timestamp}.json"
        
        output_path = f"{self.backup_dir}/{filename}"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 测试结果已保存: {output_path}")
        return output_path
    
    def generate_summary_report(self, results):
        """生成摘要报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = f"{self.backup_dir}/summary_report_{timestamp}.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("🧪 问题质量对比测试摘要报告\n")
            f.write("=" * 60 + "\n\n")
            
            test_info = results.get("test_info", {})
            f.write(f"测试时间: {test_info.get('timestamp', '未知')}\n")
            f.write(f"测试问题数量: {test_info.get('num_questions', 0)}\n")
            f.write(f"原始问题总数: {test_info.get('original_count', 0)}\n")
            f.write(f"新问题总数: {test_info.get('new_count', 0)}\n")
            f.write(f"测试模型: {', '.join(test_info.get('models', []))}\n\n")
            
            comparison = results.get("comparison", {})
            for model, comp in comparison.items():
                f.write(f"🤖 模型: {model}\n")
                f.write(f"   原始问题平均分: {comp.get('original_avg_score', 0):.3f}\n")
                f.write(f"   新问题平均分: {comp.get('new_avg_score', 0):.3f}\n")
                f.write(f"   分数提升: {comp.get('score_improvement', 0):+.3f}\n")
                f.write(f"   提升百分比: {comp.get('improvement_percent', 0):+.2f}%\n\n")
            
            # 结论
            f.write("📊 测试结论:\n")
            for model, comp in comparison.items():
                improvement = comp.get('improvement_percent', 0)
                if improvement > 5:
                    f.write(f"✅ {model}: 新问题质量显著提升 (+{improvement:.2f}%)\n")
                elif improvement > 0:
                    f.write(f"📈 {model}: 新问题质量略有提升 (+{improvement:.2f}%)\n")
                elif improvement > -5:
                    f.write(f"➡️ {model}: 新问题质量基本持平 ({improvement:.2f}%)\n")
                else:
                    f.write(f"⚠️ {model}: 新问题质量有所下降 ({improvement:.2f}%)\n")
        
        print(f"📋 摘要报告已生成: {summary_file}")
        return summary_file

def main():
    """主执行流程"""
    manager = QuestionMigrationManager()
    
    print("🚀 问题迁移和对比测试系统")
    print("=" * 60)
    
    # 步骤1: 备份原始问题
    print("\n📦 步骤1: 备份原始问题...")
    manager.backup_original_questions()
    
    # 步骤2: 加载问题
    print("\n📖 步骤2: 加载问题...")
    original_questions = manager.load_original_questions()
    new_questions = manager.load_new_questions()
    
    if not original_questions or not new_questions:
        print("❌ 问题加载失败，退出")
        return
    
    print(f"📊 原始问题: {len(original_questions)} 个")
    print(f"📊 新问题: {len(new_questions)} 个")
    
    # 步骤3: 创建新问题系统文件
    print("\n🔧 步骤3: 创建新问题系统文件...")
    new_system_file = f"{manager.backup_dir}/new_questions_system.xlsx"
    manager.create_new_question_file(new_questions, new_system_file)
    
    # 步骤4: 运行对比测试
    print("\n🧪 步骤4: 运行对比测试...")
    results = manager.run_comparison_test(
        num_questions=5,  # 测试5个问题，可以调整
        models=["gpt-3.5-turbo"]  # 可以添加更多模型
    )
    
    if results:
        # 步骤5: 保存结果
        print("\n💾 步骤5: 保存测试结果...")
        result_file = manager.save_results(results)
        summary_file = manager.generate_summary_report(results)
        
        print(f"\n🎉 完整流程执行完成！")
        print(f"📁 结果文件: {result_file}")
        print(f"📋 摘要报告: {summary_file}")
        print(f"\n💡 下一步操作:")
        print(f"1. 查看摘要报告了解测试结果")
        print(f"2. 如需切换到新问题，运行: manager.switch_to_new_questions()")
        print(f"3. 重启后端服务测试新问题")
        
    else:
        print("❌ 对比测试失败")

if __name__ == "__main__":
    main()
