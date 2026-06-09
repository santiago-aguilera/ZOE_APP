"""
Modelo SQLAlchemy para COORDINADOR (hereda de USUARIO con polimorfismo).
Mantiene los métodos POO originales.
"""
from .db import db
from .usuario_db import Usuario


class Coordinador(Usuario):
    __mapper_args__ = {
        "polymorphic_identity": "Coordinador",
    }

    def __init__(self, id=None, nombre=None, correo=None, contrasena_hash=None, **kwargs):
        super().__init__(id=id, nombre=nombre, correo=correo, contrasena_hash=contrasena_hash, rol="Coordinador", **kwargs)

    def crearMateria(self, materia):
        db.session.add(materia)
        db.session.commit()
        print(f"{self.nombre} creó la materia {materia.nombre}")

    def publicarComunicado(self, comunicado):
        db.session.add(comunicado)
        db.session.commit()
        print(f"{self.nombre} publicó el comunicado '{comunicado.titulo}'")

    def mostrarInfo(self):
        print(f"[Coordinador] {self.id} - {self.nombre}")

    def __repr__(self):
        return f"<Coordinador {self.nombre}>"