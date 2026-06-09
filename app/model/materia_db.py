"""
Modelo SQLAlchemy para MATERIA con tablas intermedias PROFESOR_MATERIA y ESTUDIANTE_MATERIA.
Mantiene los métodos POO originales.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship

from .db import db


# --- Tablas intermedias ---

class ProfesorMateria(db.Model):
    __tablename__ = "PROFESOR_MATERIA"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("USUARIO.id"), nullable=False)
    materia_id = Column(Integer, ForeignKey("MATERIA.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="profesor_materias", foreign_keys=[usuario_id])
    materia = relationship("Materia", back_populates="profesores_rel", foreign_keys=[materia_id])
    profesor_obj = relationship("Profesor", back_populates="materias_rel", foreign_keys=[usuario_id],
                                 overlaps="usuario,profesor_materias")


class EstudianteMateria(db.Model):
    __tablename__ = "ESTUDIANTE_MATERIA"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("USUARIO.id"), nullable=False)
    materia_id = Column(Integer, ForeignKey("MATERIA.id"), nullable=False)
    inscrito_en = Column(DateTime, default=datetime.now)

    usuario = relationship("Usuario", back_populates="estudiante_materias", foreign_keys=[usuario_id])
    materia = relationship("Materia", back_populates="estudiantes_rel", foreign_keys=[materia_id])
    estudiante_obj = relationship("Estudiante", back_populates="materias_rel", foreign_keys=[usuario_id],
                                   overlaps="usuario,estudiante_materias")


class Materia(db.Model):
    __tablename__ = "MATERIA"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    periodo_id = Column(Integer, ForeignKey("PERIODO_ACADEMICO.id"), nullable=False)
    creado_en = Column(DateTime, default=datetime.now)

    # Relaciones
    periodo = relationship("PeriodoAcademico", back_populates="materias")
    profesores_rel = relationship("ProfesorMateria", back_populates="materia", lazy="dynamic")
    estudiantes_rel = relationship("EstudianteMateria", back_populates="materia", lazy="dynamic")
    grupos = relationship("Grupo", back_populates="materia", lazy="dynamic")
    tareas = relationship("Tarea", back_populates="materia", lazy="dynamic")
    recursos = relationship("Recurso", back_populates="materia", lazy="dynamic")
    eventos = relationship("Cronograma", back_populates="materia", lazy="dynamic")

    def __init__(self, id=None, nombre=None, descripcion=None, periodo=None, **kwargs):
        super().__init__(**kwargs)
        if id is not None:
            self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        if periodo is not None:
            self.periodo = periodo
            self.periodo_id = periodo.id if hasattr(periodo, 'id') else periodo

    @property
    def profesores(self):
        return [pm.usuario for pm in self.profesores_rel.all()]

    @property
    def estudiantes(self):
        return [em.usuario for em in self.estudiantes_rel.all()]

    @property
    def cronograma(self):
        """Alias para Jinja2 - compatibilidad con templates existentes."""
        return self.eventos


    def get_id(self):
        return self.id

    def get_nombre(self):
        return self.nombre

    def get_periodo(self):
        return self.periodo

    def get_grupos(self):
        return self.grupos.all()

    def get_tareas(self):
        return self.tareas.all()

    def get_profesores(self):
        return self.profesores

    def get_recursos(self):
        return self.recursos.all()

    def asignarProfesor(self, profesor):
        existing = ProfesorMateria.query.filter_by(
            usuario_id=profesor.id, materia_id=self.id
        ).first()
        if not existing:
            pm = ProfesorMateria(usuario_id=profesor.id, materia_id=self.id)
            db.session.add(pm)
            db.session.commit()

    def agregarGrupo(self, grupo):
        grupo.materia_id = self.id
        db.session.add(grupo)
        db.session.commit()

    def agregarTarea(self, tarea):
        tarea.materia_id = self.id
        db.session.add(tarea)
        db.session.commit()

    def agregarRecurso(self, recurso):
        recurso.materia_id = self.id
        db.session.add(recurso)
        db.session.commit()

    def agregarEvento(self, evento):
        evento.materia_id = self.id
        db.session.add(evento)
        db.session.commit()

    def mostrarInfo(self):
        print(f"[Materia] {self.id} - {self.nombre}")

    def __repr__(self):
        return f"<Materia {self.nombre}>"