class Materia:
    def __init__(self, id, nombre, descripcion, periodo):
        self.__id = id
        self.__nombre = nombre
        self.__descripcion = descripcion
        self.__periodo = periodo
        self.__profesores = []
        self.__grupos = []
        self.__tareas = []
        self.__recursos = []
        self.__cronograma = []

    def get_id(self):
        return self.__id

    def get_nombre(self):
        return self.__nombre

    def get_periodo(self):
        return self.__periodo

    def asignarProfesor(self, profesor):
        if profesor not in self.__profesores:
            self.__profesores.append(profesor)

    def agregarGrupo(self, grupo):
        if grupo not in self.__grupos:
            self.__grupos.append(grupo)

    def agregarTarea(self, tarea):
        if tarea not in self.__tareas:
            self.__tareas.append(tarea)

    def agregarRecurso(self, recurso):
        if recurso not in self.__recursos:
            self.__recursos.append(recurso)

    def agregarEvento(self, evento):
        if evento not in self.__cronograma:
            self.__cronograma.append(evento)

    def get_grupos(self):
        return list(self.__grupos)

    def get_tareas(self):
        return list(self.__tareas)

    def get_profesores(self):
        return list(self.__profesores)

    def mostrarInfo(self):
        profesores = ", ".join([p.get_nombre() for p in self.__profesores]) or "Sin profesor asignado"
        grupos = len(self.__grupos)
        tareas = len(self.__tareas)
        recursos = len(self.__recursos)
        print(f"[Materia] {self.__id} - {self.__nombre}\n  Descripción: {self.__descripcion}\n  Periodo: {self.__periodo.get_nombre()}\n  Profesor(es): {profesores}\n  Grupos: {grupos} | Tareas: {tareas} | Recursos: {recursos}")
