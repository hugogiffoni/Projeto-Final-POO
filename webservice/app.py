"""
Aplicação Flask - Web Service da Loja de Jogos de Tabuleiro.

Este é o ponto de entrada do web service. Cria a aplicação Flask,
regista os Blueprints (rotas) e arranca o servidor.

Uso:
    python -m webservice.app
"""

from flask import Flask, jsonify

from webservice.config import Config
from webservice.routes.health import health_bp
from webservice.routes.jogos import jogos_bp 
from webservice.routes.clientes import clientes_bp 
from webservice.routes.catalogos import catalogos_bp

def create_app(config_class: type = Config) -> Flask:
    """
    Factory de criação da aplicação Flask.

    Usar uma factory (em vez de criar a app no topo do módulo) é uma
    boa prática que facilita testes e múltiplas configurações.

    Args:
        config_class: Classe de configuração a usar.

    Returns:
        Instância da aplicação Flask configurada.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Registar Blueprints (rotas) com prefixo / api
    app.register_blueprint(health_bp, url_prefix=config_class.API_PREFIX)
    app.register_blueprint(jogos_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(catalogos_bp)
    
     # sem url_prefix porque já tem no Blueprint

    # ----------------------------------------------------------------
    # Handlers de erro globais (devolvem JSON em vez de HTML)
    # ----------------------------------------------------------------
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Recurso não encontrado",
            "status": 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "error": "Método HTTP não permitido para esse endpoint",
            "status": 405
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Erro interno do servidor",
            "status": 500
        }), 500
    
    # ----------------------------------------------------------------
    # Rota raiz (informação básica do serviço)
    # ----------------------------------------------------------------

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "servico": "Loja de Jogos de Tabuleiro - API",
            "versao": "1.0.0",
            "endpoints_disponiveis": [
                f"{config_class.API_PREFIX}/health",
                f"{config_class.API_PREFIX}/jogos",
                f"{config_class.API_PREFIX}/clientes"
            ],
            "documentacao": "Ver README.md"

        })
    return app

# =====================================================================
# Entry point
# =====================================================================

if __name__ == "__main__":
    app = create_app()
    print("\n" + "=" * 60)
    print("Servidor Flask a iniciar...")
    print(f"URL: http://{Config.HOST}:{Config.PORT}")
    print(f"Health check: http://{Config.HOST}:{Config.PORT}/api/health")
    print("=" * 60 + "\n")

    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
    )
