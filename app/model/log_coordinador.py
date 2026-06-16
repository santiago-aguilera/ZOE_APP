from model.log_usuario import Usuario

class Coordinador(Usuario):
    def __init__(self, id, nombre, correo, contrasena_hash):
        super().__init__(id, nombre, correo, contrasena_hash, rol="Coordinador")

    def crearMateria(self, materia):
        print(f"{self.get_nombre()} creó la materia {materia.get_nombre()}")

    def publicarComunicado(self, comunicado):
        print(f"{self.get_nombre()} publicó el comunicado '{comunicado.get_titulo()}'")

    def mostrarInfo(self):
        print(f"[Coordinador] {self.get_id()} - {self.get_nombre()}")
