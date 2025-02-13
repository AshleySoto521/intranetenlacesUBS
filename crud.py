import pandas as pd
from database import Session
from models import *
import logging
import re

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)

def clean_sql_string(value):
    """
    Limpia caracteres no válidos para SQL y caracteres especiales Unicode.
    """
    if pd.isna(value):
        return ""
    
    # Convertir a string si no lo es
    value = str(value)
    
    # Eliminar caracteres especiales Unicode comunes que causan problemas
    value = value.replace('\xa0', ' ')  # NO-BREAK SPACE
    value = value.replace('\u200b', '')  # ZERO WIDTH SPACE
    
    # Eliminar otros caracteres Unicode no imprimibles
    value = ''.join(char for char in value if char.isprintable() or char.isspace())
    
    # Eliminar caracteres que podrían ser problemáticos en SQL
    value = re.sub(r'[\000-\010\013\014\016-\037]', '', value)
    
    # Limpiar espacios múltiples y espacios al inicio/final
    value = ' '.join(value.split())
    
    return value

def tiene_permiso(usuario, pagina):
    session_db = Session()
    try:
        user = session_db.query(usuarios).filter_by(nombre=usuario).first()
        if user:
            permisos = user.permisos.split(",")
            return "todos" in permisos or pagina in permisos
        return False
    finally:
        session_db.close()
