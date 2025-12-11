# migrate_database.py
from database.database_manager import DatabaseManager

def migrate_database():
    """Migrar la base de datos a la nueva versión"""
    print("🔧 Migrando base de datos...")
    
    db = DatabaseManager()
    
    # Esto creará las tablas si no existen y agregará las columnas faltantes
    db.init_database()
    
    print("✅ Migración completada exitosamente")

if __name__ == "__main__":
    migrate_database()