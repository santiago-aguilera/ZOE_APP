import os
from datetime import datetime

from model.log_estudiante import Estudiante
from model.log_profesor import Profesor
from model.log_coordinador import Coordinador
from model.log_periodo import PeriodoAcademico
from model.log_meteria import Materia
from model.log_grupo import Grupo
from model.log_tarea import Tarea
from model.log_entrega import Entrega
from model.log_mensaje import Mensaje
from model.log_Comunicado import Comunicado
from model.log_recurso import Recurso
from model.log_cronograma import Cronograma

usuarios = []
periodos = []
materias = []
grupos = []
tareas = []
entregas = []
mensajes = []
comunicados = []
recursos = []
eventos = []


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nPresione Enter para continuar...")


def validar_fecha(fecha_texto, campo):
    try:
        fecha = datetime.strptime(fecha_texto, "%Y-%m-%d").date()
        return fecha
    except ValueError:
        print(f"Fecha inválida para {campo}. Debe tener el formato YYYY-MM-DD.")
        return None


def menu():
    while True:
        clear_screen()
        print("--- SISTEMA ACADÉMICO ZOE ---")
        print("1. Crear Usuario")
        print("2. Crear Periodo Académico")
        print("3. Crear Materia")
        print("4. Crear Grupo")
        print("5. Asignar Profesor a Materia")
        print("6. Inscribir Estudiante a Grupo")
        print("7. Relacionar Grupo con Materia")
        print("8. Crear Tarea")
        print("9. Registrar Entrega")
        print("10. Enviar Mensaje")
        print("11. Publicar Comunicado")
        print("12. Subir Recurso")
        print("13. Crear Evento en Cronograma")
        print("14. Informes")
        print("15. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            crear_usuario()
        elif opcion == "2":
            crear_periodo()
        elif opcion == "3":
            crear_materia()
        elif opcion == "4":
            crear_grupo()
        elif opcion == "5":
            asignar_profesor_a_materia()
        elif opcion == "6":
            inscribir_estudiante_grupo()
        elif opcion == "7":
            relacionar_grupo_materia()
        elif opcion == "8":
            crear_tarea()
        elif opcion == "9":
            registrar_entrega()
        elif opcion == "10":
            enviar_mensaje()
        elif opcion == "11":
            publicar_comunicado()
        elif opcion == "12":
            subir_recurso()
        elif opcion == "13":
            crear_evento()
        elif opcion == "14":
            informes()
        elif opcion == "15":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción inválida")
        pause()


def crear_usuario():
    clear_screen()
    print("--- Crear Usuario ---")
    tipo = input("Tipo (E=Estudiante, P=Profesor, C=Coordinador): ")
    id = len(usuarios) + 1
    nombre = input("Nombre: ")
    correo = input("Correo: ")
    contrasena = input("Contraseña: ")

    if tipo.upper() == "E":
        u = Estudiante(id, nombre, correo, contrasena)
    elif tipo.upper() == "P":
        u = Profesor(id, nombre, correo, contrasena)
    elif tipo.upper() == "C":
        u = Coordinador(id, nombre, correo, contrasena)
    else:
        print("Tipo inválido")
        return

    usuarios.append(u)
    print(f"Usuario {nombre} creado")


def crear_periodo():
    clear_screen()
    print("--- Crear Periodo Académico ---")
    id = len(periodos) + 1
    nombre = input("Nombre del periodo: ")
    inicio = validar_fecha(input("Fecha inicio (YYYY-MM-DD): "), "fecha de inicio")
    if inicio is None:
        return
    fin = validar_fecha(input("Fecha fin (YYYY-MM-DD): "), "fecha fin")
    if fin is None:
        return

    p = PeriodoAcademico(id, nombre, inicio, fin)
    periodos.append(p)
    print("Periodo creado")


def crear_materia():
    clear_screen()
    print("--- Crear Materia ---")
    if not periodos:
        print("Debe crear primero un periodo académico")
        return

    print("Seleccione un periodo:")
    for i in range(len(periodos)):
        print(f"{i + 1}. {periodos[i].get_nombre()}")
    opcion = input("Ingrese un número de periodo: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(periodos):
        print("Opción inválida")
        return
    periodo = periodos[indice]

    id = len(materias) + 1
    nombre = input("Nombre de la materia: ")
    descripcion = input("Descripción: ")
    m = Materia(id, nombre, descripcion, periodo)
    materias.append(m)
    periodo.agregarMateria(m)
    print("Materia creada")


def crear_grupo():
    clear_screen()
    print("--- Crear Grupo ---")
    if not materias:
        print("Debe crear primero una materia")
        return

    print("Seleccione una materia:")
    for i in range(len(materias)):
        print(f"{i + 1}. {materias[i].get_nombre()}")
    opcion = input("Ingrese un número de materia: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(materias):
        print("Opción inválida")
        return
    materia = materias[indice]

    profesores = [u for u in usuarios if u.get_rol() == "Profesor"]
    if not profesores:
        print("No hay profesor disponible")
        return
    print("Seleccione un profesor:")
    for i in range(len(profesores)):
        print(f"{i + 1}. {profesores[i].get_nombre()}")
    opcion = input("Ingrese un número de profesor: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(profesores):
        print("Opción inválida")
        return
    profesor = profesores[indice]

    id = len(grupos) + 1
    nombre = input("Nombre del grupo: ")
    descripcion = input("Descripción: ")
    g = Grupo(id, nombre, descripcion, materia, profesor)
    grupos.append(g)
    materia.agregarGrupo(g)
    profesor.asignarMateria(materia)
    print("Grupo creado")


def asignar_profesor_a_materia():
    clear_screen()
    print("--- Asignar Profesor a Materia ---")
    profesores = [u for u in usuarios if u.get_rol() == "Profesor"]
    if not profesores:
        print("No hay profesores disponibles")
        return
    print("Seleccione un profesor:")
    for i in range(len(profesores)):
        print(f"{i + 1}. {profesores[i].get_nombre()}")
    opcion = input("Ingrese un número de profesor: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(profesores):
        print("Opción inválida")
        return
    profesor = profesores[indice]

    if not materias:
        print("No hay materias disponibles")
        return
    print("Seleccione una materia:")
    for i in range(len(materias)):
        print(f"{i + 1}. {materias[i].get_nombre()}")
    opcion = input("Ingrese un número de materia: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(materias):
        print("Opción inválida")
        return
    materia = materias[indice]

    profesor.asignarMateria(materia)
    materia.asignarProfesor(profesor)
    print(f"Profesor {profesor.get_nombre()} asignado a {materia.get_nombre()}")


def inscribir_estudiante_grupo():
    clear_screen()
    print("--- Inscribir Estudiante a Grupo ---")
    estudiantes = [u for u in usuarios if u.get_rol() == "Estudiante"]
    if not estudiantes:
        print("No hay estudiantes disponibles")
        return
    print("Seleccione un estudiante:")
    for i in range(len(estudiantes)):
        print(f"{i + 1}. {estudiantes[i].get_nombre()}")
    opcion = input("Ingrese un número de estudiante: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(estudiantes):
        print("Opción inválida")
        return
    estudiante = estudiantes[indice]

    if not grupos:
        print("No hay grupos disponibles")
        return
    print("Seleccione un grupo:")
    for i in range(len(grupos)):
        print(f"{i + 1}. {grupos[i].get_nombre()}")
    opcion = input("Ingrese un número de grupo: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(grupos):
        print("Opción inválida")
        return
    grupo = grupos[indice]

    estudiante.unirseGrupo(grupo)
    estudiante.inscribirMateria(grupo.get_materia())
    grupo.agregarEstudiante(estudiante)
    print(f"Estudiante {estudiante.get_nombre()} inscrito en {grupo.get_nombre()}")


def relacionar_grupo_materia():
    clear_screen()
    print("--- Relacionar Grupo con Materia ---")
    if not grupos:
        print("No hay grupos disponibles")
        return
    print("Seleccione un grupo:")
    for i in range(len(grupos)):
        print(f"{i + 1}. {grupos[i].get_nombre()}")
    opcion = input("Ingrese un número de grupo: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(grupos):
        print("Opción inválida")
        return
    grupo = grupos[indice]

    if not materias:
        print("No hay materias disponibles")
        return
    print("Seleccione una materia:")
    for i in range(len(materias)):
        print(f"{i + 1}. {materias[i].get_nombre()}")
    opcion = input("Ingrese un número de materia: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(materias):
        print("Opción inválida")
        return
    materia = materias[indice]

    grupo.cambiarMateria(materia)
    materia.agregarGrupo(grupo)
    print(f"Grupo {grupo.get_nombre()} relacionado con {materia.get_nombre()}")


def crear_tarea():
    clear_screen()
    print("--- Crear Tarea ---")
    if not materias:
        print("Debe crear primero una materia")
        return

    print("Seleccione una materia:")
    for i in range(len(materias)):
        print(f"{i + 1}. {materias[i].get_nombre()}")
    opcion = input("Ingrese un número de materia: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(materias):
        print("Opción inválida")
        return
    materia = materias[indice]

    profesores = [u for u in usuarios if u.get_rol() == "Profesor"]
    if not profesores:
        print("No hay profesor disponible")
        return
    print("Seleccione un profesor:")
    for i in range(len(profesores)):
        print(f"{i + 1}. {profesores[i].get_nombre()}")
    opcion = input("Ingrese un número de profesor: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(profesores):
        print("Opción inválida")
        return
    profesor = profesores[indice]

    id = len(tareas) + 1
    titulo = input("Título de la tarea: ")
    instrucciones = input("Instrucciones: ")
    fecha_limite = validar_fecha(input("Fecha límite (YYYY-MM-DD): "), "fecha límite")
    if fecha_limite is None:
        return

    t = Tarea(id, titulo, instrucciones, fecha_limite, materia, profesor)
    tareas.append(t)
    materia.agregarTarea(t)
    print("Tarea creada")


def registrar_entrega():
    clear_screen()
    print("--- Registrar Entrega ---")
    if not tareas:
        print("Debe crear primero una tarea")
        return

    print("Seleccione una tarea:")
    for i in range(len(tareas)):
        print(f"{i + 1}. {tareas[i].get_titulo()}")
    opcion = input("Ingrese un número de tarea: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(tareas):
        print("Opción inválida")
        return
    tarea = tareas[indice]

    estudiantes = [u for u in usuarios if u.get_rol() == "Estudiante"]
    if not estudiantes:
        print("No hay estudiantes disponibles")
        return
    print("Seleccione un estudiante:")
    for i in range(len(estudiantes)):
        print(f"{i + 1}. {estudiantes[i].get_nombre()}")
    opcion = input("Ingrese un número de estudiante: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(estudiantes):
        print("Opción inválida")
        return
    estudiante = estudiantes[indice]

    id = len(entregas) + 1
    archivo = input("Archivo entregado: ")
    fecha = validar_fecha(input("Fecha entrega (YYYY-MM-DD): "), "fecha de entrega")
    if fecha is None:
        return

    e = Entrega(id, tarea, estudiante, archivo, fecha)
    entregas.append(e)
    e.registrarEntrega()


def enviar_mensaje():
    clear_screen()
    print("--- Enviar Mensaje ---")
    if not usuarios:
        print("No hay usuarios disponibles")
        return
    print("Seleccione el remitente:")
    for i in range(len(usuarios)):
        print(f"{i + 1}. {usuarios[i].get_nombre()} ({usuarios[i].get_rol()})")
    opcion = input("Ingrese un número de remitente: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(usuarios):
        print("Opción inválida")
        return
    remitente = usuarios[indice]

    destinatarios = [u for u in usuarios if u != remitente]
    if not destinatarios:
        print("No hay destinatarios disponibles")
        return
    print("Seleccione el destinatario:")
    for i in range(len(destinatarios)):
        print(f"{i + 1}. {destinatarios[i].get_nombre()} ({destinatarios[i].get_rol()})")
    opcion = input("Ingrese un número de destinatario: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(destinatarios):
        print("Opción inválida")
        return
    destinatario = destinatarios[indice]

    id = len(mensajes) + 1
    asunto = input("Asunto: ")
    cuerpo = input("Cuerpo: ")
    m = Mensaje(id, remitente, destinatario, asunto, cuerpo)
    mensajes.append(m)
    m.enviarMensaje()


def publicar_comunicado():
    clear_screen()
    print("--- Publicar Comunicado ---")
    coordinador = next((u for u in usuarios if u.get_rol() == "Coordinador"), None)
    if coordinador is None:
        print("Debe haber un coordinador")
        return

    id = len(comunicados) + 1
    titulo = input("Título: ")
    contenido = input("Contenido: ")
    publicadoEn = validar_fecha(input("Fecha publicación (YYYY-MM-DD): "), "fecha de publicación")
    if publicadoEn is None:
        return

    c = Comunicado(id, titulo, contenido, coordinador, publicadoEn)
    comunicados.append(c)
    c.publicarComunicado()


def subir_recurso():
    clear_screen()
    print("--- Subir Recurso ---")
    if not materias:
        print("Debe crear primero una materia")
        return

    print("Seleccione una materia:")
    for i in range(len(materias)):
        print(f"{i + 1}. {materias[i].get_nombre()}")
    opcion = input("Ingrese un número de materia: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(materias):
        print("Opción inválida")
        return
    materia = materias[indice]

    profesores = [u for u in usuarios if u.get_rol() == "Profesor"]
    if not profesores:
        print("No hay profesor disponible")
        return
    print("Seleccione un profesor:")
    for i in range(len(profesores)):
        print(f"{i + 1}. {profesores[i].get_nombre()}")
    opcion = input("Ingrese un número de profesor: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(profesores):
        print("Opción inválida")
        return
    profesor = profesores[indice]

    id = len(recursos) + 1
    titulo = input("Título: ")
    descripcion = input("Descripción: ")
    url = input("URL archivo: ")
    tipo = input("Tipo: ")
    r = Recurso(id, titulo, descripcion, url, tipo, materia, profesor)
    recursos.append(r)
    materia.agregarRecurso(r)
    r.mostrarInfo()


def crear_evento():
    clear_screen()
    print("--- Crear Evento en Cronograma ---")
    if not materias:
        print("Debe crear primero una materia")
        return

    print("Seleccione una materia:")
    for i in range(len(materias)):
        print(f"{i + 1}. {materias[i].get_nombre()}")
    opcion = input("Ingrese un número de materia: ")
    if not opcion.isdigit():
        print("Opción inválida")
        return
    indice = int(opcion) - 1
    if indice < 0 or indice >= len(materias):
        print("Opción inválida")
        return
    materia = materias[indice]

    id = len(eventos) + 1
    titulo = input("Título: ")
    descripcion = input("Descripción: ")
    fecha = validar_fecha(input("Fecha evento (YYYY-MM-DD): "), "fecha del evento")
    if fecha is None:
        return

    ev = Cronograma(id, titulo, descripcion, fecha, materia)
    eventos.append(ev)
    materia.agregarEvento(ev)
    ev.mostrarInfo()


def informes():
    clear_screen()
    print("--- INFORMES DEL SISTEMA ---")

    print("\nUsuarios:")
    for usuario in usuarios:
        usuario.mostrarInfo()

    print("\nPeriodos Académicos:")
    for periodo in periodos:
        periodo.mostrarInfo()

    print("\nMaterias:")
    for materia in materias:
        materia.mostrarInfo()

    print("\nGrupos:")
    for grupo in grupos:
        grupo.mostrarInfo()

    print("\nTareas:")
    for tarea in tareas:
        tarea.mostrarInfo()

    print("\nEntregas:")
    for entrega in entregas:
        entrega.mostrarInfo()

    print("\nMensajes:")
    for mensaje in mensajes:
        mensaje.mostrarInfo()

    print("\nComunicados:")
    for comunicado in comunicados:
        comunicado.mostrarInfo()

    print("\nRecursos:")
    for recurso in recursos:
        recurso.mostrarInfo()

    print("\nEventos del Cronograma:")
    for evento in eventos:
        evento.mostrarInfo()




if __name__ == "__main__":
    menu()
