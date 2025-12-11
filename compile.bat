@echo off
REM Script para compilar RUSTIGONE con PyInstaller en Windows

echo.
echo ============================================================
echo  COMPILADOR - RUSTIGONE
echo ============================================================
echo.

REM Verificar si PyInstaller está instalado
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: PyInstaller no está instalado
    echo.
    echo Instalar con:
    echo   pip install pyinstaller
    echo.
    pause
    exit /b 1
)

REM Limpiar directorios anteriores
echo Limpiando directorios de compilación anterior...
if exist build rmdir /s /q build >nul
if exist dist rmdir /s /q dist >nul
if exist "RUSTIGONE.build" rmdir /s /q "RUSTIGONE.build" >nul

REM Compilar
echo.
echo Compilando RUSTIGONE...
echo Por favor, espere (esto puede tomar varios minutos)...
echo.

py -3 -m PyInstaller rustigone.spec

REM Verificar resultado
if errorlevel 1 (
    echo.
    echo ERROR: La compilación falló.
    echo.
    pause
    exit /b 1
)

REM Éxito
echo.
echo ============================================================
echo  COMPILACION EXITOSA!
echo ============================================================
echo.
echo La aplicación se encuentra en:
echo   dist\RUSTIGONE\RUSTIGONE.exe
echo.
echo Para probar:
echo   dist\RUSTIGONE\RUSTIGONE.exe
echo.
echo Para distribuir:
echo   Comprimir carpeta: dist\RUSTIGONE\
echo.
pause
