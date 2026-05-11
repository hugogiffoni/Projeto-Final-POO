"""
Endpoint de Health Check.

Permite verificar se o web service está a funcionar e se a base
de dados está acessível. Útil para testes e monitorização.
"""

from datetime import datetime
from pathlib import Path

from flask import Blueprint, jsonify

from database.connection import Database
from webservice.config import Config

