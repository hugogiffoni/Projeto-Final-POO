"""
Cliente HTTP para comunicar com o web service Flask.

Centraliza todas as chamadas à API. As páginas NiceGUI usam
estas funções em vez de fazer httpx diretamente.

Levanta APIError em caso de erro HTTP, com a mensagem do servidor.
"""