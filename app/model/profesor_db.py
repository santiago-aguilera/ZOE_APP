"""
Modelo SQLAlchemy para PROFESOR (hereda de USUARIO con polimorfismo).
Mantiene los métodos POO originales.
"""
from sqlalchemy.orm import relationship

from .db import db
from .usuario_db import Usuario


class Profesor(Usuario):
    __mapper_args__ = {
        "polymorphic_identity": "Profesor",
    }

    # Relaciones many-to-many específicas de profesor
    materias_rel = relationship("ProfesorMateria", back_populates="profesor_obj", lazy="dynamic")

    def __init__(self, id=None, nombre=None, correo=None, contrasena_hash=None, **kwargs):
        super().__init__(id=id, nombre=nombre, correo=correo, contrasena_hash=contrasena_hash, rol="Profesor", **kwargs)

    @property
    def materias(self):
        return [pm.materia for pm in self.materias_rel.all()]

    def get_materias(self):
        return self.materias

    def asignarMateria(self, materia):
        from .materia_db import ProfesorMateria
        existing = ProfesorMateria.query.filter_by(
            usuario_id=self.id, materia_id=materia.id
        ).first()
        if not existing:
            pm = ProfesorMateria(usuario_id=self.id, materia_id=materia.id)
            db.session.add(pm)
            db.session.commit()

    def mostrarInfo(self):
        print(f"[Profesor] {self.id} - {self.nombre}")

    def __repr__(self):
        return f"<Profesor {self.nombre}>"