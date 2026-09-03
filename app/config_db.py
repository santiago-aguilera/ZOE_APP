"""
Configuración General de la Aplicación y Conexión Singleton a MySQL
Adaptado para ZOE_APP con soporte para MariaDB/MySQL local.
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from pathlib import Path
import os

# Intentar cargar variables de entorno (si el archivo .env existe)
RUTA_BASE = Path(__file__).resolve().parent
RUTA_PROYECTO = RUTA_BASE.parent
load_dotenv(RUTA_PROYECTO / ".env")


class ConexionBaseDatos:
    """
    Clase Singleton para manejar la conexión a MySQL/MariaDB.
    Garantiza una única instancia de conexión activa en toda la aplicación.
    """
    _instancia = None
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._conexion = None
            
            # Configuración extraída directamente de tu phpMyAdmin
            cls._instancia._config = {
                'host': os.environ.get("DB_HOST", "127.0.0.1"),
                'port': int(os.environ.get("DB_PORT", "3306")),
                'user': os.environ.get("DB_USER", "root"),
                'password': os.environ.get("DB_PASSWORD", ""),
                'database': os.environ.get("DB_NAME", "zoe"),  # Base de datos 'zoe' de la imagen
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci',
            }
        return cls._instancia
    
    def conectar(self):
        """Establece y retorna la conexión activa a MySQL."""
        try:
            if self._conexion is None or not self._conexion.is_connected():
                self._conexion = mysql.connector.connect(**self._config)
            return self._conexion
        except Error as e:
            print(f"\n[ERROR] No se pudo conectar a MySQL: {e}")
            raise
    
    def desconectar(self):
        """Cierra la conexión de forma segura."""
        if self._conexion and self._conexion.is_connected():
            self._conexion.close()
            self._conexion = None
    
    def ejecutar_consulta(self, consulta, parametros=None):
        """Ejecuta consultas de lectura (SELECT) y retorna una lista de diccionarios."""
        conexion = self.conectar()
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute(consulta, parametros)
            resultados = cursor.fetchall()
            return resultados
        except Error as e:
            print(f"[SQL ERROR] Error en SELECT: {e}")
            raise
        finally:
            cursor.close()
    
    def ejecutar_insercion(self, consulta, parametros=None):
        """Ejecuta inserciones (INSERT) y retorna el ID del registro creado."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute(consulta, parametros)
            conexion.commit()
            return cursor.lastrowid
        except Error as e:
            conexion.rollback()
            print(f"[SQL ERROR] Error en INSERT: {e}")
            raise
        finally:
            cursor.close()
    
    def ejecutar_actualizacion(self, consulta, parametros=None):
        """Ejecuta actualizaciones o eliminaciones (UPDATE/DELETE) y retorna filas afectadas."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute(consulta, parametros)
            conexion.commit()
            return cursor.rowcount
        except Error as e:
            conexion.rollback()
            print(f"[SQL ERROR] Error en UPDATE/DELETE: {e}")
            raise
        finally:
            cursor.close()


# Instancia global del Singleton para usar en los Blueprints/Modelos
db = ConexionBaseDatos()


# ==========================================
# CONFIGURACIÓN DE ENTORNO PARA FLASK
# ==========================================

class Config:
    """Configuración base de la aplicación."""
    APP_DIR = RUTA_BASE
    TEMPLATES_FOLDER = APP_DIR / "templates"
    STATIC_FOLDER = APP_DIR / "static"
    
    SECRET_KEY = os.environ.get("SECRET_KEY", "zoe-desarrollo-cambiar-en-produccion")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"


class DevelopmentConfig(Config):
    """Configuración para desarrollo local."""
    DEBUG = True


class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False


# Diccionario para levantar la app según el entorno en app/__init__.py
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


# ==========================================
# SCRIPT DE PRUEBA DE CONEXIÓN DIRECTA
# ==========================================
if __name__ == "__main__":
    import traceback
    print("=== PROBANDO CONEXIÓN DIRECTA A TU MARIADB (ZOE) ===")
    try:
        con = db.conectar()
        if con.is_connected():
            print("\n¡CONEXIÓN EXITOSA!")
            print(f"Conectado al Host: {db._config['host']}")
            print(f"Base de datos activa: {db._config['database']}\n")
            
            # Intentar listar tus tablas reales para confirmar
            tablas = db.ejecutar_consulta("SHOW TABLES;")
            print("Tablas encontradas en 'zoe':")
            for t in tablas:
                print(f" - {list(t.values())[0]}")
                
            db.desconectar()
    except Exception as error:
        print("\n[FALLO] No se pudo establecer la comunicación.")
        print(f"Tipo de Error: {type(error).__name__}")
        print(f"Mensaje Técnico: {error}")
        print("\nRastreo del error:")
        traceback.print_exc()
