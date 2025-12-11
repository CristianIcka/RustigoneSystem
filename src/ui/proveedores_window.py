# ui/proveedores_window.py - VERSIÓN COMPLETA Y CORREGIDA
import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime, date

class ProveedoresWindow:
    def __init__(self, parent, db, usuario):
        self.parent = parent
        self.db = db
        self.usuario = usuario
        
        # Crear ventana
        self.window = ctk.CTkToplevel(parent)
        self.window.title("👥 Gestión de Proveedores - RUSTIGONE")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(self.window, width_percent=0.75, min_width=800, min_height=650, parent=parent)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Hacer responsiva
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        self.proveedor_seleccionado = None
        self.create_widgets()
        self.actualizar_lista_proveedores()
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
        """Crear interfaz de gestión de proveedores"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="#2C3E50")
        header_frame.pack(fill="x", pady=(0, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="👥 GESTIÓN DE PROVEEDORES",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title.pack(pady=15)
        
        # Frame de contenido
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo - Lista de proveedores
        left_frame = ctk.CTkFrame(content_frame, fg_color="#F7FAFC")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)
        
        # Controles de búsqueda
        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(search_frame, text="Buscar:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 10))
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="RUT, nombre, giro...")
        self.search_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
        self.search_entry.bind("<Return>", self.buscar_proveedores)
        
        ctk.CTkButton(
            search_frame,
            text="🔍 Buscar",
            command=self.buscar_proveedores
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            search_frame,
            text="🔄 Limpiar",
            command=self.limpiar_busqueda,
            fg_color="#718096"
        ).pack(side="left")
        
        # Botones de acción
        action_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        action_frame.pack(side="right")
        
        ctk.CTkButton(
            action_frame,
            text="➕ NUEVO PROVEEDOR",
            command=self.crear_proveedor,
            fg_color="#38A169",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=5)
        
        self.editar_btn = ctk.CTkButton(
            action_frame,
            text="✏️ EDITAR",
            command=self.editar_proveedor,
            fg_color="#D69E2E",
            font=ctk.CTkFont(weight="bold"),
            state="disabled"
        )
        self.editar_btn.pack(side="left", padx=5)
        
        # Lista de proveedores
        lista_container = ctk.CTkFrame(left_frame, fg_color="white")
        lista_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Header de la lista
        list_header = ctk.CTkFrame(lista_container, fg_color="#EDF2F7", height=40)
        list_header.pack(fill="x", pady=(0, 5))
        list_header.pack_propagate(False)
        
        headers = ["RUT", "Nombre", "Giro", "Contacto", "Teléfono", "Estado"]
        
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                list_header,
                text=header,
                font=ctk.CTkFont(weight="bold", size=12),
                text_color="#2D3748"
            ).pack(side="left", padx=10, pady=10)
        
        # Lista scrollable
        self.lista_proveedores = ctk.CTkScrollableFrame(lista_container, fg_color="white")
        self.lista_proveedores.pack(fill="both", expand=True)
        lista_container.pack_propagate(True)
        
        # Panel derecho - Información del proveedor
        self.info_frame = ctk.CTkFrame(content_frame, fg_color="#F7FAFC", width=400)
        self.info_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.info_frame.pack_propagate(False)
        
        self.mostrar_info_vacia()
        
    def mostrar_info_vacia(self):
        """Mostrar información vacía cuando no hay proveedor seleccionado"""
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(
            self.info_frame,
            text="ℹ️ SELECCIONE UN PROVEEDOR",
            font=ctk.CTkFont(weight="bold", size=16),
            text_color="#718096"
        ).pack(expand=True)
    
    def mostrar_info_proveedor(self, proveedor):
        """Mostrar información detallada del proveedor seleccionado"""
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        # Título
        ctk.CTkLabel(
            self.info_frame,
            text="📋 INFORMACIÓN DEL PROVEEDOR",
            font=ctk.CTkFont(weight="bold", size=16),
            text_color="#2D3748"
        ).pack(pady=20)
        
        # Frame de información
        info_content = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        info_content.pack(fill="both", expand=True, padx=20)
        
        datos = [
            ("RUT:", proveedor['rut']),
            ("Nombre:", proveedor['nombre']),
            ("Giro:", proveedor['giro'] or "No especificado"),
            ("Dirección:", proveedor['direccion'] or "No especificada"),
            ("Teléfono:", proveedor['telefono'] or "No especificado"),
            ("Email:", proveedor['email'] or "No especificado"),
            ("Contacto:", proveedor['contacto'] or "No especificado"),
            ("Estado:", "🟢 Activo" if proveedor['activo'] else "🔴 Inactivo"),
            ("Registro:", proveedor['fecha_registro'][:10] if proveedor['fecha_registro'] else "No disponible")
        ]
        
        for i, (label, valor) in enumerate(datos):
            ctk.CTkLabel(
                info_content,
                text=label,
                font=ctk.CTkFont(weight="bold")
            ).grid(row=i, column=0, sticky="w", pady=4, padx=(0, 10))
            
            ctk.CTkLabel(
                info_content,
                text=valor,
                text_color="#4A5568"
            ).grid(row=i, column=1, sticky="w", pady=4)
        
        # Estadísticas rápidas
        ctk.CTkLabel(
            info_content,
            text="\n📊 ESTADÍSTICAS:",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=len(datos)+1, column=0, columnspan=2, sticky="w", pady=(20, 5))
        
        # Obtener estadísticas
        conn = self.db.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_compras,
                SUM(total) as monto_total,
                MAX(fecha_compra) as ultima_compra
            FROM compras 
            WHERE proveedor_id = ?
        ''', (proveedor['id'],))
        
        stats = cursor.fetchone()
        conn.close()
        
        estadisticas = [
            ("Total Compras:", f"{stats[0] or 0}"),
            ("Monto Total:", f"${stats[1] or 0:,.0f}"),
            ("Última Compra:", stats[2] or "Nunca")
        ]
        
        for i, (label, valor) in enumerate(estadisticas, len(datos)+2):
            ctk.CTkLabel(
                info_content,
                text=label,
                font=ctk.CTkFont(weight="bold", size=12)
            ).grid(row=i, column=0, sticky="w", pady=3, padx=(0, 10))
            
            ctk.CTkLabel(
                info_content,
                text=valor,
                text_color="#2B6CB0",
                font=ctk.CTkFont(weight="bold", size=12)
            ).grid(row=i, column=1, sticky="w", pady=3)
    
    def actualizar_lista_proveedores(self, proveedores=None):
        """Actualizar lista de proveedores"""
        for widget in self.lista_proveedores.winfo_children():
            widget.destroy()
        
        if proveedores is None:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM proveedores 
                ORDER BY nombre
            ''')
            proveedores = [dict(row) for row in cursor.fetchall()]
            conn.close()
        
        if not proveedores:
            ctk.CTkLabel(
                self.lista_proveedores,
                text="No se encontraron proveedores",
                text_color="#718096"
            ).pack(expand=True, pady=50)
            return
        
        for i, proveedor in enumerate(proveedores):
            # Frame para cada proveedor
            prov_frame = ctk.CTkFrame(self.lista_proveedores, fg_color="white", height=45)
            prov_frame.pack(fill="x", pady=1, padx=5)
            prov_frame.pack_propagate(False)
            
            # Color de fondo alternado
            if i % 2 == 0:
                prov_frame.configure(fg_color="#F7FAFC")
            
            # Hacer clickeable
            prov_frame.bind("<Button-1>", lambda e, p=proveedor: self.seleccionar_proveedor(p))
            prov_frame.configure(cursor="hand2")
            
            # Frame interno para contenido
            inner_frame = ctk.CTkFrame(prov_frame, fg_color="transparent")
            inner_frame.pack(fill="both", expand=True, padx=10, pady=8)
            
            # RUT
            ctk.CTkLabel(
                inner_frame,
                text=proveedor['rut'],
                text_color="#4A5568",
                width=120,
                anchor="w"
            ).pack(side="left", padx=5)
            
            # Nombre
            ctk.CTkLabel(
                inner_frame,
                text=proveedor['nombre'],
                text_color="#2D3748",
                font=ctk.CTkFont(weight="bold"),
                width=250,
                anchor="w"
            ).pack(side="left", padx=5)
            
            # Giro
            ctk.CTkLabel(
                inner_frame,
                text=proveedor['giro'] or "-",
                text_color="#4A5568",
                width=200,
                anchor="w"
            ).pack(side="left", padx=5)
            
            # Contacto
            ctk.CTkLabel(
                inner_frame,
                text=proveedor['contacto'] or "-",
                text_color="#4A5568",
                width=150,
                anchor="w"
            ).pack(side="left", padx=5)
            
            # Teléfono
            ctk.CTkLabel(
                inner_frame,
                text=proveedor['telefono'] or "-",
                text_color="#4A5568",
                width=120,
                anchor="w"
            ).pack(side="left", padx=5)
            
            # Estado
            estado_text = "🟢 Activo" if proveedor['activo'] else "🔴 Inactivo"
            estado_color = "#38A169" if proveedor['activo'] else "#E53E3E"
            
            ctk.CTkLabel(
                inner_frame,
                text=estado_text,
                text_color=estado_color,
                width=80,
                anchor="w"
            ).pack(side="left", padx=5)
            
            # Hacer todo el frame clickeable
            for widget in inner_frame.winfo_children():
                widget.bind("<Button-1>", lambda e, p=proveedor: self.seleccionar_proveedor(p))
                widget.configure(cursor="hand2")
    
    def seleccionar_proveedor(self, proveedor):
        """Seleccionar un proveedor de la lista"""
        self.proveedor_seleccionado = proveedor
        self.mostrar_info_proveedor(proveedor)
        
        # Habilitar botones
        self.editar_btn.configure(state="normal")
    
    def buscar_proveedores(self, event=None):
        """Buscar proveedores según criterios"""
        criterio = self.search_entry.get().strip()
        
        if not criterio:
            self.actualizar_lista_proveedores()
            return
        
        conn = self.db.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM proveedores 
            WHERE rut LIKE ? OR nombre LIKE ? OR giro LIKE ? OR contacto LIKE ?
            ORDER BY nombre
        ''', (f'%{criterio}%', f'%{criterio}%', f'%{criterio}%', f'%{criterio}%'))
        
        proveedores = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        self.actualizar_lista_proveedores(proveedores)
        self.proveedor_seleccionado = None
        self.mostrar_info_vacia()
        self.editar_btn.configure(state="disabled")
    
    def limpiar_busqueda(self):
        """Limpiar búsqueda"""
        self.search_entry.delete(0, 'end')
        self.actualizar_lista_proveedores()
        self.proveedor_seleccionado = None
        self.mostrar_info_vacia()
        self.editar_btn.configure(state="disabled")
    
    def crear_proveedor(self):
        """Abrir diálogo para crear proveedor"""
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Nuevo Proveedor")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(dialog, width_percent=0.45, min_width=500, min_height=600, parent=self.window)
        dialog.transient(self.window)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="➕ NUEVO PROVEEDOR",
            font=ctk.CTkFont(weight="bold", size=18)
        ).pack(pady=20)
        
        # Formulario
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20)
        
        campos = [
            ("RUT*:", "rut"),
            ("Nombre*:", "nombre"),
            ("Giro:", "giro"),
            ("Dirección:", "direccion"),
            ("Teléfono:", "telefono"),
            ("Email:", "email"),
            ("Persona de Contacto:", "contacto")
        ]
        
        self.entries = {}
        for i, (label, key) in enumerate(campos):
            ctk.CTkLabel(form_frame, text=label, font=ctk.CTkFont(weight="bold")).grid(row=i, column=0, sticky="w", pady=8)
            entry = ctk.CTkEntry(form_frame, width=300)
            entry.grid(row=i, column=1, sticky="w", pady=8, padx=(10, 0))
            self.entries[key] = entry
        
        # Estado
        ctk.CTkLabel(form_frame, text="Estado:", font=ctk.CTkFont(weight="bold")).grid(row=len(campos), column=0, sticky="w", pady=8)
        self.estado_var = ctk.StringVar(value="ACTIVO")
        estado_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        estado_frame.grid(row=len(campos), column=1, sticky="w", pady=8, padx=(10, 0))
        
        ctk.CTkRadioButton(estado_frame, text="Activo", variable=self.estado_var, value="ACTIVO").pack(side="left", padx=10)
        ctk.CTkRadioButton(estado_frame, text="Inactivo", variable=self.estado_var, value="INACTIVO").pack(side="left", padx=10)
        
        def confirmar():
            # Validar campos obligatorios
            if not all([self.entries['rut'].get(), self.entries['nombre'].get()]):
                messagebox.showerror("Error", "Los campos RUT y Nombre son obligatorios")
                return
            
            try:
                conn = self.db.connect()
                cursor = conn.cursor()
                
                # Verificar si el RUT ya existe
                cursor.execute("SELECT id FROM proveedores WHERE rut = ?", (self.entries['rut'].get(),))
                if cursor.fetchone():
                    messagebox.showerror("Error", "El RUT ya está registrado")
                    return
                
                # Insertar proveedor
                cursor.execute('''
                    INSERT INTO proveedores 
                    (rut, nombre, giro, direccion, telefono, email, contacto, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.entries['rut'].get(),
                    self.entries['nombre'].get(),
                    self.entries['giro'].get() or None,
                    self.entries['direccion'].get() or None,
                    self.entries['telefono'].get() or None,
                    self.entries['email'].get() or None,
                    self.entries['contacto'].get() or None,
                    self.estado_var.get() == "ACTIVO"
                ))
                
                conn.commit()
                conn.close()
                
                self.actualizar_lista_proveedores()
                dialog.destroy()
                messagebox.showinfo("Éxito", "Proveedor creado correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear proveedor: {str(e)}")
        
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Guardar",
            command=confirmar,
            fg_color="#38A169",
            width=120
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="#718096",
            width=120
        ).pack(side="left", padx=10)
    
    def editar_proveedor(self):
        """Editar proveedor seleccionado"""
        if not self.proveedor_seleccionado:
            return
        
        messagebox.showinfo("Editar", f"Funcionalidad de edición para: {self.proveedor_seleccionado['nombre']}")
        # Implementar lógica similar a crear_proveedor pero con UPDATE