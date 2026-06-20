"""
Conexión a Base de Datos MySQL usando mysql-connector-python
Patrón Singleton para evitar conexiones duplicadas
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from pathlib import Path
import os

# Cargar variables de entorno
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class ConexionBaseDatos:
    """
    Clase Singleton para manejar la conexión a MySQL.
    Garantiza una única instancia de conexión en toda la aplicación.
    """
    _instancia = None
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._conexion = None
            cls._instancia._config = {
                'host': os.environ.get("DB_HOST", "localhost"),
                'port': int(os.environ.get("DB_PORT", "3306")),
                'user': os.environ.get("DB_USER", "root"),
                'password': os.environ.get("DB_PASSWORD", ""),
                'database': os.environ.get("DB_NAME", "sistema_tickets_v2"),
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci',
            }
        return cls._instancia
    
    def conectar(self):
        """Establece la conexión a MySQL."""
        try:
            if self._conexion is None or not self._conexion.is_connected():
                self._conexion = mysql.connector.connect(**self._config)
            return self._conexion
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            raise
    
    def desconectar(self):
        """Cierra la conexión a MySQL."""
        if self._conexion and self._conexion.is_connected():
            self._conexion.close()
            self._conexion = None
    
    def ejecutar_consulta(self, consulta, parametros=None):
        """
        Ejecuta una consulta SQL y retorna los resultados.
        
        Args:
            consulta: Consulta SQL con placeholders (%s)
            parametros: Tupla de parámetros para la consulta
            
        Returns:
            Lista de diccionarios con los resultados
        """
        conexion = self.conectar()
        cursor = conexion.cursor(dictionary=True)
        
        try:
            cursor.execute(consulta, parametros)
            resultados = cursor.fetchall()
            conexion.commit()
            return resultados
        except Error as e:
            conexion.rollback()
            print(f"Error en consulta: {e}")
            raise
        finally:
            cursor.close()
    
    def ejecutar_insercion(self, consulta, parametros=None):
        """
        Ejecuta una consulta de inserción y retorna el ID generado.
        
        Args:
            consulta: Consulta SQL INSERT con placeholders (%s)
            parametros: Tupla de parámetros para la consulta
            
        Returns:
            ID del último registro insertado
        """
        conexion = self.conectar()
        cursor = conexion.cursor()
        
        try:
            cursor.execute(consulta, parametros)
            conexion.commit()
            return cursor.lastrowid
        except Error as e:
            conexion.rollback()
            print(f"Error en inserción: {e}")
            raise
        finally:
            cursor.close()
    
    def ejecutar_actualizacion(self, consulta, parametros=None):
        """
        Ejecuta una consulta de actualización/eliminación.
        
        Args:
            consulta: Consulta SQL UPDATE/DELETE con placeholders (%s)
            parametros: Tupla de parámetros para la consulta
            
        Returns:
            Número de filas afectadas
        """
        conexion = self.conectar()
        cursor = conexion.cursor()
        
        try:
            cursor.execute(consulta, parametros)
            conexion.commit()
            return cursor.rowcount
        except Error as e:
            conexion.rollback()
            print(f"Error en actualización: {e}")
            raise
        finally:
            cursor.close()


# Instancia global de conexión (Singleton)
db = ConexionBaseDatos()


# Configuración de Flask
class Config:
    """Configuración base de la aplicación."""
    
    # Rutas
    APP_DIR = Path(__file__).resolve().parent
    TEMPLATES_FOLDER = APP_DIR / "templates"
    STATIC_FOLDER = APP_DIR / "static"
    
    # Sesiones
    SECRET_KEY = os.environ.get("SECRET_KEY", "zoe-desarrollo-cambiar-en-produccion")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora en segundos
    
    # Desarrollo
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"


class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True


class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False


# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}