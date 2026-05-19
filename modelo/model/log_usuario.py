class Usuario:
    def __init__(self, id, nombre, correo, contrasena_hash, rol):
        self.__id = id
        self.__nombre = nombre
        self.__correo = correo
        self.__contrasena_hash = contrasena_hash
        self.__rol = rol
        self.__sesion_activa = False

    def get_id(self):
        return self.__id

    def get_nombre(self):
        return self.__nombre

    def set_nombre(self, nombre):
        self.__nombre = nombre

    def get_correo(self):
        return self.__correo

    def set_correo(self, correo):
        self.__correo = correo

    def get_rol(self):
        return self.__rol

    def iniciarSesion(self, correo, contrasena_hash):
        if self.__correo == correo and self.__contrasena_hash == contrasena_hash:
            self.__sesion_activa = True
            print(f"Sesión iniciada para {self.__nombre} ({self.__rol})")
        else:
            print("Credenciales incorrectas")

    def cerrarSesion(self):
        if self.__sesion_activa:
            self.__sesion_activa = False
            print(f"Sesión cerrada para {self.__nombre}")
        else:
            print("No hay sesión activa para cerrar")

    def mostrarInfo(self):
        print(f"[{self.__rol}] {self.__id} - {self.__nombre} | {self.__correo}")
