from flask import Blueprint, request, jsonify
from app.services.graph.get_graph import generate_graph

bp = Blueprint('chart', __name__)
@bp.route('/api/chart', methods=['POST'])

def generate_plot():
    form=request.form
    data = form.get("data")
    type = form.get("type")
    requirements = form.get("inputValue")
    color = form.get("color")
    selected_model = form.get("selectedModel")
    template = form.get("template")
    history_code = form.get("history_code")

    try:
        img_base64,code = generate_graph(data, type, selected_model, requirements,color,template,history_code)
        return jsonify({
            "img_base64": img_base64,
            "code": code
        })
    except Exception as e:
        print("Error occurred while generating chart:", str(e))
        return jsonify({"error": str(e)}), 500
