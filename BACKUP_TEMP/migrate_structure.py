# migrate_structure.py
import os
import shutil
from pathlib import Path

def create_new_structure():
    """Crea la nueva estructura de carpetas"""
    folders = [
        'src/ui',
        'src/models', 
        'src/utils',
        'docs',
        'tests'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        # Crear __init__.py en cada carpeta Python
        if '/' in folder:
            init_file = os.path.join(folder, '__init__.py')
            Path(init_file).touch()
    
    print("✅ Estructura de carpetas creada")

def suggest_file_moves():
    """Sugiere cómo mover los archivos basado en nombres comunes"""
    file_mappings = {
        'database.py': 'src/models/',
        'db_*.py': 'src/models/',
        '*window.py': 'src/ui/',
        '*_window.py': 'src/ui/', 
        'login.py': 'src/ui/',
        'ventas.py': 'src/ui/',
        'inventario.py': 'src/ui/',
        'caja.py': 'src/ui/',
        'compras.py': 'src/ui/',
        'reportes.py': 'src/ui/',
        'usuarios.py': 'src/ui/',
        'proveedores.py': 'src/ui/',
        'validators.py': 'src/utils/',
        'helpers.py': 'src/utils/',
        'utils.py': 'src/utils/',
    }
    
    return file_mappings

if __name__ == "__main__":
    create_new_structure()
    mappings = suggest_file_moves()
    print("📁 Sugerencias de migración:")
    for pattern, destination in mappings.items():
        print(f"   {pattern} → {destination}")