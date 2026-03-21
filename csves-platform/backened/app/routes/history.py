from flask import Blueprint, request, jsonify
from ..models import HistoryChart
from app import db

bp = Blueprint('history_charts', __name__)

@bp.route('/api/history_charts', methods=['POST'])
def add_history_chart():
    data = request.json
    new_chart = HistoryChart(
        Chart_type=data['Chart_type'],
        Chart_code=data['Template_code'],
        Chart_graph=data['Template_graph']
    )
    db.session.add(new_chart)
    db.session.commit()
    return jsonify({"message": "图表已保存至历史记录"}), 201
