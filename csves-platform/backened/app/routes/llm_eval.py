from flask import Blueprint, request, jsonify
from app.services.evaluation_service import evaluate_questions

eval_bp = Blueprint("evaluate", __name__)

@eval_bp.route("/evaluate", methods=["POST"])
def evaluate():
    """
    调用后端模型接口：
    输入：
        {
          "questions": ["人工智能是否会取代人类的工作？", ...],
          "models": ["DeepSeek-R1"]
        }
    输出：
        {
          "qa_list": [{ "question": "...", "answer": "..." }, ...],
          "scores": { "富强": 0.82, "民主": 0.75, ... }
        }
    """
    data = request.get_json()
    questions = data.get("questions", [])
    model_names = data.get("models", ["DeepSeek-R1"])

    if not questions:
        return jsonify({"error": "缺少 questions 参数"}), 400

    # ✅ 直接接收字典
    result = evaluate_questions(questions, model_names)

    # ✅ 返回 JSON
    return jsonify(result)
