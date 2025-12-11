# force_migrate.py
import sqlite3
import os
from database.database_manager import DatabaseManager

def force_migrate():
    """Migración forzada de la base de datos"""
    print("🔧 Ejecutando migración forzada...")
    
    # Verificar si la base de datos existe
    if not os.path.exists('rustigone.db'):
        print("❌ No se encontró la base de datos")
        return
    
    try:
        # Conectar directamente a SQLite
        conn = sqlite3.connect('rustigone.db')
        cursor = conn.cursor()
        
        # Verificar estructura actual
        cursor.execute("PRAGMA table_info(ventas)")
        columns = [column[1] for column in cursor.fetchall()]
        print("📋 Columnas actuales en 'ventas':", columns)
        
        # Agregar columnas faltantes si no existen
        if 'monto_recibido' not in columns:
            print("➕ Agregando columna 'monto_recibido'...")
            cursor.execute('ALTER TABLE ventas ADD COLUMN monto_recibido REAL DEFAULT 0')
        
        if 'vuelto' not in columns:
            print("➕ Agregando columna 'vuelto'...")
            cursor.execute('ALTER TABLE ventas ADD COLUMN vuelto REAL DEFAULT 0')
        
        conn.commit()
        conn.close()
        
        print("✅ Migración forzada completada exitosamente")
        
        # Verificar cambios
        check_migration()
        
    except Exception as e:
        print(f"❌ Error en migración forzada: {e}")

def check_migration():
    """Verificar que la migración fue exitosa"""
    conn = sqlite3.connect('rustigone.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(ventas)")
    columns = cursor.fetchall()
    
    print("\n📊 ESTRUCTURA ACTUALIZADA DE 'ventas':")
    print("-" * 40)
    for column in columns:
        col_id, col_name, col_type, not_null, default_val, pk = column
        print(f"  {col_name} ({col_type}) {'PK' if pk else ''}")
    
    # Verificar específicamente las columnas nuevas
    column_names = [col[1] for col in columns]
    if 'monto_recibido' in column_names and 'vuelto' in column_names:
        print("\n🎉 ¡Migración exitosa! Las columnas están presentes.")
    else:
        print("\n⚠️  Algunas columnas aún faltan.")
    
    conn.close()

if __name__ == "__main__":
    force_migrate()