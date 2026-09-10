from middleware.auth import token_required
from flask import Blueprint, request, jsonify
from models.category import create_category, get_categories, update_category, delete_category

bp = Blueprint('categories', __name__, url_prefix='/api/categories')



@bp.route('/', methods=['POST'])
@token_required
def create(current_user_id):
    data = request.json
    data['user_id'] = current_user_id
    category_id = create_category(data)
    return jsonify({"message": "Category created successfully", "id": category_id}), 201

@bp.route('/', methods=['GET'])
@token_required
def list_categories(current_user_id):
    user_id = current_user_id
    categories = get_categories(user_id)
    return jsonify(categories), 200

@bp.route('/<int:category_id>', methods=['PUT'])
@token_required
def update(current_user_id, category_id):
    data = request.json
    user_id = current_user_id
    rows = update_category(category_id, user_id, data)
    if rows > 0:
        return jsonify({"message": "Category updated successfully"}), 200
    return jsonify({"error": "Category not found or no changes made"}), 404

@bp.route('/<int:category_id>', methods=['DELETE'])
@token_required
def delete(current_user_id, category_id):
    user_id = current_user_id
    rows = delete_category(category_id, user_id)
    if rows > 0:
        return jsonify({"message": "Category deleted successfully"}), 200
    return jsonify({"error": "Category not found"}), 404
