from model.log_usuario import Usuario

class Estudiante(Usuario):
    def __init__(self, id, nombre, correo, contrasena_hash):
        super().__init__(id, nombre, correo, contrasena_hash, rol="Estudiante")
        self.__materias = []
        self.__grupos = []

    def inscribirMateria(self, materia):
        if materia not in self.__materias:
            self.__materias.append(materia)

    def unirseGrupo(self, grupo):
        if grupo not in self.__grupos:
            self.__grupos.append(grupo)

    def get_materias(self):
        return list(self.__materias)

    def get_grupos(self):
        return list(self.__grupos)

    def entregarTarea(self, tarea):
        print(f"{self.get_nombre()} entregó la tarea: {tarea.get_titulo()}")

    def mostrarInfo(self):
        grupos = ", ".join([g.get_nombre() for g in self.__grupos]) or "Sin grupo"
        materias = ", ".join([m.get_nombre() for m in self.__materias]) or "Sin materias"
        print(f"[Estudiante] {self.get_id()} - {self.get_nombre()} | Grupos: {grupos} | Materias: {materias}")
