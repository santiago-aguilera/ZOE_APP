from datetime import datetime

class Tarea:
    def __init__(self, id, titulo, instrucciones, fecha_limite, materia, creadoPor):
        self.__id = id
        self.__titulo = titulo
        self.__instrucciones = instrucciones
        self.__fecha_limite = self._validar_fecha(fecha_limite)
        self.__materia = materia
        self.__creadoPor = creadoPor
        self.__entregas = []

    def _validar_fecha(self, fecha_texto):
        if isinstance(fecha_texto, datetime):
            return fecha_texto.date()
        if hasattr(fecha_texto, "strftime"):
            return fecha_texto
        try:
            return datetime.strptime(fecha_texto, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Fecha inválida para la fecha límite. Use YYYY-MM-DD.")

    def get_titulo(self):
        return self.__titulo

    def get_fecha_limite(self):
        return self.__fecha_limite

    def get_materia(self):
        return self.__materia

    def get_creador(self):
        return self.__creadoPor

    def registrarEntrega(self, entrega):
        self.__entregas.append(entrega)

    def get_entregas(self):
        return list(self.__entregas)

    def mostrarInfo(self):
        fecha_texto = self.__fecha_limite.strftime("%Y-%m-%d")
        print(f"[Tarea] {self.__id} - {self.__titulo}\n  Materia: {self.__materia.get_nombre()}\n  Fecha límite: {fecha_texto}\n  Creada por: {self.__creadoPor.get_nombre()}")
