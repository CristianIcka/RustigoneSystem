# ui/corregir_stock_window.py
import customtkinter as ctk
import sqlite3

class CorregirStockWindow:
    def __init__(self, parent, db, inventario_window, producto):
        self.parent = parent
        self.db = db
        self.inventario_window = inventario_window
        self.producto = producto
        
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Corregir Stock - RUSTIGONE")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(self.window, width_percent=0.4, min_width=420, min_height=280, parent=parent)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        # Estado de maximización
        self._is_maximized = False
        # Botón maximizar/restaurar
        self.maximize_btn = ctk.CTkButton(self.window, text="🗖", width=40, height=30, command=self.toggle_maximize, fg_color="#3182CE", text_color="white")
        self.maximize_btn.place(relx=0.98, rely=0.01, anchor="ne")

    def toggle_maximize(self):
        if not self._is_maximized:
            self.window.state('zoomed')
            self._is_maximized = True
            self.maximize_btn.configure(text="🗗")
        else:
            self.window.state('normal')
            self._is_maximized = False
            self.maximize_btn.configure(text="🗖")
    
    def create_widgets(self):
        """Crear interfaz para corregir stock"""
        main_frame = ctk.CTkFrame(self.window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            main_frame,
            text="🔧 CORREGIR STOCK",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#3182CE"
        ).pack(pady=20)
        
        # Información del producto
        info_frame = ctk.CTkFrame(main_frame, fg_color="#EDF2F7", corner_radius=10)
        info_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Producto: {self.producto['nombre']}",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Stock actual: {self.producto['stock_actual']} {self.producto['unidad_medida']}",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)
        
        # Nuevo stock
        ctk.CTkLabel(main_frame, text="Nuevo Stock:", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        self.nuevo_stock_entry = ctk.CTkEntry(
            main_frame,
            width=200,
            height=40,
            placeholder_text=f"Ingrese nuevo stock"
        )
        self.nuevo_stock_entry.pack(pady=10)
        self.nuevo_stock_entry.insert(0, str(self.producto['stock_actual']))
        
        # Botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="💾 ACTUALIZAR STOCK",
            command=self.actualizar_stock,
            width=180,
            height=45,
            fg_color="#38A169",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="❌ CANCELAR",
            command=self.window.destroy,
            width=180,
            height=45,
            fg_color="#E53E3E",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=1, padx=10)
    
    def actualizar_stock(self):
        """Actualizar stock del producto"""
        try:
            nuevo_stock = float(self.nuevo_stock_entry.get())
            
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE productos SET stock_actual = ? WHERE id = ?",
                (nuevo_stock, self.producto['id'])
            )
            conn.commit()
            conn.close()
            
            self.mostrar_exito("Stock actualizado exitosamente")
            self.inventario_window.refrescar_lista()
            self.window.destroy()
            
        except ValueError:
            self.mostrar_error("Ingrese un valor numérico válido para el stock")
    
    def mostrar_error(self, mensaje):
        """Mostrar mensaje de error"""
        error_window = ctk.CTkToplevel(self.window)
        error_window.title("Error")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(error_window, width_percent=0.35, min_width=400, min_height=150, parent=self.window)
        error_window.transient(self.window)
        error_window.grab_set()
        
        ctk.CTkLabel(error_window, text="❌ " + mensaje).pack(expand=True, pady=20)
        ctk.CTkButton(error_window, text="Aceptar", command=error_window.destroy).pack(pady=10)
    
    def mostrar_exito(self, mensaje):
        """Mostrar mensaje de éxito"""
        exito_window = ctk.CTkToplevel(self.window)
        exito_window.title("Éxito")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(exito_window, width_percent=0.35, min_width=400, min_height=150, parent=self.window)
        exito_window.transient(self.window)
        exito_window.grab_set()
        
        ctk.CTkLabel(exito_window, text="✅ " + mensaje).pack(expand=True, pady=20)
        ctk.CTkButton(exito_window, text="Aceptar", command=exito_window.destroy).pack(pady=10)