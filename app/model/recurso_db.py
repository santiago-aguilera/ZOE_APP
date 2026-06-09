"""
Modelo SQLAlchemy para RECURSO.
Mantiene los métodos POO originales.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .db import db


class Recurso(db.Model):
    __tablename__ = "RECURSO"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    url_archivo = Column(String(255), nullable=True)
    tipo = Column(String(50), nullable=True)
    materia_id = Column(Integer, ForeignKey("MATERIA.id"), nullable=False)
    creado_por = Column(Integer, ForeignKey("USUARIO.id"), nullable=False)
    creado_en = Column(DateTime, default=datetime.now)

    # Relaciones
    materia = relationship("Materia", back_populates="recursos")
    creador = relationship("Usuario", back_populates="recursos_creados", foreign_keys=[creado_por])

    def __init__(self, id=None, titulo=None, descripcion=None, urlArchivo=None,
                 tipo=None, materia=None, creadoPor=None, **kwargs):
        super().__init__(**kwargs)
        if id is not None:
            self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.url_archivo = urlArchivo
        self.tipo = tipo
        if materia is not None:
            self.materia_id = materia.id if hasattr(materia, 'id') else materia
            self.materia = materia if hasattr(materia, 'id') else None
        if creadoPor is not None:
            self.creado_por = creadoPor.id if hasattr(creadoPor, 'id') else creadoPor
            self.creador = creadoPor if hasattr(creadoPor, 'id') else None

    @property
    def creadoPor(self):
        """Alias para Jinja2 - compatibilidad con templates existentes."""
        return self.creador

    @property
    def urlArchivo(self):
        """Alias para Jinja2 - compatibilidad con templates existentes."""
        return self.url_archivo

    def get_titulo(self):
        return self.titulo

    def get_descripcion(self):
        return self.descripcion

    def get_url_archivo(self):
        return self.url_archivo

    def get_tipo(self):
        return self.tipo

    def get_materia(self):
        return self.materia

    def get_creador(self):
        return self.creador

    def mostrarInfo(self):
        print(f"[Recurso] {self.id} - {self.titulo} | Tipo: {self.tipo}")

    def __repr__(self):
        return f"<Recurso {self.titulo}>"