from flask_sqlalchemy import SQLAlchemy
from app import db

class UserTable(db.Model):
    __tablename__ = 'User_table'

    User_ID = db.Column(db.Integer, primary_key=True, nullable=False)
    User_name = db.Column(db.String(50), nullable=False)
    User_avatar = db.Column(db.String(255))
    User_phone = db.Column(db.String(20), unique=True, nullable=False)
    User_level = db.Column(db.String(20), nullable=False, default='普通用户')
    User_password = db.Column(db.String(100), nullable=False)
    User_email = db.Column(db.String(100))
    User_credit = db.Column(db.Integer, default=999)

    history_charts = db.relationship('HistoryChart', backref='creator', lazy=True)
    chart_favorites = db.relationship('ChartFavorite', backref='user', lazy=True)
    color_favorites = db.relationship('ColorFavorite', backref='user', lazy=True)
    history_chats = db.relationship('HistoryChat', backref='user', lazy=True)


class HistoryChart(db.Model):
    __tablename__ = 'History_chart'

    Chart_ID = db.Column(db.Integer, primary_key=True, nullable=False)
    Chart_name = db.Column(db.String(100), nullable=False)
    Chart_type = db.Column(db.String(50), nullable=False)
    Creator_ID = db.Column(db.Integer, db.ForeignKey('User_table.User_ID'), nullable=False)
    Chart_code = db.Column(db.Text, nullable=False)
    Chart_desc = db.Column(db.Text, nullable=False)
    Chart_data = db.Column(db.Text, nullable=False)
    Chart_graph = db.Column(db.LargeBinary, nullable=False)  # MEDIUMBLOB 用 LargeBinary 即可
    Create_time = db.Column(db.DateTime, nullable=False)


class ChartTemplate(db.Model):
    __tablename__ = 'Chart_template'

    Template_ID = db.Column(db.Integer, primary_key=True, nullable=False)
    Chart_type = db.Column(db.String(50), nullable=False)
    Call_count = db.Column(db.Integer, nullable=False)
    Template_code = db.Column(db.Text, nullable=False)
    Template_graph = db.Column(db.Text, nullable=False)

    favorites = db.relationship('ChartFavorite', backref='template', lazy=True)


class ColorStyle(db.Model):
    __tablename__ = 'Color_style'

    Color_style_ID = db.Column(db.Integer, primary_key=True, nullable=False)
    Style_type = db.Column(db.String(50), nullable=False)
    Color_codes = db.Column(db.String(255), nullable=False)
    Call_count = db.Column(db.Integer, nullable=False)

    favorites = db.relationship('ColorFavorite', backref='color_style', lazy=True)


class ChartFavorite(db.Model):
    __tablename__ = 'Chart_favorite'

    Template_ID = db.Column(db.Integer, db.ForeignKey('Chart_template.Template_ID'), primary_key=True, nullable=False)
    User_ID = db.Column(db.Integer, db.ForeignKey('User_table.User_ID'), primary_key=True, nullable=False)


class ColorFavorite(db.Model):
    __tablename__ = 'Color_favorite'

    Color_style_ID = db.Column(db.Integer, db.ForeignKey('Color_style.Color_style_ID'), primary_key=True, nullable=False)
    User_ID = db.Column(db.Integer, db.ForeignKey('User_table.User_ID'), primary_key=True, nullable=False)


class PromptTemplate(db.Model):
    __tablename__ = 'Prompt_template'

    Prompt_ID = db.Column(db.Integer, primary_key=True, nullable=False)
    Prompt_content = db.Column(db.Text, nullable=False)
    Call_count = db.Column(db.Integer, nullable=False)


class HistoryChat(db.Model):
    __tablename__ = 'History_chat'

    Dialog_ID = db.Column(db.Integer, primary_key=True, nullable=False)
    Dialog_date = db.Column(db.DateTime, nullable=False)
    Dialog_content = db.Column(db.Text, nullable=False)
    User_ID = db.Column(db.Integer, db.ForeignKey('User_table.User_ID'), nullable=False)
