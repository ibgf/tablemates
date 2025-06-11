import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 初始化 Flask 应用
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 用户表
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.Enum('player', 'merchant'), nullable=False)  # 玩家 or 商户
    ludo_balance = db.Column(db.Float, default=0)  # 预留 Ludo 余额
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    level_id = db.Column(db.Integer, db.ForeignKey('user_levels.id'), nullable=True)

# 用户级别表
class UserLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.Enum('player', 'merchant'), nullable=False)
    level_name = db.Column(db.String(50), nullable=False)
    level_order = db.Column(db.Integer, nullable=False)
    permissions = db.Column(db.JSON, default={})

# 商户类型表
class MerchantType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    merchant_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)

# 商户级别表
class MerchantLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    merchant_type_id = db.Column(db.Integer, db.ForeignKey('merchant_type.id'), nullable=False)
    level_name = db.Column(db.String(50), nullable=False)
    level_order = db.Column(db.Integer, nullable=False)
    permissions = db.Column(db.JSON, default={})

# 商户角色表
class MerchantRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    merchant_type_id = db.Column(db.Integer, db.ForeignKey('merchant_type.id'), nullable=False)
    role_name = db.Column(db.String(50), nullable=False)
    role_order = db.Column(db.Integer, nullable=False)
    permissions = db.Column(db.JSON, default={})

# API: 用户注册
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if 'email' not in data or 'password' not in data or 'user_type' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    new_user = User(
        email=data['email'],
        password=data['password'],
        user_type=data['user_type']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

# API: 用户登录
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email'], password=data['password']).first()
    if user:
        return jsonify({'message': 'Login successful', 'user_id': user.id, 'user_type': user.user_type})
    return jsonify({'error': 'Invalid credentials'}), 401

# API: 获取用户级别
@app.route('/user_levels', methods=['GET'])
def get_user_levels():
    levels = UserLevel.query.all()
    return jsonify([{'id': lvl.id, 'name': lvl.level_name, 'user_type': lvl.user_type} for lvl in levels])

if __name__ == '__main__':
    if not os.path.exists('users.db'):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
