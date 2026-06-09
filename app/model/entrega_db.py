"""
Modelo SQLAlchemy para ENTREGA.
Mantiene los métodos POO originales.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .db import db


class Entrega(db.Model):
    __tablename__ = "ENTREGA"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tarea_id = Column(Integer, ForeignKey("TAREA.id"), nullable=False)
    estudiante_id = Column(Integer, ForeignKey("USUARIO.id"), nullable=False)
    archivo_url = Column(String(255), nullable=True)
    fecha_entrega = Column(DateTime, nullable=False, default=datetime.now)
    estado = Column(String(50), default="Pendiente")
    calificacion = Column(String(50), nullable=True)
    comentario_profesor = Column(Text, nullable=True)

    # Relaciones
    tarea = relationship("Tarea", back_populates="entregas")
    estudiante_obj = relationship("Estudiante", back_populates="entregas", foreign_keys=[estudiante_id])

    def __init__(self, id=None, tarea=None, estudiante=None, archivo_url=None,
                 fecha_entrega=None, **kwargs):
        super().__init__(**kwargs)
        if id is not None:
            self.id = id
        if tarea is not None:
            self.tarea_id = tarea.id if hasattr(tarea, 'id') else tarea
            self.tarea = tarea if hasattr(tarea, 'id') else None
        if estudiante is not None:
            self.estudiante_id = estudiante.id if hasattr(estudiante, 'id') else estudiante
            self.estudiante_obj = estudiante if hasattr(estudiante, 'id') else None
        self.archivo_url = archivo_url
        self.fecha_entrega = self._parse_date(fecha_entrega) if isinstance(fecha_entrega, str) else fecha_entrega
        if self.estado is None:
            self.estado = "Pendiente"

    @staticmethod
    def _parse_date(val):
        if isinstance(val, (date, datetime)):
            return val if isinstance(val, datetime) else datetime.combine(val, datetime.min.time())
        if val and isinstance(val, str):
            try:
                return datetime.strptime(val, "%Y-%m-%d")
            except ValueError:
                pass
            try:
                return datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None
        return val if val else datetime.now()

    def get_id(self):
        return self.id

    def get_tarea(self):
        return self.tarea

    @property
    def estudiante(self):
        """Alias para Jinja2 - compatibilidad con templates existentes."""
        return self.estudiante_obj

    def get_estudiante(self):
        return self.estudiante_obj

    def get_archivo_url(self):
        return self.archivo_url

    def get_fecha_entrega(self):
        return self.fecha_entrega

    def get_estado(self):
        return self.estado

    def get_calificacion(self):
        return self.calificacion

    def registrarEntrega(self):
        self.estado = "Entregado"
        db.session.commit()

    def calificarEntrega(self, calificacion):
        self.calificacion = calificacion
        db.session.commit()
        print(f"Entrega {self.id} calificada con {calificacion}")

    def mostrarInfo(self):
        print(f"[Entrega] {self.id} - Tarea: {self.tarea.titulo} | Estudiante: {self.estudiante_obj.nombre}")

    def __repr__(self):
        return f"<Entrega {self.id} - {self.estado}>"