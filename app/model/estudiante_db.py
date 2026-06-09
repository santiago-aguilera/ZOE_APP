"""
Modelo SQLAlchemy para ESTUDIANTE (hereda de USUARIO con polimorfismo).
Mantiene los métodos POO originales con operaciones de BD.
"""
from sqlalchemy.orm import relationship

from .db import db
from .usuario_db import Usuario


class Estudiante(Usuario):
    __mapper_args__ = {
        "polymorphic_identity": "Estudiante",
    }

    # Relaciones many-to-many específicas de estudiante
    materias_rel = relationship("EstudianteMateria", back_populates="estudiante_obj", lazy="dynamic")
    grupos_rel = relationship("EstudianteGrupo", back_populates="estudiante_obj", lazy="dynamic")
    entregas = relationship("Entrega", back_populates="estudiante_obj", lazy="dynamic")

    def __init__(self, id=None, nombre=None, correo=None, contrasena_hash=None, **kwargs):
        super().__init__(id=id, nombre=nombre, correo=correo, contrasena_hash=contrasena_hash, rol="Estudiante", **kwargs)

    @property
    def materias(self):
        return [em.materia for em in self.materias_rel.all()]

    @property
    def grupos(self):
        return [eg.grupo for eg in self.grupos_rel.all()]

    def get_materias(self):
        return self.materias

    def get_grupos(self):
        return self.grupos

    def inscribirMateria(self, materia):
        from .materia_db import EstudianteMateria
        existing = EstudianteMateria.query.filter_by(
            usuario_id=self.id, materia_id=materia.id
        ).first()
        if not existing:
            em = EstudianteMateria(usuario_id=self.id, materia_id=materia.id)
            db.session.add(em)
            db.session.commit()

    def unirseGrupo(self, grupo):
        from .grupo_db import EstudianteGrupo
        existing = EstudianteGrupo.query.filter_by(
            usuario_id=self.id, grupo_id=grupo.id
        ).first()
        if not existing:
            eg = EstudianteGrupo(usuario_id=self.id, grupo_id=grupo.id)
            db.session.add(eg)
            db.session.commit()

    def entregarTarea(self, tarea, archivo_url=""):
        from datetime import datetime
        from .entrega_db import Entrega
        entrega = Entrega(
            tarea_id=tarea.id,
            estudiante_id=self.id,
            archivo_url=archivo_url,
            fecha_entrega=datetime.now(),
            estado="Entregado",
        )
        db.session.add(entrega)
        db.session.commit()
        print(f"{self.nombre} entregó la tarea: {tarea.titulo}")

    def mostrarInfo(self):
        print(f"[Estudiante] {self.id} - {self.nombre}")