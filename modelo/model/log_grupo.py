class Grupo:
    def __init__(self, id, nombre, descripcion, materia, creadoPor):
        self.__id = id
        self.__nombre = nombre
        self.__descripcion = descripcion
        self.__materia = materia
        self.__creadoPor = creadoPor
        self.__estudiantes = []

    def get_id(self):
        return self.__id

    def get_nombre(self):
        return self.__nombre

    def get_materia(self):
        return self.__materia

    def get_profesor(self):
        return self.__creadoPor

    def agregarEstudiante(self, estudiante):
        if estudiante not in self.__estudiantes:
            self.__estudiantes.append(estudiante)

    def get_estudiantes(self):
        return list(self.__estudiantes)

    def cambiarMateria(self, materia):
        self.__materia = materia

    def mostrarInfo(self):
        estudiantes = ", ".join([e.get_nombre() for e in self.__estudiantes]) or "Sin estudiantes"
        print(f"[Grupo] {self.__id} - {self.__nombre}\n  Materia: {self.__materia.get_nombre()}\n  Profesor: {self.__creadoPor.get_nombre()}\n  Estudiantes: {estudiantes}")
