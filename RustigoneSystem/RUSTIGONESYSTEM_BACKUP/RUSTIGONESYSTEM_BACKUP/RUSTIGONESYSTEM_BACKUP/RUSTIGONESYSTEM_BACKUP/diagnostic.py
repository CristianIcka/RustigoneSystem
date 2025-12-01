# diagnostic.py - Ejecuta este archivo temporalmente
import os

def check_files():
    print("🔍 VERIFICANDO ARCHIVOS EXISTENTES...")
    
    # Verificar estructura de carpetas
    folders = ['ui', 'database']
    for folder in folders:
        if os.path.exists(folder):
            print(f"✅ Carpeta '{folder}' existe")
            files = os.listdir(folder)
            print(f"   Archivos en {folder}/: {files}")
        else:
            print(f"❌ Carpeta '{folder}' NO existe")
    
    # Verificar archivos específicos
    required_files = [
        'main.py',
        'ui/main_window.py',
        'ui/login_window.py', 
        'ui/ventas_window.py',
        'ui/inventario_window.py',
        'ui/caja_window.py',
        'ui/compras_window.py',
        'database/database_manager.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} existe")
        else:
            print(f"❌ {file} NO existe")

if __name__ == "__main__":
    check_files()