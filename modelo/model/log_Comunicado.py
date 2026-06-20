class Comunicado:
    def __init__(self, id, titulo, contenido, creadoPor, publicadoEn, activo=True):
        self.__id = id
        self.__titulo = titulo
        self.__contenido = contenido
        self.__creadoPor = creadoPor
        self.__publicadoEn = publicadoEn
        self.__activo = activo

    def get_titulo(self):
        return self.__titulo

    def publicarComunicado(self):
        print(f"Comunicado '{self.__titulo}' publicado por {self.__creadoPor.get_nombre()}")

    def mostrarInfo(self):
        estado = "Activo" if self.__activo else "Inactivo"
        fecha = self.__publicadoEn.strftime("%Y-%m-%d") if hasattr(self.__publicadoEn, "strftime") else str(self.__publicadoEn)
        print(f"[Comunicado] {self.__id} - {self.__titulo}\n  Fecha: {fecha}\n  Autor: {self.__creadoPor.get_nombre()}\n  Estado: {estado}\n  Contenido: {self.__contenido}")
