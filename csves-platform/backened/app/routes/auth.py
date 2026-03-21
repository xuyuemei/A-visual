from flask import Blueprint, request, jsonify
#from models import db, UserTable
from ..models import db, UserTable  
from werkzeug.security import generate_password_hash, check_password_hash

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/api/login', methods=['POST'])
def login():
    user_account = request.form.get('userAccount')
    user_password = request.form.get('userPassword')

    if not user_account or not user_password:
        return jsonify({'code': 400, 'message': '账号和密码不能为空'})

    user = UserTable.query.filter_by(User_name=user_account).first()
    if not user:
        return jsonify({'code': 401, 'message': '用户不存在'})

    # 明文比对（开发用）：
    if user.User_password != user_password:
        return jsonify({'code': 403, 'message': '密码错误'})

    # 若启用加密密码：
    # if not check_password_hash(user.User_password, user_password):
    #     return jsonify({'code': 403, 'message': '密码错误'})

    return jsonify({'code': 200, 'message': '登录成功', 'data': {
        'userId': user.User_ID,
        'username': user.User_name,
        'level': user.User_level,
    }})

@user_routes.route('/api/signin', methods=['POST'])
def signin():
    username = request.form.get('userAccount')
    password = request.form.get('userPassword')
    phone = request.form.get('userPhone')
    email = request.form.get('userEmail')

    if not username or not password or not phone:
        return jsonify({'code': 400, 'message': '用户名、手机号和密码不能为空'})

    # 查重用户名或手机号
    if UserTable.query.filter_by(User_name=username).first():
        return jsonify({'code': 409, 'message': '用户名已存在'})
    if UserTable.query.filter_by(User_phone=phone).first():
        return jsonify({'code': 409, 'message': '手机号已注册'})

    # 可使用加密存储密码（推荐）
    # hashed_pwd = generate_password_hash(password)
    # user = UserTable(User_name=username, User_phone=phone, User_password=hashed_pwd, User_email=email)
    
    # 明文存储密码（仅用于开发测试）
    user = UserTable(User_name=username, User_phone=phone, User_password=password, User_email=email)

    db.session.add(user)
    db.session.commit()

    return jsonify({'code': 200, 'message': '注册成功', 'data': {
        'userId': user.User_ID,
        'username': user.User_name
    }})
