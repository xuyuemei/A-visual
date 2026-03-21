# app/routes/models.py
from flask import Blueprint, jsonify

models_bp = Blueprint("models", __name__)

@models_bp.route("/models", methods=["GET"])
def get_models():
    models = [
        {"name": "DeepSeek-R1", "source": "DeepSeek", "date": "2024-11"},
        {"name": "Claude-3.5-Haiku", "source": "Anthropic", "date": "2024-10"},
        {"name": "GPT-4o", "source": "OpenAI", "date": "2024-08"},
    ]
    return jsonify({"models": models})
