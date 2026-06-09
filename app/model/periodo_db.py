"""
Modelo SQLAlchemy para PERIODO_ACADEMICO.
Mantiene los métodos POO como lógica de negocio.
"""
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.orm import relationship

from .db import db


class PeriodoAcademico(db.Model):
    __tablename__ = "PERIODO_ACADEMICO"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    activo = Column(Boolean, default=True)

    # Relaciones
    materias = relationship("Materia", back_populates="periodo", lazy="dynamic")
    usuarios = relationship("Usuario", back_populates="periodo", lazy="dynamic")

    def __init__(self, id=None, nombre=None, fecha_inicio=None, fecha_fin=None, activo=True, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.nombre = nombre
        self.fecha_inicio = self._parse_date(fecha_inicio) if isinstance(fecha_inicio, str) else fecha_inicio
        self.fecha_fin = self._parse_date(fecha_fin) if isinstance(fecha_fin, str) else fecha_fin
        self.activo = activo

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

    def agregarMateria(self, materia):
        """Método POO: agrega una materia al período."""
        self.materias.append(materia)
        db.session.add(materia)

    def get_nombre(self):
        return self.nombre

    def mostrarInfo(self):
        print(f"[PeriodoAcademico] {self.id} - {self.nombre} ({self.fecha_inicio} a {self.fecha_fin})")

    def __repr__(self):
        return f"<PeriodoAcademico {self.nombre}>"