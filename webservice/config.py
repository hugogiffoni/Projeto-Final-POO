"""
Configurações do Web Service Flask.

Centraliza todas as definições da aplicação (porta, debug, caminho da BD)
num só lugar, facilitando manutenção e futuras alterações.
"""
from pathlib import Path

class Config:
    """Configuração base da aplicação Flask."""

    # Servidor 
    HOST: str = "127.0.0.1"
    PORT: int = 5000
    DEBUG: bool = True

    # Base de dados (caminho absoluto para evitar problemas de CWD)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATABASE_PATH: Path = BASE_DIR / "database" / "loja_jogos.db"

    # API
    API_PREFIX: str = "/api"
    JSON_AS_ASCII: bool = False  # Permite acentos no JSON (ç,ã,etc.)
    JSON_SORT_KEYS: bool = False  # Mantém a ordem dos campos no JSON