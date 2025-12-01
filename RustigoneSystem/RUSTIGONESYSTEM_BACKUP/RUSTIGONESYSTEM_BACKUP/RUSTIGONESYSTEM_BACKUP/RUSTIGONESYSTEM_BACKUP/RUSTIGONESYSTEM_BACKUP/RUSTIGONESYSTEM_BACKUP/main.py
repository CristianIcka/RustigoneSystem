# main.py (actualizado)
# import customtkinter as ctk
# from database.database_manager import DatabaseManager
# from ui.login_window import LoginWindow
# import os

# class RustigoneApp:
#     def __init__(self):
#         # Configurar apariencia
#         ctk.set_appearance_mode("Light")
#         ctk.set_default_color_theme("blue")
        
#         # Inicializar base de datos
#         self.db = DatabaseManager()
#         self.db.init_database()
        
#         # Crear ventana principal
#         self.root = ctk.CTk()
#         self.root.title("Panadería RUSTIGONE - Sistema de Gestión")
#         self.root.geometry("1200x800")
#         self.root.resizable(True, True)
        
#         # Mostrar ventana de login
#         self.show_login()
        
#     def show_login(self):
#         """Mostrar ventana de login"""
#         LoginWindow(self.root, self.db, self.on_login_success)
        
#     def on_login_success(self, usuario):
#         """Callback cuando el login es exitoso"""
#         print(f"Usuario {usuario['nombre']} logueado exitosamente")
#         self.show_main_window(usuario)
        
#     def show_main_window(self, usuario):
#         """Mostrar ventana principal después del login"""
#         from ui.main_window import MainWindow
#         MainWindow(self.root, self.db, usuario)
        
#     def run(self):
#         """Ejecutar aplicación"""
#         self.root.mainloop()# main.py - VERSIÓN ACTUALIZADA
import customtkinter as ctk
import traceback
import sys
from database.database_manager import DatabaseManager
from ui.login_window import LoginWindow

class RustigoneApp:
    def __init__(self):
        try:
            print("🚀 Iniciando aplicación RUSTIGONE...")
            
            # Configurar apariencia
            ctk.set_appearance_mode("Light")
            ctk.set_default_color_theme("blue")
            
            # Inicializar base de datos
            self.db = DatabaseManager()
            self.db.init_database()
            
            # Crear ventana principal
            self.root = ctk.CTk()
            self.root.title("Panadería RUSTIGONE - Sistema de Gestión")
            self.root.geometry("1200x800")
            self.root.resizable(True, True)
            
            # Mostrar ventana de login
            self.show_login()
            
            print("✅ Aplicación inicializada correctamente")
            
        except Exception as e:
            print(f"❌ Error crítico al iniciar aplicación: {e}")
            traceback.print_exc()
            sys.exit(1)
        
    def show_login(self):
        """Mostrar ventana de login"""
        try:
            print("🔐 Mostrando ventana de login...")
            LoginWindow(self.root, self.db, self.on_login_success)
        except Exception as e:
            print(f"❌ Error al mostrar login: {e}")
            traceback.print_exc()
        
    def on_login_success(self, usuario):
        """Callback cuando el login es exitoso"""
        try:
            print(f"✅ Usuario {usuario['nombre']} logueado exitosamente")
            self.show_main_window(usuario)
        except Exception as e:
            print(f"❌ Error después del login: {e}")
            traceback.print_exc()
        
    def show_main_window(self, usuario):
        """Mostrar ventana principal después del login"""
        try:
            print("🖥️ Cargando ventana principal...")
            from ui.main_window import MainWindow
            MainWindow(self.root, self.db, usuario)
            print("✅ Ventana principal cargada")
        except Exception as e:
            print(f"❌ Error al cargar ventana principal: {e}")
            traceback.print_exc()
            # Mostrar error al usuario
            from tkinter import messagebox
            messagebox.showerror("Error", f"No se pudo cargar la interfaz principal: {str(e)}")
        
    def run(self):
        """Ejecutar aplicación"""
        try:
            print("🎯 Iniciando loop principal...")
            self.root.mainloop()
        except Exception as e:
            print(f"❌ Error durante ejecución: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    app = RustigoneApp()
    app.run()

if __name__ == "__main__":
    app = RustigoneApp()
    app.run()