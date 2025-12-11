# check_database.py
import sqlite3

def check_database_structure():
    """Verificar la estructura actual de la base de datos"""
    conn = sqlite3.connect('rustigone.db')
    cursor = conn.cursor()
    
    print("📊 ESTRUCTURA DE LA BASE DE DATOS:")
    print("=" * 50)
    
    # Ver tablas existentes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n📋 TABLA: {table_name}")
        print("-" * 30)
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for column in columns:
            col_id, col_name, col_type, not_null, default_val, pk = column
            print(f"  {col_name} ({col_type}) {'PK' if pk else ''} {'NOT NULL' if not_null else ''} {f'DEFAULT {default_val}' if default_val else ''}")
    
    conn.close()

if __name__ == "__main__":
    check_database_structure()