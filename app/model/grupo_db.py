"""
Modelo SQLAlchemy para GRUPO y ESTUDIANTE_GRUPO.
Mantiene los métodos POO originales.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .db import db


class EstudianteGrupo(db.Model):
    __tablename__ = "ESTUDIANTE_GRUPO"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("USUARIO.id"), nullable=False)
    grupo_id = Column(Integer, ForeignKey("GRUPO.id"), nullable=False)
    unido_en = Column(DateTime, default=datetime.now)

    usuario = relationship("Usuario", back_populates="estudiante_grupos", foreign_keys=[usuario_id])
    grupo = relationship("Grupo", back_populates="estudiantes_rel", foreign_keys=[grupo_id])
    estudiante_obj = relationship("Estudiante", back_populates="grupos_rel", foreign_keys=[usuario_id],
                                   overlaps="usuario,estudiante_grupos")


class Grupo(db.Model):
    __tablename__ = "GRUPO"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    materia_id = Column(Integer, ForeignKey("MATERIA.id"), nullable=False)
    creado_por = Column(Integer, ForeignKey("USUARIO.id"), nullable=False)
    creado_en = Column(DateTime, default=datetime.now)

    # Relaciones
    materia = relationship("Materia", back_populates="grupos")
    creador = relationship("Usuario", back_populates="grupos_creados", foreign_keys=[creado_por])
    estudiantes_rel = relationship("EstudianteGrupo", back_populates="grupo", lazy="dynamic")

    def __init__(self, id=None, nombre=None, descripcion=None, materia=None, creadoPor=None, **kwargs):
        super().__init__(**kwargs)
        if id is not None:
            self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        if materia is not None:
            self.materia_id = materia.id if hasattr(materia, 'id') else materia
            self.materia = materia if hasattr(materia, 'id') else None
        if creadoPor is not None:
            self.creado_por = creadoPor.id if hasattr(creadoPor, 'id') else creadoPor
            self.creador = creadoPor if hasattr(creadoPor, 'id') else None

    @property
    def estudiantes(self):
        return [eg.usuario for eg in self.estudiantes_rel.all()]

    def get_id(self):
        return self.id

    def get_nombre(self):
        return self.nombre

    def get_materia(self):
        return self.materia

    def get_profesor(self):
        return self.creador

    def get_estudiantes(self):
        return self.estudiantes

    def agregarEstudiante(self, estudiante):
        existing = EstudianteGrupo.query.filter_by(
            usuario_id=estudiante.id, grupo_id=self.id
        ).first()
        if not existing:
            eg = EstudianteGrupo(usuario_id=estudiante.id, grupo_id=self.id)
            db.session.add(eg)
            db.session.commit()

    def cambiarMateria(self, materia):
        self.materia_id = materia.id if hasattr(materia, 'id') else materia
        db.session.commit()

    def mostrarInfo(self):
        print(f"[Grupo] {self.id} - {self.nombre}")

    def __repr__(self):
        return f"<Grupo {self.nombre}>"