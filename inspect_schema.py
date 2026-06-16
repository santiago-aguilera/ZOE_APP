#!/usr/bin/env python3
"""
Script para inspeccionar el esquema existente de la BD ZOE
"""

import sys
import os
from pathlib import Path
import pymysql

# Variables de conexión
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "zoe"

def inspect_database():
    """Inspecciona el esquema de la BD ZOE."""
    try:
        # Conectar a MySQL
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        
        cursor = connection.cursor()
        
        print("=" * 70)
        print("📊 ESQUEMA DE LA BD ZOE")
        print("=" * 70)
        
        # Obtener lista de tablas
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"\n📋 TABLAS ({len(tables)}):")
        for table_name in tables:
            table = table_name[0]
            print(f"\n  🔹 {table.upper()}")
            
            # Obtener estructura de la tabla
            cursor.execute(f"DESCRIBE `{table}`")
            columns = cursor.fetchall()
            
            for col in columns:
                name, type_, nullable, key, default, extra = col
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                key_str = f"[{key}]" if key else ""
                print(f"     - {name:<20} {type_:<15} {nullable_str:<10} {key_str} {extra}")
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"❌ ERROR al conectar: {str(e)}")
        print("\n🔍 Soluciona:")
        print("  1. Abre XAMPP y activa MySQL")
        print("  2. Ve a http://localhost/phpmyadmin")
        print("  3. Crea la BD 'zoe' si no existe")
        return False
    
    return True


if __name__ == "__main__":
    success = inspect_database()
    sys.exit(0 if success else 1)
