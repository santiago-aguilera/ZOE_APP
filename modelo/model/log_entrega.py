from datetime import datetime

class Entrega:
    def __init__(self, id, tarea, estudiante, archivo_url, fecha_entrega):
        self.__id = id
        self.__tarea = tarea
        self.__estudiante = estudiante
        self.__archivo_url = archivo_url
        self.__fecha_entrega = self._validar_fecha(fecha_entrega)
        self.__estado = "Pendiente"
        self.__calificacion = None

    def _validar_fecha(self, fecha_texto):
        if isinstance(fecha_texto, datetime):
            return fecha_texto.date()
        if hasattr(fecha_texto, "strftime"):
            return fecha_texto
        try:
            return datetime.strptime(fecha_texto, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Fecha inválida para la entrega. Use YYYY-MM-DD.")

    def registrarEntrega(self):
        self.__estado = "Entregado"
        self.__tarea.registrarEntrega(self)
        print(f"{self.__estudiante.get_nombre()} entregó '{self.__tarea.get_titulo()}'")

    def calificarEntrega(self, calificacion):
        self.__calificacion = calificacion
        print(f"Entrega {self.__id} calificada con {calificacion}")

    def mostrarInfo(self):
        fecha_texto = self.__fecha_entrega.strftime("%Y-%m-%d")
        calif = self.__calificacion if self.__calificacion is not None else "No calificada"
        print(f"[Entrega] {self.__id} - Tarea: {self.__tarea.get_titulo()}\n  Estudiante: {self.__estudiante.get_nombre()}\n  Fecha: {fecha_texto}\n  Estado: {self.__estado} | Calificación: {calif}")
