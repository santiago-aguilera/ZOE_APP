"""
Modelo SQLAlchemy para TAREA.
Mantiene los métodos POO originales.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .db import db


class Tarea(db.Model):
    __tablename__ = "TAREA"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    instrucciones = Column(Text, nullable=True)
    fecha_limite = Column(Date, nullable=False)
    materia_id = Column(Integer, ForeignKey("MATERIA.id"), nullable=False)
    creado_por = Column(Integer, ForeignKey("USUARIO.id"), nullable=False)
    creado_en = Column(DateTime, default=datetime.now)

    # Relaciones
    materia = relationship("Materia", back_populates="tareas")
    creador = relationship("Usuario", back_populates="tareas_creadas", foreign_keys=[creado_por])
    entregas = relationship("Entrega", back_populates="tarea", lazy="dynamic")

    def __init__(self, id=None, titulo=None, instrucciones=None, fecha_limite=None,
                 materia=None, creadoPor=None, **kwargs):
        super().__init__(**kwargs)
        if id is not None:
            self.id = id
        self.titulo = titulo
        self.instrucciones = instrucciones
        self.fecha_limite = self._parse_date(fecha_limite) if isinstance(fecha_limite, str) else fecha_limite
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

    def get_id(self):
        return self.id

    def get_titulo(self):
        return self.titulo

    def get_instrucciones(self):
        return self.instrucciones

    def get_fecha_limite(self):
        return self.fecha_limite

    def get_materia(self):
        return self.materia

    @property
    def creadoPor(self):
        """Alias para Jinja2 - compatibilidad con templates existentes."""
        return self.creador

    def get_creador(self):
        return self.creador

    def get_entregas(self):
        return self.entregas.all()

    def registrarEntrega(self, entrega_info=None):
        """registrarEntrega - añade entrega existente a la sesión."""
        if entrega_info:
            db.session.add(entrega_info)
            db.session.commit()

    def mostrarInfo(self):
        print(f"[Tarea] {self.id} - {self.titulo}")

    def __repr__(self):
        return f"<Tarea {self.titulo}>"