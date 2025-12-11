#!/usr/bin/env python3
"""
Script de preparación para empaquetado.
Verifica que todo esté listo para compilar con PyInstaller.
"""
import sys
import os
import shutil
from pathlib import Path

def print_section(title):
    """Imprimir encabezado de sección"""
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print(f"{'='*60}")

def check_pyinstaller():
    """Verificar que PyInstaller esté instalado"""
    print_section("VERIFICANDO PYINSTALLER")
    try:
        import PyInstaller
        print(f"✓ PyInstaller instalado: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("✗ PyInstaller NO instalado")
        print("  Instalar con: pip install pyinstaller")
        return False

def check_icon():
    """Verificar/crear ícono"""
    print_section("VERIFICANDO ÍCONO")
    icon_path = Path("icon.ico")
    
    if icon_path.exists():
        print(f"✓ Ícono encontrado: {icon_path}")
        return True
    else:
        print(f"⚠️  Ícono no encontrado: {icon_path}")
        print("   Se usa ícono por defecto de Windows")
        return False

def clean_build_dirs():
    """Limpiar directorios de compilación anterior"""
    print_section("LIMPIANDO DIRECTORIOS DE COMPILACIÓN")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"✓ Eliminado: {dir_name}/")
            except Exception as e:
                print(f"⚠️  No se pudo eliminar {dir_name}/: {e}")
        else:
            print(f"  {dir_name}/ (no existe)")
    
    # Limpiar archivos .pyc
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, file))
                except:
                    pass

def verify_structure():
    """Verificar estructura necesaria"""
    print_section("VERIFICANDO ESTRUCTURA DE PROYECTO")
    
    required = {
        'src/main.py': 'Archivo principal',
        'src/models/database_manager.py': 'Gestor de BD',
        'src/ui/responsive.py': 'Helper responsivo',
        'requirements.txt': 'Dependencias',
        'rustigone.spec': 'Configuración PyInstaller',
    }
    
    all_ok = True
    for filepath, description in required.items():
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✓ {filepath:40} - {description}")
        else:
            print(f"✗ {filepath:40} - {description} [FALTA]")
            all_ok = False
    
    return all_ok

def create_build_instructions():
    """Crear archivo de instrucciones de compilación"""
    print_section("CREANDO INSTRUCCIONES DE COMPILACIÓN")
    
    instructions = """
# INSTRUCCIONES DE COMPILACIÓN - RUSTIGONE

## Requisitos previos:
1. Python 3.8+ instalado
2. PyInstaller instalado: `pip install pyinstaller`
3. Todas las dependencias: `pip install -r requirements.txt`

## Pasos para compilar:

### Opción 1: Usando el spec file (recomendado)
```bash
pyinstaller rustigone.spec
```

### Opción 2: Comando manual
```bash
pyinstaller --name=RUSTIGONE \\
    --onedir \\
    --windowed \\
    --add-data "src/ui:ui" \\
    --add-data "src/models:models" \\
    --hidden-import=customtkinter \\
    --hidden-import=PIL \\
    --hidden-import=matplotlib \\
    --hidden-import=pandas \\
    --hidden-import=screeninfo \\
    --hidden-import=bcrypt \\
    src/main.py
```

## Resultado:
- La carpeta `dist/RUSTIGONE/` contendrá el ejecutable y todas las dependencias
- El ejecutable será: `dist/RUSTIGONE/RUSTIGONE.exe`

## Para distribuir:
1. Comprimir la carpeta `dist/RUSTIGONE/`
2. Los usuarios solo necesitan extraer y ejecutar `RUSTIGONE.exe`
3. No necesitan Python instalado

## Notas:
- La base de datos `rustigone.db` se creará automáticamente al primer uso
- El archivo de configuración estará en el mismo directorio que el ejecutable
- Para actualizar, recompilar y reemplazar la carpeta dist

## Solución de problemas:

### Error: "module not found: customtkinter"
- Asegurate de instalar todas las dependencias: `pip install -r requirements.txt`

### Error: "icon.ico not found"
- No es crítico, usa el ícono por defecto de Windows
- Para agregar ícono personalizado, crear `icon.ico` en la raíz del proyecto

### El ejecutable es muy grande (200MB+)
- Es normal debido a Python y todas las librerías
- Usar `--onefile` si prefieres un único ejecutable (más lento de iniciar)

### Antivirus bloquea el ejecutable
- PyInstaller a veces genera falsos positivos
- Excepcionar la carpeta dist/ en el antivirus
- O compilar exclusivamente para tu PC

"""
    
    readme_path = "BUILD_INSTRUCTIONS.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"✓ Instrucciones creadas: {readme_path}")

def main():
    """Ejecutar verificaciones"""
    print("\n" + "="*60)
    print("📦 PREPARACIÓN PARA EMPAQUETADO - RUSTIGONE")
    print("="*60)
    
    checks = {
        'PyInstaller': check_pyinstaller(),
        'Estructura': verify_structure(),
        'Ícono': check_icon(),
    }
    
    # Limpiar directorios
    clean_build_dirs()
    
    # Crear instrucciones
    create_build_instructions()
    
    # Resumen
    print_section("RESUMEN DE PREPARACIÓN")
    
    for check, result in checks.items():
        status = "✓" if result else "✗"
        print(f"{status} {check:30} {'OK' if result else 'ERROR'}")
    
    if all(checks.values()):
        print("\n✅ LISTO PARA COMPILAR")
        print("\nEjecutar:")
        print("  pyinstaller rustigone.spec")
        print("\nO:")
        print("  python -m PyInstaller rustigone.spec")
        return 0
    else:
        print("\n⚠️  Hay problemas que resolver antes de compilar")
        if not checks['PyInstaller']:
            print("\nInstalador PyInstaller:")
            print("  pip install pyinstaller")
        return 1

if __name__ == "__main__":
    sys.exit(main())
