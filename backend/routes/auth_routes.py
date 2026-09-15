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
        user_id = cursor.lastrowid
        
        # Injetar categorias e conta padrão para novos usuários
        accounts = [
            ('Nubank', 'checking', 0.0),
            ('PicPay', 'checking', 0.0),
            ('Mercado Pago', 'checking', 0.0)
        ]
        for acc in accounts:
            cursor.execute("INSERT INTO accounts (user_id, name, account_type, initial_balance) VALUES (?, ?, ?, ?)", (user_id, acc[0], acc[1], acc[2]))
            
        default_cats = [
            ('Salário', 'income', '#10b981'),
            ('Pagamentos de Terceiros', 'income', '#34d399'),
            ('Alimentação', 'expense', '#ef4444'),
            ('Moradia', 'expense', '#f59e0b'),
            ('Lazer', 'expense', '#3b82f6'),
            ('Transporte', 'expense', '#8b5cf6'),
            ('Esportes', 'expense', '#14b8a6'),
            ('Assinaturas e Serviços', 'expense', '#ec4899')
        ]
        for c in default_cats:
            cursor.execute("INSERT INTO categories (user_id, name, type, color) VALUES (?, ?, ?, ?)", (user_id, c[0], c[1], c[2]))
            
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
