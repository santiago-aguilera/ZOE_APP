"""
Modelo SQLAlchemy para COMUNICADO.
Mantiene los métodos POO originales.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .db import db


class Comunicado(db.Model):
    __tablename__ = "COMUNICADO"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    contenido = Column(Text, nullable=True)
    creado_por = Column(Integer, ForeignKey("USUARIO.id"), nullable=False)
    publicado_en = Column(DateTime, default=datetime.now)
    activo = Column(Boolean, default=True)

    # Relaciones
    creador = relationship("Usuario", back_populates="comunicados_creados", foreign_keys=[creado_por])

    def __init__(self, id=None, titulo=None, contenido=None, creadoPor=None,
                 publicadoEn=None, activo=True, **kwargs):
        super().__init__(**kwargs)
        if id is not None:
            self.id = id
        self.titulo = titulo
        self.contenido = contenido
        if creadoPor is not None:
            self.creado_por = creadoPor.id if hasattr(creadoPor, 'id') else creadoPor
            self.creador = creadoPor if hasattr(creadoPor, 'id') else None
        self.publicado_en = publicadoEn if publicadoEn else datetime.now()
        self.activo = activo

    @property
    def creadoPor(self):
        """Alias para Jinja2 - compatibilidad con templates existentes."""
        return self.creador

    @property
    def publicadoEn(self):
        """Alias para Jinja2 - compatibilidad con templates existentes."""
        return self.publicado_en

    def get_titulo(self):
        return self.titulo

    def get_contenido(self):
        return self.contenido

    def get_creador(self):
        return self.creador

    def get_publicado_en(self):
        return self.publicado_en

    def es_activo(self):
        return self.activo

    def publicarComunicado(self):
        db.session.add(self)
        db.session.commit()
        print(f"Comunicado '{self.titulo}' publicado por {self.creador.nombre}")

    def mostrarInfo(self):
        estado = "Activo" if self.activo else "Inactivo"
        print(f"[Comunicado] {self.id} - {self.titulo} | Estado: {estado}")

    def __repr__(self):
        return f"<Comunicado {self.titulo}>"