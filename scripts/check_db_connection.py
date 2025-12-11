#!/usr/bin/env python3
"""
Script para verificar la conexión a la base de datos y estado general del sistema.
"""
import sys
import os

# Agregar src al path (la carpeta src donde están los módulos)
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(script_dir), 'src')
sys.path.insert(0, src_dir)

def check_database_connection():
    """Verificar conexión a la base de datos"""
    print("=" * 60)
    print("🔍 VERIFICANDO CONEXIÓN A BASE DE DATOS")
    print("=" * 60)
    
    try:
        from models.database_manager import DatabaseManager
        
        # Intentar conectar
        db = DatabaseManager()
        print("✓ Instancia DatabaseManager creada")
        
        # Inicializar BD
        db.init_database()
        print("✓ Base de datos inicializada/conectada")
        
        # Obtener conexión
        conn = db.connect()
        
        # Verificar tablas
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n✓ Tablas encontradas ({len(tables)}):")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - {table[0]}: {count} registros")
        
        conn.close()
        print("\n✅ Conexión a BD: OK")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en conexión a BD: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_dependencies():
    """Verificar que todas las dependencias estén instaladas"""
    print("\n" + "=" * 60)
    print("📦 VERIFICANDO DEPENDENCIAS")
    print("=" * 60)
    
    dependencies = {
        'customtkinter': 'GUI Framework',
        'PIL': 'Procesamiento de imágenes',
        'matplotlib': 'Gráficos',
        'pandas': 'Análisis de datos',
        'screeninfo': 'Detección de monitores',
        'bcrypt': 'Hash de contraseñas',
        'sqlite3': 'Base de datos'
    }
    
    all_ok = True
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {module:20} - {description}")
        except ImportError:
            print(f"✗ {module:20} - {description} [FALTA]")
            all_ok = False
    
    if all_ok:
        print("\n✅ Todas las dependencias: OK")
    else:
        print("\n⚠️  Faltan dependencias. Instalar con: pip install -r requirements.txt")
    
    return all_ok


def check_file_structure():
    """Verificar estructura de archivos"""
    print("\n" + "=" * 60)
    print("📁 VERIFICANDO ESTRUCTURA DE ARCHIVOS")
    print("=" * 60)
    
    required_files = [
        'src/main.py',
        'src/models/database_manager.py',
        'src/ui/responsive.py',
        'src/ui/login_window.py',
        'src/ui/main_window.py',
        'requirements.txt',
    ]
    
    all_ok = True
    for filepath in required_files:
        full_path = os.path.join(os.path.dirname(__file__), '..', filepath)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"✓ {filepath:40} ({size} bytes)")
        else:
            print(f"✗ {filepath:40} [NO ENCONTRADO]")
            all_ok = False
    
    if all_ok:
        print("\n✅ Estructura de archivos: OK")
    else:
        print("\n❌ Faltan archivos críticos")
    
    return all_ok


def main():
    """Ejecutar todas las verificaciones"""
    print("\n" + "🔧 DIAGNÓSTICO DEL SISTEMA RUSTIGONE" + "\n")
    
    results = {
        'dependencies': check_dependencies(),
        'files': check_file_structure(),
        'database': check_database_connection(),
    }
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)
    
    status = "✅ SISTEMA LISTO PARA PRODUCCIÓN" if all(results.values()) else "⚠️  HAY PROBLEMAS"
    
    for check, result in results.items():
        icon = "✓" if result else "✗"
        print(f"{icon} {check.upper()}: {'OK' if result else 'ERROR'}")
    
    print("\n" + status)
    print("=" * 60 + "\n")
    
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
