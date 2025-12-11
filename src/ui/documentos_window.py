# ui/documentos_window.py
import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime

class DocumentosWindow:
    def __init__(self, parent, db, usuario, proveedor):
        self.parent = parent
        self.db = db
        self.usuario = usuario
        self.proveedor = proveedor
        
        # Crear ventana
        self.window = ctk.CTkToplevel(parent)
        self.window.title(f"📄 Documentos - {proveedor['nombre']}")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(self.window, width_percent=0.7, min_width=750, min_height=600, parent=parent)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.actualizar_lista_documentos()
        # Estado de maximización
        self._is_maximized = False
        # Botón maximizar/restaurar
        self.maximize_btn = ctk.CTkButton(self.window, text="🗖", width=40, height=30, command=self.toggle_maximize, fg_color="#2C3E50", text_color="white")
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
        """Crear interfaz de documentos"""
        # Implementar interfaz similar a proveedores
        # para gestionar facturas, boletas y guías
        pass
    
    def actualizar_lista_documentos(self):
        """Actualizar lista de documentos"""
        # Implementar lógica para mostrar documentos
        pass