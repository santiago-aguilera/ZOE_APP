"""
Paquete modelo — modelos SQLAlchemy del negocio ZOE.
El sufijo _db indica que son modelos de base de datos.
"""
from .db import db

from .usuario_db import Usuario
from .estudiante_db import Estudiante
from .profesor_db import Profesor
from .coordinador_db import Coordinador
from .materia_db import Materia, ProfesorMateria, EstudianteMateria
from .grupo_db import Grupo, EstudianteGrupo
from .tarea_db import Tarea
from .entrega_db import Entrega
from .comunicado_db import Comunicado
from .mensaje_db import Mensaje
from .cronograma_db import Cronograma
from .recurso_db import Recurso
from .periodo_db import PeriodoAcademico

__all__ = [
    "db",
    "Usuario", "Estudiante", "Profesor", "Coordinador",
    "Materia", "ProfesorMateria", "EstudianteMateria",
    "Grupo", "EstudianteGrupo",
    "Tarea", "Entrega",
    "Comunicado", "Mensaje", "Cronograma", "Recurso",
    "PeriodoAcademico",
]
