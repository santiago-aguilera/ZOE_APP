from model.log_usuario import Usuario

class Profesor(Usuario):
    def __init__(self, id, nombre, correo, contrasena_hash):
        super().__init__(id, nombre, correo, contrasena_hash, rol="Profesor")
        self.__materias = []

    def asignarMateria(self, materia):
        if materia not in self.__materias:
            self.__materias.append(materia)

    def get_materias(self):
        return list(self.__materias)

    def mostrarInfo(self):
        materias = ", ".join([m.get_nombre() for m in self.__materias]) or "Sin materias asignadas"
        print(f"[Profesor] {self.get_id()} - {self.get_nombre()} | Materias: {materias}")
