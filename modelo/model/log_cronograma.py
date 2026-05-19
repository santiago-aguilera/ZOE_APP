from datetime import datetime

class Cronograma:
    def __init__(self, id, titulo, descripcion, fechaEvento, materia):
        self.__id = id
        self.__titulo = titulo
        self.__descripcion = descripcion
        self.__fechaEvento = self._validar_fecha(fechaEvento)
        self.__materia = materia

    def _validar_fecha(self, fecha_texto):
        if isinstance(fecha_texto, datetime):
            return fecha_texto.date()
        if hasattr(fecha_texto, "strftime"):
            return fecha_texto
        try:
            return datetime.strptime(fecha_texto, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Fecha inválida para el evento. Use YYYY-MM-DD.")

    def get_titulo(self):
        return self.__titulo

    def mostrarInfo(self):
        fecha = self.__fechaEvento.strftime("%Y-%m-%d")
        print(f"[Evento] {self.__id} - {self.__titulo}\n  Materia: {self.__materia.get_nombre()}\n  Fecha: {fecha}\n  Descripción: {self.__descripcion}")
