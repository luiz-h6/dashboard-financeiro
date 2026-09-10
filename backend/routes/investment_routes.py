from middleware.auth import token_required
from flask import Blueprint, request, jsonify
from services.investment_service import sync_investment_prices

bp = Blueprint('investments', __name__, url_prefix='/api/investments')



@bp.route('/sync-prices', methods=['POST'])
@token_required
def sync_prices(current_user_id):
    """
    Força a sincronização das cotações (Renda Variável) usando a API pública.
    """
    user_id = current_user_id
    try:
        result = sync_investment_prices(user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "Failed to sync investment prices", "details": str(e)}), 500
