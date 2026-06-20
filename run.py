"""
Punto de entrada principal de la aplicación ZOE.
Ejecutar con: python run.py
"""

from app import create_app

app = create_app("development")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Iniciando ZOE - Plataforma de Gestión Documental")
    print("=" * 60)
    print("📍 URL: http://localhost:5000")
    print("🔧 Modo: Desarrollo")
    print("💾 Base de datos: MySQL (zoe)")
    print("=" * 60)
    
    app.run(host="localhost", port=5000, debug=True)