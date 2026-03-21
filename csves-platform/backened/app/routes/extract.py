from flask import Blueprint, jsonify, request
from app.services.question_service import extract_questions, extract_single_question

extract_bp = Blueprint("extract", __name__)

@extract_bp.route("/extract", methods=["GET"])
def get_questions():
    """随机抽取若干问题"""
    questions = extract_questions(n=5)
    return jsonify({"status": "ok", "questions": questions})

@extract_bp.route("/extract_single", methods=["POST"])
def get_single_question():
    """基于当前问题列表，抽取一个不重复的新问题"""
    data = request.get_json(force=True)
    current_questions = data.get("current_questions", [])
    new_question = extract_single_question(current_questions)
    return jsonify({"status": "ok", "question": new_question})
