from flask import Blueprint, request, jsonify
from ..models import ChartTemplate
from app import db

bp = Blueprint('template', __name__)

@bp.route('/api/templates', methods=['GET'])
def get_templates_by_type():
    chart_type = request.args.get('chart_type')
    if not chart_type:
        return jsonify({"error": "Missing chart_type parameter"}), 400

    templates = ChartTemplate.query.filter_by(Chart_type=chart_type).all()

    result = []
    for t in templates:
        result.append({
            "Template_ID": t.Template_ID,
            "Template_code": t.Template_code,
            "Template_graph": t.Template_graph  # base64 字符串
        })

    return jsonify(result)

# 新增接口，添加模板
@bp.route('/api/templates', methods=['POST'])
def add_template():
    data = request.json
    required_fields = ['Chart_type', 'Template_code', 'Template_graph']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # 查询当前最大 Template_ID
    max_id = db.session.query(db.func.max(ChartTemplate.Template_ID)).scalar()
    if max_id is None:
        max_id = 0  # 如果没有数据，则从0开始

    new_template = ChartTemplate(
        Template_ID=max_id + 1,  # 新ID = 最大ID + 1
        Chart_type=data['Chart_type'],
        Call_count=0,  # 初始化计数
        Template_code=data['Template_code'],
        Template_graph=data['Template_graph'],
    )

    try:
        db.session.add(new_template)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500

    return jsonify({"message": "Template added successfully", "Template_ID": new_template.Template_ID}), 201
