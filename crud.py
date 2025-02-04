import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import exists, text
from database import get_engine
from models import Contrato, usuarios
from datetime import date
import logging
import re

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)

def process_upload_file(df, usuario_logeado):
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    duplicated_accounts = []
    invalid_rows = []

    # Mapeo de columnas del Excel a las columnas de la base de datos
    column_mapping = {
        "NUMERO DE REMESA": "numero_remesa",
        "NUMERO DE TARJETA": "numero_tarjeta",
        "NUMERO DE CUENTA A 10 DIGITOS": "numero_cuenta",
        "TITULAR": "titular",
        "NIVEL DE CUENTA": "nivel_cuenta",
        "CC": "cc",
        "SUCURSAL": "sucursal",
        "MOTIVO": "motivo",
        "OBSERVACIONES": "observaciones"
    }

    # Convertir valores nulos a cadenas vacías antes de procesar el DataFrame
    df = df.fillna("")

    # Asegurar que las columnas tengan el tipo correcto
    try:
        df["NUMERO DE REMESA"] = df["NUMERO DE REMESA"].astype(str)
        df["NUMERO DE TARJETA"] = df["NUMERO DE TARJETA"].astype(str)
        df["NUMERO DE CUENTA A 10 DIGITOS"] = pd.to_numeric(df["NUMERO DE CUENTA A 10 DIGITOS"], errors='coerce').fillna(0).astype(int)
        df["TITULAR"] = df["TITULAR"].astype(str)
        df["NIVEL DE CUENTA"] = pd.to_numeric(df["NIVEL DE CUENTA"], errors='coerce').fillna(0).astype(int)
        df["CC"] = pd.to_numeric(df["CC"], errors='coerce').fillna(0).astype(int)
        df["SUCURSAL"] = df["SUCURSAL"].astype(str)
        df["MOTIVO"] = df["MOTIVO"].astype(str)
        df["OBSERVACIONES"] = df["OBSERVACIONES"].astype(str)
    except ValueError as e:
        logging.error(f"Error al convertir columnas: {e}")
        return {
            "status": "error",
            "message": f"Error al procesar las columnas del archivo: {e}",
            "duplicated_accounts": [],
            "invalid_rows": [],
        }

    # Procesamiento de las filas del DataFrame
    for _, row in df.iterrows():
        numero_cuenta = row["NUMERO DE CUENTA A 10 DIGITOS"]

        # Validar que el número de cuenta tenga entre 8 y 10 dígitos
        if len(str(numero_cuenta)) < 8 or len(str(numero_cuenta)) > 10:
            invalid_rows.append(row.to_dict())
            continue

        # Verificar si el número de cuenta ya existe
        exists_query = session.query(exists().where(Contrato.numero_cuenta == numero_cuenta)).scalar()
        if exists_query:
            duplicated_accounts.append(numero_cuenta)
            continue

        # Validar que los datos sean correctos
        if pd.isna(numero_cuenta) or pd.isna(row["TITULAR"]) or pd.isna(row["NIVEL DE CUENTA"]) or pd.isna(row["SUCURSAL"]):
            invalid_rows.append(row.to_dict())
            continue

        # Crear una nueva instancia de Contrato
        contrato = Contrato(
            numero_remesa=row["NUMERO DE REMESA"],
            numero_tarjeta=row["NUMERO DE TARJETA"],
            numero_cuenta=numero_cuenta,
            titular=row["TITULAR"],
            nivel_cuenta=row["NIVEL DE CUENTA"],
            cc=row["CC"],
            sucursal=row["SUCURSAL"],
            motivo=row["MOTIVO"],
            observaciones=row["OBSERVACIONES"],
            fecha_carga=date.today(),
            usuario=usuario_logeado,
            estatus="Pendiente"
        )

        # Intentar agregar el contrato a la base de datos
        try:
            session.add(contrato)
        except IntegrityError:
            session.rollback()
            invalid_rows.append(row.to_dict())

    # Intentar hacer commit de la sesión
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f"Error al hacer commit: {e}")
        return {
            "status": "error",
            "message": f"Error al cargar los datos: {str(e)}",
            "duplicated_accounts": duplicated_accounts,
            "invalid_rows": invalid_rows,
        }

    # Generar mensaje para el usuario
    if duplicated_accounts or invalid_rows:
        mensaje = f"Archivo procesado. Se encontraron {len(duplicated_accounts)} números de cuenta duplicados: {', '.join(map(str, duplicated_accounts))}."
        if invalid_rows:
            mensaje += f" Además, hubo {len(invalid_rows)} filas con datos inválidos."
        return {"status": "warning", "message": mensaje, "duplicated_accounts": duplicated_accounts, "invalid_rows": invalid_rows}
    else:
        return {"status": "success", "message": "Todos los datos se cargaron correctamente."}

def download():
    # Conectar a la base de datos y obtener los datos
    engine = get_engine()
    query = "SELECT * FROM contratos"
    df = pd.read_sql(query, engine)
    
    # Exportar los datos a un archivo Excel
    file_path = "base_de_datos.xlsx"
    df.to_excel(file_path, index=False)
    return file_path

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