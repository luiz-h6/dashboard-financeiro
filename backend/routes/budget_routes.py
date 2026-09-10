from middleware.auth import token_required
from flask import Blueprint, request, jsonify
from models.budget import set_budget, get_budgets, delete_budget

budget_bp = Blueprint('budget_bp', __name__)

def get_user_id():
    return request.headers.get('X-User-Id')

@budget_bp.route('/', methods=['POST'])
def add_or_update_budget():
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    data['user_id'] = user_id
    budget_id = set_budget(data)
    return jsonify({"message": "Budget saved", "id": budget_id}), 201

@budget_bp.route('/', methods=['GET'])
def list_budgets():
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    month_year = request.args.get('month_year')
    budgets = get_budgets(user_id, month_year)
    return jsonify(budgets), 200

@budget_bp.route('/<int:budget_id>', methods=['DELETE'])
def remove_budget(budget_id):
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    deleted = delete_budget(budget_id, user_id)
    if deleted:
        return jsonify({"message": "Budget deleted"}), 200
    return jsonify({"error": "Budget not found"}), 404
