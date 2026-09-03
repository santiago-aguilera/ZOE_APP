"""
Blueprints de la aplicación ZOE.
Cada blueprint maneja un módulo específico de la aplicación.
"""

from flask import Blueprint

# Definir blueprints
auth_bp = Blueprint('auth', __name__)
dashboard_bp = Blueprint('dashboard', __name__)
usuarios_bp = Blueprint('usuarios', __name__)
tareas_bp = Blueprint('tareas', __name__)
materias_bp = Blueprint('materias', __name__)
grupos_bp = Blueprint('grupos', __name__)
cursos_bp = Blueprint('cursos', __name__)
especialidades_bp = Blueprint('especialidades', __name__)
comunicados_bp = Blueprint('comunicados', __name__)
recursos_bp = Blueprint('recursos', __name__)
cronograma_bp = Blueprint('cronograma', __name__)
mensajeria_bp = Blueprint('mensajeria', __name__)
reportes_bp = Blueprint('reportes', __name__)
configuracion_bp = Blueprint('configuracion', __name__)
valoraciones_bp = Blueprint('valoraciones', __name__)
parametrizacion_bp = Blueprint('parametrizacion', __name__)
matricula_bp = Blueprint('matricula', __name__)
archivo_bp = Blueprint('archivo', __name__)

# Importar rutas de cada blueprint para registrar los endpoints
from app.blueprints.auth import routes as auth_routes
from app.blueprints.dashboard import routes as dashboard_routes
from app.blueprints.usuarios import routes as usuarios_routes
from app.blueprints.tareas import routes as tareas_routes
from app.blueprints.materias import routes as materias_routes
from app.blueprints.grupos import routes as grupos_routes
from app.blueprints.cursos import routes as cursos_routes
from app.blueprints.especialidades import routes as especialidades_routes
from app.blueprints.comunicados import routes as comunicados_routes
from app.blueprints.recursos import routes as recursos_routes
from app.blueprints.cronograma import routes as cronograma_routes
from app.blueprints.mensajeria import routes as mensajeria_routes
from app.blueprints.reportes import routes as reportes_routes
from app.blueprints.configuracion import routes as configuracion_routes
from app.blueprints.valoraciones import routes as valoraciones_routes
from app.blueprints.parametrizacion import routes as parametrizacion_routes
from app.blueprints.matricula import routes as matricula_routes
from app.blueprints.archivo import routes as archivo_routes

# Lista de todos los blueprints para registro
blueprints = [
    (auth_bp, '/auth'),
    (dashboard_bp, '/'),
    (usuarios_bp, '/usuarios'),
    (tareas_bp, '/tareas'),
    (materias_bp, '/materias'),
    (grupos_bp, '/grupos'),
    (cursos_bp, '/cursos'),
    (especialidades_bp, '/especialidades'),
    (comunicados_bp, '/comunicados'),
    (recursos_bp, '/recursos'),
    (cronograma_bp, '/cronograma'),
    (mensajeria_bp, '/mensajeria'),
    (reportes_bp, '/reportes'),
    (configuracion_bp, '/configuracion'),
    (valoraciones_bp, '/valoraciones'),
    (parametrizacion_bp, '/parametrizacion'),
    (matricula_bp, '/matricula'),
    (archivo_bp, '/archivo'),
]