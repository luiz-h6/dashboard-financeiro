from middleware.auth import token_required
from flask import Blueprint, request, jsonify
from models.account import create_account, get_accounts, get_account_by_id, update_account, delete_account

bp = Blueprint('accounts', __name__, url_prefix='/api/accounts')



@bp.route('/', methods=['POST'])
@token_required
def create(current_user_id):
    data = request.json
    data['user_id'] = current_user_id
    account_id = create_account(data)
    return jsonify({"message": "Account created successfully", "id": account_id}), 201

@bp.route('/', methods=['GET'])
@token_required
def list_accounts(current_user_id):
    user_id = current_user_id
    accounts = get_accounts(user_id)
    return jsonify(accounts), 200

@bp.route('/<int:account_id>', methods=['GET'])
@token_required
def get_account(current_user_id, account_id):
    user_id = current_user_id
    account = get_account_by_id(account_id, user_id)
    if account:
        return jsonify(account), 200
    return jsonify({"error": "Account not found"}), 404

@bp.route('/<int:account_id>', methods=['PUT'])
@token_required
def update(current_user_id, account_id):
    data = request.json
    user_id = current_user_id
    rows = update_account(account_id, user_id, data)
    if rows > 0:
        return jsonify({"message": "Account updated successfully"}), 200
    return jsonify({"error": "Account not found or no changes made"}), 404

@bp.route('/<int:account_id>', methods=['DELETE'])
@token_required
def delete(current_user_id, account_id):
    user_id = current_user_id
    rows = delete_account(account_id, user_id)
    if rows > 0:
        return jsonify({"message": "Account deleted successfully"}), 200
    return jsonify({"error": "Account not found"}), 404
