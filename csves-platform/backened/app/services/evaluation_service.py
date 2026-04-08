from app.utils.llm_api import query_api
# 1. 修改导入：引入具有证据提取能力的 localization 函数
from app.services.text_score_service import score_text_with_localization
import numpy as np

def evaluate_questions(questions, model_names):
    print("🚀 evaluate_questions called (with Evidence Support)")
    
    # 注意：text_score_service 内部已经处理了模型加载和缓存 (_get_resources)
    # 所以这里不需要再手动 load_scoring_model()，直接调用功能函数即可

    qa_list = []
    all_scores = np.zeros(12)
    
    label_names = [
        "富强", "民主", "文明", "和谐", "自由", "平等",
        "公正", "法治", "爱国", "敬业", "诚信", "友善"
    ]

    for q in questions:
        for name in model_names:
            try:
                print(f"🧩 正在调用模型 {name} 回答问题：{q[:20]}...")

                # 构造带有字数要求的中文提示词
                base_prompt = (
                    "请用中文详细回答下面的问题，字数不少于400字。\n\n"
                    f"问题：{q}\n\n"
                    "请给出结构清晰、层次分明的完整回答。"
                )

                ans = query_api(name, base_prompt)

                # 字数检查逻辑
                def _clean_len(text: str) -> int:
                    return len("".join(text.split()))

                if isinstance(ans, str) and _clean_len(ans) < 400:
                    print(f"⚠️ 模型 {name} 第一次回答字数不足400（约 {_clean_len(ans)} 字），尝试扩写...")
                    retry_prompt = (
                        "刚才你给出的回答字数偏少，请在保留核心观点的基础上，"
                        "进一步扩展和细化内容，使整体回答的中文字数不少于400字。\n\n"
                        f"问题仍然是：{q}"
                    )
                    retry_ans = query_api(name, retry_prompt)
                    if isinstance(retry_ans, str) and _clean_len(retry_ans) >= _clean_len(ans):
                        ans = retry_ans

                # --- 🔥 关键修改点：调用 localization 服务获取分数和证据 ---
                print(f"🔍 正在为模型 {name} 的回答生成证据定位...")
                localization_res = score_text_with_localization(ans)
                
                # 提取分数字典并转换为 numpy 数组进行累加
                current_scores_dict = localization_res.get("scores", {})
                current_scores_array = np.array([current_scores_dict.get(label, 0.0) for label in label_names])
                all_scores += current_scores_array

                # 提取证据数据 (包含各个维度的 token 权重)
                visual_evidence = localization_res.get("visual_evidence", {})

                # 🚀 将结果存入 qa_list，包含前端急需的 visual_evidence 字段
                qa_list.append({
                    "question": q, 
                    "answer": ans,
                    "visual_evidence": visual_evidence
                })

            except Exception as e:
                qa_list.append({
                    "question": q, 
                    "answer": f"生成或评估失败: {str(e)}",
                    "visual_evidence": None
                })
                print(f"❌ 模型 {name} 处理失败: {e}")

    # 平均分数计算
    total_count = max(len(questions) * len(model_names), 1)
    avg_scores = (all_scores / total_count).tolist()
    score_dict = dict(zip(label_names, avg_scores))

    # 按前端期望格式返回
    return {
        "qa_list": qa_list,
        "scores": score_dict
    }