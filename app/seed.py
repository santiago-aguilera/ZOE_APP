"""
Script de datos de prueba para ZOE.
Crea un usuario por cada rol: Coordinador, Profesor, Estudiante.
Ejecutar con: python seed.py
"""
import sys
from pathlib import Path
from datetime import date

# Configurar sys.path para que funcione como script
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.model import (
    db, Usuario, Estudiante, Profesor, Coordinador,
    PeriodoAcademico, Materia, Comunicado,
)
from config import Config
from flask import Flask

app = Flask(
    __name__,
    template_folder=str(Config.TEMPLATES_FOLDER),
    static_folder=str(Config.STATIC_FOLDER),
)
app.config.from_object(Config)
db.init_app(app)


def main():
    with app.app_context():
        # Limpiar tablas
        db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0"))
        for tabla in [
            "ENTREGA", "MENSAJE", "RECURSO", "TAREA", "GRUPO",
            "ESTUDIANTE_GRUPO", "PROFESOR_MATERIA", "ESTUDIANTE_MATERIA",
            "CRONOGRAMA", "COMUNICADO", "MATERIA", "USUARIO", "PERIODO_ACADEMICO",
        ]:
            db.session.execute(db.text(f"DELETE FROM `{tabla}`"))
        db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 1"))
        db.session.commit()

        # 1. Crear Período Académico
        periodo = PeriodoAcademico(
            nombre="Periodo 1 - 2026",
            fecha_inicio=date(2026, 2, 1),
            fecha_fin=date(2026, 6, 30),
            activo=True,
        )
        db.session.add(periodo)
        db.session.commit()
        print(f"[OK] Período creado: {periodo.nombre} (id={periodo.id})")

        # 2. Crear usuarios de prueba (uno por cada rol)
        usuarios_demo = [
            Coordinador(
                nombre="Ana Coordinadora",
                correo="coord@zoe.app",
                contrasena_hash="admin123",
                periodo_id=periodo.id,
            ),
            Profesor(
                nombre="Carlos Profesor",
                correo="prof@zoe.app",
                contrasena_hash="profe123",
                periodo_id=periodo.id,
            ),
            Estudiante(
                nombre="Pedro Estudiante",
                correo="est@zoe.app",
                contrasena_hash="est123",
                periodo_id=periodo.id,
            ),
        ]
        for u in usuarios_demo:
            db.session.add(u)
        db.session.commit()
        print(f"[OK] 3 usuarios creados (coord/prof/est)")

        # 3. Crear una materia de ejemplo
        materia = Materia(
            nombre="Matemáticas IB",
            descripcion="Curso introductorio de matemáticas para IB",
            periodo=periodo,
        )
        db.session.add(materia)
        db.session.commit()
        print(f"[OK] Materia creada: {materia.nombre}")

        # 4. Asignar profesor a la materia (POO encapsulado)
        prof = Usuario.query.filter_by(correo="prof@zoe.app").first()
        if isinstance(prof, Profesor):
            prof.asignarMateria(materia)
            print(f"[OK] Profesor {prof.nombre} asignado a {materia.nombre}")

        # 5. Inscribir estudiante en la materia (POO)
        est = Usuario.query.filter_by(correo="est@zoe.app").first()
        if isinstance(est, Estudiante):
            est.inscribirMateria(materia)
            print(f"[OK] Estudiante {est.nombre} inscrito en {materia.nombre}")

        # 6. Publicar un comunicado (POO Coordinador.publicarComunicado)
        coord = Usuario.query.filter_by(correo="coord@zoe.app").first()
        com = Comunicado(
            titulo="Bienvenida al ciclo escolar 2026",
            contenido="Las clases inician el 1 de febrero. Revisar el cronograma.",
            creadoPor=coord,
            publicadoEn=date.today(),
            activo=True,
        )
        com.publicarComunicado()
        print(f"[OK] Comunicado publicado: {com.titulo}")

        print("\n=== USUARIOS DE PRUEBA CREADOS ===")
        print("Coordinador: coord@zoe.app  / admin123")
        print("Profesor:    prof@zoe.app   / profe123")
        print("Estudiante:  est@zoe.app    / est123")
        print("====================================")


if __name__ == "__main__":
    main()
