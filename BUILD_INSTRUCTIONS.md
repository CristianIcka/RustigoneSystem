
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
pyinstaller --name=RUSTIGONE \
    --onedir \
    --windowed \
    --add-data "src/ui:ui" \
    --add-data "src/models:models" \
    --hidden-import=customtkinter \
    --hidden-import=PIL \
    --hidden-import=matplotlib \
    --hidden-import=pandas \
    --hidden-import=screeninfo \
    --hidden-import=bcrypt \
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

