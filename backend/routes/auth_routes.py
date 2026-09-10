from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from db import get_db

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400
        
    hashed_password = generate_password_hash(password)
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", 
                       (name, email, hashed_password))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'error': 'Email already exists'}), 400
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if user and check_password_hash(user['password_hash'], password):
        # Generate JWT token
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'token': token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email']
            }
        }), 200
        
    return jsonify({'error': 'Invalid credentials'}), 401
