# models/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Maquina(Base):
    __tablename__ = "maquina"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False, unique=True)
    ubicacion = Column(String(255))
    largo = Column(Float)
    direccion = Column(Boolean, default=True)
    
    tramos = relationship("Tramo", back_populates="maquina", cascade="all, delete-orphan")

class Tramo(Base):
    __tablename__ = "tramo"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_maquina = Column(Integer, ForeignKey("maquina.id"), nullable=False)
    numero_tramo = Column(Integer, nullable=False)
    largo_tramo = Column(Float)
    nota = Column(String(255))
    
    maquina = relationship("Maquina", back_populates="tramos")

class Historial(Base):
    __tablename__ = "historial"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    image_path = Column(String(255))
    eje_x = Column(Integer)
    eje_y = Column(Integer)
    eje_x2 = Column(Integer)
    eje_y2 = Column(Integer)
    largo = Column(Integer)
    ancho = Column(Integer)
    etiqueta = Column(String(50))
    prediccion = Column(String(50))
    modelo_correa = Column(String(50))
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    fecha_video = Column(DateTime)
    tramo = Column(Integer)

# models/models.py (agregar esta clase)
class Modelo(Base):
    __tablename__ = "modelo"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    accuracy = Column(Float, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    nombre_modelo = Column(String(255))    