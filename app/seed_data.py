"""
ZOE — Población inicial de la base de datos.
Ejecutar: python app/seed_data.py
Primero asegúrate de tener MySQL corriendo (XAMPP) y haber ejecutado schema.sql.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date, datetime
from app import create_app
from app.models import db, PeriodoAcademico, Usuario, Materia, Tarea, Cronograma, Recurso, Grupo, Mensaje


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # ===== PERÍODO =====
        p1 = PeriodoAcademico(
            nombre='Primer Período 2026',
            fecha_inicio=date(2026, 1, 26),
            fecha_fin=date(2026, 4, 10),
            activo=True
        )
        db.session.add(p1)
        db.session.commit()

        # ===== USUARIOS =====
        coordinador = Usuario(nombre='Carlos Gil', correo='coord@colegio.mx', rol='coordinador', periodo_id=p1.id)
        coordinador.set_password('admin123')
        db.session.add(coordinador)

        profesores = [
            ('Lic. Roberto Medina', 'prof.medina@colegio.mx'),
            ('Lic. María Reyes', 'prof.reyes@colegio.mx'),
            ('Lic. Laura Torres', 'prof.torres@colegio.mx'),
            ('Lic. Diana Gómez', 'prof.gomez@colegio.mx'),
            ('Coord. Carlos Pérez', 'prof.perez@colegio.mx'),
        ]
        prof_objs = []
        for nombre, correo in profesores:
            u = Usuario(nombre=nombre, correo=correo, rol='profesor', periodo_id=p1.id)
            u.set_password('prof123')
            db.session.add(u)
            prof_objs.append(u)

        estudiantes = [
            'Ana Martínez', 'Carlos Rodríguez', 'Sofía Ortega',
            'Luis Herrera', 'Valentina Ríos', 'Juan Morales'
        ]
        est_objs = []
        for nombre in estudiantes:
            correo = nombre.lower().replace(' ', '.') + '@colegio.mx'
            u = Usuario(nombre=nombre, correo=correo, rol='estudiante', periodo_id=p1.id)
            u.set_password('est123')
            db.session.add(u)
            est_objs.append(u)

        db.session.commit()

        # ===== MATERIAS =====
        materias_data = [
            ('Matemáticas', 'regular', 'Álgebra, geometría y estadística'),
            ('Inglés', 'regular', 'Comprensión lectora y expresión escrita'),
            ('Lengua y Literatura', 'regular', 'Análisis literario y producción textual'),
            ('Desarrollo de Lenguas', 'troncal', 'Portafolio de lectura y expresión oral'),
            ('HPP', 'troncal', 'Herramientas del Pensamiento Profesional'),
            ('Aprendizaje y Servicio', 'troncal', 'Proyectos de impacto social y servicio'),
            ('Proyecto de Reflexión', 'troncal', 'Investigación, análisis y reflexión crítica'),
        ]
        mat_objs = {}
        for nombre, tipo, desc in materias_data:
            m = Materia(nombre=nombre, tipo=tipo, descripcion=desc, periodo_id=p1.id)
            db.session.add(m)
            mat_objs[nombre] = m
        db.session.commit()

        # Asignar profesores a materias
        prof_map = {
            'Matemáticas': prof_objs[0],
            'Lengua y Literatura': prof_objs[1],
            'Inglés': prof_objs[2],
            'Desarrollo de Lenguas': prof_objs[3],
            'HPP': prof_objs[4],
            'Aprendizaje y Servicio': prof_objs[4],
            'Proyecto de Reflexión': prof_objs[0],
        }

        # ===== TAREAS =====
        tareas_data = [
            ('Proyecto de Reflexión — Borrador 2', date(2026, 6, 11), 'alta', 'Proyecto de Reflexión'),
            ('Análisis literario — Páramo', date(2026, 6, 13), 'media', 'Lengua y Literatura'),
            ('Ensayo argumentativo — Environment', date(2026, 6, 15), 'media', 'Inglés'),
            ('Informe de horas de servicio', date(2026, 6, 18), 'baja', 'Aprendizaje y Servicio'),
            ('Ensayo — Series y Sucesiones', date(2026, 6, 22), 'alta', 'Matemáticas'),
        ]
        for titulo, fecha, prioridad, materia_nombre in tareas_data:
            t = Tarea(
                titulo=titulo,
                fecha_limite=fecha,
                prioridad=prioridad,
                materia_id=mat_objs[materia_nombre].id,
                creado_por=prof_map[materia_nombre].id
            )
            db.session.add(t)

        # ===== CRONOGRAMA =====
        crono_data = [
            ('Proyecto de Reflexión — Borrador 2', date(2026, 6, 9), 'pendiente', 'Proyecto de Reflexión'),
            ('Análisis literario — Páramo', date(2026, 6, 11), 'pendiente', 'Lengua y Literatura'),
            ('Ensayo — Series y Sucesiones', date(2026, 6, 15), 'revisión', 'Matemáticas'),
            ('Portafolio de lectura', date(2026, 6, 18), 'revisión', 'Desarrollo de Lenguas'),
            ('Ensayo argumentativo — Environment', date(2026, 6, 22), 'completada', 'Inglés'),
            ('Informe de horas de servicio', date(2026, 6, 28), 'pendiente', 'Aprendizaje y Servicio'),
        ]
        for titulo, fecha, estado, materia_nombre in crono_data:
            c = Cronograma(
                titulo=titulo,
                fecha_evento=fecha,
                tipo=estado,
                materia_id=mat_objs[materia_nombre].id,
                creado_por=prof_map[materia_nombre].id
            )
            db.session.add(c)

        # ===== RECURSOS =====
        recursos_data = [
            ('Guía de laboratorio — Química', 'documento', 'Proyecto de Reflexión'),
            ('Presentación — Series y Sucesiones', 'presentacion', 'Matemáticas'),
            ('Guía de reflexión — HPP', 'enlace', 'HPP'),
            ('Video — Análisis literario Páramo', 'video', 'Lengua y Literatura'),
            ('Guía de lectura — Desarrollo de Lenguas', 'documento', 'Desarrollo de Lenguas'),
            ('Plantilla — Informe de Servicio', 'documento', 'Aprendizaje y Servicio'),
        ]
        for titulo, tipo, materia_nombre in recursos_data:
            r = Recurso(
                titulo=titulo,
                tipo=tipo,
                materia_id=mat_objs[materia_nombre].id,
                creado_por=prof_map[materia_nombre].id
            )
            db.session.add(r)

        # ===== GRUPOS (por materia) =====
        for nombre, tipo, desc in materias_data:
            g = Grupo(
                nombre=f'{nombre} — 11°',
                descripcion=f'Grupo de estudio de {nombre}',
                materia_id=mat_objs[nombre].id,
                creado_por=coordinador.id
            )
            db.session.add(g)

        # ===== MENSAJES =====
        m1 = Mensaje(
            remitente_id=prof_objs[4].id,
            destinatario_id=est_objs[0].id,
            asunto='Recordatorio evaluaciones IB',
            cuerpo='Buenos días. Recuerden que esta semana inician las evaluaciones IB.',
            leido=False
        )
        m2 = Mensaje(
            remitente_id=prof_objs[0].id,
            destinatario_id=est_objs[0].id,
            asunto='Revisión del ensayo',
            cuerpo='La revisión del ensayo de Matemáticas ya está disponible.',
            leido=False
        )
        db.session.add(m1)
        db.session.add(m2)

        db.session.commit()
        print('✅ Base de datos poblada exitosamente.')


if __name__ == '__main__':
    seed()