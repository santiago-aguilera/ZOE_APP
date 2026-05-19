class Recurso:
    def __init__(self, id, titulo, descripcion, urlArchivo, tipo, materia, creadoPor):
        self.__id = id
        self.__titulo = titulo
        self.__descripcion = descripcion
        self.__urlArchivo = urlArchivo
        self.__tipo = tipo
        self.__materia = materia
        self.__creadoPor = creadoPor

    def get_titulo(self):
        return self.__titulo

    def mostrarInfo(self):
        print(f"[Recurso] {self.__id} - {self.__titulo}\n  Materia: {self.__materia.get_nombre()}\n  Tipo: {self.__tipo}\n  Autor: {self.__creadoPor.get_nombre()}\n  URL: {self.__urlArchivo}")
