"""
Aplicação Flask - Web Service da Loja de Jogos de Tabuleiro.

Este é o ponto de entrada do web service. Cria a aplicação Flask,
regista os Blueprints (rotas) e arranca o servidor.

Uso:
    python -m webservice.app
"""

from flask import Flask, jsonify

from webservice.config import Config
from webservice.routes import health_bp

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

    