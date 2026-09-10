from flask import Flask, jsonify
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Importa a configuração de banco de dados
import db

# Importa as rotas
from routes.auth_routes import auth_bp
from routes.account_routes import bp as accounts_bp
from routes.category_routes import bp as categories_bp
from routes.transaction_routes import bp as transactions_bp
from routes.analytics_routes import bp as analytics_bp
from routes.investment_routes import bp as investments_bp
from routes.budget_routes import budget_bp as budget_bp

load_dotenv()

def create_app():
    # Servir o frontend diretamente do Flask
    import os
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='/')
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_change_in_production')
    CORS(app) # Habilita acesso do frontend HTML estático

    # Inicializa a conexão com o banco de dados e cria tabelas se não existirem
    db.init_app(app)
    db.init_db(app)

    # Registra os Blueprints (Rotas)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(accounts_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(investments_bp)
    app.register_blueprint(budget_bp, url_prefix='/api/budgets')

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"}), 200

    @app.route('/')
    def serve_index():
        return app.send_static_file('index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        return app.send_static_file(path)

    @app.route('/api/db-check', methods=['GET'])
    def health_check_db():
        """Rota de verificação de saúde da API e status do banco de dados"""
        try:
            # Tenta obter uma conexão e realizar uma query simples
            conn = db.get_db()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 AS status")
                result = cursor.fetchone()
            
            return jsonify({
                "status": "success",
                "message": "A API e o Banco de Dados estão funcionando corretamente!",
                "db_status": result
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": "Falha na conexão com o Banco de Dados.",
                "error": str(e)
            }), 500

    return app

if __name__ == '__main__':
    app = create_app()
    # Executa a aplicação na porta 5000 (desenvolvimento)
    app.run(debug=True, port=5000)
