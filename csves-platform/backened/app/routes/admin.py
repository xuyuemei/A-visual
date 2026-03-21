from flask import Blueprint, request, jsonify
from models import db, ChartTemplate
from sqlalchemy import or_

chart_template_routes = Blueprint('chart_template_routes', __name__)

@chart_template_routes.route('/api/chart-template/list', methods=['POST'])
def list_chart_templates():
    try:
        name = request.form.get('name', '')
        chart_type = request.form.get('chartType', '')
        current = int(request.form.get('current', 1))
        page_size = int(request.form.get('pageSize', 6))

        query = ChartTemplate.query

        # 按名称模糊搜索
        if name:
            query = query.filter(ChartTemplate.Template_code.ilike(f"%{name}%"))

        # 按类型搜索
        if chart_type:
            query = query.filter(ChartTemplate.Chart_type == chart_type)

        total = query.count()

        # 分页处理
        templates = query.order_by(ChartTemplate.Template_ID.desc()) \
            .offset((current - 1) * page_size).limit(page_size).all()

        data = [{
            'id': t.Template_ID,
            'name': f'模板-{t.Template_ID}',
            'chartType': t.Chart_type,
            'callCount': t.Call_count,
            'templateGraph': t.Template_graph,
        } for t in templates]

        return jsonify({
            'code': 200,
            'message': '获取模板成功',
            'data': {
                'records': data,
                'total': total,
                'current': current,
                'pageSize': page_size,
            }
        })

    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'})
