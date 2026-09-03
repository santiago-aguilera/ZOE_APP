"""
Diagnóstico de login para ZOE.

Corré esto en la carpeta del proyecto (donde está run.py) con:
    python diagnostico_login.py

Te va a decir EXACTAMENTE por qué el login está fallando, sin adivinar.
"""

import sys
sys.path.insert(0, '.')

print("=" * 70)
print("PASO 1: ¿Se puede conectar a la base de datos?")
print("=" * 70)
try:
    from app.config_db import db, config
    print(f"  Host: {config.get('host')}")
    print(f"  Puerto: {config.get('port')}")
    print(f"  Base de datos: {config.get('database')}")
    print(f"  Usuario BD: {config.get('user')}")
    resultado = db.ejecutar_consulta("SELECT DATABASE() as bd_actual")
    print(f"  ✅ Conexión OK. Base activa: {resultado[0]['bd_actual']}")
except Exception as e:
    print(f"  ❌ NO SE PUDO CONECTAR: {e}")
    print("\n  → Revisá tu app/.env (o las variables de entorno DB_HOST, DB_USER,")
    print("    DB_PASSWORD, DB_NAME) y que MySQL/MariaDB esté corriendo.")
    sys.exit(1)

print()
print("=" * 70)
print("PASO 2: ¿Existe la tabla 'usuario' y tiene datos?")
print("=" * 70)
try:
    total = db.ejecutar_consulta("SELECT COUNT(*) as total FROM usuario")
    print(f"  ✅ Tabla 'usuario' existe, con {total[0]['total']} registros.")
    if total[0]['total'] == 0:
        print("\n  → La tabla está VACÍA. Tenés que importar app/static/sql/DB.sql")
        print("    completo (pestaña SQL de phpMyAdmin, sin seleccionar ninguna")
        print("    base antes), no solo crear la base vacía.")
        sys.exit(1)
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    print("\n  → Tu base de datos no tiene el esquema actual. Reimportá TODO")
    print("    app/static/sql/DB.sql desde cero (el script hace DROP DATABASE")
    print("    + CREATE DATABASE, así que es seguro volver a correrlo).")
    sys.exit(1)

print()
print("=" * 70)
print("PASO 3: ¿Existe el usuario admin@zoe.com?")
print("=" * 70)
from app.models import Usuario
correo_a_probar = input("Correo a probar [admin@zoe.com]: ").strip() or "admin@zoe.com"
usuario = Usuario.obtener_por_correo(correo_a_probar.lower())

if not usuario:
    print(f"  ❌ NO existe ningún usuario con correo '{correo_a_probar}'.")
    print("\n  Usuarios que SÍ existen en tu base de datos:")
    todos = Usuario.obtener_todos()
    for u in todos[:15]:
        print(f"    - {u.correo}  (rol: {u.rol}, activo: {u.activo})")
    sys.exit(1)

print(f"  ✅ Usuario encontrado: {usuario.nombre} (rol: {usuario.rol})")
print(f"     Activo: {usuario.activo}")
print(f"     Hash guardado: {usuario.contrasena_hash[:40]}...")

if not usuario.activo:
    print("\n  → El usuario existe pero está INACTIVO (activo=0). El login lo")
    print("    rechaza aunque la contraseña sea correcta. Activalo desde Usuarios.")
    sys.exit(1)

print()
print("=" * 70)
print("PASO 4: ¿La contraseña es correcta?")
print("=" * 70)
from werkzeug.security import check_password_hash
import getpass
password_a_probar = getpass.getpass("Contraseña a probar (no se muestra en pantalla): ")

try:
    ok = check_password_hash(usuario.contrasena_hash, password_a_probar)
except Exception as e:
    print(f"  ❌ ERROR al verificar el hash: {e}")
    print("\n  → El hash guardado en la base de datos está corrupto o usa un")
    print("    algoritmo (ej. scrypt) que tu versión de Werkzeug no soporta.")
    print("    Revisá 'pip show werkzeug' — necesitás 2.0 o más nueva.")
    sys.exit(1)

if ok:
    print("  ✅ ¡La contraseña es CORRECTA! El login debería funcionar.")
    print("     Si igual falla en el navegador, puede ser un problema de")
    print("     cookies/sesión — probá en una ventana de incógnito.")
else:
    print("  ❌ La contraseña NO coincide con el hash guardado.")
    print("\n  → Si nunca cambiaste la contraseña del admin de DB.sql, la")
    print("    correcta es: admin123")
    print("    Si la olvidaste o la cambiaste, generá un hash nuevo así:")
    print()
    print("    python3 -c \"from werkzeug.security import generate_password_hash; print(generate_password_hash('TU_NUEVA_CONTRASENA'))\"")
    print()
    print("    Y actualizala en la base con:")
    print(f"    UPDATE usuario SET contrasena_hash='<el_hash_generado>' WHERE correo='{correo_a_probar}';")
