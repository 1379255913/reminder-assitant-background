from flask import jsonify, redirect, render_template, request, flash, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
pymysql.install_as_MySQLdb()
from . import main
from .errors import bad_request,servererror
from app.models import *
from app.run import db
from .decorators import login_limit, generate_token, validate_token


# 登录状态保持
# @main.context_processor
# def login_status():
#     # 从session中获取username
#     username = session.get('username')
#     # 如果有email信息，则证明已经登录了，我们从数据库中获取登陆者的昵称，来返回到全局
#     if username:
#         try:
#             str1 = UserInformation.query.filter_by(username=username).first()
#             if str1:
#                 return {'username': str1.username, 'nickname': str1.nickname}
#         except Exception as e:
#             raise e
#     # 如果email信息不存在，则未登录，返回空
#     return {}
@main.route("/indexf", methods=['POST'])
@login_limit
def indexf():
    return jsonify({'error': 'unauthorized', 'message': "eeeeee",'code':401})

# 登录
@main.route("/login", methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.get_json()['username']
        password = request.get_json()['password']
        if not all([username, password]):
            return bad_request('missing param')
        try:
            str1 = UserInformation.query.filter_by(username=username).first()
            if str1 is None:
                return bad_request('this user is not exist')
            if check_password_hash(str1.password, password):
                # session['username'] = username
                # session.permanent = True
                response = jsonify({'data': {
                    'username': username,
                    'token' : str(generate_token(username),'utf-8'),
                    'nickname' : str1.nickname,
                }, 'message': 'OK', 'code': 200}
                )
                response.status_code = 200
                return response
            else:
                return bad_request('password error')
        except Exception:
            raise Exception


# 注册
@main.route("/register", methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.get_json()['username']
        nickname = request.get_json()['nickname']
        password_1 = request.get_json()['password_1']
        password_2 = request.get_json()['password_2']
        if not all([username, nickname, password_1, password_2]):
            return bad_request("缺少参数")
        if password_1!=password_2: return bad_request('两次密码输入不一致')
        password = generate_password_hash(password_1, method="pbkdf2:sha256", salt_length=8)
        try:
            str1 = UserInformation.query.filter_by(username=username).first()
            if str1:
                return bad_request('username repeated')
            else:
                inf = UserInformation(username=username,password=password,nickname=nickname)
                db.session.add(inf)
                db.session.commit()
                response = jsonify({'data':{
                    'username':username,
                    'nickname':nickname,
                }, 'message': 'OK','code':200}
                )
                response.status_code = 200
                return response
        except Exception:
            return servererror('Internal server error')


@main.route("/changenickname", methods=['POST'])
@login_limit
def changenickname():
    if request.method == 'POST':
        nickname = request.get_json()['nickname']
        if not nickname: return bad_request("缺少参数")
        token = request.headers["Authorization"]
        t = validate_token(token.encode("utf-8"))
        str1 = db.session.query(UserInformation).filter_by(username=t["user"]).first()
        str1.nickname = nickname
        db.session.commit()
        response = jsonify({'data': {
            'nickname': str1.nickname,
        }, 'message': 'OK', 'code': 200}
        )
        response.status_code = 200
        return response


@main.route("/changepassword", methods=['POST'])
@login_limit
def changepassword():
    if request.method == 'POST':
        old_password = request.get_json()['old_password']
        password_1 = request.get_json()['password1']
        password_2 = request.get_json()['password2']
        if not all([old_password, password_1, password_2]):
            return bad_request("缺少参数")
        if password_1!=password_2: return bad_request('两次密码输入不一致')
        token = request.headers["Authorization"]
        t = validate_token(token.encode("utf-8"))
        str1 = db.session.query(UserInformation).filter_by(username=t["user"]).first()
        if check_password_hash(str1.password, old_password):
            str1.password = generate_password_hash(password_1, method="pbkdf2:sha256", salt_length=8)
            db.session.commit()
        else:return bad_request("密码错误")
        response = jsonify({'data': {
            'username': str1.username,
        }, 'message': 'OK', 'code': 200}
        )
        response.status_code = 200
        return response