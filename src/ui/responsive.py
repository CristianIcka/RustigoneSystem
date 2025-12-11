"""Helpers centralizados para tamaño / centrado y grids responsivos.

Uso: desde `ui.responsive` importar `set_window_size_and_center`,
`center_window`, `apply_responsive_grid`, etc.
"""
from typing import Optional, Sequence

def get_primary_monitor():
    """Obtener dimensiones de pantalla usando tkinter directamente."""
    try:
        import tkinter as tk
        # Crear ventana temporal solo para obtener dimensiones
        temp = tk.Tk()
        temp.withdraw()  # Ocultar ventana
        screen_width = temp.winfo_screenwidth()
        screen_height = temp.winfo_screenheight()
        temp.destroy()
        
        # Retornar objeto con las dimensiones
        return type("Monitor", (), {
            "width": screen_width,
            "height": screen_height,
            "x": 0,
            "y": 0
        })()
    except Exception as e:
        print(f"Error getting monitor: {e}")
        # Fallback a valores estándar
        return type("Monitor", (), {
            "width": 1920,
            "height": 1080,
            "x": 0,
            "y": 0
        })()


def compute_adaptive_size(screen_width: int, screen_height: int,
                          width_percent: float = 0.7, height_percent: float = 0.7,
                          min_width: int = 650, min_height: int = 500):
    width = max(int(screen_width * width_percent), min_width)
    height = max(int(screen_height * height_percent), min_height)
    return width, height


def center_window(window, width: int, height: int, parent: Optional[object] = None):
    """Centrar `window` en el monitor primario de forma simple y confiable."""
    try:
        # Obtener dimensiones del monitor
        window.update()  # Actualizar estado de ventana
        
        if parent is not None and hasattr(parent, 'winfo_exists'):
            try:
                if parent.winfo_exists():
                    parent.update()
                    parent_x = parent.winfo_x()
                    parent_y = parent.winfo_y()
                    parent_w = parent.winfo_width()
                    parent_h = parent.winfo_height()
                    
                    # Centrar respecto al padre
                    x = parent_x + (parent_w - width) // 2
                    y = parent_y + (parent_h - height) // 2
                else:
                    raise Exception("Parent doesn't exist")
            except Exception:
                # Centrar en pantalla si padre no disponible
                monitor = get_primary_monitor()
                x = (monitor.width - width) // 2
                y = (monitor.height - height) // 2
        else:
            # Centrar en el monitor
            monitor = get_primary_monitor()
            x = max(0, (monitor.width - width) // 2)
            y = max(0, (monitor.height - height) // 2)
        
        window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Traer ventana al frente y darle foco
        window.lift()
        window.focus()
        
    except Exception as e:
        print(f"Error centering window: {e}")
        # Fallback: solo aplicar tamaño
        try:
            window.geometry(f"{width}x{height}")
            window.lift()
            window.focus()
        except Exception:
            pass


def set_window_size_and_center(window, width_percent: float = 0.7, height_percent: float = 0.7,
                               min_width: int = 650, min_height: int = 500,
                               parent: Optional[object] = None):
    """Calcular tamaño adaptativo y centrar la ventana.

    - `width_percent` y `height_percent` definen el porcentaje de la pantalla.
    - `min_width`/`min_height` evitan tamaños demasiado pequeños.
    - `parent` si se proporciona centra respecto al padre.
    """
    monitor = get_primary_monitor()
    width, height = compute_adaptive_size(monitor.width, monitor.height,
                                          width_percent, height_percent,
                                          min_width, min_height)
    center_window(window, width, height, parent=parent)


def apply_responsive_grid(container, cols: int = 1, rows: int = 1,
                          col_weights: Optional[Sequence[int]] = None,
                          row_weights: Optional[Sequence[int]] = None,
                          uniform: Optional[str] = None):
    """Configura `grid_columnconfigure` y `grid_rowconfigure` de forma centralizada.

    - `col_weights` y `row_weights` pueden ser secuencias con pesos específicos.
    - `uniform` si se pasa se aplica a cada columna/fila.
    """
    col_weights = col_weights or [1] * cols
    row_weights = row_weights or [1] * rows

    for i in range(cols):
        weight = col_weights[i] if i < len(col_weights) else 1
        if uniform:
            container.grid_columnconfigure(i, weight=weight, uniform=uniform)
        else:
            container.grid_columnconfigure(i, weight=weight)

    for j in range(rows):
        weight = row_weights[j] if j < len(row_weights) else 1
        if uniform:
            container.grid_rowconfigure(j, weight=weight, uniform=uniform)
        else:
            container.grid_rowconfigure(j, weight=weight)
