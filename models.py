from sqlalchemy import Column, Integer, String, Date, Boolean, BigInteger, Numeric
from sqlalchemy.ext.declarative import declarative_base
from datetime import date
from sqlalchemy import Column, Integer, String
from database import Base

Base = declarative_base()

class Contrato(Base):
    __tablename__ = 'contratos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_remesa = Column(String, nullable=True)
    numero_tarjeta = Column(String, nullable=True)
    numero_cuenta = Column(BigInteger, nullable=False)
    titular = Column(String, nullable=False)
    nivel_cuenta = Column(Integer, nullable=True)
    cc = Column(Integer, nullable=False)
    sucursal = Column(String, nullable=False)
    motivo = Column(String, nullable=True)
    observaciones = Column(String, nullable=True)
    fecha_carga = Column(Date, nullable=False, default=date.today)
    usuario=Column(String (255), nullable=False)
    estatus=Column(String, nullable=False, default="SOLICITADO")
    url=Column(String, nullable=True)

class usuarios(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    correo = Column(String(255), unique=True, nullable=False)
    contrasena = Column(String, nullable=False)
    es_maestro = Column(Boolean, default=False)

class Spei(Base):
    __tablename__ = 'spei'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_tramite = Column(Date, nullable=False)
    cc = Column(Integer, nullable=False)
    sucursal = Column(String, nullable=False)
    cuenta_origen = Column(BigInteger, nullable=False)
    titular = Column(String, nullable=False)
    cuenta_destino = Column(String(18), nullable=False)
    beneficiario = Column(String, nullable=False)
    importe = Column(Numeric(10, 2), nullable=False)
    autorizador = Column(String, nullable=False)
    estatus = Column(String, nullable=False, default='ENVIADO')
    usuario = Column(String, nullable=False)

class Retiros(Base):
    __tablename__ = 'retiros'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_tramite = Column(Date, nullable=False)
    cc = Column(Integer, nullable=False)
    sucursal = Column(String, nullable=False)
    cr = Column(String, nullable=False)
    cuenta_origen = Column(BigInteger, nullable=False)
    titular = Column(String, nullable=False)
    cuenta_destino = Column(BigInteger, nullable=False)
    beneficiario = Column(String, nullable=False)
    importe = Column(Numeric(14, 2), nullable=False)
    clave_autorizacion = Column(String, nullable=False)
    operacion = Column(String, nullable=False)
    usuario = Column(String, nullable=False)
    motivo = Column(String, nullable=True)

class Nominales(Base):
    __tablename__ = 'nominales'
    id = Column(Integer, primary_key=True, autoincrement=True)
    remesa = Column(String, nullable=False)
    numero_cuenta = Column(BigInteger, nullable=True)
    tarjeta = Column(String(16), nullable=False)
    beneficiario = Column(String, nullable=False)
    cc = Column(Integer, nullable=True)
    sucursal = Column(String, nullable=False)
    entidad = Column(String, nullable=False)
    incidencia = Column(String, nullable=False)
    observaciones = Column(String, nullable=True)
    fecha_incidencia = Column(Date, nullable=False, default=date.today)
    usuario = Column(String, nullable=False)