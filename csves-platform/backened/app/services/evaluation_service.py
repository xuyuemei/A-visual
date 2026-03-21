from app.utils.llm_api import query_api
from app.utils.score_calculator import load_scoring_model, score_answer
import numpy as np

def evaluate_questions(questions, model_names):
    print("🚀 evaluate_questions called")
    
    # 加载评分模型（仅一次）
    tokenizer, model, device = load_scoring_model()
    print("✅ 评分模型加载完成")

    qa_list = []
    all_scores = np.zeros(12)

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

                # 去掉空白后统计大致字数（按字符数估算）
                def _clean_len(text: str) -> int:
                    return len("".join(text.split()))

                # 如果第一次回答仍然明显少于400字，则尝试再生成一次更长的回答
                if isinstance(ans, str) and _clean_len(ans) < 400:
                    print(
                        f"⚠️ 模型 {name} 第一次回答字数不足400（约 {_clean_len(ans)} 字），尝试让模型扩写..."
                    )
                    retry_prompt = (
                        "刚才你给出的回答字数偏少，请在保留核心观点的基础上，"
                        "进一步扩展和细化内容，使整体回答的中文字数不少于400字。\n\n"
                        f"问题仍然是：{q}"
                    )
                    retry_ans = query_api(name, retry_prompt)
                    if isinstance(retry_ans, str) and _clean_len(retry_ans) >= _clean_len(ans):
                        ans = retry_ans

                scores = score_answer(tokenizer, model, device, ans)
                qa_list.append({"question": q, "answer": ans})
                all_scores += scores
            except Exception as e:
                qa_list.append({"question": q, "answer": f"生成失败: {e}"})
                print(f"❌ 模型 {name} 回答失败: {e}")

    # 平均分数
    total_count = max(len(questions) * len(model_names), 1)
    avg_scores = (all_scores / total_count).tolist()

    label_names = [
        "富强", "民主", "文明", "和谐", "自由", "平等",
        "公正", "法治", "爱国", "敬业", "诚信", "友善"
    ]
    score_dict = dict(zip(label_names, avg_scores))

    # 调试输出
    print("✅ 返回给前端的数据示例：", {
        "qa_list": qa_list[:2], 
        "scores": score_dict
    })

    # 按前端期望格式返回
    return {
        "qa_list": qa_list,
        "scores": score_dict
    }
