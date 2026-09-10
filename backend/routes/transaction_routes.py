from middleware.auth import token_required
from flask import Blueprint, request, jsonify
from models.transaction import create_transaction, get_transactions, update_transaction, delete_transaction

bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')



@bp.route('/', methods=['POST'])
@token_required
def create(current_user_id):
    data = request.json
    data['user_id'] = current_user_id
    
    # Tratamento simples para garantir formato
    if 'is_essential' not in data:
        data['is_essential'] = False
        
    transaction_id = create_transaction(data)
    return jsonify({"message": "Transaction created successfully", "id": transaction_id}), 201

@bp.route('/', methods=['GET'])
@token_required
def list_transactions(current_user_id):
    user_id = current_user_id
    month = request.args.get('month')
    year = request.args.get('year')
    transactions = get_transactions(user_id, month, year)
    return jsonify(transactions), 200

@bp.route('/<int:transaction_id>', methods=['PUT'])
@token_required
def update(current_user_id, transaction_id):
    data = request.json
    user_id = current_user_id
    rows = update_transaction(transaction_id, user_id, data)
    if rows > 0:
        return jsonify({"message": "Transaction updated successfully"}), 200
    return jsonify({"error": "Transaction not found or no changes made"}), 404

@bp.route('/<int:transaction_id>', methods=['DELETE'])
@token_required
def delete(current_user_id, transaction_id):
    user_id = current_user_id
    rows = delete_transaction(transaction_id, user_id)
    if rows > 0:
        return jsonify({"message": "Transaction deleted successfully"}), 200
    return jsonify({"error": "Transaction not found"}), 404
