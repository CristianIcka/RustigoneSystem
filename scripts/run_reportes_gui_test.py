import sys, os, traceback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Añadir la carpeta `src` para que los paquetes `src.*` y `ui.*` sean importables
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import tkinter as tk
from src.models.database_manager import DatabaseManager
# Importar ReportesWindow (nota: el módulo usa `from ui.responsive import ...`,
# por eso añadimos `src` al path para que `ui` sea resolvible)
from src.ui.reportes_window import ReportesWindow

# Crear root oculto
root = tk.Tk()
root.withdraw()

db = DatabaseManager()
usuario = {'id': 1, 'nombre': 'Tester', 'rol': 'admin'}

try:
    print('Instanciando ReportesWindow...')
    rw = ReportesWindow(root, db, usuario)
    print('Llamando a generar_reporte()...')
    rw.generar_reporte()
    print('generar_reporte() completado sin excepciones')
except Exception as e:
    print('Excepción al ejecutar ReportesWindow:')
    traceback.print_exc()
finally:
    try:
        root.destroy()
    except Exception:
        pass
