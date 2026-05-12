"""
Ponto de entrada da GUI NiceGUI.

Executa com:
    python -m gui.main

(O Flask deve estar a correr em paralelo noutro terminal.)
"""
from nicegui import ui

from gui.paginas.home import criar_pagina_home
