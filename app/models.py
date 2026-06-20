"""
Modelos POO para ZOE.
Clases que representan las tablas de la base de datos MySQL.
Cada clase tiene atributos equivalentes a las columnas y métodos CRUD.
"""

from app.config_db import db
from datetime import datetime
from typing import List, Dict, Optional, Any


class Usuario:
    """Modelo de Usuario - Representa la tabla 'usuario'."""
    
    def __init__(self, id=None, nombre=None, correo=None, contrasena_hash=None, 
                 rol=None, periodo_id=None, activo=True):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.contrasena_hash = contrasena_hash
        self.rol = rol
        self.periodo_id = periodo_id
        self.activo = activo
    
    def guardar(self) -> int:
        """Crea un nuevo usuario en la BD. Retorna el ID generado."""
        consulta = """
            INSERT INTO usuario (nombre, correo, contrasena_hash, rol, periodo_id, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        parametros = (self.nombre, self.correo, self.contrasena_hash, 
                     self.rol, self.periodo_id, self.activo)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id
    
    def actualizar(self) -> bool:
        """Actualiza el usuario en la BD."""
        consulta = """
            UPDATE usuario 
            SET nombre=%s, correo=%s, rol=%s, activo=%s
            WHERE id=%s
        """
        parametros = (self.nombre, self.correo, self.rol, self.activo, self.id)
        filas_afectadas = db.ejecutar_actualizacion(consulta, parametros)
        return filas_afectadas > 0
    
    def eliminar(self) -> bool:
        """Elimina el usuario de la BD."""
        consulta = "DELETE FROM usuario WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (self.id,))
        return filas_afectadas > 0
    
    @classmethod
    def obtener_por_id(cls, id: int) -> Optional['Usuario']:
        """Obtiene un usuario por su ID."""
        consulta = "SELECT * FROM usuario WHERE id=%s"
        resultados = db.ejecutar_consulta(consulta, (id,))
        if resultados:
            return cls._desde_diccionario(resultados[0])
        return None
    
    @classmethod
    def obtener_por_correo(cls, correo: str) -> Optional['Usuario']:
        """Obtiene un usuario por su correo electrónico."""
        consulta = "SELECT * FROM usuario WHERE correo=%s"
        resultados = db.ejecutar_consulta(consulta, (correo,))
        if resultados:
            return cls._desde_diccionario(resultados[0])
        return None
    
    @classmethod
    def obtener_todos(cls) -> List['Usuario']:
        """Obtiene todos los usuarios."""
        consulta = "SELECT * FROM usuario"
        resultados = db.ejecutar_consulta(consulta)
        return [cls._desde_diccionario(row) for row in resultados]
    
    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Usuario':
        """Crea una instancia de Usuario desde un diccionario."""
        return cls(
            id=datos.get('id'),
            nombre=datos.get('nombre'),
            correo=datos.get('correo'),
            contrasena_hash=datos.get('contrasena_hash'),
            rol=datos.get('rol'),
            periodo_id=datos.get('periodo_id'),
            activo=datos.get('activo', True)
        )
    
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la instancia a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'correo': self.correo,
            'rol': self.rol,
            'periodo_id': self.periodo_id,
            'activo': self.activo
        }
    
    def __repr__(self):
        return f"<Usuario {self.nombre} ({self.rol})>"


class Materia:
    """Modelo de Materia - Representa la tabla 'materia'."""
    
    def __init__(self, id=None, nombre=None, descripcion=None, 
                 periodo_id=None, creado_en=None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.periodo_id = periodo_id
        self.creado_en = creado_en
    
    def guardar(self) -> int:
        """Crea una nueva materia en la BD."""
        consulta = """
            INSERT INTO materia (nombre, descripcion, periodo_id)
            VALUES (%s, %s, %s)
        """
        parametros = (self.nombre, self.descripcion, self.periodo_id)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id
    
    def actualizar(self) -> bool:
        """Actualiza la materia en la BD."""
        consulta = """
            UPDATE materia 
            SET nombre=%s, descripcion=%s, periodo_id=%s
            WHERE id=%s
        """
        parametros = (self.nombre, self.descripcion, self.periodo_id, self.id)
        filas_afectadas = db.ejecutar_actualizacion(consulta, parametros)
        return filas_afectadas > 0
    
    def eliminar(self) -> bool:
        """Elimina la materia de la BD."""
        consulta = "DELETE FROM materia WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (self.id,))
        return filas_afectadas > 0
    
    @classmethod
    def obtener_por_id(cls, id: int) -> Optional['Materia']:
        """Obtiene una materia por su ID."""
        consulta = "SELECT * FROM materia WHERE id=%s"
        resultados = db.ejecutar_consulta(consulta, (id,))
        if resultados:
            return cls._desde_diccionario(resultados[0])
        return None
    
    @classmethod
    def obtener_todas(cls) -> List['Materia']:
        """Obtiene todas las materias."""
        consulta = "SELECT * FROM materia"
        resultados = db.ejecutar_consulta(consulta)
        return [cls._desde_diccionario(row) for row in resultados]
    
    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Materia':
        """Crea una instancia de Materia desde un diccionario."""
        return cls(
            id=datos.get('id'),
            nombre=datos.get('nombre'),
            descripcion=datos.get('descripcion'),
            periodo_id=datos.get('periodo_id'),
            creado_en=datos.get('creado_en')
        )
    
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la instancia a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'periodo_id': self.periodo_id
        }
    
    def __repr__(self):
        return f"<Materia {self.nombre}>"


class Tarea:
    """Modelo de Tarea - Representa la tabla 'tarea'."""
    
    def __init__(self, id=None, titulo=None, instrucciones=None, 
                 fecha_limite=None, materia_id=None, creado_por=None, creado_en=None):
        self.id = id
        self.titulo = titulo
        self.instrucciones = instrucciones
        self.fecha_limite = fecha_limite
        self.materia_id = materia_id
        self.creado_por = creado_por
        self.creado_en = creado_en
    
    def guardar(self) -> int:
        """Crea una nueva tarea en la BD."""
        consulta = """
            INSERT INTO tarea (titulo, instrucciones, fecha_limite, materia_id, creado_por)
            VALUES (%s, %s, %s, %s, %s)
        """
        parametros = (self.titulo, self.instrucciones, self.fecha_limite,
                     self.materia_id, self.creado_por)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id
    
    def actualizar(self) -> bool:
        """Actualiza la tarea en la BD."""
        consulta = """
            UPDATE tarea 
            SET titulo=%s, instrucciones=%s, fecha_limite=%s, materia_id=%s
            WHERE id=%s
        """
        parametros = (self.titulo, self.instrucciones, self.fecha_limite,
                     self.materia_id, self.id)
        filas_afectadas = db.ejecutar_actualizacion(consulta, parametros)
        return filas_afectadas > 0
    
    def eliminar(self) -> bool:
        """Elimina la tarea de la BD."""
        consulta = "DELETE FROM tarea WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (self.id,))
        return filas_afectadas > 0
    
    @classmethod
    def obtener_por_id(cls, id: int) -> Optional['Tarea']:
        """Obtiene una tarea por su ID."""
        consulta = "SELECT * FROM tarea WHERE id=%s"
        resultados = db.ejecutar_consulta(consulta, (id,))
        if resultados:
            return cls._desde_diccionario(resultados[0])
        return None
    
    @classmethod
    def obtener_todas(cls) -> List['Tarea']:
        """Obtiene todas las tareas."""
        consulta = """
            SELECT t.*, m.nombre as materia_nombre, u.nombre as creador_nombre
            FROM tarea t
            LEFT JOIN materia m ON t.materia_id = m.id
            LEFT JOIN usuario u ON t.creado_por = u.id
        """
        resultados = db.ejecutar_consulta(consulta)
        tareas = []
        for row in resultados:
            tarea = cls._desde_diccionario(row)
            tarea.materia_nombre = row.get('materia_nombre')
            tarea.creador_nombre = row.get('creador_nombre')
            tareas.append(tarea)
        return tareas
    
    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Tarea':
        """Crea una instancia de Tarea desde un diccionario."""
        return cls(
            id=datos.get('id'),
            titulo=datos.get('titulo'),
            instrucciones=datos.get('instrucciones'),
            fecha_limite=datos.get('fecha_limite'),
            materia_id=datos.get('materia_id'),
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
            'materia_id': self.materia_id,
            'creador': self.creador_nombre
        }
    
    def __repr__(self):
        return f"<Tarea {self.titulo}>"


class Grupo:
    """Modelo de Grupo - Representa la tabla 'grupo'."""
    
    def __init__(self, id=None, nombre=None, descripcion=None,
                 materia_id=None, creado_por=None, creado_en=None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.materia_id = materia_id
        self.creado_por = creado_por
        self.creado_en = creado_en
    
    def guardar(self) -> int:
        """Crea un nuevo grupo en la BD."""
        consulta = """
            INSERT INTO grupo (nombre, descripcion, materia_id, creado_por)
            VALUES (%s, %s, %s, %s)
        """
        parametros = (self.nombre, self.descripcion, self.materia_id, self.creado_por)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id
    
    def actualizar(self) -> bool:
        """Actualiza el grupo en la BD."""
        consulta = """
            UPDATE grupo 
            SET nombre=%s, descripcion=%s, materia_id=%s
            WHERE id=%s
        """
        parametros = (self.nombre, self.descripcion, self.materia_id, self.id)
        filas_afectadas = db.ejecutar_actualizacion(consulta, parametros)
        return filas_afectadas > 0
    
    def eliminar(self) -> bool:
        """Elimina el grupo de la BD."""
        consulta = "DELETE FROM grupo WHERE id=%s"
        filas_afectadas = db.ejecutar_actualizacion(consulta, (self.id,))
        return filas_afectadas > 0
    
    @classmethod
    def obtener_por_id(cls, id: int) -> Optional['Grupo']:
        """Obtiene un grupo por su ID."""
        consulta = "SELECT * FROM grupo WHERE id=%s"
        resultados = db.ejecutar_consulta(consulta, (id,))
        if resultados:
            return cls._desde_diccionario(resultados[0])
        return None
    
    @classmethod
    def obtener_todos(cls) -> List['Grupo']:
        """Obtiene todos los grupos."""
        consulta = """
            SELECT g.*, m.nombre as materia_nombre, u.nombre as profesor_nombre
            FROM grupo g
            LEFT JOIN materia m ON g.materia_id = m.id
            LEFT JOIN usuario u ON g.creado_por = u.id
        """
        resultados = db.ejecutar_consulta(consulta)
        grupos = []
        for row in resultados:
            grupo = cls._desde_diccionario(row)
            grupo.materia_nombre = row.get('materia_nombre')
            grupo.profesor_nombre = row.get('profesor_nombre')
            grupos.append(grupo)
        return grupos
    
    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'Grupo':
        """Crea una instancia de Grupo desde un diccionario."""
        return cls(
            id=datos.get('id'),
            nombre=datos.get('nombre'),
            descripcion=datos.get('descripcion'),
            materia_id=datos.get('materia_id'),
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


class PeriodoAcademico:
    """Modelo de Período Académico - Representa la tabla 'periodo_academico'."""
    
    def __init__(self, id=None, nombre=None, fecha_inicio=None, 
                 fecha_fin=None, activo=True):
        self.id = id
        self.nombre = nombre
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.activo = activo
    
    def guardar(self) -> int:
        """Crea un nuevo período en la BD."""
        consulta = """
            INSERT INTO periodo_academico (nombre, fecha_inicio, fecha_fin, activo)
            VALUES (%s, %s, %s, %s)
        """
        parametros = (self.nombre, self.fecha_inicio, self.fecha_fin, self.activo)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id
    
    @classmethod
    def obtener_todos(cls) -> List['PeriodoAcademico']:
        """Obtiene todos los períodos."""
        consulta = "SELECT * FROM periodo_academico"
        resultados = db.ejecutar_consulta(consulta)
        return [cls._desde_diccionario(row) for row in resultados]
    
    @classmethod
    def _desde_diccionario(cls, datos: Dict[str, Any]) -> 'PeriodoAcademico':
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
        return f"<PeriodoAcademico {self.nombre}>"


class Recurso:
    """Modelo de Recurso - Representa la tabla 'recurso'."""
    
    def __init__(self, id=None, titulo=None, descripcion=None,
                 url_archivo=None, tipo=None, materia_id=None,
                 creado_por=None, creado_en=None):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.url_archivo = url_archivo
        self.tipo = tipo
        self.materia_id = materia_id
        self.creado_por = creado_por
        self.creado_en = creado_en
    
    def guardar(self) -> int:
        """Crea un nuevo recurso en la BD."""
        consulta = """
            INSERT INTO recurso (titulo, descripcion, url_archivo, tipo, materia_id, creado_por)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        parametros = (self.titulo, self.descripcion, self.url_archivo,
                     self.tipo, self.materia_id, self.creado_por)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id
    
    @classmethod
    def obtener_todos(cls) -> List['Recurso']:
        """Obtiene todos los recursos."""
        consulta = """
            SELECT r.*, m.nombre as materia_nombre, u.nombre as autor_nombre
            FROM recurso r
            LEFT JOIN materia m ON r.materia_id = m.id
            LEFT JOIN usuario u ON r.creado_por = u.id
        """
        resultados = db.ejecutar_consulta(consulta)
        return [cls._desde_diccionario(row) for row in resultados]
    
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
                 fecha_evento=None, tipo=None, materia_id=None,
                 creado_por=None, creado_en=None):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_evento = fecha_evento
        self.tipo = tipo
        self.materia_id = materia_id
        self.creado_por = creado_por
        self.creado_en = creado_en
    
    def guardar(self) -> int:
        """Crea un nuevo evento en la BD."""
        consulta = """
            INSERT INTO cronograma (titulo, descripcion, fecha_evento, tipo, materia_id, creado_por)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        parametros = (self.titulo, self.descripcion, self.fecha_evento,
                     self.tipo, self.materia_id, self.creado_por)
        self.id = db.ejecutar_insercion(consulta, parametros)
        return self.id
    
    @classmethod
    def obtener_todos(cls) -> List['Cronograma']:
        """Obtiene todos los eventos del cronograma."""
        consulta = """
            SELECT c.*, m.nombre as materia_nombre
            FROM cronograma c
            LEFT JOIN materia m ON c.materia_id = m.id
            ORDER BY c.fecha_evento ASC
        """
        resultados = db.ejecutar_consulta(consulta)
        eventos = []
        for row in resultados:
            evento = cls._desde_diccionario(row)
            evento.materia_nombre = row.get('materia_nombre')
            eventos.append(evento)
        return eventos
    
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
            creado_por=datos.get('creado_por'),
            creado_en=datos.get('creado_en')
        )
    
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la instancia a diccionario."""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'fecha': self.fecha_evento,
            'materia': self.materia_nombre if hasattr(self, 'materia_nombre') else 'Sin asignar'
        }
    
    def __repr__(self):
        return f"<Cronograma {self.titulo}>"


class Mensaje:
    """Modelo de Mensaje - Representa la tabla 'mensaje'."""
    
    def __init__(self, id=None, remitente_id=None, destinatario_id=None,
                 asunto=None, cuerpo=None, enviado_en=None, leido=False,
                 eliminado_remitente=False, eliminado_destinatario=False):
        self.id = id
        self.remitente_id = remitente_id
        self.destinatario_id = destinatario_id
        self.asunto = asunto
        self.cuerpo = cuerpo
        self.enviado_en = enviado_en
        self.leido = leido
        self.eliminado_remitente = eliminado_remitente
        self.eliminado_destinatario = eliminado_destinatario
    
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
    def obtener_recibidos(cls, usuario_id: int) -> List['Mensaje']:
        """Obtiene mensajes recibidos por un usuario."""
        consulta = """
            SELECT m.*, u.nombre as remitente_nombre
            FROM mensaje m
            LEFT JOIN usuario u ON m.remitente_id = u.id
            WHERE m.destinatario_id=%s AND m.eliminado_destinatario=0
            ORDER BY m.enviado_en DESC
        """
        resultados = db.ejecutar_consulta(consulta, (usuario_id,))
        mensajes = []
        for row in resultados:
            msg = cls._desde_diccionario(row)
            msg.remitente_nombre = row.get('remitente_nombre')
            mensajes.append(msg)
        return mensajes
    
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
            eliminado_destinatario=datos.get('eliminado_destinatario', False)
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