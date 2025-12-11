# ui/main_window.py - VERSIÓN CORREGIDA (SOLO UN BOTÓN SALIR)
import customtkinter as ctk
from tkinter import messagebox
import traceback
import screeninfo

class MainWindow:
    def __init__(self, parent, db, usuario):
        try:
            self.parent = parent
            self.db = db
            self.usuario = usuario
            
            print(f"🔧 Inicializando MainWindow para: {usuario['nombre']}")
            
            # Limpiar ventana principal
            for widget in self.parent.winfo_children():
                widget.destroy()
            
            self.parent.title(f"Panadería RUSTIGONE - {usuario['nombre']} ({usuario['rol']})")
            
            # Hacer ventana responsiva
            self.setup_responsive_window()
            
            # Crear interfaz principal
            self.create_widgets()
            
            print("✅ MainWindow inicializado correctamente")
            
        except Exception as e:
            print(f"❌ Error en MainWindow.__init__: {e}")
            traceback.print_exc()
            raise
    
    def setup_responsive_window(self):
        """Configurar ventana responsiva"""
        try:
            # Usar helper centralizado para tamaño y centrado
            from ui.responsive import set_window_size_and_center
            set_window_size_and_center(self.parent, width_percent=0.7, min_width=750, min_height=600, parent=None)
            # Configurar grid responsivo base
            self.parent.grid_columnconfigure(0, weight=1)
            self.parent.grid_rowconfigure(0, weight=1)
            
        except Exception as e:
            print(f"⚠️ No se pudo configurar ventana responsiva: {e}")
            try:
                from ui.responsive import set_window_size_and_center
                set_window_size_and_center(self.parent, width_percent=0.7, min_width=750, min_height=600, parent=None)
            except Exception as e2:
                print(f"⚠️ Fallback al geometry: {e2}")
                # Valores por defecto
                self.parent.geometry("1200x800")
    
    def create_widgets(self):
        """Crear interfaz principal responsiva"""
        try:
            print("🔧 Creando widgets responsivos...")
            
            # Frame principal con grid responsivo
            main_frame = ctk.CTkFrame(self.parent, fg_color="#2C3E50")
            main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            main_frame.grid_columnconfigure(0, weight=1)
            main_frame.grid_rowconfigure(1, weight=1)
            
            # Header
            header_frame = ctk.CTkFrame(main_frame, fg_color="#34495E", height=80)
            header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))
            header_frame.grid_columnconfigure(0, weight=1)
            header_frame.grid_rowconfigure(0, weight=1)
            
            # Título responsivo
            title = ctk.CTkLabel(
                header_frame,
                text="🏪 PANADERÍA RUSTIGONE",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="white"
            )
            title.grid(row=0, column=0, sticky="w", padx=20, pady=20)
            
            # Info usuario
            user_info = ctk.CTkLabel(
                header_frame,
                text=f"👤 {self.usuario['nombre']} | {self.usuario['rol'].upper()}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#ECF0F1"
            )
            user_info.grid(row=0, column=1, sticky="e", padx=20, pady=20)
            
            # Contenido principal responsivo
            content_frame = ctk.CTkFrame(main_frame, fg_color="white")
            content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
            content_frame.grid_columnconfigure(0, weight=1)
            content_frame.grid_rowconfigure(1, weight=1)
            
            # Título de módulos
            modules_title = ctk.CTkLabel(
                content_frame,
                text="📦 MÓDULOS DEL SISTEMA",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#2C3E50"
            )
            modules_title.grid(row=0, column=0, pady=20)
            
            # Frame de botones responsivo
            buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            buttons_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
            
            # Configurar grid responsivo para botones - 3 COLUMNAS, 3 FILAS
            for i in range(3):
                buttons_frame.grid_columnconfigure(i, weight=1, uniform="columns")
            for i in range(3):
                buttons_frame.grid_rowconfigure(i, weight=1, uniform="rows")
            
            # ✅ DISTRIBUCIÓN CORREGIDA - SOLO UN BOTÓN SALIR
            buttons_config = [
                # Fila 1
                ("🛒 VENTAS", "Punto de venta y facturación", self.open_ventas, 0, 0),
                ("📦 INVENTARIO", "Gestión de productos y stock", self.open_inventario, 0, 1),
                ("💰 CAJA/ARQUEO", "Control de caja y arqueos", self.open_caja, 0, 2),
                
                # Fila 2
                ("📋 COMPRAS", "Registro de compras a proveedores", self.open_compras, 1, 0),
                ("👥 PROVEEDORES", "Gestión de proveedores", self.open_proveedores, 1, 1),
                ("📊 REPORTES", "Reportes gerenciales avanzados", self.open_reportes, 1, 2),
                
                # Fila 3 - SOLO UN BOTÓN SALIR CENTRADO
                ("🚪 SALIR", "Salir del sistema", self.salir, 2, 1),
            ]
            
            # ✅ Solo agregar usuarios si es admin - REEMPLAZANDO UN BOTÓN EXISTENTE
            if self.usuario['rol'] == 'admin':
                # Reemplazar el botón de reportes con usuarios en fila 2, columna 2
                buttons_config[5] = ("👥 USUARIOS", "Gestión de usuarios del sistema", self.open_usuarios, 1, 2)
                # Agregar reportes en fila 3, columna 0
                buttons_config.append(("📊 REPORTES", "Reportes gerenciales avanzados", self.open_reportes, 2, 0))
                # Mover salir a columna 2
                buttons_config[6] = ("🚪 SALIR", "Salir del sistema", self.salir, 2, 2)
            
            # Crear todos los botones
            for text, description, command, row, col in buttons_config:
                self.create_module_button(buttons_frame, text, description, command, row, col)
            
            # Footer
            footer_frame = ctk.CTkFrame(main_frame, fg_color="#34495E", height=40)
            footer_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=(10, 0))
            
            footer_text = ctk.CTkLabel(
                footer_frame,
                text="© 2024 Panadería RUSTIGONE - Sistema de Gestión Integral",
                text_color="#BDC3C7",
                font=ctk.CTkFont(size=12)
            )
            footer_text.pack(pady=10)
            
            print("✅ Widgets responsivos creados correctamente")
            
        except Exception as e:
            print(f"❌ Error en create_widgets: {e}")
            traceback.print_exc()
            raise
    
    def create_module_button(self, parent, text, description, command, row, col):
        """Crear botón de módulo estilizado y responsivo"""
        try:
            button_frame = ctk.CTkFrame(parent, fg_color="transparent")
            button_frame.grid(row=row, column=col, sticky="nsew", padx=15, pady=15)
            button_frame.grid_columnconfigure(0, weight=1)
            button_frame.grid_rowconfigure(0, weight=1)
            button_frame.grid_rowconfigure(1, weight=0)
            
            # Botón responsivo que se expande
            button = ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                height=80,  # Altura fija pero ancho responsivo
                fg_color="#3498DB",
                hover_color="#2980B9",
                font=ctk.CTkFont(size=16, weight="bold"),
                anchor="center"
            )
            button.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            
            # Descripción
            description_label = ctk.CTkLabel(
                button_frame,
                text=description,
                text_color="#7F8C8D",
                font=ctk.CTkFont(size=11),
                wraplength=200,
                justify="center"
            )
            description_label.grid(row=1, column=0, sticky="nsew", padx=5, pady=(2, 5))
            
            return button
            
        except Exception as e:
            print(f"❌ Error creando botón {text}: {e}")
            raise
    
    def center_window(self, window, width, height):
        """Centrar ventana en la pantalla"""
        try:
            screen = screeninfo.get_monitors()[0]
            x = (screen.width - width) // 2
            y = (screen.height - height) // 2
            window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            # Fallback si screeninfo no funciona
            print(f"⚠️ screeninfo fallo al centrar ventana: {e}")
            window.update_idletasks()
            x = (window.winfo_screenwidth() - width) // 2
            y = (window.winfo_screenheight() - height) // 2
            window.geometry(f"{width}x{height}+{x}+{y}")
    
    def open_ventas(self):
        """Abrir módulo de ventas"""
        try:
            print("🛒 Abriendo módulo de ventas...")
            from ui.ventas_window import VentasWindow
            ventas_window = VentasWindow(self.parent, self.db, self.usuario)
            from ui.responsive import set_window_size_and_center
            set_window_size_and_center(ventas_window.window, width_percent=0.7, min_width=750, min_height=600, parent=self.parent)
        except Exception as e:
            error_msg = f"Error al abrir ventas: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            messagebox.showerror("Error", error_msg)
    
    def open_inventario(self):
        """Abrir módulo de inventario"""
        try:
            print("📦 Abriendo módulo de inventario...")
            from ui.inventario_window import InventarioWindow
            inventario_window = InventarioWindow(self.parent, self.db, self.usuario)
            from ui.responsive import set_window_size_and_center
            set_window_size_and_center(inventario_window.window, width_percent=0.75, min_width=800, min_height=650, parent=self.parent)
        except Exception as e:
            error_msg = f"Error al abrir inventario: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            messagebox.showerror("Error", error_msg)
    
    def open_caja(self):
        """Abrir módulo de caja/arqueo"""
        try:
            print("💰 Abriendo módulo de caja...")
            from ui.caja_window import CajaWindow
            caja_window = CajaWindow(self.parent, self.db, self.usuario)
            from ui.responsive import set_window_size_and_center
            set_window_size_and_center(caja_window.window, width_percent=0.7, min_width=750, min_height=650, parent=self.parent)
        except Exception as e:
            error_msg = f"Error al abrir caja: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            messagebox.showerror("Error", error_msg)
    
    def open_compras(self):
        """Abrir módulo de compras"""
        try:
            print("📋 Abriendo módulo de compras...")
            from ui.compras_window import ComprasWindow
            compras_window = ComprasWindow(self.parent, self.db, self.usuario)
            from ui.responsive import set_window_size_and_center
            set_window_size_and_center(compras_window.window, width_percent=0.7, min_width=750, min_height=600, parent=self.parent)
        except Exception as e:
            error_msg = f"Error al abrir compras: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            messagebox.showerror("Error", error_msg)
    
    def open_proveedores(self):
        """Abrir módulo de proveedores"""
        try:
            print("👥 Abriendo módulo de proveedores...")
            from ui.proveedores_window import ProveedoresWindow
            proveedores_window = ProveedoresWindow(self.parent, self.db, self.usuario)
            from ui.responsive import set_window_size_and_center
            set_window_size_and_center(proveedores_window.window, width_percent=0.75, min_width=800, min_height=650, parent=self.parent)
        except Exception as e:
            error_msg = f"Error al abrir proveedores: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            messagebox.showerror("Error", error_msg)
    
    def open_reportes(self):
        """Abrir módulo de reportes gerenciales"""
        try:
            print("📊 Abriendo módulo de reportes...")
            from ui.reportes_window import ReportesWindow
            reportes_window = ReportesWindow(self.parent, self.db, self.usuario)
            from ui.responsive import set_window_size_and_center
            set_window_size_and_center(reportes_window.window, width_percent=0.8, min_width=850, min_height=700, parent=self.parent)
        except Exception as e:
            error_msg = f"Error al abrir reportes: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            messagebox.showerror("Error", error_msg)
    
    def open_usuarios(self):
        """Abrir módulo de usuarios (solo admin)"""
        try:
            print("👥 Abriendo módulo de usuarios...")
            from ui.usuarios_window import UsuariosWindow
            usuarios_window = UsuariosWindow(self.parent, self.db, self.usuario)
            from ui.responsive import set_window_size_and_center
            set_window_size_and_center(usuarios_window.window, width_percent=0.7, min_width=750, min_height=550, parent=self.parent)
        except Exception as e:
            error_msg = f"Error al abrir usuarios: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            messagebox.showerror("Error", error_msg)
    
    def salir(self):
        """Salir del sistema"""
        if messagebox.askyesno("Salir", "¿Está seguro que desea salir del sistema?"):
            self.parent.quit()