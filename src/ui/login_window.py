# ui/login_window.py
import customtkinter as ctk
from utils.validators import validar_password, validar_email

class LoginWindow:
    def __init__(self, parent, db, on_login_success):
        self.parent = parent
        self.db = db
        self.on_login_success = on_login_success
        
        # Crear frame de login
        self.frame = ctk.CTkFrame(parent, fg_color="white")
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Crear widgets de la ventana de login"""
        # Logo y título
        self.title_label = ctk.CTkLabel(
            self.frame, 
            text="PANADERÍA RUSTIGONE",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#2B6CB0"
        )
        self.title_label.pack(pady=(40, 20))
        
        self.subtitle_label = ctk.CTkLabel(
            self.frame,
            text="Sistema de Gestión",
            font=ctk.CTkFont(size=18),
            text_color="#4A5568"
        )
        self.subtitle_label.pack(pady=(0, 40))
        
        # Frame de formulario
        form_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        form_frame.pack(pady=20)
        
        # Email
        ctk.CTkLabel(form_frame, text="Email:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        self.email_entry = ctk.CTkEntry(
            form_frame, 
            width=300,
            height=40,
            placeholder_text="usuario@ejemplo.com"
        )
        self.email_entry.grid(row=1, column=0, pady=(0, 15))
        
        # Contraseña
        ctk.CTkLabel(form_frame, text="Contraseña:", font=ctk.CTkFont(weight="bold")).grid(
            row=2, column=0, sticky="w", pady=(0, 5)
        )
        self.password_entry = ctk.CTkEntry(
            form_frame,
            width=300,
            height=40,
            show="•",
            placeholder_text="Mínimo 8 caracteres, 1 mayúscula, 1 número, 1 especial"
        )
        self.password_entry.grid(row=3, column=0, pady=(0, 20))
        
        # Botones
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, pady=20)
        
        self.login_button = ctk.CTkButton(
            button_frame,
            text="Iniciar Sesión",
            command=self.login,
            width=140,
            height=45,
            fg_color="#2B6CB0",
            font=ctk.CTkFont(weight="bold")
        )
        self.login_button.grid(row=0, column=0, padx=5)
        
        self.clean_button = ctk.CTkButton(
            button_frame,
            text="Limpiar",
            command=self.clean_form,
            width=140,
            height=45,
            fg_color="#48BB78",
            font=ctk.CTkFont(weight="bold")
        )
        self.clean_button.grid(row=0, column=1, padx=5)
        
        self.exit_button = ctk.CTkButton(
            button_frame,
            text="Salir",
            command=self.parent.quit,
            width=140,
            height=45,
            fg_color="#E53E3E",
            font=ctk.CTkFont(weight="bold")
        )
        self.exit_button.grid(row=0, column=2, padx=5)
        
        # Enlace recuperar contraseña
        self.recover_label = ctk.CTkLabel(
            form_frame,
            text="¿Olvidaste tu contraseña?",
            text_color="#2B6CB0",
            cursor="hand2",
            font=ctk.CTkFont(underline=True)
        )
        self.recover_label.grid(row=5, column=0, pady=10)
        self.recover_label.bind("<Button-1>", lambda e: self.recover_password())
        
    def login(self):
        """Manejar intento de login"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        
        if not email or not password:
            self.show_error("Por favor complete todos los campos")
            return
            
        if not validar_email(email):
            self.show_error("Formato de email inválido")
            return
            
        # Verificar usuario en base de datos
        user = self.db.get_user_by_email(email)
        if not user:
            self.show_error("Usuario no encontrado")
            return
            
        if not self.db.verify_password(password, user['password_hash']):
            self.show_error("Contraseña incorrecta")
            return
            
        # Login exitoso
        self.on_login_success(user)
        
    def clean_form(self):
        """Limpiar formulario"""
        self.email_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        
    def recover_password(self):
        """Recuperar contraseña"""
        self.show_info("Función de recuperación en desarrollo")
        
    def show_error(self, message):
        """Mostrar mensaje de error"""
        error_window = ctk.CTkToplevel(self.parent)
        error_window.title("Error")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(error_window, width_percent=0.25, min_width=300, min_height=150, parent=self.parent)
        error_window.transient(self.parent)
        error_window.grab_set()
        
        ctk.CTkLabel(error_window, text="❌ " + message, 
                    font=ctk.CTkFont(weight="bold")).pack(pady=20)
        ctk.CTkButton(error_window, text="Aceptar", 
                     command=error_window.destroy).pack(pady=10)
        
    def show_info(self, message):
        """Mostrar mensaje informativo"""
        info_window = ctk.CTkToplevel(self.parent)
        info_window.title("Información")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(info_window, width_percent=0.25, min_width=300, min_height=150, parent=self.parent)
        info_window.transient(self.parent)
        info_window.grab_set()
        
        ctk.CTkLabel(info_window, text="ℹ️ " + message,
                    font=ctk.CTkFont(weight="bold")).pack(pady=20)
        ctk.CTkButton(info_window, text="Aceptar",
                     command=info_window.destroy).pack(pady=10)