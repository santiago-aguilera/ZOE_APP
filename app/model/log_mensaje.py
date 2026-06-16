class Mensaje:
    def __init__(self, id, remitente, destinatario, asunto, cuerpo):
        self.__id = id
        self.__remitente = remitente
        self.__destinatario = destinatario
        self.__asunto = asunto
        self.__cuerpo = cuerpo
        self.__leido = False

    def enviarMensaje(self):
        print(f"Mensaje enviado de {self.__remitente.get_nombre()} a {self.__destinatario.get_nombre()}")

    def leerMensaje(self):
        self.__leido = True
        print(f"Mensaje leído: {self.__asunto}")

    def mostrarInfo(self):
        estado = "Leído" if self.__leido else "No leído"
        print(f"[Mensaje] {self.__id} - {self.__asunto}\n  De: {self.__remitente.get_nombre()}\n  Para: {self.__destinatario.get_nombre()}\n  Estado: {estado}")
