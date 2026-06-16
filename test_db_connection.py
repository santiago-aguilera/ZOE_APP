#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión a MySQL desde Flask.
Ejecutar desde la raíz del proyecto: python test_db_connection.py
"""

import sys
import os
from pathlib import Path

# Agregar al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Importar Flask y configuración
from app.main import app, db, init_db

def test_connection():
    """Prueba la conexión a la BD."""
    print("=" * 70)
    print("🔧 PRUEBA DE CONEXIÓN A BD ZOE")
    print("=" * 70)
    
    # Mostrar configuración
    print("\n📋 CONFIGURACIÓN:")
    print(f"  Host: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1].split('/')[0]}")
    print(f"  Base de Datos: zoe")
    print(f"  URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"  Debug: {app.config['DEBUG']}")
    
    # Intentar inicializar BD
    print("\n⏳ Inicializando base de datos...")
    try:
        with app.app_context():
            init_db()
            print("✅ Base de datos inicializada correctamente")
            
            # Contar registros
            from app.models import Usuario, Materia, Grupo, Tarea
            usuarios = Usuario.query.count()
            materias = Materia.query.count()
            grupos = Grupo.query.count()
            tareas = Tarea.query.count()
            
            print("\n📊 REGISTROS EN LA BD:")
            print(f"  Usuarios: {usuarios}")
            print(f"  Materias: {materias}")
            print(f"  Grupos: {grupos}")
            print(f"  Tareas: {tareas}")
            
            # Mostrar usuarios
            print("\n👥 USUARIOS EN LA BD:")
            for user in Usuario.query.all():
                print(f"  - {user.nombre} ({user.correo}) - {user.rol}")
            
            print("\n✅ ¡CONEXIÓN EXITOSA!")
            print("\n🚀 Para iniciar el servidor:")
            print("   cd app")
            print("   python main.py")
            print("\nO desde la raíz:")
            print("   python -m app.main")
            
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\n🔍 SOLUCIÓN:")
        print("  1. Asegúrate que XAMPP esté corriendo (MySQL debe estar activo)")
        print("  2. Verifica que la BD 'zoe' exista en phpMyAdmin")
        print("  3. Comprueba las credenciales en el archivo .env")
        print("  4. Revisa los logs de MySQL en XAMPP")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
