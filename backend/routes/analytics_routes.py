from middleware.auth import token_required
from flask import Blueprint, request, jsonify
from services.analytics_service import get_dashboard_data

bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

def get_current_user_id():
    # Simulação do auth
    return request.headers.get('X-User-Id', 1)

@bp.route('/dashboard', methods=['GET'])
@token_required
def dashboard(current_user_id):
    """
    Retorna todos os dados processados via Pandas para o Dashboard Principal.
    """
    user_id = current_user_id
    try:
        data = get_dashboard_data(user_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": "Failed to generate dashboard data", "details": str(e)}), 500
