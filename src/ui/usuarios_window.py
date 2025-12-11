# ui/usuarios_window.py
import customtkinter as ctk
from tkinter import messagebox
import sqlite3

class UsuariosWindow:
    def __init__(self, parent, db, usuario):
        self.parent = parent
        self.db = db
        self.usuario = usuario
        
        # Verificar permisos
        if usuario['rol'] != 'admin':
            messagebox.showerror("Error", "No tiene permisos para acceder a este módulo")
            return
        
        # Crear ventana
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Gestión de Usuarios - RUSTIGONE")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(self.window, width_percent=0.7, min_width=750, min_height=550, parent=parent)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.actualizar_lista_usuarios()
        # Estado de maximización
        self._is_maximized = False
        # Botón maximizar/restaurar
        self.maximize_btn = ctk.CTkButton(self.window, text="🗖", width=40, height=30, command=self.toggle_maximize, fg_color="#2B6CB0", text_color="white")
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
        """Crear interfaz de gestión de usuarios"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        title = ctk.CTkLabel(
            main_frame,
            text="👥 GESTIÓN DE USUARIOS",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#2B6CB0"
        )
        title.pack(pady=10)
        
        # Botones de acción
        action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=(0, 10))
        
        self.crear_btn = ctk.CTkButton(
            action_frame,
            text="➕ CREAR USUARIO",
            command=self.crear_usuario,
            fg_color="#38A169",
            font=ctk.CTkFont(weight="bold")
        )
        self.crear_btn.pack(side="left", padx=5)
        
        # Frame de lista
        list_frame = ctk.CTkFrame(main_frame, fg_color="#F7FAFC")
        list_frame.pack(fill="both", expand=True)
        
        # Header de la lista
        header_frame = ctk.CTkFrame(list_frame, fg_color="#EDF2F7", height=40)
        header_frame.pack(fill="x", pady=(0, 5))
        header_frame.pack_propagate(False)
        
        headers = ["ID", "Nombre", "Email", "Rol", "Estado", "Acciones"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                text_color="#2D3748"
            ).grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Lista de usuarios
        self.lista_frame = ctk.CTkScrollableFrame(list_frame, fg_color="white")
        self.lista_frame.pack(fill="both", expand=True)
        list_frame.pack_propagate(True)
        
    def actualizar_lista_usuarios(self):
        """Actualizar lista de usuarios"""
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        
        conn = self.db.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nombre, email, rol, activo 
            FROM usuarios 
            ORDER BY id
        ''')
        
        usuarios = cursor.fetchall()
        conn.close()
        
        for i, usuario in enumerate(usuarios):
            user_frame = ctk.CTkFrame(self.lista_frame, fg_color="white")
            user_frame.pack(fill="x", pady=2, padx=5)
            
            # Datos del usuario
            ctk.CTkLabel(
                user_frame,
                text=str(usuario[0]),
                text_color="#4A5568"
            ).grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            ctk.CTkLabel(
                user_frame,
                text=usuario[1],
                text_color="#2D3748",
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            ctk.CTkLabel(
                user_frame,
                text=usuario[2],
                text_color="#4A5568"
            ).grid(row=0, column=2, padx=10, pady=5, sticky="w")
            
            ctk.CTkLabel(
                user_frame,
                text=usuario[3],
                text_color="#2B6CB0"
            ).grid(row=0, column=3, padx=10, pady=5, sticky="w")
            
            estado_text = "🟢 Activo" if usuario[4] else "🔴 Inactivo"
            estado_color = "#38A169" if usuario[4] else "#E53E3E"
            
            ctk.CTkLabel(
                user_frame,
                text=estado_text,
                text_color=estado_color
            ).grid(row=0, column=4, padx=10, pady=5, sticky="w")
            
            # Botones de acción
            action_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
            action_frame.grid(row=0, column=5, padx=10, pady=5, sticky="e")
            
            if usuario[0] != 1:  # No permitir modificar al admin principal
                ctk.CTkButton(
                    action_frame,
                    text="Editar",
                    width=60,
                    height=30,
                    command=lambda u=usuario: self.editar_usuario(u)
                ).pack(side="left", padx=2)
                
                if usuario[4]:  # Activo
                    ctk.CTkButton(
                        action_frame,
                        text="Desactivar",
                        width=80,
                        height=30,
                        fg_color="#D69E2E",
                        command=lambda u=usuario: self.cambiar_estado_usuario(u, False)
                    ).pack(side="left", padx=2)
                else:  # Inactivo
                    ctk.CTkButton(
                        action_frame,
                        text="Activar",
                        width=80,
                        height=30,
                        fg_color="#38A169",
                        command=lambda u=usuario: self.cambiar_estado_usuario(u, True)
                    ).pack(side="left", padx=2)
    
    def crear_usuario(self):
        """Abrir diálogo para crear usuario"""
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Crear Usuario")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(dialog, width_percent=0.3, min_width=330, min_height=420, parent=self.window)
        dialog.transient(self.window)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Nombre:").pack(pady=5)
        nombre_entry = ctk.CTkEntry(dialog)
        nombre_entry.pack(pady=5, fill="x", padx=20)
        
        ctk.CTkLabel(dialog, text="Email:").pack(pady=5)
        email_entry = ctk.CTkEntry(dialog)
        email_entry.pack(pady=5, fill="x", padx=20)
        
        ctk.CTkLabel(dialog, text="Contraseña:").pack(pady=5)
        password_entry = ctk.CTkEntry(dialog, show="*")
        password_entry.pack(pady=5, fill="x", padx=20)
        
        ctk.CTkLabel(dialog, text="Confirmar Contraseña:").pack(pady=5)
        confirm_password_entry = ctk.CTkEntry(dialog, show="*")
        confirm_password_entry.pack(pady=5, fill="x", padx=20)
        
        ctk.CTkLabel(dialog, text="Rol:").pack(pady=5)
        rol_var = ctk.StringVar(value="cajero")
        rol_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        rol_frame.pack(pady=5)
        
        roles = [("Administrador", "admin"), ("Cajero", "cajero"), ("Inventario", "inventario")]
        for text, value in roles:
            ctk.CTkRadioButton(
                rol_frame,
                text=text,
                variable=rol_var,
                value=value
            ).pack(side="left", padx=10)
        
        def confirmar():
            # Validaciones
            if not all([nombre_entry.get(), email_entry.get(), password_entry.get()]):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            if password_entry.get() != confirm_password_entry.get():
                messagebox.showerror("Error", "Las contraseñas no coinciden")
                return
            
            try:
                conn = self.db.connect()
                cursor = conn.cursor()
                
                # Verificar si el email ya existe
                cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email_entry.get(),))
                if cursor.fetchone():
                    messagebox.showerror("Error", "El email ya está registrado")
                    return
                
                # Crear usuario
                password_hash = self.db.hash_password(password_entry.get())
                cursor.execute('''
                    INSERT INTO usuarios (nombre, email, password_hash, rol)
                    VALUES (?, ?, ?, ?)
                ''', (nombre_entry.get(), email_entry.get(), password_hash, rol_var.get()))
                
                conn.commit()
                conn.close()
                
                self.actualizar_lista_usuarios()
                dialog.destroy()
                messagebox.showinfo("Éxito", "Usuario creado correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear usuario: {str(e)}")
        
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Crear",
            command=confirmar,
            fg_color="#38A169"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="#718096"
        ).pack(side="left", padx=10)
    
    def editar_usuario(self, usuario):
        """Editar usuario existente"""
        messagebox.showinfo("Editar", f"Editar usuario: {usuario[1]}")
        # Implementar edición similar a crear_usuario pero con datos precargados
    
    def cambiar_estado_usuario(self, usuario, activo):
        """Activar/desactivar usuario"""
        estado = "activar" if activo else "desactivar"
        if messagebox.askyesno("Confirmar", f"¿Está seguro de {estado} al usuario {usuario[1]}?"):
            try:
                conn = self.db.connect()
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE usuarios SET activo = ? WHERE id = ?
                ''', (activo, usuario[0]))
                
                conn.commit()
                conn.close()
                
                self.actualizar_lista_usuarios()
                messagebox.showinfo("Éxito", f"Usuario {estado}do correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cambiar estado: {str(e)}")