"""
Modelos POO para ZOE.
Clases que representan las tablas de la base de datos MySQL.
Cada clase tiene atributos equivalentes a las columnas y métodos CRUD.
"""

from app.config_db import db
from datetime import datetime
from typing import List, Dict, Optional, Any
from app.decorators import modulo_requerido


# Escala de valoración IB/MEN: cualitativa, no numérica. El orden importa:
# se usa para calcular promedios ponderados y comparar contra el mínimo
# de aprobación (Bajo < Básico < Alto < Superior).
ESCALA_VALORATIVA = ('Bajo', 'Básico', 'Alto', 'Superior')
VALOR_ORDINAL = {nombre: i + 1 for i, nombre in enumerate(ESCALA_VALORATIVA)}
ORDINAL_A_VALOR = {i + 1: nombre for i, nombre in enumerate(ESCALA_VALORATIVA)}


# Escala de valoración IB/MEN: cualitativa, no numérica. El orden importa:
# se usa para calcular promedios ponderados y comparar contra el mínimo
# de aprobación (Bajo < Básico < Alto < Superior).
ESCALA_VALORATIVA = ('Bajo', 'Básico', 'Alto', 'Superior')
VALOR_ORDINAL = {nombre: i + 1 for i, nombre in enumerate(ESCALA_VALORATIVA)}
ORDINAL_A_VALOR = {i + 1: nombre for i, nombre in enumerate(ESCALA_VALORATIVA)}

# Estados del proceso de Matrícula BI (característica transversal del
# estudiante, no un concepto aparte). Todo estudiante nuevo arranca en
# NO_MATRICULADO.
# NOTA TÉCNICA: por ahora TODOS los estudiantes nuevos entran como
# NO_MATRICULADO por defecto. Más adelante se podría implementar un flujo
# de admisión/matrícula inicial distinto (ej: que ciertos programas o
# convenios ingresen ya en otro estado); mientras eso no exista, este es
# el único punto de entrada.
ESTADOS_MATRICULA = (
    'NO_MATRICULADO', 'EN_PROCESO', 'PENDIENTE', 'MATRICULADO',
    'ACTIVO', 'RETIRADO', 'FINALIZADO', 'CANCELADO'
)
ESTADO_MATRICULA_DEFECTO = 'NO_MATRICULADO'
ETIQUETAS_ESTADO_MATRICULA = {
    'NO_MATRICULADO': 'No matriculado', 'EN_PROCESO': 'En proceso', 'PENDIENTE': 'Pendiente',
    'MATRICULADO': 'Matriculado', 'ACTIVO': 'Activo', 'RETIRADO': 'Retirado',
    'FINALIZADO': 'Finalizado', 'CANCELADO': 'Cancelado'
}


class Usuario:
    """Modelo de Usuario - Representa la tabla 'usuario'."""
    
    def __init__(self, id=None, nombre=None, correo=None, contrasena_hash=None, 
                 rol=None, cohorte_id=None, curso_id=None,
                 estado_matricula=ESTADO_MATRICULA_DEFECTO, activo=True):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.contrasena_hash = contrasena_hash
        self.rol = rol
        self.cohorte_id = cohorte_id
        self.curso_id = curso_id
        self.estado_matricula = estado_matricula or ESTADO_MATRICULA_DEFECTO
        self.activo = activo
    
    def guardar(self) -> int:
        """Crea un nuevo usuario en la BD. Los estudiantes siempre arrancan
        en NO_MATRICULADO (ver nota técnica junto a ESTADOS_MATRICULA)."""
        consulta = """
            INSERT INTO usuario (nombre, correo, contrasena_hash, rol, cohorte_id, curso_id, estado_matricula, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        parametros = (
            self.nombre, self.correo, self.contrasena_hash, self.rol,
            self.cohorte_id, self.curso_id,
            self.estado_matricula if self.rol == 'estudiante' else None,
            self.activo
        )
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id
    
    def actualizar(self) -> bool:
        """Actualiza el usuario en la BD (no toca la contraseña)."""
        consulta = """
            UPDATE usuario 
            SET nombre=%s, correo=%s, rol=%s, cohorte_id=%s, curso_id=%s, estado_matricula=%s, activo=%s
            WHERE id=%s
        """
        parametros = (
            self.nombre, self.correo, self.rol, self.cohorte_id, self.curso_id,
            self.estado_matricula if self.rol == 'estudiante' else None,
            self.activo, self.id
        )
        filas_afectadas = db.ejecutar_actualizacion(consulta, parametros)
        return filas_afectadas > 0

    def cambiar_contrasena(self, nueva_hash: str) -> bool:
        """Actualiza la contraseña (hash) del usuario en la BD."""
        if not self.id:
            return False
        consulta = "UPDATE usuario SET contrasena_hash=%s WHERE id=%s"
        filas = db.ejecutar_actualizacion(consulta, (nueva_hash, self.id))
        if filas > 0:
            self.contrasena_hash = nueva_hash
            return True
        return False

    def cambiar_estado_matricula(self, nuevo_estado: str, registrado_por: int = None, observacion: str = None) -> bool:
        """Cambia el estado ACTUAL de matrícula BI de un estudiante.
        usuario.estado_matricula es la ÚNICA fuente de verdad: no existe
        historial ni tabla paralela. Los parámetros registrado_por/
        observacion se aceptan por compatibilidad de firma pero no se
        persisten (decisión de diseño explícita: sin historial)."""
        if nuevo_estado not in ESTADOS_MATRICULA:
            raise ValueError(f"Estado de matrícula inválido: {nuevo_estado}")
        consulta = "UPDATE usuario SET estado_matricula=%s WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (nuevo_estado, self.id))
        return filas_afectadas > 0

    @classmethod
    def obtener_todos(cls, cohorte_id: Optional[int] = None,
                      curso_id: Optional[int] = None,
                      estado_matricula: Optional[str] = None,
                      rol: Optional[str] = None) -> List['Usuario']:
        """Obtiene usuarios, combinando los filtros que se pasen: cohorte,
        curso, estado de matrícula BI y/o rol. Todos son opcionales."""
        condiciones, parametros = [], []
        if cohorte_id:
            condiciones.append("cohorte_id=%s")
            parametros.append(cohorte_id)
        if curso_id:
            condiciones.append("curso_id=%s")
            parametros.append(curso_id)
        if estado_matricula:
            condiciones.append("estado_matricula=%s")
            parametros.append(estado_matricula)
        if rol:
            condiciones.append("rol=%s")
            parametros.append(rol)
        consulta = "SELECT * FROM usuario"
        if condiciones:
            consulta += " WHERE " + " AND ".join(condiciones)
        resultados = db.ejecutar_consulta(consulta, tuple(parametros))
        return [cls._desde_diccionario(row) for row in resultados]

    @classmethod
    def obtener_por_correo(cls, correo: str):
        """Obtiene un usuario por su correo electrónico."""
        correo = (correo or '').strip()
        if not correo:
            return None
        consulta = "SELECT * FROM usuario WHERE LOWER(correo)=LOWER(%s)"
        resultados = db.ejecutar_consulta(consulta, (correo,))
        if resultados:
            return cls._desde_diccionario(resultados[0])
        return None

    @classmethod
    def obtener_materias(cls, usuario_id: int):
        """Devuelve la lista de materias (id/nombre) a las que está inscrito el
        estudiante según su curso asignado. Retorna lista vacía si no corresponde.
        """
        consulta = """
            SELECT DISTINCT m.id, m.nombre
            FROM usuario u
            JOIN curso_materia cm ON cm.curso_id = u.curso_id
            JOIN materia m ON cm.materia_id = m.id
            WHERE u.id = %s AND u.rol = 'estudiante'
            ORDER BY m.nombre
        """
        return db.ejecutar_consulta(consulta, (usuario_id,))

    @classmethod
    def contar_tareas_estudiante(cls, usuario_id: int) -> int:
        """Cuenta las tareas disponibles para un estudiante según su curso."""
        consulta = """
            SELECT COUNT(DISTINCT t.id) as cnt
            FROM tarea t
            JOIN curso_materia cm ON t.curso_materia_id = cm.id
            JOIN usuario u ON u.curso_id = cm.curso_id
            WHERE u.id = %s
        """
        resultado = db.ejecutar_consulta(consulta, (usuario_id,))
        return resultado[0]['cnt'] if resultado else 0

    @classmethod
    def obtener_estadisticas_matricula(cls, cohorte_id: Optional[int] = None) -> Dict[str, int]:
        """Cuenta estudiantes por estado de matrícula BI, opcionalmente
        filtrado por cohorte. Siempre trae los 8 estados, aunque estén en 0."""
        condicion = "AND cohorte_id = %s" if cohorte_id else ""
        parametros = (cohorte_id,) if cohorte_id else ()
        consulta = f"""
            SELECT estado_matricula, COUNT(*) as total FROM usuario
            WHERE rol = 'estudiante' {condicion}
            GROUP BY estado_matricula
        """
        resultados = db.ejecutar_consulta(consulta, parametros)
        conteos = {estado: 0 for estado in ESTADOS_MATRICULA}
        total = 0
        for row in resultados:
            estado = row.get('estado_matricula') or 'NO_MATRICULADO'
            conteos[estado] = row['total']
            total += row['total']
        conteos['TOTAL'] = total
        return conteos

    @classmethod
    def candidatos_matricula(cls, cohorte_id: int) -> List[Dict[str, Any]]:
        """Estudiantes de once (grado 11) de la cohorte que todavía NO
        avanzaron a MATRICULADO/ACTIVO/FINALIZADO: son los candidatos que
        el coordinador puede escoger para avanzar su matrícula BI a mitad
        del segundo año. Lista vacía si no hay ninguno."""
        if not cohorte_id:
            return []
        consulta = """
            SELECT u.id, u.nombre, u.estado_matricula
            FROM usuario u
            JOIN curso c ON c.id = u.curso_id
            WHERE u.cohorte_id = %s AND c.grado = 11 AND u.rol = 'estudiante'
              AND (u.estado_matricula IS NULL OR u.estado_matricula NOT IN ('MATRICULADO', 'ACTIVO', 'FINALIZADO'))
            ORDER BY u.nombre
        """
        return db.ejecutar_consulta(consulta, (cohorte_id,))

    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Usuario':
        """Crea una instancia de Usuario desde un diccionario."""
        return cls(
            id=datos.get('id'),
            nombre=datos.get('nombre'),
            correo=datos.get('correo'),
            contrasena_hash=datos.get('contrasena_hash'),
            rol=datos.get('rol'),
            cohorte_id=datos.get('cohorte_id'),
            curso_id=datos.get('curso_id'),
            estado_matricula=datos.get('estado_matricula') or ESTADO_MATRICULA_DEFECTO,
            activo=datos.get('activo', True)
        )
    
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la instancia a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'correo': self.correo,
            'rol': self.rol,
            'cohorte_id': self.cohorte_id,
            'activo': self.activo
        }
    
    def __repr__(self):
        return f"<Usuario {self.nombre} ({self.rol})>"

    @classmethod
    def obtener_por_id(cls, id: int) -> Optional['Usuario']:
        """Obtiene un usuario por su ID."""
        consulta = "SELECT * FROM usuario WHERE id=%s"
        resultados = db.ejecutar_consulta(consulta, (id,))
        if resultados:
            return cls._desde_diccionario(resultados[0])
        return None

    @classmethod
    def buscar(cls, texto: str, limite: int = 5) -> List['Usuario']:
        """Busca usuarios por nombre o correo. Lista vacía si no hay coincidencias."""
        consulta = "SELECT * FROM usuario WHERE nombre LIKE %s OR correo LIKE %s ORDER BY nombre LIMIT %s"
        patron = f"%{texto}%"
        resultados = db.ejecutar_consulta(consulta, (patron, patron, limite))
        return [cls._desde_diccionario(row) for row in resultados]

    def eliminar(self) -> bool:
        """Elimina el usuario de la BD. Las FK protegen la integridad:
        si el usuario (típicamente un profesor) creó contenido académico
        (tareas, recursos, valoraciones, archivo histórico, etc.), la BD
        rechaza el borrado con RESTRICT en vez de eliminarlo todo en
        cascada silenciosamente. Las relaciones puramente de membresía
        (entrega, estudiante_grupo, estudiante_especialidad) sí están en
        CASCADE a nivel de BD."""
        consulta = "DELETE FROM usuario WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (self.id,))
        return filas_afectadas > 0


class Materia:
    """Modelo de Materia - Representa la tabla 'materia'.

    Las materias son un catálogo REUTILIZABLE: no pertenecen a una cohorte
    ni a un curso. Se reutilizan entre cohortes y se conectan a un curso
    puntual (con su profesor) a través de la Asignación Académica
    (ver Curso.asignar_materia / tabla curso_materia): MATERIA -> ASIGNACIÓN
    ACADÉMICA -> CURSO + PROFESOR.
    """
    
    def __init__(self, id=None, nombre=None, descripcion=None, 
                 creado_en=None, valoracion_minima_aprobatoria='Básico'):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.creado_en = creado_en
        self.valoracion_minima_aprobatoria = valoracion_minima_aprobatoria
    
    def guardar(self) -> int:
        """Crea una nueva materia en la BD (catálogo global, reutilizable)."""
        consulta = """
            INSERT INTO materia (nombre, descripcion)
            VALUES (%s, %s)
        """
        parametros = (self.nombre, self.descripcion)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id
    
    def actualizar(self) -> bool:
        """Actualiza la materia en la BD."""
        consulta = """
            UPDATE materia 
            SET nombre=%s, descripcion=%s
            WHERE id=%s
        """
        parametros = (self.nombre, self.descripcion, self.id)
        filas_afectadas = db.ejecutar_actualizacion(consulta, parametros)
        return filas_afectadas > 0
    
    def eliminar(self) -> bool:
        """Elimina la materia de la BD."""
        consulta = "DELETE FROM materia WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (self.id,))
        return filas_afectadas > 0

    def actualizar_valoracion_minima(self, valoracion_minima: str) -> bool:
        """Actualiza solo la valoración mínima de aprobación de la materia
        (una de: Bajo, Básico, Alto, Superior)."""
        consulta = "UPDATE materia SET valoracion_minima_aprobatoria=%s WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (valoracion_minima, self.id))
        return filas_afectadas > 0
    
    @classmethod
    def progreso_estudiante(cls, estudiante_id: int) -> List[Dict[str, Any]]:
        """
        Calcula el % de tareas entregadas por un estudiante, por materia,
        pero SOLO dentro de la asignación académica de SU curso (nunca
        mezcla tareas de otro curso aunque comparta materia).
        Devuelve lista vacía si no hay materias con tareas todavía.
        """
        if not estudiante_id:
            return []
        consulta = """
            SELECT m.id as materia_id, m.nombre as materia_nombre,
                   COUNT(DISTINCT t.id) as total_tareas,
                   COUNT(DISTINCT e.id) as entregadas
            FROM usuario est
            JOIN curso_materia cm ON cm.curso_id = est.curso_id
            JOIN materia m ON cm.materia_id = m.id
            JOIN tarea t ON t.curso_materia_id = cm.id
            LEFT JOIN entrega e
                ON e.tarea_id = t.id
                AND e.estudiante_id = %s
                AND e.estado IN ('entregada', 'calificada')
            WHERE est.id = %s
            GROUP BY m.id, m.nombre
            ORDER BY m.nombre
        """
        resultados = db.ejecutar_consulta(consulta, (estudiante_id, estudiante_id))
        progreso = []
        for row in resultados:
            total = row['total_tareas'] or 0
            entregadas = row['entregadas'] or 0
            porcentaje = round((entregadas / total) * 100) if total > 0 else 0
            progreso.append({
                'materia': row['materia_nombre'],
                'porcentaje': porcentaje
            })
        return progreso

    # ---------------------------------------------------------------
    # Ya no hay asignación directa profesor-materia ni estudiante-materia:
    # ambas se gestionan por medio del curso (ver Curso.asignar_materia,
    # Curso.inscribir_estudiante en la sección de Curso).
    # ---------------------------------------------------------------

    @classmethod
    def obtener_ids_por_profesor(cls, profesor_id: int) -> List[int]:
        """
        IDs de las materias que dicta un profesor: primero busca en los
        cursos donde está asignado a dictarla (curso_materia); si no hay
        ninguna asignada todavía, usa como respaldo las materias donde el
        profesor ya creó al menos una tarea. Lista vacía si no tiene ninguna.
        """
        consulta_asignadas = "SELECT DISTINCT materia_id FROM curso_materia WHERE profesor_id=%s"
        asignadas = db.ejecutar_consulta(consulta_asignadas, (profesor_id,))
        if asignadas:
            return [row['materia_id'] for row in asignadas]

        consulta_respaldo = """
            SELECT DISTINCT cm.materia_id FROM tarea t
            JOIN curso_materia cm ON t.curso_materia_id = cm.id
            WHERE t.creado_por=%s
        """
        respaldo = db.ejecutar_consulta(consulta_respaldo, (profesor_id,))
        return [row['materia_id'] for row in respaldo]

    @classmethod
    def obtener_por_id(cls, id: int) -> Optional['Materia']:
        """Obtiene una materia por su ID."""
        consulta = "SELECT * FROM materia WHERE id=%s"
        resultados = db.ejecutar_consulta(consulta, (id,))
        if resultados:
            return cls._desde_diccionario(resultados[0])
        return None
    
    @classmethod
    def progreso_general(cls, materia_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Calcula el % de avance de cada materia: tareas que ya tienen
        al menos una entrega, sobre el total de tareas de esa materia.
        Si materia_ids se especifica, filtra solo esas materias (para el rol profesor).
        Si una materia no tiene tareas, su progreso es 0 (no división por cero).
        Lista vacía si no hay materias cargadas.
        """
        condicion = ""
        parametros: tuple = ()
        if materia_ids:
            placeholders = ','.join(['%s'] * len(materia_ids))
            condicion = f"WHERE m.id IN ({placeholders})"
            parametros = tuple(materia_ids)

        consulta = f"""
            SELECT m.id, m.nombre,
                   COUNT(DISTINCT t.id) as total_tareas,
                   COUNT(DISTINCT CASE WHEN ent.id IS NOT NULL THEN t.id END) as tareas_con_entrega
            FROM materia m
            LEFT JOIN curso_materia cm ON cm.materia_id = m.id
            LEFT JOIN tarea t ON t.curso_materia_id = cm.id
            LEFT JOIN entrega ent ON ent.tarea_id = t.id
            {condicion}
            GROUP BY m.id, m.nombre
            ORDER BY m.nombre
        """
        resultados = db.ejecutar_consulta(consulta, parametros)
        progreso = []
        for row in resultados:
            total = row.get('total_tareas') or 0
            hechas = row.get('tareas_con_entrega') or 0
            porcentaje = round((hechas / total) * 100) if total > 0 else 0
            progreso.append({
                'materia_id': row.get('id'),
                'nombre': row.get('nombre'),
                'porcentaje': porcentaje
            })
        return progreso

    @classmethod
    def buscar(cls, texto: str, limite: int = 5) -> List['Materia']:
        """Busca materias por nombre. Lista vacía si no hay coincidencias."""
        consulta = "SELECT * FROM materia WHERE nombre LIKE %s ORDER BY nombre LIMIT %s"
        resultados = db.ejecutar_consulta(consulta, (f"%{texto}%", limite))
        return [cls._desde_diccionario(row) for row in resultados]

    @classmethod
    def obtener_todas(cls) -> List['Materia']:
        """Obtiene todas las materias (catálogo global, reutilizable), con
        el conteo real de cursos donde se dicta y de profesores distintos."""
        consulta = """
            SELECT m.*, COUNT(DISTINCT cm.curso_id) as total_cursos,
                   COUNT(DISTINCT cm.profesor_id) as total_profesores
            FROM materia m
            LEFT JOIN curso_materia cm ON cm.materia_id = m.id
            GROUP BY m.id
            ORDER BY m.nombre
        """
        resultados = db.ejecutar_consulta(consulta)
        materias = []
        for row in resultados:
            materia = cls._desde_diccionario(row)
            materia.total_cursos = row.get('total_cursos') or 0
            materia.total_profesores = row.get('total_profesores') or 0
            materias.append(materia)
        return materias

    @classmethod
    def obtener_asignaciones(cls, materia_id: int) -> List[Dict[str, Any]]:
        """Cursos donde se dicta esta materia, con el profesor asignado a
        cada uno (MATERIA -> ASIGNACIÓN ACADÉMICA -> CURSO + PROFESOR)."""
        consulta = """
            SELECT cm.id as curso_materia_id, c.id as curso_id, c.codigo as curso_codigo,
                   c.grado, c.seccion, u.id as profesor_id, u.nombre as profesor_nombre
            FROM curso_materia cm
            JOIN curso c ON cm.curso_id = c.id
            LEFT JOIN usuario u ON cm.profesor_id = u.id
            WHERE cm.materia_id = %s
            ORDER BY c.grado, c.seccion
        """
        return db.ejecutar_consulta(consulta, (materia_id,))
    
    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Materia':
        """Crea una instancia de Materia desde un diccionario."""
        return cls(
            id=datos.get('id'),
            nombre=datos.get('nombre'),
            descripcion=datos.get('descripcion'),
            creado_en=datos.get('creado_en'),
            valoracion_minima_aprobatoria=datos.get('valoracion_minima_aprobatoria', 'Básico')
        )
    
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la instancia a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion
        }
    
    def __repr__(self):
        return f"<Materia {self.nombre}>"


class Tarea:
    """Modelo de Tarea - Representa la tabla 'tarea'.

    Una tarea pertenece a una ASIGNACIÓN ACADÉMICA puntual
    (curso_materia_id = MATERIA + CURSO + PROFESOR), no solo a una materia.
    Así, "Matemáticas en 1001 con el Profesor A" nunca se mezcla con
    "Matemáticas en 1002 con el Profesor B": cada una tiene sus propias
    tareas, y solo llegan a los estudiantes de ESE curso específico.
    """

    def __init__(self, id=None, titulo=None, instrucciones=None, fecha_limite=None,
                 curso_materia_id=None, creado_por=None, creado_en=None):
        self.id = id
        self.titulo = titulo
        self.instrucciones = instrucciones
        self.fecha_limite = fecha_limite
        self.curso_materia_id = curso_materia_id
        self.creado_por = creado_por
        self.creado_en = creado_en

    def guardar(self) -> int:
        """Crea una nueva tarea en la BD, ligada a una asignación académica
        (curso_materia_id) puntual."""
        consulta = """
            INSERT INTO tarea (titulo, instrucciones, fecha_limite, curso_materia_id, creado_por)
            VALUES (%s, %s, %s, %s, %s)
        """
        parametros = (self.titulo, self.instrucciones, self.fecha_limite,
                     self.curso_materia_id, self.creado_por)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id
    
    def actualizar(self) -> bool:
        """Actualiza la tarea en la BD."""
        consulta = """
            UPDATE tarea 
            SET titulo=%s, instrucciones=%s, fecha_limite=%s, curso_materia_id=%s
            WHERE id=%s
        """
        parametros = (self.titulo, self.instrucciones, self.fecha_limite,
                     self.curso_materia_id, self.id)
        filas_afectadas = db.ejecutar_actualizacion(consulta, parametros)
        return filas_afectadas > 0
    
    def eliminar(self) -> bool:
        """Elimina la tarea de la BD (sus entregas se eliminan en cascada)."""
        consulta = "DELETE FROM tarea WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (self.id,))
        return filas_afectadas > 0

    # Columnas que siempre se traen para no repetir el JOIN en cada método.
    _SELECT_CONTEXTO = """
        SELECT t.*, m.id as materia_id, m.nombre as materia_nombre,
               c.id as curso_id, c.codigo as curso_codigo,
               cm.profesor_id as profesor_id, u.nombre as creador_nombre
        FROM tarea t
        JOIN curso_materia cm ON t.curso_materia_id = cm.id
        JOIN materia m ON cm.materia_id = m.id
        JOIN curso c ON cm.curso_id = c.id
        LEFT JOIN usuario u ON t.creado_por = u.id
    """

    @classmethod
    def obtener_por_id(cls, id: int) -> Optional['Tarea']:
        """Obtiene una tarea por su ID, con su contexto académico completo
        (materia, curso, profesor)."""
        consulta = cls._SELECT_CONTEXTO + " WHERE t.id=%s"
        resultados = db.ejecutar_consulta(consulta, (id,))
        return cls._desde_diccionario_contexto(resultados[0]) if resultados else None

    @classmethod
    def obtener_proximas(cls, limite: int = 5) -> List['Tarea']:
        """Obtiene las próximas tareas por fecha límite. Lista vacía si no hay ninguna."""
        consulta = cls._SELECT_CONTEXTO + " WHERE t.fecha_limite >= CURDATE() ORDER BY t.fecha_limite ASC LIMIT %s"
        resultados = db.ejecutar_consulta(consulta, (limite,))
        return [cls._desde_diccionario_contexto(row) for row in resultados]

    @classmethod
    def buscar(cls, texto: str, limite: int = 5) -> List['Tarea']:
        """Busca tareas por título. Lista vacía si no hay coincidencias."""
        consulta = cls._SELECT_CONTEXTO + " WHERE t.titulo LIKE %s ORDER BY t.titulo LIMIT %s"
        resultados = db.ejecutar_consulta(consulta, (f"%{texto}%", limite))
        return [cls._desde_diccionario_contexto(row) for row in resultados]

    @classmethod
    def obtener_todas(cls, curso_materia_id: Optional[int] = None,
                       profesor_id: Optional[int] = None,
                       curso_id: Optional[int] = None) -> List['Tarea']:
        """Todas las tareas, opcionalmente filtradas por asignación académica
        puntual, profesor (sus asignaciones) o curso. Combinables entre sí."""
        condiciones, parametros = [], []
        if curso_materia_id:
            condiciones.append("t.curso_materia_id = %s")
            parametros.append(curso_materia_id)
        if profesor_id:
            condiciones.append("cm.profesor_id = %s")
            parametros.append(profesor_id)
        if curso_id:
            condiciones.append("cm.curso_id = %s")
            parametros.append(curso_id)
        consulta = cls._SELECT_CONTEXTO
        if condiciones:
            consulta += " WHERE " + " AND ".join(condiciones)
        consulta += " ORDER BY t.fecha_limite DESC"
        resultados = db.ejecutar_consulta(consulta, tuple(parametros))
        return [cls._desde_diccionario_contexto(row) for row in resultados]

    @classmethod
    def obtener_para_estudiante(cls, estudiante_id: int) -> List['Tarea']:
        """Tareas que le corresponden a un estudiante: solo las de la
        asignación académica de SU curso (nunca las de otro curso, aunque
        sea la misma materia). Lista vacía si no tiene curso asignado."""
        consulta = cls._SELECT_CONTEXTO + """
            JOIN usuario est ON est.curso_id = cm.curso_id AND est.rol = 'estudiante'
            WHERE est.id = %s
            ORDER BY t.fecha_limite ASC
        """
        resultados = db.ejecutar_consulta(consulta, (estudiante_id,))
        return [cls._desde_diccionario_contexto(row) for row in resultados]

    @classmethod
    def obtener_destinatarios(cls, tarea_id: int) -> List[Dict[str, Any]]:
        """Estudiantes destinatarios reales de una tarea: los del curso de
        su asignación académica específica, ni uno más."""
        consulta = """
            SELECT u.id, u.nombre, u.correo, u.estado_matricula
            FROM tarea t
            JOIN curso_materia cm ON t.curso_materia_id = cm.id
            JOIN usuario u ON u.curso_id = cm.curso_id AND u.rol = 'estudiante'
            WHERE t.id = %s
            ORDER BY u.nombre
        """
        return db.ejecutar_consulta(consulta, (tarea_id,))

    @classmethod
    def _desde_diccionario_contexto(cls, datos: Dict[str, Any]) -> 'Tarea':
        """Crea una Tarea desde un diccionario que ya incluye el contexto
        académico (materia_nombre, curso_codigo, profesor_id, etc.)."""
        tarea = cls(
            id=datos.get('id'),
            titulo=datos.get('titulo'),
            instrucciones=datos.get('instrucciones'),
            fecha_limite=datos.get('fecha_limite'),
            curso_materia_id=datos.get('curso_materia_id'),
            creado_por=datos.get('creado_por'),
            creado_en=datos.get('creado_en')
        )
        tarea.materia_id = datos.get('materia_id')
        tarea.materia_nombre = datos.get('materia_nombre')
        tarea.curso_id = datos.get('curso_id')
        tarea.curso_codigo = datos.get('curso_codigo')
        tarea.profesor_id = datos.get('profesor_id')
        tarea.creador_nombre = datos.get('creador_nombre')
        return tarea

    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Tarea':
        """Crea una instancia de Tarea desde un diccionario plano (sin contexto)."""
        return cls(
            id=datos.get('id'),
            titulo=datos.get('titulo'),
            instrucciones=datos.get('instrucciones'),
            fecha_limite=datos.get('fecha_limite'),
            curso_materia_id=datos.get('curso_materia_id'),
            creado_por=datos.get('creado_por'),
            creado_en=datos.get('creado_en')
        )
    
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la instancia a diccionario."""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'instrucciones': self.instrucciones,
            'fecha_limite': self.fecha_limite,
            'curso_materia_id': self.curso_materia_id,
            'materia_nombre': getattr(self, 'materia_nombre', None),
            'curso_codigo': getattr(self, 'curso_codigo', None),
            'creador': getattr(self, 'creador_nombre', None)
        }
    
    def __repr__(self):
        return f"<Tarea {self.titulo}>"


class Grupo:
    """Modelo de Grupo - Representa la tabla 'grupo'.

    Un grupo de estudio es una agrupación de estudiantes, INDEPENDIENTE
    del curso (curso ≠ grupo). Puede tener contexto opcional (materia,
    curso, cohorte) para organizarse mejor, pero ninguno de esos campos
    lo convierte en un curso ni es obligatorio: puede ser un grupo
    totalmente institucional sin ningún contexto."""
    
    def __init__(self, id=None, nombre=None, descripcion=None,
                 materia_id=None, curso_id=None, cohorte_id=None,
                 activo=True, creado_por=None, creado_en=None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.materia_id = materia_id
        self.curso_id = curso_id
        self.cohorte_id = cohorte_id
        self.activo = activo
        self.creado_por = creado_por
        self.creado_en = creado_en
    
    def guardar(self) -> int:
        """Crea un nuevo grupo en la BD."""
        consulta = """
            INSERT INTO grupo (nombre, descripcion, materia_id, curso_id, cohorte_id, creado_por)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        parametros = (self.nombre, self.descripcion, self.materia_id,
                     self.curso_id, self.cohorte_id, self.creado_por)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id
    
    def actualizar(self) -> bool:
        """Actualiza el grupo en la BD."""
        consulta = """
            UPDATE grupo 
            SET nombre=%s, descripcion=%s, materia_id=%s, curso_id=%s, cohorte_id=%s, activo=%s
            WHERE id=%s
        """
        parametros = (self.nombre, self.descripcion, self.materia_id,
                     self.curso_id, self.cohorte_id, self.activo, self.id)
        filas_afectadas = db.ejecutar_actualizacion(consulta, parametros)
        return filas_afectadas > 0
    
    def eliminar(self) -> bool:
        """Elimina el grupo de la BD (sus relaciones estudiante_grupo se
        eliminan en cascada; los estudiantes NO se eliminan)."""
        consulta = "DELETE FROM grupo WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (self.id,))
        return filas_afectadas > 0
    
    @classmethod
    def obtener_por_id(cls, id: int) -> Optional['Grupo']:
        """Obtiene un grupo por su ID."""
        consulta = """
            SELECT g.*, m.nombre as materia_nombre, c.codigo as curso_codigo, co.nombre as cohorte_nombre
            FROM grupo g
            LEFT JOIN materia m ON g.materia_id = m.id
            LEFT JOIN curso c ON g.curso_id = c.id
            LEFT JOIN cohorte co ON g.cohorte_id = co.id
            WHERE g.id=%s
        """
        resultados = db.ejecutar_consulta(consulta, (id,))
        if resultados:
            grupo = cls._desde_diccionario(resultados[0])
            grupo.materia_nombre = resultados[0].get('materia_nombre')
            grupo.curso_codigo = resultados[0].get('curso_codigo')
            grupo.cohorte_nombre = resultados[0].get('cohorte_nombre')
            return grupo
        return None
    
    @classmethod
    def buscar(cls, texto: str, limite: int = 5) -> List['Grupo']:
        """Busca grupos por nombre. Lista vacía si no hay coincidencias."""
        consulta = """
            SELECT g.*, m.nombre as materia_nombre
            FROM grupo g
            LEFT JOIN materia m ON g.materia_id = m.id
            WHERE g.nombre LIKE %s
            ORDER BY g.nombre LIMIT %s
        """
        resultados = db.ejecutar_consulta(consulta, (f"%{texto}%", limite))
        grupos = []
        for row in resultados:
            grupo = cls._desde_diccionario(row)
            grupo.materia_nombre = row.get('materia_nombre')
            grupos.append(grupo)
        return grupos

    @classmethod
    def obtener_todos(cls, curso_id: Optional[int] = None, cohorte_id: Optional[int] = None) -> List['Grupo']:
        """Obtiene todos los grupos, con conteo real de estudiantes
        inscritos. curso_id/cohorte_id filtran opcionalmente por el
        contexto del grupo (no obligatorio, un grupo puede no tener)."""
        condiciones, parametros = [], []
        if curso_id:
            condiciones.append("g.curso_id = %s")
            parametros.append(curso_id)
        if cohorte_id:
            condiciones.append("g.cohorte_id = %s")
            parametros.append(cohorte_id)
        condicion_sql = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""
        consulta = f"""
            SELECT g.*, m.nombre as materia_nombre, c.codigo as curso_codigo,
                   co.nombre as cohorte_nombre, u.nombre as profesor_nombre,
                   COUNT(DISTINCT eg.usuario_id) as total_estudiantes
            FROM grupo g
            LEFT JOIN materia m ON g.materia_id = m.id
            LEFT JOIN curso c ON g.curso_id = c.id
            LEFT JOIN cohorte co ON g.cohorte_id = co.id
            LEFT JOIN usuario u ON g.creado_por = u.id
            LEFT JOIN estudiante_grupo eg ON eg.grupo_id = g.id
            {condicion_sql}
            GROUP BY g.id
            ORDER BY g.nombre
        """
        resultados = db.ejecutar_consulta(consulta, tuple(parametros))
        grupos = []
        for row in resultados:
            grupo = cls._desde_diccionario(row)
            grupo.materia_nombre = row.get('materia_nombre')
            grupo.curso_codigo = row.get('curso_codigo')
            grupo.cohorte_nombre = row.get('cohorte_nombre')
            grupo.profesor_nombre = row.get('profesor_nombre')
            grupo.total_estudiantes = row.get('total_estudiantes') or 0
            grupos.append(grupo)
        return grupos

    @classmethod
    def obtener_asignaciones(cls) -> List[Dict[str, Any]]:
        """Lista todas las inscripciones estudiante-grupo, con nombres. Vacía si no hay ninguna."""
        consulta = """
            SELECT eg.id, u.id as usuario_id, u.nombre as estudiante_nombre,
                   g.id as grupo_id, g.nombre as grupo_nombre
            FROM estudiante_grupo eg
            JOIN usuario u ON eg.usuario_id = u.id
            JOIN grupo g ON eg.grupo_id = g.id
            ORDER BY g.nombre, u.nombre
        """
        return db.ejecutar_consulta(consulta)

    @classmethod
    def inscribir_estudiante(cls, grupo_id: int, estudiante_id: int) -> bool:
        """Inscribe a un estudiante en un grupo. No falla si ya estaba inscrito."""
        consulta = "INSERT IGNORE INTO estudiante_grupo (usuario_id, grupo_id) VALUES (%s, %s)"
        db.ejecutar_insercion(consulta, (estudiante_id, grupo_id))
        return True

    @classmethod
    def quitar_estudiante(cls, asignacion_id: int) -> bool:
        """Elimina una inscripción estudiante-grupo por su id."""
        consulta = "DELETE FROM estudiante_grupo WHERE id=%s"
        db.ejecutar_actualizacion(consulta, (asignacion_id,))
        return True
    
    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Grupo':
        """Crea una instancia de Grupo desde un diccionario."""
        return cls(
            id=datos.get('id'),
            nombre=datos.get('nombre'),
            descripcion=datos.get('descripcion'),
            materia_id=datos.get('materia_id'),
            curso_id=datos.get('curso_id'),
            cohorte_id=datos.get('cohorte_id'),
            activo=datos.get('activo', True),
            creado_por=datos.get('creado_por'),
            creado_en=datos.get('creado_en')
        )
    
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la instancia a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'materia_id': self.materia_id,
            'profesor': self.profesor_nombre
        }
    
    def __repr__(self):
        return f"<Grupo {self.nombre}>"


class Comunicado:
    """Modelo de Comunicado - Representa la tabla 'comunicado'."""
    
    def __init__(self, id=None, titulo=None, contenido=None,
                 creado_por=None, publicado_en=None, activo=True):
        self.id = id
        self.titulo = titulo
        self.contenido = contenido
        self.creado_por = creado_por
        self.publicado_en = publicado_en
        self.activo = activo
    
    def guardar(self) -> int:
        """Crea un nuevo comunicado en la BD."""
        consulta = """
            INSERT INTO comunicado (titulo, contenido, creado_por, activo)
            VALUES (%s, %s, %s, %s)
        """
        parametros = (self.titulo, self.contenido, self.creado_por, self.activo)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id
    
    def actualizar(self) -> bool:
        """Actualiza el comunicado en la BD."""
        consulta = """
            UPDATE comunicado 
            SET titulo=%s, contenido=%s, activo=%s
            WHERE id=%s
        """
        parametros = (self.titulo, self.contenido, self.activo, self.id)
        filas_afectadas = db.ejecutar_actualizacion(consulta, parametros)
        return filas_afectadas > 0
    
    def eliminar(self) -> bool:
        """Elimina el comunicado de la BD."""
        consulta = "DELETE FROM comunicado WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (self.id,))
        return filas_afectadas > 0
    
    @classmethod
    def obtener_por_id(cls, id: int) -> Optional['Comunicado']:
        """Obtiene un comunicado por su ID."""
        consulta = "SELECT * FROM comunicado WHERE id=%s"
        resultados = db.ejecutar_consulta(consulta, (id,))
        if resultados:
            return cls._desde_diccionario(resultados[0])
        return None
    
    @classmethod
    def obtener_activos(cls) -> List['Comunicado']:
        """Obtiene todos los comunicados activos."""
        consulta = """
            SELECT c.*, u.nombre as autor_nombre
            FROM comunicado c
            LEFT JOIN usuario u ON c.creado_por = u.id
            WHERE c.activo=1
            ORDER BY c.publicado_en DESC
        """
        resultados = db.ejecutar_consulta(consulta)
        comunicados = []
        for row in resultados:
            com = cls._desde_diccionario(row)
            com.autor_nombre = row.get('autor_nombre')
            comunicados.append(com)
        return comunicados
    
    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Comunicado':
        """Crea una instancia de Comunicado desde un diccionario."""
        return cls(
            id=datos.get('id'),
            titulo=datos.get('titulo'),
            contenido=datos.get('contenido'),
            creado_por=datos.get('creado_por'),
            publicado_en=datos.get('publicado_en'),
            activo=datos.get('activo', True)
        )
    
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la instancia a diccionario."""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'contenido': self.contenido,
            'autor': self.autor_nombre,
            'fecha': self.publicado_en.strftime('%Y-%m-%d') if self.publicado_en else ''
        }
    
    def __repr__(self):
        return f"<Comunicado {self.titulo}>"


class Cohorte:
    """Modelo de Cohorte Académico - Representa la tabla 'cohorte'."""
    
    def __init__(self, id=None, nombre=None, fecha_inicio=None, 
                 fecha_fin=None, activo=True):
        self.id = id
        self.nombre = nombre
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.activo = activo
    
    def guardar(self) -> int:
        """Crea una nueva cohorte en la BD y le genera automáticamente sus
        4 especialidades. Los cursos NO se generan aquí: son un catálogo
        global fijo (1001-1004/1101-1104) independiente de la cohorte,
        creado una sola vez (ver Curso.crear_catalogo_por_defecto)."""
        consulta = """
            INSERT INTO cohorte (nombre, fecha_inicio, fecha_fin, activo)
            VALUES (%s, %s, %s, %s)
        """
        parametros = (self.nombre, self.fecha_inicio, self.fecha_fin, self.activo)
        self.id = db.ejecutar_insercion(consulta, parametros)
        if self.id:
            Especialidad.crear_paquete_por_defecto(self.id)
        return self.id
    
    @classmethod
    def obtener_todos(cls) -> List['Cohorte']:
        """Obtiene todos los cohortes."""
        consulta = "SELECT * FROM cohorte"
        resultados = db.ejecutar_consulta(consulta)
        return [cls._desde_diccionario(row) for row in resultados]

    @classmethod
    def obtener_por_id(cls, id: int) -> Optional['Cohorte']:
        """Obtiene una cohorte por su ID."""
        consulta = "SELECT * FROM cohorte WHERE id=%s"
        resultados = db.ejecutar_consulta(consulta, (id,))
        return cls._desde_diccionario(resultados[0]) if resultados else None

    def actualizar(self) -> bool:
        """Actualiza los datos de la cohorte en la BD."""
        consulta = """
            UPDATE cohorte
            SET nombre=%s, fecha_inicio=%s, fecha_fin=%s, activo=%s
            WHERE id=%s
        """
        parametros = (self.nombre, self.fecha_inicio, self.fecha_fin, self.activo, self.id)
        filas_afectadas = db.ejecutar_actualizacion(consulta, parametros)
        return filas_afectadas > 0

    def eliminar(self) -> bool:
        """Elimina la cohorte de la BD."""
        consulta = "DELETE FROM cohorte WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (self.id,))
        return filas_afectadas > 0
    
    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Cohorte':
        """Crea una instancia desde un diccionario."""
        return cls(
            id=datos.get('id'),
            nombre=datos.get('nombre'),
            fecha_inicio=datos.get('fecha_inicio'),
            fecha_fin=datos.get('fecha_fin'),
            activo=datos.get('activo', True)
        )
    
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la instancia a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre
        }
    
    def __repr__(self):
        return f"<Cohorte {self.nombre}>"


# Grados y secciones que forman el paquete fijo de cursos de cada cohorte:
# décimo (1001-1004) el primer año, once (1101-1104) el segundo año.
GRADOS_CURSO = (10, 11)
SECCIONES_CURSO = (1, 2, 3, 4)


class Curso:
    """Modelo de Curso - Representa la tabla 'curso'.

    Un curso (1001-1004 décimo, 1101-1104 once) es un catálogo FIJO e
    INDEPENDIENTE de las cohortes: el mismo curso "1001" se reutiliza cohorte
    tras cohorte, no se vuelve a crear cada vez. La cohorte es solo un filtro
    de contexto para ver qué estudiantes de qué cohorte están en un curso
    puntual en un momento dado (usuario.curso_id + usuario.cohorte_id).
    No reemplaza a 'grupo': grupo sigue existiendo para equipos de trabajo,
    independiente del curso.
    """

    def __init__(self, id=None, codigo=None, nombre=None, grado=None, seccion=None,
                 activo=True, creado_en=None):
        self.id = id
        self.codigo = codigo
        self.nombre = nombre
        self.grado = grado
        self.seccion = seccion
        self.activo = activo
        self.creado_en = creado_en

    def guardar(self) -> int:
        """Crea un nuevo curso en la BD (catálogo global, sin cohorte)."""
        consulta = """
            INSERT INTO curso (codigo, nombre, grado, seccion, activo)
            VALUES (%s, %s, %s, %s, %s)
        """
        parametros = (self.codigo, self.nombre, self.grado, self.seccion, self.activo)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id

    def actualizar(self) -> bool:
        """Actualiza nombre/grado/sección/estado de un curso."""
        consulta = "UPDATE curso SET codigo=%s, nombre=%s, grado=%s, seccion=%s, activo=%s WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(
            consulta, (self.codigo, self.nombre, self.grado, self.seccion, self.activo, self.id)
        )
        return filas_afectadas > 0

    def eliminar(self) -> bool:
        """Elimina el curso de la BD (falla si tiene estudiantes/materias
        relacionadas, por las FK; se recomienda desactivar en su lugar)."""
        consulta = "DELETE FROM curso WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (self.id,))
        return filas_afectadas > 0

    @classmethod
    def crear_catalogo_por_defecto(cls) -> None:
        """Genera una única vez el catálogo fijo de 8 cursos: 1001-1004
        (décimo) y 1101-1104 (once). No falla si ya existían. A diferencia
        del diseño anterior, esto NO se dispara por cada cohorte: los cursos
        son globales y se reutilizan cohorte tras cohorte."""
        consulta = "INSERT IGNORE INTO curso (codigo, nombre, grado, seccion) VALUES (%s, %s, %s, %s)"
        for grado in GRADOS_CURSO:
            base = 1000 if grado == 10 else 1100
            for seccion in SECCIONES_CURSO:
                codigo = base + seccion
                db.ejecutar_insercion(consulta, (codigo, str(codigo), grado, seccion))

    @classmethod
    def obtener_por_id(cls, id: int) -> Optional['Curso']:
        """Obtiene un curso por su ID."""
        consulta = "SELECT * FROM curso WHERE id=%s"
        resultados = db.ejecutar_consulta(consulta, (id,))
        return cls._desde_diccionario(resultados[0]) if resultados else None

    @classmethod
    def obtener_todos(cls, cohorte_id: Optional[int] = None) -> List['Curso']:
        """Obtiene todos los cursos del catálogo. `cohorte_id` es solo un
        FILTRO de contexto: si se pasa, el conteo de estudiantes se limita a
        esa cohorte (el curso en sí no pertenece a ninguna)."""
        condicion = "AND u.cohorte_id = %s" if cohorte_id else ""
        parametros = (cohorte_id,) if cohorte_id else ()
        consulta = f"""
            SELECT c.*, COUNT(DISTINCT u.id) as total_estudiantes
            FROM curso c
            LEFT JOIN usuario u ON u.curso_id = c.id AND u.rol = 'estudiante' {condicion}
            GROUP BY c.id
            ORDER BY c.grado, c.seccion
        """
        resultados = db.ejecutar_consulta(consulta, parametros)
        cursos = []
        for row in resultados:
            curso = cls._desde_diccionario(row)
            curso.total_estudiantes = row.get('total_estudiantes') or 0
            cursos.append(curso)
        return cursos

    @classmethod
    def buscar(cls, texto: str, limite: int = 5) -> List['Curso']:
        """Busca cursos por código o nombre. Lista vacía si no hay coincidencias."""
        consulta = """
            SELECT * FROM curso
            WHERE codigo LIKE %s OR nombre LIKE %s
            ORDER BY grado, seccion LIMIT %s
        """
        patron = f"%{texto}%"
        resultados = db.ejecutar_consulta(consulta, (patron, patron, limite))
        return [cls._desde_diccionario(row) for row in resultados]

    # -- Estudiantes del curso (usuario.curso_id directo) -----------------------

    @classmethod
    def inscribir_estudiante(cls, curso_id: int, estudiante_id: int) -> bool:
        """Asigna un estudiante a un curso (reemplaza el curso anterior si tenía)."""
        consulta = "UPDATE usuario SET curso_id=%s WHERE id=%s AND rol='estudiante'"
        db.ejecutar_actualizacion(consulta, (curso_id, estudiante_id))
        return True

    @classmethod
    def quitar_estudiante(cls, estudiante_id: int) -> bool:
        """Quita a un estudiante de su curso actual."""
        consulta = "UPDATE usuario SET curso_id=NULL WHERE id=%s"
        db.ejecutar_actualizacion(consulta, (estudiante_id,))
        return True

    @classmethod
    def obtener_estudiantes(cls, curso_id: int, cohorte_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Estudiantes de un curso. `cohorte_id` filtra opcionalmente por
        cohorte (útil porque el mismo curso se reutiliza entre cohortes)."""
        condicion = "AND u.cohorte_id = %s" if cohorte_id else ""
        parametros = (curso_id, cohorte_id) if cohorte_id else (curso_id,)
        consulta = f"""
            SELECT u.id as usuario_id, u.nombre, u.correo, u.estado_matricula, u.cohorte_id,
                   co.nombre as cohorte_nombre
            FROM usuario u
            LEFT JOIN cohorte co ON u.cohorte_id = co.id
            WHERE u.curso_id = %s AND u.rol = 'estudiante' {condicion}
            ORDER BY u.nombre
        """
        return db.ejecutar_consulta(consulta, parametros)

    # -- Paquete de materias del curso (con su profesor asignado) --------------

    @classmethod
    def asignar_materia(cls, curso_id: int, materia_id: int, profesor_id: Optional[int] = None) -> int:
        """Agrega una materia al paquete del curso, opcionalmente con el
        profesor que la dictará en ese curso."""
        consulta = """
            INSERT INTO curso_materia (curso_id, materia_id, profesor_id)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE profesor_id = VALUES(profesor_id)
        """
        return db.ejecutar_insercion(consulta, (curso_id, materia_id, profesor_id))

    @classmethod
    def quitar_materia(cls, curso_materia_id: int) -> bool:
        """Quita una materia del paquete del curso."""
        consulta = "DELETE FROM curso_materia WHERE id=%s"
        db.ejecutar_actualizacion(consulta, (curso_materia_id,))
        return True

    @classmethod
    def asignar_profesor_materia(cls, curso_materia_id: int, profesor_id: Optional[int]) -> bool:
        """Cambia el profesor que dicta una materia dentro de un curso."""
        consulta = "UPDATE curso_materia SET profesor_id=%s WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (profesor_id, curso_materia_id))
        return filas_afectadas > 0

    @classmethod
    def obtener_materias(cls, curso_id: int) -> List[Dict[str, Any]]:
        """Lista el paquete de materias de un curso, con el profesor
        asignado a dictar cada una (si ya se asignó)."""
        consulta = """
            SELECT cm.id as curso_materia_id, m.id as materia_id, m.nombre as materia_nombre,
                   u.id as profesor_id, u.nombre as profesor_nombre
            FROM curso_materia cm
            JOIN materia m ON cm.materia_id = m.id
            LEFT JOIN usuario u ON cm.profesor_id = u.id
            WHERE cm.curso_id = %s
            ORDER BY m.nombre
        """
        return db.ejecutar_consulta(consulta, (curso_id,))

    @classmethod
    def obtener_profesores(cls, curso_id: int) -> List[Dict[str, Any]]:
        """Profesores distintos que dictan alguna materia en este curso."""
        consulta = """
            SELECT DISTINCT u.id, u.nombre, u.correo
            FROM curso_materia cm
            JOIN usuario u ON cm.profesor_id = u.id
            WHERE cm.curso_id = %s
            ORDER BY u.nombre
        """
        return db.ejecutar_consulta(consulta, (curso_id,))

    @classmethod
    def obtener_grupos(cls, curso_id: int) -> List[Dict[str, Any]]:
        """Grupos de estudio cuyos integrantes pertenecen a este curso
        (un grupo es independiente del curso, pero puede coincidir en la práctica)."""
        consulta = """
            SELECT DISTINCT g.id, g.nombre, g.descripcion,
                   COUNT(DISTINCT eg.usuario_id) as total_estudiantes
            FROM grupo g
            JOIN estudiante_grupo eg ON eg.grupo_id = g.id
            JOIN usuario u ON u.id = eg.usuario_id
            WHERE u.curso_id = %s
            GROUP BY g.id
            ORDER BY g.nombre
        """
        return db.ejecutar_consulta(consulta, (curso_id,))

    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Curso':
        """Crea una instancia de Curso desde un diccionario."""
        return cls(
            id=datos.get('id'),
            codigo=datos.get('codigo'),
            nombre=datos.get('nombre'),
            grado=datos.get('grado'),
            seccion=datos.get('seccion'),
            activo=datos.get('activo', True),
            creado_en=datos.get('creado_en')
        )

    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la instancia a diccionario."""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'grado': self.grado,
            'seccion': self.seccion,
            'activo': self.activo
        }

    def __repr__(self):
        return f"<Curso {self.codigo}>"


# Catálogo fijo de especialidades. Cada cohorte nueva genera automáticamente
# una fila por cada una (igual que con los cursos).
NOMBRES_ESPECIALIDAD = (
    "Programación de Software",
    "Diseño Multimedia",
    "Ambiental",
    "Administración de Empresas",
)


class Especialidad:
    """Modelo de Especialidad - Representa la tabla 'especialidad'.

    Funciona igual que un Curso (agrupa estudiantes dentro de una cohorte),
    pero por especialidad en vez de por grado/sección, y con un solo
    profesor asignado (no un paquete de materias).
    """

    def __init__(self, id=None, nombre=None, cohorte_id=None,
                 profesor_id=None, activo=True, creado_en=None):
        self.id = id
        self.nombre = nombre
        self.cohorte_id = cohorte_id
        self.profesor_id = profesor_id
        self.activo = activo
        self.creado_en = creado_en

    def guardar(self) -> int:
        """Crea una nueva especialidad en la BD."""
        consulta = """
            INSERT INTO especialidad (nombre, cohorte_id, profesor_id, activo)
            VALUES (%s, %s, %s, %s)
        """
        parametros = (self.nombre, self.cohorte_id, self.profesor_id, self.activo)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id

    def eliminar(self) -> bool:
        """Elimina la especialidad de la BD."""
        consulta = "DELETE FROM especialidad WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (self.id,))
        return filas_afectadas > 0

    @classmethod
    def crear_paquete_por_defecto(cls, cohorte_id: int) -> None:
        """Genera automáticamente las 4 especialidades de una cohorte nueva."""
        consulta = """
            INSERT IGNORE INTO especialidad (nombre, cohorte_id)
            VALUES (%s, %s)
        """
        for nombre in NOMBRES_ESPECIALIDAD:
            db.ejecutar_insercion(consulta, (nombre, cohorte_id))

    @classmethod
    def obtener_por_id(cls, id: int) -> Optional['Especialidad']:
        """Obtiene una especialidad por su ID."""
        consulta = """
            SELECT e.*, u.nombre as profesor_nombre
            FROM especialidad e
            LEFT JOIN usuario u ON e.profesor_id = u.id
            WHERE e.id=%s
        """
        resultados = db.ejecutar_consulta(consulta, (id,))
        if not resultados:
            return None
        especialidad = cls._desde_diccionario(resultados[0])
        especialidad.profesor_nombre = resultados[0].get('profesor_nombre')
        return especialidad

    @classmethod
    def obtener_todas(cls, cohorte_id: Optional[int] = None) -> List['Especialidad']:
        """Lista las especialidades (opcionalmente filtradas por cohorte),
        con el profesor asignado y el conteo de estudiantes inscritos."""
        condicion = "WHERE e.cohorte_id = %s" if cohorte_id else ""
        parametros = (cohorte_id,) if cohorte_id else ()
        consulta = f"""
            SELECT e.*, co.nombre as cohorte_nombre, u.nombre as profesor_nombre,
                   COUNT(DISTINCT ee.usuario_id) as total_estudiantes
            FROM especialidad e
            LEFT JOIN cohorte co ON e.cohorte_id = co.id
            LEFT JOIN usuario u ON e.profesor_id = u.id
            LEFT JOIN estudiante_especialidad ee ON ee.especialidad_id = e.id
            {condicion}
            GROUP BY e.id
            ORDER BY e.nombre
        """
        resultados = db.ejecutar_consulta(consulta, parametros)
        especialidades = []
        for row in resultados:
            especialidad = cls._desde_diccionario(row)
            especialidad.cohorte_nombre = row.get('cohorte_nombre')
            especialidad.profesor_nombre = row.get('profesor_nombre')
            especialidad.total_estudiantes = row.get('total_estudiantes') or 0
            especialidades.append(especialidad)
        return especialidades

    @classmethod
    def buscar(cls, texto: str, limite: int = 5) -> List['Especialidad']:
        """Busca especialidades por nombre. Lista vacía si no hay coincidencias."""
        consulta = "SELECT * FROM especialidad WHERE nombre LIKE %s LIMIT %s"
        resultados = db.ejecutar_consulta(consulta, (f"%{texto}%", limite))
        return [cls._desde_diccionario(row) for row in resultados]

    @classmethod
    def asignar_profesor(cls, especialidad_id: int, profesor_id: Optional[int]) -> bool:
        """Asigna o cambia el profesor de la especialidad."""
        consulta = "UPDATE especialidad SET profesor_id=%s WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (profesor_id, especialidad_id))
        return filas_afectadas > 0

    @classmethod
    def inscribir_estudiante(cls, especialidad_id: int, estudiante_id: int) -> bool:
        """Inscribe a un estudiante en la especialidad. No falla si ya estaba."""
        consulta = "INSERT IGNORE INTO estudiante_especialidad (usuario_id, especialidad_id) VALUES (%s, %s)"
        db.ejecutar_insercion(consulta, (estudiante_id, especialidad_id))
        return True

    @classmethod
    def quitar_estudiante(cls, asignacion_id: int) -> bool:
        """Elimina una inscripción estudiante-especialidad por su id."""
        consulta = "DELETE FROM estudiante_especialidad WHERE id=%s"
        db.ejecutar_actualizacion(consulta, (asignacion_id,))
        return True

    @classmethod
    def obtener_estudiantes(cls, especialidad_id: int) -> List[Dict[str, Any]]:
        """Lista los estudiantes inscritos en una especialidad."""
        consulta = """
            SELECT ee.id as asignacion_id, u.id as usuario_id, u.nombre, u.correo
            FROM estudiante_especialidad ee
            JOIN usuario u ON ee.usuario_id = u.id
            WHERE ee.especialidad_id = %s
            ORDER BY u.nombre
        """
        return db.ejecutar_consulta(consulta, (especialidad_id,))

    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Especialidad':
        return cls(
            id=datos.get('id'),
            nombre=datos.get('nombre'),
            cohorte_id=datos.get('cohorte_id'),
            profesor_id=datos.get('profesor_id'),
            activo=datos.get('activo', True),
            creado_en=datos.get('creado_en')
        )

    def __repr__(self):
        return f"<Especialidad {self.nombre}>"


# Catálogo de módulos que se pueden activar/desactivar y restringir por rol
# desde Parametrización. La clave es la que se usa en el sidebar y en
# @modulo_requerido(...). No incluye Dashboard/Usuarios/Configuración/
# Parametrización: son el núcleo del sistema y no se pueden apagar.
MODULOS_POR_DEFECTO = (
    ('tareas', 'Tareas', 'Asignación y entrega de tareas'),
    ('materias', 'Materias', 'Catálogo de materias por cohorte'),
    ('cursos', 'Cursos', 'Cursos 1001-1004 / 1101-1104'),
    ('especialidades', 'Especialidades', 'Programación, Diseño, Ambiental, Administración'),
    ('grupos', 'Grupos de trabajo', 'Equipos de trabajo dentro de una materia'),
    ('valoraciones', 'Valoraciones', 'Libro de valoraciones Bajo/Básico/Alto/Superior'),
    ('archivo', 'Archivo Histórico', 'Proyectos archivados de cohortes anteriores'),
    ('recursos', 'Recursos', 'Material de apoyo compartido'),
    ('comunicados', 'Información', 'Comunicados y avisos'),
    ('cronograma', 'Cronograma', 'Calendario de eventos académicos'),
    ('mensajeria', 'Mensajería', 'Mensajes directos entre usuarios'),
    ('reportes', 'Reportes', 'Reportes y estadísticas'),
)
ROLES_SISTEMA = ('estudiante', 'profesor', 'coordinador')

# Acciones disponibles por módulo para la matriz de permisos granular.
# 'ver' es la acción base (controla si el módulo aparece en el sidebar);
# el resto son acciones puntuales dentro del módulo. Los módulos no
# listados aquí (o las acciones no listadas) caen en ver/crear/editar/eliminar
# por defecto en la UI de Parametrización.
ACCIONES_POR_MODULO = {
    'cursos': ('ver', 'crear', 'editar', 'eliminar', 'asignar'),
    'materias': ('ver', 'crear', 'editar', 'eliminar'),
    'usuarios': ('ver', 'crear', 'editar', 'eliminar'),
    'matricula': ('ver', 'crear', 'editar', 'cambiar_estado'),
    'grupos': ('ver', 'crear', 'editar', 'eliminar', 'asignar'),
    'tareas': ('ver', 'crear', 'editar', 'eliminar', 'calificar'),
    'especialidades': ('ver', 'crear', 'editar', 'eliminar', 'asignar'),
    'valoraciones': ('ver', 'crear', 'editar'),
    'recursos': ('ver', 'crear', 'editar', 'eliminar'),
    'comunicados': ('ver', 'crear', 'editar', 'eliminar'),
    'cronograma': ('ver', 'crear', 'editar', 'eliminar'),
    'archivo': ('ver', 'crear', 'eliminar'),
    'mensajeria': ('ver', 'crear'),
    'reportes': ('ver',),
    'parametrizacion': ('ver', 'configurar'),
}
ETIQUETAS_ACCION = {
    'ver': 'Ver', 'crear': 'Crear', 'editar': 'Editar', 'eliminar': 'Eliminar',
    'cambiar_estado': 'Cambiar estado', 'asignar': 'Asignar', 'calificar': 'Calificar',
    'administrar': 'Administrar', 'configurar': 'Configurar',
}
# Módulos con matriz de permisos por acción, aunque no todos sean
# "desactivables" desde Módulos del sistema (usuarios/matrícula son núcleo).
MODULOS_CON_ACCIONES = ('cursos', 'materias', 'usuarios', 'matricula', 'grupos', 'tareas', 'especialidades')


class ModuloSistema:
    """Modelo de ModuloSistema - Representa la tabla 'modulo_sistema'.
    Permite al coordinador activar/desactivar módulos completos del sistema
    desde Parametrización, sin tocar código."""

    def __init__(self, clave=None, nombre=None, descripcion=None, activo=True):
        self.clave = clave
        self.nombre = nombre
        self.descripcion = descripcion
        self.activo = activo

    @classmethod
    def obtener_todos(cls) -> List['ModuloSistema']:
        """Lista todos los módulos configurables, ordenados por nombre."""
        consulta = "SELECT * FROM modulo_sistema ORDER BY nombre"
        resultados = db.ejecutar_consulta(consulta)
        return [cls(clave=r['clave'], nombre=r['nombre'], descripcion=r['descripcion'], activo=bool(r['activo'])) for r in resultados]

    @classmethod
    def mapa_activos(cls) -> Dict[str, bool]:
        """{clave: activo} de todos los módulos. Módulos no listados en la
        tabla se consideran activos por defecto (fail-open, para no romper
        el sidebar si a un módulo nuevo todavía no le corresponde fila)."""
        consulta = "SELECT clave, activo FROM modulo_sistema"
        resultados = db.ejecutar_consulta(consulta)
        return {r['clave']: bool(r['activo']) for r in resultados}

    @classmethod
    def esta_activo(cls, clave: str) -> bool:
        """True si el módulo está activo (o si no existe fila, por defecto True)."""
        consulta = "SELECT activo FROM modulo_sistema WHERE clave=%s"
        resultado = db.ejecutar_consulta(consulta, (clave,))
        return bool(resultado[0]['activo']) if resultado else True

    @classmethod
    def actualizar_estado(cls, clave: str, activo: bool) -> bool:
        """Activa o desactiva un módulo."""
        consulta = "UPDATE modulo_sistema SET activo=%s WHERE clave=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (activo, clave))
        return filas_afectadas > 0


class RolPermiso:
    """Modelo de RolPermiso - Representa la tabla 'rol_permiso'.
    Matriz ROL x MÓDULO x ACCIÓN: además de activar/desactivar un módulo
    entero (ver), el coordinador puede otorgar/quitar acciones puntuales
    (crear, editar, eliminar, y las que correspondan a cada módulo)."""

    @classmethod
    def obtener_matriz(cls, accion: str = 'ver') -> Dict[tuple, bool]:
        """{(rol, modulo_clave): permitido} para una acción puntual (por
        defecto 'ver', que es lo que controla la visibilidad del módulo)."""
        consulta = "SELECT rol, modulo_clave, permitido FROM rol_permiso WHERE accion=%s"
        resultados = db.ejecutar_consulta(consulta, (accion,))
        return {(r['rol'], r['modulo_clave']): bool(r['permitido']) for r in resultados}

    @classmethod
    def tiene_permiso(cls, rol: str, modulo_clave: str) -> bool:
        """True si ese rol puede VER ese módulo. Mínimo privilegio: si no
        hay fila explícita, se DENIEGA (excepto coordinador, que siempre
        puede todo)."""
        return cls.tiene_permiso_accion(rol, modulo_clave, 'ver')

    @classmethod
    def tiene_permiso_accion(cls, rol: str, modulo_clave: str, accion: str) -> bool:
        """True si ese rol puede ejecutar esa acción puntual sobre ese
        módulo. Por defecto, el coordinador siempre puede todo.

        Comportamiento por defecto cuando la tabla rol_permiso está vacía:
        - Para la acción 'ver' se aplica fail-open (se permite) para evitar
          bloquear el acceso cuando la parametrización no está cargada aún.
        - Para otras acciones se mantiene el comportamiento fail-closed
          (se deniega si no hay fila explícita).
        """
        if rol == 'coordinador':
            return True  # el coordinador siempre puede administrar todo

        # Si la tabla de permisos no tiene filas y la acción es 'ver',
        # permitimos el acceso por defecto (fail-open) para no bloquear
        # sistemas recién importados sin parametrización.
        try:
            contador = db.ejecutar_consulta("SELECT COUNT(*) as cnt FROM rol_permiso")
            total_perm = contador[0]['cnt'] if contador else 0
        except Exception:
            total_perm = 0

        if accion == 'ver' and total_perm == 0:
            return True

        consulta = "SELECT permitido FROM rol_permiso WHERE rol=%s AND modulo_clave=%s AND accion=%s"
        resultado = db.ejecutar_consulta(consulta, (rol, modulo_clave, accion))
        return bool(resultado[0]['permitido']) if resultado else False

    @classmethod
    def actualizar(cls, rol: str, modulo_clave: str, permitido: bool, accion: str = 'ver') -> bool:
        """Guarda (o actualiza) si un rol puede ejecutar una acción sobre un módulo."""
        consulta = """
            INSERT INTO rol_permiso (rol, modulo_clave, accion, permitido)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE permitido=VALUES(permitido)
        """
        db.ejecutar_insercion(consulta, (rol, modulo_clave, accion, permitido))
        return True

    @classmethod
    def obtener_matriz_completa(cls) -> Dict[tuple, bool]:
        """{(rol, modulo_clave, accion): permitido} de TODA la matriz guardada."""
        consulta = "SELECT rol, modulo_clave, accion, permitido FROM rol_permiso"
        resultados = db.ejecutar_consulta(consulta)
        return {(r['rol'], r['modulo_clave'], r['accion']): bool(r['permitido']) for r in resultados}


class ConfiguracionSistema:
    """Modelo de ConfiguracionSistema - Representa la tabla 'configuracion_sistema'.
    Almacén clave/valor genérico para ajustes base del sistema (nombre de la
    institución, correo de soporte, etc.), editable desde Parametrización."""

    @classmethod
    def obtener_todas(cls) -> List[Dict[str, Any]]:
        """Lista todos los ajustes, ordenados por clave."""
        consulta = "SELECT * FROM configuracion_sistema ORDER BY clave"
        return db.ejecutar_consulta(consulta)

    @classmethod
    def obtener(cls, clave: str, por_defecto: str = None) -> Optional[str]:
        """Valor de un ajuste puntual (o el valor por defecto si no existe)."""
        consulta = "SELECT valor FROM configuracion_sistema WHERE clave=%s"
        resultado = db.ejecutar_consulta(consulta, (clave,))
        return resultado[0]['valor'] if resultado else por_defecto

    @classmethod
    def actualizar(cls, clave: str, valor: str) -> bool:
        """Actualiza el valor de un ajuste existente."""
        consulta = "UPDATE configuracion_sistema SET valor=%s, actualizado_en=NOW() WHERE clave=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (valor, clave))
        return filas_afectadas > 0


class Recurso:
    """Modelo de Recurso - Representa la tabla 'recurso'.
    materia_id y curso_id son opcionales: un recurso puede ser general
    (institucional), de una materia (cualquier curso) o de un curso puntual
    (para no filtrar el material de un curso a otro sin querer)."""
    
    def __init__(self, id=None, titulo=None, descripcion=None,
                 url_archivo=None, tipo=None, materia_id=None, curso_id=None,
                 creado_por=None, creado_en=None):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.url_archivo = url_archivo
        self.tipo = tipo
        self.materia_id = materia_id
        self.curso_id = curso_id
        self.creado_por = creado_por
        self.creado_en = creado_en
    
    def guardar(self) -> int:
        """Crea un nuevo recurso en la BD."""
        consulta = """
            INSERT INTO recurso (titulo, descripcion, url_archivo, tipo, materia_id, curso_id, creado_por)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        parametros = (self.titulo, self.descripcion, self.url_archivo,
                     self.tipo, self.materia_id, self.curso_id, self.creado_por)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id

    def actualizar(self) -> bool:
        """Actualiza el recurso en la BD."""
        consulta = """
            UPDATE recurso
            SET titulo=%s, descripcion=%s, url_archivo=%s, tipo=%s, materia_id=%s, curso_id=%s
            WHERE id=%s
        """
        parametros = (self.titulo, self.descripcion, self.url_archivo,
                     self.tipo, self.materia_id, self.curso_id, self.id)
        filas_afectadas = db.ejecutar_actualizacion(consulta, parametros)
        return filas_afectadas > 0

    def eliminar(self) -> bool:
        """Elimina el recurso de la BD."""
        consulta = "DELETE FROM recurso WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (self.id,))
        return filas_afectadas > 0

    @classmethod
    def obtener_por_id(cls, id: int) -> Optional['Recurso']:
        """Obtiene un recurso por su ID."""
        consulta = "SELECT * FROM recurso WHERE id=%s"
        resultados = db.ejecutar_consulta(consulta, (id,))
        return cls._desde_diccionario(resultados[0]) if resultados else None

    @classmethod
    def buscar(cls, texto: str, limite: int = 5) -> List['Recurso']:
        """Busca recursos por título. Lista vacía si no hay coincidencias."""
        consulta = "SELECT * FROM recurso WHERE titulo LIKE %s ORDER BY titulo LIMIT %s"
        resultados = db.ejecutar_consulta(consulta, (f"%{texto}%", limite))
        return [cls._desde_diccionario(row) for row in resultados]

    @classmethod
    def obtener_todos(cls, curso_id: Optional[int] = None) -> List['Recurso']:
        """Obtiene todos los recursos, opcionalmente filtrados por curso
        (para no mostrar el material de un curso en otro)."""
        condicion = "WHERE r.curso_id = %s" if curso_id else ""
        parametros = (curso_id,) if curso_id else ()
        consulta = f"""
            SELECT r.*, m.nombre as materia_nombre, u.nombre as autor_nombre, c.codigo as curso_codigo
            FROM recurso r
            LEFT JOIN materia m ON r.materia_id = m.id
            LEFT JOIN usuario u ON r.creado_por = u.id
            LEFT JOIN curso c ON r.curso_id = c.id
            {condicion}
            ORDER BY r.creado_en DESC
        """
        resultados = db.ejecutar_consulta(consulta, parametros)
        recursos = []
        for row in resultados:
            recurso = cls._desde_diccionario(row)
            recurso.materia_nombre = row.get('materia_nombre')
            recurso.autor_nombre = row.get('autor_nombre')
            recurso.curso_codigo = row.get('curso_codigo')
            recursos.append(recurso)
        return recursos
    
    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Recurso':
        """Crea una instancia desde un diccionario."""
        return cls(
            id=datos.get('id'),
            titulo=datos.get('titulo'),
            descripcion=datos.get('descripcion'),
            url_archivo=datos.get('url_archivo'),
            tipo=datos.get('tipo'),
            materia_id=datos.get('materia_id'),
            curso_id=datos.get('curso_id'),
            creado_por=datos.get('creado_por'),
            creado_en=datos.get('creado_en')
        )
    
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la instancia a diccionario."""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'tipo': self.tipo,
            'materia': self.materia_nombre if hasattr(self, 'materia_nombre') else 'Sin asignar',
            'autor': self.autor_nombre if hasattr(self, 'autor_nombre') else 'Sistema'
        }
    
    def __repr__(self):
        return f"<Recurso {self.titulo}>"


class Cronograma:
    """Modelo de Cronograma - Representa la tabla 'cronograma'."""

    def __init__(self, id=None, titulo=None, descripcion=None,
                 fecha_evento=None, tipo=None, materia_id=None, curso_id=None,
                 creado_por=None, creado_en=None):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_evento = fecha_evento
        self.tipo = tipo
        self.materia_id = materia_id
        self.curso_id = curso_id
        self.creado_por = creado_por
        self.creado_en = creado_en

    # ------------------- CRUD -------------------

    def guardar(self) -> int:
        """Crea un nuevo evento en la BD."""
        consulta = """
            INSERT INTO cronograma (titulo, descripcion, fecha_evento, tipo, materia_id, curso_id, creado_por)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        parametros = (self.titulo, self.descripcion, self.fecha_evento, self.tipo,
                      self.materia_id, self.curso_id, self.creado_por)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id

    def actualizar(self):
        """Actualiza un evento existente."""
        consulta = """
            UPDATE cronograma
            SET titulo=%s, descripcion=%s, fecha_evento=%s, tipo=%s, materia_id=%s, curso_id=%s
            WHERE id=%s
        """
        parametros = (self.titulo, self.descripcion, self.fecha_evento,
                      self.tipo, self.materia_id, self.curso_id, self.id)
        db.ejecutar_actualizacion(consulta, parametros)

    def eliminar(self):
        """Elimina un evento de cronograma por ID."""
        consulta = "DELETE FROM cronograma WHERE id=%s"
        db.ejecutar_actualizacion(consulta, (self.id,))

    # ------------------- Métodos de clase -------------------

    @classmethod
    def obtener_todos(cls, profesor_id: int = None) -> List['Cronograma']:
        """Obtiene todos los eventos del cronograma, opcionalmente filtrados por profesor."""
        consulta = """
            SELECT c.*, m.nombre as materia_nombre, cu.codigo as curso_codigo
            FROM cronograma c
            LEFT JOIN materia m ON c.materia_id = m.id
            LEFT JOIN curso cu ON c.curso_id = cu.id
        """
        parametros = ()
        
        # Filtrar por profesor si se pasa el ID
        if profesor_id:
            consulta += " WHERE c.creado_por = %s"
            parametros = (profesor_id,)
            
        consulta += " ORDER BY c.fecha_evento ASC"
        
        resultados = db.ejecutar_consulta(consulta, parametros)
        eventos = []
        for row in resultados:
            evento = cls._desde_diccionario(row)
            evento.materia_nombre = row.get('materia_nombre')
            evento.curso_codigo = row.get('curso_codigo')
            eventos.append(evento)
        return eventos

    @classmethod
    def obtener_por_id(cls, id: int) -> 'Cronograma':
        """Obtiene un evento por su ID."""
        consulta = """
            SELECT c.*, m.nombre as materia_nombre
            FROM cronograma c
            LEFT JOIN materia m ON c.materia_id = m.id
            WHERE c.id=%s
        """
        resultados = db.ejecutar_consulta(consulta, (id,))
        if resultados:
            evento = cls._desde_diccionario(resultados[0])
            evento.materia_nombre = resultados[0].get('materia_nombre')
            return evento
        return None

    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Cronograma':
        """Crea una instancia desde un diccionario."""
        return cls(
            id=datos.get('id'),
            titulo=datos.get('titulo'),
            descripcion=datos.get('descripcion'),
            fecha_evento=datos.get('fecha_evento'),
            tipo=datos.get('tipo'),
            materia_id=datos.get('materia_id'),
            curso_id=datos.get('curso_id'),
            creado_por=datos.get('creado_por'),
            creado_en=datos.get('creado_en')
        )

    # ------------------- Utilidades -------------------

    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la instancia a diccionario."""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'fecha': self.fecha_evento,
            'materia': getattr(self, 'materia_nombre', 'Sin asignar')
        }

    def __repr__(self):
        return f"<Cronograma {self.titulo}>"


class Mensaje:
    """Modelo de Mensaje - Representa la tabla 'mensaje'."""
    
    def __init__(self, id=None, remitente_id=None, destinatario_id=None,
                 asunto=None, cuerpo=None, enviado_en=None, leido=False,
                 eliminado_remitente=False, eliminado_destinatario=False, grupo_id=None):
        self.id = id
        self.remitente_id = remitente_id
        self.destinatario_id = destinatario_id
        self.asunto = asunto
        self.cuerpo = cuerpo
        self.enviado_en = enviado_en
        self.leido = leido
        self.eliminado_remitente = eliminado_remitente
        self.eliminado_destinatario = eliminado_destinatario
        self.grupo_id = grupo_id
    
    def guardar(self) -> int:
        """Crea un nuevo mensaje en la BD."""
        consulta = """
            INSERT INTO mensaje (remitente_id, destinatario_id, asunto, cuerpo, leido)
            VALUES (%s, %s, %s, %s, %s)
        """
        parametros = (self.remitente_id, self.destinatario_id, 
                     self.asunto, self.cuerpo, self.leido)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id
    
    @classmethod
    def contar_no_leidos(cls, usuario_id: int) -> int:
        """Cuenta los mensajes no leídos de un usuario. Devuelve 0 si no hay ninguno."""
        if not usuario_id:
            return 0
        consulta = """
            SELECT COUNT(*) as total FROM mensaje
            WHERE destinatario_id=%s AND leido=0 AND eliminado_destinatario=0
        """
        resultado = db.ejecutar_consulta(consulta, (usuario_id,))
        return resultado[0]['total'] if resultado else 0

    @classmethod
    def obtener_recibidos(cls, usuario_id: int) -> List['Mensaje']:
        """Obtiene mensajes recibidos por un usuario, con nombre del remitente y del grupo (si aplica)."""
        consulta = """
            SELECT m.*, u.nombre as remitente_nombre, g.nombre as grupo_nombre
            FROM mensaje m
            LEFT JOIN usuario u ON m.remitente_id = u.id
            LEFT JOIN grupo g ON m.grupo_id = g.id
            WHERE m.destinatario_id=%s AND m.eliminado_destinatario=0
            ORDER BY m.enviado_en DESC
        """
        resultados = db.ejecutar_consulta(consulta, (usuario_id,))
        mensajes = []
        for row in resultados:
            msg = cls._desde_diccionario(row)
            msg.remitente_nombre = row.get('remitente_nombre')
            msg.grupo_nombre = row.get('grupo_nombre')
            mensajes.append(msg)
        return mensajes

    @classmethod
    def enviar_a_grupo(cls, remitente_id: int, grupo_id: int, asunto: str, cuerpo: str) -> int:
        """
        Envía un mensaje a TODOS los estudiantes inscritos en un grupo: crea una
        copia individual por cada uno (para que cada quien tenga su propio estado
        de leído), etiquetada con grupo_id. Devuelve cuántos lo recibieron (0 si
        el grupo no tiene estudiantes inscritos todavía).
        """
        consulta_miembros = "SELECT usuario_id FROM estudiante_grupo WHERE grupo_id=%s"
        miembros = db.ejecutar_consulta(consulta_miembros, (grupo_id,))

        for miembro in miembros:
            consulta = """
                INSERT INTO mensaje (remitente_id, destinatario_id, grupo_id, asunto, cuerpo, leido)
                VALUES (%s, %s, %s, %s, %s, 0)
            """
            db.ejecutar_insercion(consulta, (
                remitente_id, miembro['usuario_id'], grupo_id, asunto, cuerpo
            ))

        return len(miembros)

    @classmethod
    def marcar_leido(cls, mensaje_id: int, usuario_id: int) -> bool:
        """Marca un mensaje como leído (solo si el destinatario es quien lo pide)."""
        consulta = "UPDATE mensaje SET leido=1 WHERE id=%s AND destinatario_id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (mensaje_id, usuario_id))
        return filas_afectadas > 0

    @classmethod
    def eliminar_para_usuario(cls, mensaje_id: int, usuario_id: int) -> bool:
        """
        Borrado 'suave': oculta el mensaje SOLO de la bandeja de quien lo borra.
        Si el mensaje ya estaba oculto para ambos lados (remitente y destinatario),
        recién ahí se borra físicamente de la BD.
        """
        consulta_estado = "SELECT remitente_id, destinatario_id, eliminado_remitente, eliminado_destinatario FROM mensaje WHERE id=%s"
        resultado = db.ejecutar_consulta(consulta_estado, (mensaje_id,))
        if not resultado:
            return False
        fila = resultado[0]

        if fila['remitente_id'] == usuario_id:
            db.ejecutar_actualizacion("UPDATE mensaje SET eliminado_remitente=1 WHERE id=%s", (mensaje_id,))
            eliminado_remitente, eliminado_destinatario = True, fila['eliminado_destinatario']
        elif fila['destinatario_id'] == usuario_id:
            db.ejecutar_actualizacion("UPDATE mensaje SET eliminado_destinatario=1 WHERE id=%s", (mensaje_id,))
            eliminado_remitente, eliminado_destinatario = fila['eliminado_remitente'], True
        else:
            return False

        if eliminado_remitente and eliminado_destinatario:
            db.ejecutar_actualizacion("DELETE FROM mensaje WHERE id=%s", (mensaje_id,))
        return True

    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Mensaje':
        """Crea una instancia desde un diccionario."""
        return cls(
            id=datos.get('id'),
            remitente_id=datos.get('remitente_id'),
            destinatario_id=datos.get('destinatario_id'),
            asunto=datos.get('asunto'),
            cuerpo=datos.get('cuerpo'),
            enviado_en=datos.get('enviado_en'),
            leido=datos.get('leido', False),
            eliminado_remitente=datos.get('eliminado_remitente', False),
            eliminado_destinatario=datos.get('eliminado_destinatario', False),
            grupo_id=datos.get('grupo_id')
        )
    
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la instancia a diccionario."""
        return {
            'id': self.id,
            'remitente': self.remitente_nombre if hasattr(self, 'remitente_nombre') else 'Sistema',
            'asunto': self.asunto,
            'leido': self.leido
        }
    
    def __repr__(self):
        return f"<Mensaje {self.asunto}>"

class Entrega:
    """Modelo de Entrega - Representa la tabla 'entrega' (entregas de tareas)."""

    def __init__(self, id=None, tarea_id=None, estudiante_id=None,
                 archivo_url=None, archivo_nombre_original=None, comentario=None,
                 estado='pendiente', nota=None, entregado_en=None):
        self.id = id
        self.tarea_id = tarea_id
        self.estudiante_id = estudiante_id
        self.archivo_url = archivo_url
        self.archivo_nombre_original = archivo_nombre_original
        self.comentario = comentario
        self.estado = estado  # pendiente | entregada | calificada
        self.nota = nota
        self.entregado_en = entregado_en

    def guardar(self) -> int:
        """
        Registra o actualiza la entrega de un estudiante para una tarea
        (un estudiante solo puede tener UNA entrega por tarea; si ya existía,
        la reemplaza en vez de duplicarla).
        """
        existente = Entrega.obtener_por_estudiante_y_tarea(self.tarea_id, self.estudiante_id)
        if existente:
            self.id = existente.id
            consulta = """
                UPDATE entrega
                SET archivo_url=%s, archivo_nombre_original=%s, comentario_profesor=%s,
                    estado='entregada', fecha_entrega=NOW()
                WHERE id=%s
            """
            db.ejecutar_actualizacion(consulta, (
                self.archivo_url, self.archivo_nombre_original, self.comentario, self.id
            ))
        else:
            consulta = """
                INSERT INTO entrega
                    (tarea_id, estudiante_id, archivo_url, archivo_nombre_original,
                     comentario_profesor, estado, fecha_entrega)
                VALUES (%s, %s, %s, %s, %s, 'entregada', NOW())
            """
            self.id = db.ejecutar_insercion(consulta, (
                self.tarea_id, self.estudiante_id, self.archivo_url,
                self.archivo_nombre_original, self.comentario
            ))
        return self.id

    def calificar(self, nota: float, comentario: str = None) -> bool:
        """Asigna una nota (y opcionalmente un comentario del profesor) y marca como calificada."""
        consulta = "UPDATE entrega SET calificacion=%s, comentario_profesor=%s, estado='calificada' WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (nota, comentario, self.id))
        return filas_afectadas > 0

    @classmethod
    def obtener_por_estudiante_y_tarea(cls, tarea_id: int, estudiante_id: int) -> Optional['Entrega']:
        """Busca si un estudiante ya entregó una tarea específica. None si no hay nada todavía."""
        consulta = "SELECT * FROM entrega WHERE tarea_id=%s AND estudiante_id=%s"
        resultados = db.ejecutar_consulta(consulta, (tarea_id, estudiante_id))
        return cls._desde_diccionario(resultados[0]) if resultados else None

    @classmethod
    def obtener_por_id(cls, id: int) -> Optional['Entrega']:
        """Obtiene una entrega por su ID, con datos de la tarea y el estudiante."""
        consulta = """
            SELECT e.*, u.nombre as estudiante_nombre, t.titulo as tarea_titulo, t.creado_por as tarea_creador_id
            FROM entrega e
            LEFT JOIN usuario u ON e.estudiante_id = u.id
            LEFT JOIN tarea t ON e.tarea_id = t.id
            WHERE e.id=%s
        """
        resultados = db.ejecutar_consulta(consulta, (id,))
        if not resultados:
            return None
        row = resultados[0]
        entrega = cls._desde_diccionario(row)
        entrega.estudiante_nombre = row.get('estudiante_nombre')
        entrega.tarea_titulo = row.get('tarea_titulo')
        entrega.tarea_creador_id = row.get('tarea_creador_id')
        return entrega

    @classmethod
    def obtener_por_tarea(cls, tarea_id: int) -> List['Entrega']:
        """Obtiene todas las entregas realizadas de una tarea, con nombre del estudiante."""
        consulta = """
            SELECT e.*, u.nombre as estudiante_nombre
            FROM entrega e
            LEFT JOIN usuario u ON e.estudiante_id = u.id
            WHERE e.tarea_id=%s
            ORDER BY e.fecha_entrega DESC
        """
        resultados = db.ejecutar_consulta(consulta, (tarea_id,))
        entregas = []
        for row in resultados:
            entrega = cls._desde_diccionario(row)
            entrega.estudiante_nombre = row.get('estudiante_nombre')
            entregas.append(entrega)
        return entregas

    @classmethod
    def obtener_estado_por_tarea(cls, tarea_id: int) -> List[Dict[str, Any]]:
        """
        Roster completo para la pantalla de revisión del profesor: SOLO los
        estudiantes del curso de la asignación académica específica de esta
        tarea (nunca estudiantes de otro curso, aunque compartan materia),
        con su entrega si existe. Lista vacía si el curso no tiene estudiantes.
        """
        consulta = """
            SELECT
                u.id AS estudiante_id, u.nombre AS estudiante_nombre,
                e.id AS entrega_id, e.archivo_url, e.archivo_nombre_original,
                e.comentario_profesor AS comentario, e.estado AS entrega_estado, e.calificacion AS nota, e.fecha_entrega
            FROM tarea t
            JOIN curso_materia cm ON t.curso_materia_id = cm.id
            JOIN usuario u ON u.curso_id = cm.curso_id AND u.rol = 'estudiante'
            LEFT JOIN entrega e ON e.tarea_id = t.id AND e.estudiante_id = u.id
            WHERE t.id = %s
            ORDER BY u.nombre
        """
        return db.ejecutar_consulta(consulta, (tarea_id,))

    @classmethod
    def contar_por_tarea(cls, tarea_id: int) -> int:
        """Cuenta cuántas entregas tiene una tarea. 0 si no hay ninguna."""
        consulta = "SELECT COUNT(*) as total FROM entrega WHERE tarea_id=%s"
        resultado = db.ejecutar_consulta(consulta, (tarea_id,))
        return resultado[0]['total'] if resultado else 0

    @classmethod
    def contar_completadas_estudiante(cls, estudiante_id: int) -> int:
        """Entregas ya hechas (entregada o calificada) por un estudiante. 0 si no hay ninguna."""
        if not estudiante_id:
            return 0
        consulta = """
            SELECT COUNT(*) as total FROM entrega
            WHERE estudiante_id=%s AND estado IN ('entregada', 'calificada')
        """
        resultado = db.ejecutar_consulta(consulta, (estudiante_id,))
        return resultado[0]['total'] if resultado else 0

    @classmethod
    def contar_por_calificar_profesor(cls, profesor_id: int) -> int:
        """Entregas 'entregada' (aún sin calificar) de tareas creadas por este profesor. 0 si no hay."""
        if not profesor_id:
            return 0
        consulta = """
            SELECT COUNT(*) as total
            FROM entrega e
            JOIN tarea t ON e.tarea_id = t.id
            WHERE t.creado_por=%s AND e.estado='entregada'
        """
        resultado = db.ejecutar_consulta(consulta, (profesor_id,))
        return resultado[0]['total'] if resultado else 0

    @classmethod
    def estadisticas_por_materia(cls, materia_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Desglose de promedio, % calificadas y % a tiempo POR CADA MATERIA.
        Si materia_ids se especifica, filtra solo esas materias (para el rol profesor).
        Lista vacía si no hay materias con entregas todavía.
        """
        condicion = ""
        parametros: tuple = ()
        if materia_ids:
            placeholders = ','.join(['%s'] * len(materia_ids))
            condicion = f"WHERE m.id IN ({placeholders})"
            parametros = tuple(materia_ids)

        consulta = f"""
            SELECT
                m.id as materia_id, m.nombre as materia_nombre,
                COUNT(e.id) as total_entregas,
                AVG(e.calificacion) as promedio,
                SUM(CASE WHEN e.calificacion IS NOT NULL THEN 1 ELSE 0 END) as calificadas,
                SUM(CASE WHEN e.fecha_entrega <= t.fecha_limite THEN 1 ELSE 0 END) as a_tiempo
            FROM materia m
            JOIN curso_materia cm ON cm.materia_id = m.id
            JOIN tarea t ON t.curso_materia_id = cm.id
            LEFT JOIN entrega e ON e.tarea_id = t.id
            {condicion}
            GROUP BY m.id, m.nombre
            HAVING total_entregas > 0
            ORDER BY promedio DESC
        """
        resultados = db.ejecutar_consulta(consulta, parametros)
        salida = []
        for row in resultados:
            total = row['total_entregas'] or 0
            salida.append({
                'materia_id': row['materia_id'],
                'materia_nombre': row['materia_nombre'],
                'total_entregas': total,
                'promedio': round(row['promedio'], 1) if row['promedio'] else 0,
                'tasa_calificadas': round((row['calificadas'] or 0) / total * 100) if total else 0,
                'tasa_a_tiempo': round((row['a_tiempo'] or 0) / total * 100) if total else 0,
            })
        return salida

    @classmethod
    def top_estudiantes(cls, materia_ids: Optional[List[int]] = None, limite: int = 5) -> List[Dict[str, Any]]:
        """Ranking de estudiantes por promedio (solo los que ya tienen al menos una nota)."""
        condicion = ""
        parametros: tuple = ()
        if materia_ids:
            placeholders = ','.join(['%s'] * len(materia_ids))
            condicion = f"AND cm.materia_id IN ({placeholders})"
            parametros = tuple(materia_ids)

        consulta = f"""
            SELECT u.id as estudiante_id, u.nombre as estudiante_nombre,
                   AVG(e.calificacion) as promedio, COUNT(e.id) as total_entregas
            FROM entrega e
            JOIN usuario u ON e.estudiante_id = u.id
            JOIN tarea t ON e.tarea_id = t.id
            JOIN curso_materia cm ON t.curso_materia_id = cm.id
            WHERE e.calificacion IS NOT NULL {condicion}
            GROUP BY u.id, u.nombre
            ORDER BY promedio DESC
            LIMIT {int(limite)}
        """
        resultados = db.ejecutar_consulta(consulta, parametros)
        return [
            {
                'estudiante_id': r['estudiante_id'],
                'estudiante_nombre': r['estudiante_nombre'],
                'promedio': round(r['promedio'], 1) if r['promedio'] else 0,
                'total_entregas': r['total_entregas']
            }
            for r in resultados
        ]

    @classmethod
    def entregas_por_semana(cls, semanas: int = 8) -> List[Dict[str, Any]]:
        """
        Cantidad de entregas realizadas por semana, últimas N semanas.
        Sirve para graficar la tendencia de actividad. Lista vacía si no hay entregas.
        """
        consulta = """
            SELECT YEARWEEK(fecha_entrega, 3) as semana_iso,
                   MIN(DATE(fecha_entrega)) as semana_inicio,
                   COUNT(*) as total
            FROM entrega
            WHERE fecha_entrega >= DATE_SUB(CURDATE(), INTERVAL %s WEEK)
            GROUP BY semana_iso
            ORDER BY semana_iso
        """
        resultados = db.ejecutar_consulta(consulta, (semanas,))
        return [
            {'semana': r['semana_inicio'].strftime('%d/%m') if r['semana_inicio'] else '', 'total': r['total']}
            for r in resultados
        ]

    @classmethod
    def estadisticas_generales(cls, materia_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Calcula promedio general, % de entregas calificadas y % de entregas a tiempo.
        Si materia_ids se especifica, filtra solo esas materias (para el rol profesor).
        Todo en 0 si todavía no hay entregas registradas (sin división por cero).
        """
        condicion = ""
        parametros: tuple = ()
        if materia_ids:
            placeholders = ','.join(['%s'] * len(materia_ids))
            condicion = f"WHERE cm.materia_id IN ({placeholders})"
            parametros = tuple(materia_ids)

        consulta = f"""
            SELECT
                AVG(e.calificacion) as promedio,
                COUNT(*) as total_entregas,
                SUM(CASE WHEN e.calificacion IS NOT NULL THEN 1 ELSE 0 END) as calificadas,
                SUM(CASE WHEN e.fecha_entrega <= t.fecha_limite THEN 1 ELSE 0 END) as a_tiempo
            FROM entrega e
            JOIN tarea t ON e.tarea_id = t.id
            JOIN curso_materia cm ON t.curso_materia_id = cm.id
            {condicion}
        """
        resultado = db.ejecutar_consulta(consulta, parametros)
        if not resultado or not resultado[0]['total_entregas']:
            return {'promedio': 0, 'tasa_calificadas': 0, 'tasa_a_tiempo': 0}

        fila = resultado[0]
        total = fila['total_entregas']
        return {
            'promedio': round(fila['promedio'], 1) if fila['promedio'] else 0,
            'tasa_calificadas': round((fila['calificadas'] or 0) / total * 100),
            'tasa_a_tiempo': round((fila['a_tiempo'] or 0) / total * 100),
        }

    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Entrega':
        return cls(
            id=datos.get('id'),
            tarea_id=datos.get('tarea_id'),
            estudiante_id=datos.get('estudiante_id'),
            archivo_url=datos.get('archivo_url'),
            archivo_nombre_original=datos.get('archivo_nombre_original'),
            comentario=datos.get('comentario_profesor'),
            estado=datos.get('estado', 'pendiente'),
            nota=datos.get('calificacion'),
            entregado_en=datos.get('fecha_entrega')
        )

    def __repr__(self):
        return f"<Entrega tarea={self.tarea_id} estudiante={self.estudiante_id}>"

class ActividadValorativa:
    """
    Modelo de ActividadValorativa - Representa la tabla 'actividad_valorativa'.
    El profesor define libremente estas actividades por materia (examen, tarea,
    participación, proyecto...) cada una con su % de peso en la nota final.
    """

    def __init__(self, id=None, materia_id=None, nombre=None, tipo='otro',
                 porcentaje=0, fecha=None, creado_por=None, creado_en=None):
        self.id = id
        self.materia_id = materia_id
        self.nombre = nombre
        self.tipo = tipo
        self.porcentaje = porcentaje
        self.fecha = fecha
        self.creado_por = creado_por
        self.creado_en = creado_en

    def guardar(self) -> int:
        """Crea una nueva actividad valorativa en la BD."""
        consulta = """
            INSERT INTO actividad_valorativa (materia_id, nombre, tipo, porcentaje, fecha, creado_por)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        parametros = (self.materia_id, self.nombre, self.tipo, self.porcentaje, self.fecha, self.creado_por)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id

    def actualizar(self) -> bool:
        """Actualiza la actividad en la BD."""
        consulta = """
            UPDATE actividad_valorativa
            SET nombre=%s, tipo=%s, porcentaje=%s, fecha=%s
            WHERE id=%s
        """
        parametros = (self.nombre, self.tipo, self.porcentaje, self.fecha, self.id)
        filas_afectadas = db.ejecutar_actualizacion(consulta, parametros)
        return filas_afectadas > 0

    def eliminar(self) -> bool:
        """Elimina la actividad de la BD (y en cascada sus valoraciones)."""
        consulta = "DELETE FROM actividad_valorativa WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (self.id,))
        return filas_afectadas > 0

    @classmethod
    def obtener_por_id(cls, id: int) -> Optional['ActividadValorativa']:
        """Obtiene una actividad por su ID."""
        consulta = "SELECT * FROM actividad_valorativa WHERE id=%s"
        resultados = db.ejecutar_consulta(consulta, (id,))
        return cls._desde_diccionario(resultados[0]) if resultados else None

    @classmethod
    def obtener_por_materia(cls, materia_id: int) -> List['ActividadValorativa']:
        """Lista las actividades de una materia, ordenadas por fecha. Vacía si no hay ninguna."""
        consulta = "SELECT * FROM actividad_valorativa WHERE materia_id=%s ORDER BY fecha, id"
        resultados = db.ejecutar_consulta(consulta, (materia_id,))
        return [cls._desde_diccionario(row) for row in resultados]

    @classmethod
    def suma_porcentajes(cls, materia_id: int) -> float:
        """Suma de los % de peso de todas las actividades de una materia. 0 si no hay ninguna."""
        consulta = "SELECT SUM(porcentaje) as total FROM actividad_valorativa WHERE materia_id=%s"
        resultado = db.ejecutar_consulta(consulta, (materia_id,))
        total = resultado[0]['total'] if resultado else None
        return float(total) if total is not None else 0.0

    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'ActividadValorativa':
        return cls(
            id=datos.get('id'),
            materia_id=datos.get('materia_id'),
            nombre=datos.get('nombre'),
            tipo=datos.get('tipo', 'otro'),
            porcentaje=datos.get('porcentaje', 0),
            fecha=datos.get('fecha'),
            creado_por=datos.get('creado_por'),
            creado_en=datos.get('creado_en')
        )

    def __repr__(self):
        return f"<ActividadValorativa {self.nombre} ({self.porcentaje}%)>"


class ValoracionActividad:
    """
    Modelo de ValoracionActividad - Representa la tabla 'valoracion_actividad'.
    La nota puntual de un estudiante en una actividad valorativa concreta.
    """

    def __init__(self, id=None, actividad_id=None, estudiante_id=None,
                 valor=None, comentario=None, calificado_en=None):
        self.id = id
        self.actividad_id = actividad_id
        self.estudiante_id = estudiante_id
        self.valor = valor
        self.comentario = comentario
        self.calificado_en = calificado_en

    def guardar(self) -> int:
        """
        Guarda o actualiza la valoración de un estudiante en una actividad
        (upsert): si ya existía la reemplaza, si no la crea. `valor` debe
        ser uno de: Bajo, Básico, Alto, Superior.
        """
        consulta = """
            INSERT INTO valoracion_actividad (actividad_id, estudiante_id, valor, comentario)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE valor=VALUES(valor), comentario=VALUES(comentario), calificado_en=NOW()
        """
        parametros = (self.actividad_id, self.estudiante_id, self.valor, self.comentario)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id

    @classmethod
    def obtener_boletin(cls, materia_id: int) -> List[Dict[str, Any]]:
        """
        Boletín consolidado de una materia: por cada estudiante inscrito,
        su valoración final (según el % de cada actividad, promediado en la
        escala Bajo/Básico/Alto/Superior) y si aprobó contra la valoración
        mínima de la materia. Lista vacía si la materia no tiene estudiantes.
        """
        consulta = """
            SELECT
                u.id as estudiante_id, u.nombre as estudiante_nombre,
                m.valoracion_minima_aprobatoria,
                ae.id as actividad_id, ae.porcentaje, va.valor
            FROM curso_materia cm
            JOIN usuario u ON u.curso_id = cm.curso_id AND u.rol = 'estudiante'
            JOIN materia m ON m.id = cm.materia_id
            LEFT JOIN actividad_valorativa ae ON ae.materia_id = cm.materia_id
            LEFT JOIN valoracion_actividad va ON va.actividad_id = ae.id AND va.estudiante_id = u.id
            WHERE cm.materia_id = %s
            ORDER BY u.nombre
        """
        filas = db.ejecutar_consulta(consulta, (materia_id,))

        estudiantes = {}
        for f in filas:
            eid = f['estudiante_id']
            if eid not in estudiantes:
                estudiantes[eid] = {
                    'estudiante_id': eid,
                    'estudiante_nombre': f['estudiante_nombre'],
                    'umbral': f['valoracion_minima_aprobatoria'],
                    'actividades': set(),
                    'calificadas': set(),
                    'suma_ponderada': 0.0,
                    'peso_calificado': 0.0,
                }
            e = estudiantes[eid]
            if f['actividad_id'] is not None:
                e['actividades'].add(f['actividad_id'])
                if f['valor']:
                    e['calificadas'].add(f['actividad_id'])
                    peso = float(f['porcentaje'] or 0)
                    e['suma_ponderada'] += VALOR_ORDINAL[f['valor']] * peso
                    e['peso_calificado'] += peso

        boletin = []
        for e in estudiantes.values():
            umbral_ordinal = VALOR_ORDINAL.get(e['umbral'], VALOR_ORDINAL['Básico'])
            if e['peso_calificado'] > 0:
                promedio_ordinal = e['suma_ponderada'] / e['peso_calificado']
                valoracion_final = ORDINAL_A_VALOR[min(4, max(1, round(promedio_ordinal)))]
            else:
                valoracion_final = None
            total = len(e['actividades'])
            calificadas = len(e['calificadas'])
            boletin.append({
                'estudiante_id': e['estudiante_id'],
                'estudiante_nombre': e['estudiante_nombre'],
                'total_actividades': total,
                'actividades_calificadas': calificadas,
                'valoracion_final': valoracion_final,
                'aprobado': (valoracion_final is not None and VALOR_ORDINAL[valoracion_final] >= umbral_ordinal),
                'completo': total == calificadas and total > 0
            })
        return boletin

    @classmethod
    def obtener_notas_materia(cls, materia_id: int) -> Dict[tuple, str]:
        """Diccionario {(actividad_id, estudiante_id): valor} para armar la matriz rápido."""
        consulta = """
            SELECT va.* FROM valoracion_actividad va
            JOIN actividad_valorativa ae ON va.actividad_id = ae.id
            WHERE ae.materia_id = %s
        """
        resultados = db.ejecutar_consulta(consulta, (materia_id,))
        return {(r['actividad_id'], r['estudiante_id']): r.get('valor') for r in resultados}

    @classmethod
    def obtener_detalle_estudiante(cls, materia_id: int, estudiante_id: int) -> List[Dict[str, Any]]:
        """
        Desglose actividad por actividad de UN estudiante en una materia:
        qué actividad, cuánto pesa, qué valoración sacó (o si todavía no la calificaron).
        Lista vacía si la materia no tiene actividades cargadas.
        """
        consulta = """
            SELECT ae.id as actividad_id, ae.nombre, ae.tipo, ae.porcentaje, ae.fecha,
                   va.valor, va.comentario
            FROM actividad_valorativa ae
            LEFT JOIN valoracion_actividad ca
                ON ca.actividad_id = ae.id AND ca.estudiante_id = %s
            WHERE ae.materia_id = %s
            ORDER BY ae.fecha, ae.id
        """
        return db.ejecutar_consulta(consulta, (estudiante_id, materia_id))

    def __repr__(self):
        return f"<ValoracionActividad actividad={self.actividad_id} estudiante={self.estudiante_id}>"


class ProyectoArchivado:
    """
    Modelo de ProyectoArchivado - Representa la tabla 'proyecto_archivado'.
    Archivo histórico de proyectos ya concluidos de cursos/cohortes anteriores,
    buscable por texto con índice FULLTEXT.
    """

    def __init__(self, id=None, titulo=None, descripcion=None, autor=None,
                 materia_id=None, cohorte_id=None, url_archivo=None,
                 palabras_clave=None, creado_por=None, creado_en=None):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.autor = autor
        self.materia_id = materia_id
        self.cohorte_id = cohorte_id
        self.url_archivo = url_archivo
        self.palabras_clave = palabras_clave
        self.creado_por = creado_por
        self.creado_en = creado_en

    def guardar(self) -> int:
        """Archiva un nuevo proyecto en la BD."""
        consulta = """
            INSERT INTO proyecto_archivado
                (titulo, descripcion, autor, materia_id, cohorte_id, url_archivo, palabras_clave, creado_por)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        parametros = (self.titulo, self.descripcion, self.autor, self.materia_id,
                     self.cohorte_id, self.url_archivo, self.palabras_clave, self.creado_por)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id

    def eliminar(self) -> bool:
        """Elimina el proyecto archivado."""
        consulta = "DELETE FROM proyecto_archivado WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (self.id,))
        return filas_afectadas > 0

    @classmethod
    def obtener_todos(cls, limite: int = 50) -> List['ProyectoArchivado']:
        """Lista los proyectos archivados más recientes."""
        consulta = """
            SELECT p.*, m.nombre as materia_nombre, per.nombre as cohorte_nombre
            FROM proyecto_archivado p
            LEFT JOIN materia m ON p.materia_id = m.id
            LEFT JOIN cohorte per ON p.cohorte_id = per.id
            ORDER BY p.creado_en DESC
            LIMIT %s
        """
        resultados = db.ejecutar_consulta(consulta, (limite,))
        proyectos = []
        for row in resultados:
            p = cls._desde_diccionario(row)
            p.materia_nombre = row.get('materia_nombre')
            p.cohorte_nombre = row.get('cohorte_nombre')
            proyectos.append(p)
        return proyectos

    @classmethod
    def buscar(cls, texto: str = None, materia_id: int = None, cohorte_id: int = None, limite: int = 30) -> List['ProyectoArchivado']:
        """
        Búsqueda con filtros combinables: texto libre (título/descripción/palabras clave),
        materia y cohorte. Lista vacía si no hay coincidencias.
        """
        condiciones = []
        parametros = []

        if texto:
            condiciones.append("(p.titulo LIKE %s OR p.descripcion LIKE %s OR p.palabras_clave LIKE %s)")
            patron = f"%{texto}%"
            parametros += [patron, patron, patron]
        if materia_id:
            condiciones.append("p.materia_id = %s")
            parametros.append(materia_id)
        if cohorte_id:
            condiciones.append("p.cohorte_id = %s")
            parametros.append(cohorte_id)

        where = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""
        consulta = f"""
            SELECT p.*, m.nombre as materia_nombre, per.nombre as cohorte_nombre
            FROM proyecto_archivado p
            LEFT JOIN materia m ON p.materia_id = m.id
            LEFT JOIN cohorte per ON p.cohorte_id = per.id
            {where}
            ORDER BY p.creado_en DESC
            LIMIT %s
        """
        parametros.append(limite)
        resultados = db.ejecutar_consulta(consulta, tuple(parametros))
        proyectos = []
        for row in resultados:
            p = cls._desde_diccionario(row)
            p.materia_nombre = row.get('materia_nombre')
            p.cohorte_nombre = row.get('cohorte_nombre')
            proyectos.append(p)
        return proyectos

@classmethod
def contar_busqueda(cls, texto: str = None, materia_id: int = None, cohorte_id: int = None) -> int:
    """Cuenta resultados con los mismos filtros que buscar(), para paginar."""
    condiciones = []
    parametros = []
    if texto:
        condiciones.append("(titulo LIKE %s OR descripcion LIKE %s OR palabras_clave LIKE %s)")
        patron = f"%{texto}%"
        parametros += [patron, patron, patron]
    if materia_id:
        condiciones.append("materia_id = %s")
        parametros.append(materia_id)
    if cohorte_id:
        condiciones.append("cohorte_id = %s")
        parametros.append(cohorte_id)
    where = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""
    consulta = f"SELECT COUNT(*) as total FROM proyecto_archivado {where}"
    resultado = db.ejecutar_consulta(consulta, tuple(parametros))
    return resultado[0]['total'] if resultado else 0

@classmethod
def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'ProyectoArchivado':
    return cls(
        id=datos.get('id'),
        titulo=datos.get('titulo'),
        descripcion=datos.get('descripcion'),
        autor=datos.get('autor'),
        materia_id=datos.get('materia_id'),
        cohorte_id=datos.get('cohorte_id'),
        url_archivo=datos.get('url_archivo'),
        palabras_clave=datos.get('palabras_clave'),
        creado_por=datos.get('creado_por'),
        creado_en=datos.get('creado_en')
    )

    def __repr__(self):
        return f"<ProyectoArchivado {self.titulo}>"
