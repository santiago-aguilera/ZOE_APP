"""
Modelo SQLAlchemy para CRONOGRAMA.
Mantiene los métodos POO originales.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .db import db


class Cronograma(db.Model):
    __tablename__ = "CRONOGRAMA"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_evento = Column(Date, nullable=False)
    tipo = Column(String(50), nullable=True)
    materia_id = Column(Integer, ForeignKey("MATERIA.id"), nullable=False)
    creado_por = Column(Integer, ForeignKey("USUARIO.id"), nullable=False)
    creado_en = Column(DateTime, default=datetime.now)

    # Relaciones
    materia = relationship("Materia", back_populates="eventos")
    creador = relationship("Usuario", back_populates="eventos_creados", foreign_keys=[creado_por])

    def __init__(self, id=None, titulo=None, descripcion=None, fechaEvento=None,
                 tipo=None, materia=None, creadoPor=None, **kwargs):
        super().__init__(**kwargs)
        if id is not None:
            self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_evento = self._parse_date(fechaEvento) if isinstance(fechaEvento, str) else fechaEvento
        self.tipo = tipo
        if materia is not None:
            self.materia_id = materia.id if hasattr(materia, 'id') else materia
            self.materia = materia if hasattr(materia, 'id') else None
        if creadoPor is not None:
            self.creado_por = creadoPor.id if hasattr(creadoPor, 'id') else creadoPor
            self.creador = creadoPor if hasattr(creadoPor, 'id') else None

    @staticmethod
    def _parse_date(val):
        if isinstance(val, (date, datetime)):
            return val if isinstance(val, date) else val.date()
        if val and isinstance(val, str):
            try:
                return datetime.strptime(val, "%Y-%m-%d").date()
            except ValueError:
                return None
        return val

    @property
    def fechaEvento(self):
        """Alias para Jinja2 - compatibilidad con templates existentes."""
        return self.fecha_evento

    def get_titulo(self):
        return self.titulo

    def get_fecha_evento(self):
        return self.fecha_evento

    def get_materia(self):
        return self.materia

    def mostrarInfo(self):
        print(f"[Evento] {self.id} - {self.titulo}")

    def __repr__(self):
        return f"<Cronograma {self.titulo}>"