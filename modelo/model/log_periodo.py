from datetime import datetime

class PeriodoAcademico:
    def __init__(self, id, nombre, fecha_inicio, fecha_fin, activo=True):
        self.__id = id
        self.__nombre = nombre
        self.__fecha_inicio = self._validar_fecha(fecha_inicio)
        self.__fecha_fin = self._validar_fecha(fecha_fin)
        if self.__fecha_fin < self.__fecha_inicio:
            raise ValueError("La fecha fin debe ser posterior a la fecha de inicio.")
        self.__activo = activo
        self.__materias = []

    def _validar_fecha(self, fecha_texto):
        if isinstance(fecha_texto, datetime):
            return fecha_texto.date()
        if hasattr(fecha_texto, "strftime"):
            return fecha_texto
        try:
            return datetime.strptime(fecha_texto, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Fecha inválida. Use YYYY-MM-DD.")

    def get_id(self):
        return self.__id

    def get_nombre(self):
        return self.__nombre

    def get_fecha_inicio(self):
        return self.__fecha_inicio

    def get_fecha_fin(self):
        return self.__fecha_fin

    def agregarMateria(self, materia):
        if materia not in self.__materias:
            self.__materias.append(materia)

    def cerrarPeriodo(self):
        self.__activo = False
        print(f"Periodo {self.__nombre} cerrado")

    def mostrarInfo(self):
        estado = "Activo" if self.__activo else "Cerrado"
        inicio = self.__fecha_inicio.strftime("%Y-%m-%d")
        fin = self.__fecha_fin.strftime("%Y-%m-%d")
        materias = len(self.__materias)
        print(f"[Periodo] {self.__id} - {self.__nombre} ({estado})\n  Inicio: {inicio} | Fin: {fin} | Materias: {materias}")
