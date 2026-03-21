# app/routes/text_score.py
from flask import Blueprint, request, jsonify
from app.services.text_score_service import (
  score_text,
  score_texts,
  score_text_with_localization,
  score_texts_with_localization,
)

text_score_bp = Blueprint("text_score", __name__)

@text_score_bp.route("/score_text", methods=["POST"])
def score_text_api():
    """
    单条：
      { "text": "..." }
    多条：
      { "texts": ["...", "..."] }

    返回：
      单条：{ "scores": {...} }
      多条：{ "results": [...], "scores": {...平均分...}, "count": N }
    """
    data = request.get_json(silent=True) or {}

    # ✅ 多条优先
    if isinstance(data.get("texts"), list):
        try:
            return jsonify(score_texts(data["texts"]))
        except Exception as e:
            return jsonify({"error": f"评分失败: {str(e)}"}), 500

    # ✅ 单条
    text = data.get("text", "")
    if not str(text).strip():
        return jsonify({"error": "缺少 text 或 texts 参数"}), 400

    try:
        return jsonify(score_text(text))
    except Exception as e:
        return jsonify({"error": f"评分失败: {str(e)}"}), 500


@text_score_bp.route("/score_text_batch", methods=["POST"])
def score_text_batch_api():
    """
    批量接口（兼容你前端现在打的 /api/score_text_batch）
    输入：
      { "texts": ["...", "..."] }
    输出：
      { "results": [...], "scores": {...平均分...}, "count": N }
    """
    data = request.get_json(silent=True) or {}
    texts = data.get("texts", [])

    if not isinstance(texts, list) or len([str(t).strip() for t in texts if str(t).strip()]) == 0:
        return jsonify({"error": "缺少 texts 参数"}), 400

    try:
        return jsonify(score_texts(texts))
    except Exception as e:
        return jsonify({"error": f"评分失败: {str(e)}"}), 500


@text_score_bp.route("/score_text_localize", methods=["POST"])
def score_text_localize_api():
    """
    文本定位接口：
      输入：{ "text": "..." }
      输出：整体评分 + 句子定位 + 关键词定位
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    if not str(text).strip():
        return jsonify({"error": "缺少 text 参数"}), 400

    try:
        return jsonify(score_text_with_localization(text))
    except Exception as e:
        return jsonify({"error": f"文本定位失败: {str(e)}"}), 500


@text_score_bp.route("/score_text_localize_batch", methods=["POST"])
def score_text_localize_batch_api():
    """
    批量文本定位接口：
      输入：{ "texts": ["...", "..."] }
      输出：每条文本分别的定位结果
    """
    data = request.get_json(silent=True) or {}
    texts = data.get("texts", [])

    if not isinstance(texts, list) or len([str(t).strip() for t in texts if str(t).strip()]) == 0:
        return jsonify({"error": "缺少 texts 参数"}), 400

    try:
        return jsonify(score_texts_with_localization(texts))
    except Exception as e:
        return jsonify({"error": f"批量文本定位失败: {str(e)}"}), 500
