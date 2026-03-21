from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# 初始化数据库实例
db = SQLAlchemy()

def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)

    # 开启跨域支持（允许携带 cookie）
    CORS(app, supports_credentials=True)

    # 加载配置文件（如数据库 URI）
    app.config.from_pyfile('../config.py')

    # 初始化 SQLAlchemy
    db.init_app(app)
    print(f"✅ 数据库连接成功：{app.config['SQLALCHEMY_DATABASE_URI']}")

    # ===== 注册原有蓝图 =====
    from .routes import auth, upload, chart, dataprocess, template
    # app.register_blueprint(auth.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(dataprocess.bp)
    app.register_blueprint(chart.bp)
    app.register_blueprint(template.bp)

    # ===== 注册新增功能蓝图 =====
    # 🔹 问题抽取接口 /api/extract
    from .routes.extract import extract_bp
    app.register_blueprint(extract_bp, url_prefix="/api")

    from .routes.models import models_bp
    app.register_blueprint(models_bp, url_prefix="/api")

    # 🔹 模型评估接口 /api/evaluate
    from .routes.llm_eval import eval_bp
    app.register_blueprint(eval_bp, url_prefix="/api")

    # 🔹 新增：文本评分接口 /api/score_text
    from .routes.text_score import text_score_bp
    app.register_blueprint(text_score_bp, url_prefix="/api")
    print("✅ 文本评分蓝图注册完成：/api/score_text")

    # 🔹 新增：doc/docx 文档解析接口 /api/parse_doc_text
    from .routes.doc_parse import doc_parse_bp
    app.register_blueprint(doc_parse_bp, url_prefix="/api")

    # 🔹 新增：图片分析接口 /api/analyze_image
    from .routes.image_analysis import image_analysis_bp
    app.register_blueprint(image_analysis_bp, url_prefix="/api")
    print("✅ 图片分析蓝图注册完成：/api/analyze_image")

    # 🔹 新增：视频分析接口 /api/analyze_video
    from .routes.video_analysis import video_analysis_bp
    app.register_blueprint(video_analysis_bp, url_prefix="/api")
    print("✅ 视频分析蓝图注册完成：/api/analyze_video")

    # 🔹 新增：模型回答分析接口 /api/analyze
    from .routes.analysis import bp as analysis_bp
    app.register_blueprint(analysis_bp)
    print("✅ 分析蓝图注册完成")

    print("✅ 所有蓝图注册完成：upload, dataprocess, chart, template, extract, evaluate, image_analysis, video_analysis, analysis")
    print("✅ 所有蓝图注册完成：upload, dataprocess, chart, template, extract, evaluate, image_analysis, analysis")

    return app