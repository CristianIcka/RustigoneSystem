# ui/ventas_window.py - VERSIÓN MEJORADA Y COMPLETAMENTE ADAPTATIVA
import customtkinter as ctk
from datetime import datetime
import sqlite3
import os
import screeninfo
import tkinter as tk

class VentasWindow:
    def __init__(self, parent, db, usuario):
        self.parent = parent
        self.db = db
        self.usuario = usuario
        self.carrito = []
        self.total_venta = 0.0
        self.iva = 0.19  # 19% IVA
        
        # Crear ventana de ventas
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Módulo de Ventas - RUSTIGONE")
        
        # Configurar ventana responsiva
        self.setup_responsive_window()
        
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.actualizar_totales()
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
    
    def setup_responsive_window(self):
        """Configurar ventana responsiva para cualquier monitor"""
        try:
            # Usar helper centralizado para tamaño y centrado
            from ui.responsive import set_window_size_and_center
            set_window_size_and_center(self.window, width_percent=0.8, min_width=1000, min_height=700, parent=self.parent)
            # Hacer ventana responsiva
            self.window.minsize(1000, 700)
            self.window.grid_columnconfigure(0, weight=1)
            self.window.grid_rowconfigure(0, weight=1)
            
        except Exception as e:
            print(f"⚠️ Error configurando ventana responsiva: {e}")
            # Intentar usar helper de centrado, si falla usar geometry como fallback
            try:
                from ui.responsive import set_window_size_and_center
                set_window_size_and_center(self.window, width_percent=0.8, min_width=1000, min_height=700, parent=self.parent)
            except Exception as e2:
                print(f"⚠️ Fallback al geometry: {e2}")
                self.window.geometry("1200x800")
                self.center_window(self.window, 1200, 800, self.parent)
    
    def get_primary_monitor(self):
        """Obtener información del monitor primario"""
        try:
            return screeninfo.get_monitors()[0]
        except Exception as e:
            # Fallback si screeninfo no funciona
            print(f"⚠️ screeninfo fallo: {e}")
            root = tk.Tk()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()
            return type('Monitor', (), {'width': width, 'height': height})()
    
    def center_window(self, window, width, height, parent=None):
        """Centrar ventana en el monitor"""
        try:
            if parent and parent.winfo_exists():
                # Centrar respecto a la ventana padre
                x = parent.winfo_x() + (parent.winfo_width() - width) // 2
                y = parent.winfo_y() + (parent.winfo_height() - height) // 2
            else:
                # Centrar en el monitor principal
                monitor = self.get_primary_monitor()
                x = (monitor.width - width) // 2
                y = (monitor.height - height) // 2
            
            window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            print(f"⚠️ Error centrando ventana: {e}")
            # Fallback
            window.geometry(f"{width}x{height}")
    
    def create_widgets(self):
        """Crear interfaz completa de ventas con diseño responsivo"""
        # Frame principal con grid responsivo
        main_frame = ctk.CTkFrame(self.window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurar grid responsivo
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Título
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        title = ctk.CTkLabel(
            title_frame,
            text="🏪 MÓDULO DE VENTAS",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#2B6CB0"
        )
        title.pack(pady=10)
        
        # Frame de búsqueda y entrada
        search_frame = ctk.CTkFrame(main_frame, fg_color="#F7FAFC", corner_radius=10)
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(1, weight=1)  # Entrada de búsqueda expandible
        
        # Entrada de código de barras
        ctk.CTkLabel(
            search_frame, 
            text="Código de Barras:",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.codigo_entry = ctk.CTkEntry(
            search_frame,
            height=40,
            placeholder_text="Escanear código o ingresar manualmente"
        )
        self.codigo_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.codigo_entry.bind("<Return>", self.buscar_producto)
        
        # Botón buscar
        self.buscar_btn = ctk.CTkButton(
            search_frame,
            text="Buscar Producto",
            command=self.buscar_producto,
            fg_color="#2B6CB0"
        )
        self.buscar_btn.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        
        # Frame principal dividido
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.grid(row=2, column=0, sticky="nsew")
        
        # Configurar grid responsivo para contenido
        content_frame.grid_columnconfigure(0, weight=3)  # Left frame más ancho
        content_frame.grid_columnconfigure(1, weight=1)  # Right frame menos ancho
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Left - Información producto y carrito
        left_frame = ctk.CTkFrame(content_frame, fg_color="white")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)  # Carrito expandible
        
        # Información del producto
        product_frame = ctk.CTkFrame(left_frame, fg_color="#EDF2F7", corner_radius=10)
        product_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        product_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            product_frame,
            text="INFORMACIÓN DEL PRODUCTO",
            font=ctk.CTkFont(weight="bold", size=16),
            text_color="#2D3748"
        ).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Grid de información del producto
        info_grid = ctk.CTkFrame(product_frame, fg_color="transparent")
        info_grid.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        info_grid.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(info_grid, text="Nombre:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.nombre_label = ctk.CTkLabel(info_grid, text="-", text_color="#4A5568")
        self.nombre_label.grid(row=0, column=1, sticky="w", pady=5, padx=(10, 0))
        
        ctk.CTkLabel(info_grid, text="Precio:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.precio_label = ctk.CTkLabel(info_grid, text="$0", text_color="#2B6CB0", font=ctk.CTkFont(weight="bold"))
        self.precio_label.grid(row=1, column=1, sticky="w", pady=5, padx=(10, 0))
        
        ctk.CTkLabel(info_grid, text="Stock:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.stock_label = ctk.CTkLabel(info_grid, text="0", text_color="#38A169")
        self.stock_label.grid(row=2, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Cantidad a agregar
        ctk.CTkLabel(info_grid, text="Cantidad:", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, sticky="w", pady=5)
        self.cantidad_var = ctk.StringVar(value="1")
        self.cantidad_entry = ctk.CTkEntry(
            info_grid,
            textvariable=self.cantidad_var
        )
        self.cantidad_entry.grid(row=3, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Botón agregar al carrito
        self.agregar_btn = ctk.CTkButton(
            product_frame,
            text="Agregar al Carrito",
            command=self.agregar_al_carrito,
            height=45,
            fg_color="#38A169",
            font=ctk.CTkFont(weight="bold"),
            state="disabled"
        )
        self.agregar_btn.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        
        # Carrito de compras
        carrito_container = ctk.CTkFrame(left_frame, fg_color="transparent")
        carrito_container.grid(row=1, column=0, sticky="nsew")
        carrito_container.grid_columnconfigure(0, weight=1)
        carrito_container.grid_rowconfigure(0, weight=1)
        
        ctk.CTkLabel(
            carrito_container,
            text="🛒 CARRITO DE COMPRA",
            font=ctk.CTkFont(weight="bold", size=16),
            text_color="#2D3748"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Treeview del carrito
        self.carrito_tree = ctk.CTkScrollableFrame(carrito_container, fg_color="white")
        self.carrito_tree.grid(row=1, column=0, sticky="nsew")
        carrito_container.grid_rowconfigure(1, weight=1)
        carrito_container.grid_columnconfigure(0, weight=1)
        
        # Right - Resumen y pago
        right_frame = ctk.CTkFrame(content_frame, fg_color="#F7FAFC")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(2, weight=1)  # Espacio para botones
        
        ctk.CTkLabel(
            right_frame,
            text="RESUMEN DE VENTA",
            font=ctk.CTkFont(weight="bold", size=18),
            text_color="#2D3748"
        ).grid(row=0, column=0, pady=20)
        
        # Información de totales
        totals_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        totals_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        totals_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(totals_frame, text="Subtotal:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", pady=8)
        self.subtotal_label = ctk.CTkLabel(totals_frame, text="$0", font=ctk.CTkFont(weight="bold"))
        self.subtotal_label.grid(row=0, column=1, sticky="e", pady=8)
        
        ctk.CTkLabel(totals_frame, text="IVA (19%):", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", pady=8)
        self.iva_label = ctk.CTkLabel(totals_frame, text="$0", font=ctk.CTkFont(weight="bold"))
        self.iva_label.grid(row=1, column=1, sticky="e", pady=8)
        
        ctk.CTkLabel(totals_frame, text="TOTAL:", font=ctk.CTkFont(weight="bold", size=16)).grid(row=2, column=0, sticky="w", pady=12)
        self.total_label = ctk.CTkLabel(totals_frame, text="$0", font=ctk.CTkFont(weight="bold", size=16), text_color="#2B6CB0")
        self.total_label.grid(row=2, column=1, sticky="e", pady=12)
        
        # Medio de pago
        ctk.CTkLabel(
            right_frame,
            text="Medio de Pago:",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=2, column=0, pady=(20, 5), sticky="w", padx=20)
        
        self.medio_pago = ctk.CTkComboBox(
            right_frame,
            values=["EFECTIVO", "DÉBITO", "CRÉDITO"],
            height=40
        )
        self.medio_pago.set("EFECTIVO")
        self.medio_pago.grid(row=3, column=0, sticky="ew", pady=5, padx=20)
        
        # Botones de acción
        button_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, sticky="ew", pady=20, padx=20)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        button_frame.grid_rowconfigure(2, weight=1)
        
        self.pagar_btn = ctk.CTkButton(
            button_frame,
            text="💳 PAGAR",
            command=self.procesar_pago,
            height=50,
            fg_color="#2B6CB0",
            font=ctk.CTkFont(weight="bold", size=16)
        )
        self.pagar_btn.grid(row=0, column=0, sticky="ew", pady=5)
        
        self.limpiar_btn = ctk.CTkButton(
            button_frame,
            text="🔄 LIMPIAR",
            command=self.limpiar_carrito,
            height=40,
            fg_color="#38A169",
            font=ctk.CTkFont(weight="bold")
        )
        self.limpiar_btn.grid(row=1, column=0, sticky="ew", pady=5)
        
        self.cancelar_btn = ctk.CTkButton(
            button_frame,
            text="❌ CANCELAR",
            command=self.window.destroy,
            height=40,
            fg_color="#E53E3E",
            font=ctk.CTkFont(weight="bold")
        )
        self.cancelar_btn.grid(row=2, column=0, sticky="ew", pady=5)
        
        # Producto actual
        self.producto_actual = None

    # ... (el resto de los métodos se mantienen igual: buscar_producto, mostrar_producto, etc.)
    # Solo se modifica la estructura de la ventana principal, la funcionalidad es la misma

    def buscar_producto(self, event=None):
        """Buscar producto por código de barras"""
        codigo = self.codigo_entry.get().strip()
        if not codigo:
            self.mostrar_error("Ingrese un código de barras")
            return
            
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, c.nombre as categoria_nombre 
                FROM productos p 
                LEFT JOIN categorias c ON p.categoria_id = c.id 
                WHERE p.codigo_barras = ? AND p.activo = 1
            ''', (codigo,))
            
            producto = cursor.fetchone()
            conn.close()
            
            if producto:
                self.producto_actual = dict(producto)
                self.mostrar_producto(self.producto_actual)
                self.cantidad_entry.focus()
                self.agregar_btn.configure(state="normal")
            else:
                self.mostrar_error("Producto no encontrado")
                self.limpiar_producto()
                
        except Exception as e:
            self.mostrar_error(f"Error al buscar producto: {str(e)}")

    def mostrar_producto(self, producto):
        """Mostrar información del producto encontrado"""
        self.nombre_label.configure(text=producto['nombre'])
        self.precio_label.configure(text=f"${producto['precio_venta']:,.0f}")
        self.stock_label.configure(text=f"{producto['stock_actual']} {producto['unidad_medida']}")
        
        # Configurar cantidad máxima
        self.cantidad_var.set("1")

    def limpiar_producto(self):
        """Limpiar información del producto"""
        self.producto_actual = None
        self.nombre_label.configure(text="-")
        self.precio_label.configure(text="$0")
        self.stock_label.configure(text="0")
        self.cantidad_var.set("1")
        self.agregar_btn.configure(state="disabled")
        self.codigo_entry.delete(0, 'end')
        self.codigo_entry.focus()

    def agregar_al_carrito(self):
        """Agregar producto al carrito"""
        if not self.producto_actual:
            self.mostrar_error("No hay producto seleccionado")
            return
            
        try:
            cantidad = float(self.cantidad_var.get())
            if cantidad <= 0:
                self.mostrar_error("La cantidad debe ser mayor a 0")
                return
                
            if cantidad > self.producto_actual['stock_actual']:
                self.mostrar_error(f"Stock insuficiente. Disponible: {self.producto_actual['stock_actual']}")
                return
            
            # Calcular subtotal
            subtotal = cantidad * self.producto_actual['precio_venta']
            
            # Agregar al carrito
            item_carrito = {
                'id': self.producto_actual['id'],
                'codigo_barras': self.producto_actual['codigo_barras'],
                'nombre': self.producto_actual['nombre'],
                'precio': self.producto_actual['precio_venta'],
                'cantidad': cantidad,
                'subtotal': subtotal,
                'unidad_medida': self.producto_actual['unidad_medida']
            }
            
            self.carrito.append(item_carrito)
            self.actualizar_carrito_tree()
            self.actualizar_totales()
            self.limpiar_producto()
            
        except ValueError:
            self.mostrar_error("Cantidad inválida")

    def actualizar_carrito_tree(self):
        """Actualizar la visualización del carrito"""
        # Limpiar treeview anterior
        for widget in self.carrito_tree.winfo_children():
            widget.destroy()
        
        if not self.carrito:
            # Mostrar mensaje de carrito vacío
            empty_label = ctk.CTkLabel(
                self.carrito_tree,
                text="Carrito vacío",
                text_color="#A0AEC0",
                font=ctk.CTkFont(size=14)
            )
            empty_label.pack(expand=True)
            return
        
        # Crear headers
        headers_frame = ctk.CTkFrame(self.carrito_tree, fg_color="transparent")
        headers_frame.pack(fill="x", pady=(0, 10))
        
        headers = ["Producto", "Cant", "Precio", "Subtotal", ""]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                text_color="#2D3748"
            )
            if i == 0:
                label.pack(side="left", padx=5, pady=5, fill="x", expand=True)
            else:
                label.pack(side="left", padx=5, pady=5)
        
        # Agregar items
        for idx, item in enumerate(self.carrito):
            item_frame = ctk.CTkFrame(self.carrito_tree, fg_color="white")
            item_frame.pack(fill="x", pady=2)
            
            # Nombre del producto
            nombre_label = ctk.CTkLabel(
                item_frame,
                text=item['nombre'],
                text_color="#4A5568"
            )
            nombre_label.pack(side="left", padx=5, pady=5, fill="x", expand=True)
            
            # Cantidad
            cant_label = ctk.CTkLabel(
                item_frame,
                text=f"{item['cantidad']} {item['unidad_medida']}",
                text_color="#4A5568"
            )
            cant_label.pack(side="left", padx=5, pady=5)
            
            # Precio unitario
            precio_label = ctk.CTkLabel(
                item_frame,
                text=f"${item['precio']:,.0f}",
                text_color="#4A5568"
            )
            precio_label.pack(side="left", padx=5, pady=5)
            
            # Subtotal
            subtotal_label = ctk.CTkLabel(
                item_frame,
                text=f"${item['subtotal']:,.0f}",
                text_color="#2B6CB0",
                font=ctk.CTkFont(weight="bold")
            )
            subtotal_label.pack(side="left", padx=5, pady=5)
            
            # Botón eliminar
            eliminar_btn = ctk.CTkButton(
                item_frame,
                text="❌",
                fg_color="transparent",
                hover_color="#FED7D7",
                text_color="#E53E3E",
                command=lambda i=idx: self.eliminar_del_carrito(i)
            )
            eliminar_btn.pack(side="left", padx=5, pady=5)

    def eliminar_del_carrito(self, index):
        """Eliminar item del carrito"""
        if 0 <= index < len(self.carrito):
            self.carrito.pop(index)
            self.actualizar_carrito_tree()
            self.actualizar_totales()

    def actualizar_totales(self):
        """Actualizar totales de la venta"""
        subtotal = sum(item['subtotal'] for item in self.carrito)
        iva = subtotal * self.iva
        total = subtotal
        
        self.subtotal_label.configure(text=f"${subtotal:,.0f}")
        self.iva_label.configure(text=f"${iva:,.0f}")
        self.total_label.configure(text=f"${total:,.0f}")
        
        self.total_venta = total
        
        # Habilitar/deshabilitar botón pagar
        self.pagar_btn.configure(state="normal" if self.carrito else "disabled")

    def procesar_pago(self):
        """Procesar el pago de la venta"""
        if not self.carrito:
            self.mostrar_error("El carrito está vacío")
            return
            
        medio_pago = self.medio_pago.get()
        
        # Si es efectivo, solicitar monto pagado
        if medio_pago == "EFECTIVO":
            self.solicitar_monto_efectivo()
        else:
            # Para tarjetas, confirmar directamente
            self.confirmar_pago_tarjeta(medio_pago)
#*************************************************************************
    def solicitar_monto_efectivo(self):
        """Solicitar monto pagado en efectivo - LAYOUT CON PACK"""
        # Crear ventana para ingresar monto
        self.monto_window = ctk.CTkToplevel(self.window)
        self.monto_window.title("Pago en Efectivo")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(self.monto_window, width_percent=0.35, min_width=380, min_height=420, parent=self.window)
        self.monto_window.transient(self.window)
        self.monto_window.grab_set()
        
        # ✅ CONFIGURACIÓN CON PACK - MÁS ROBUSTA
        main_frame = ctk.CTkFrame(self.monto_window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título en la parte superior
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            title_frame,
            text="💵 PAGO EN EFECTIVO",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#2D3748"
        ).pack(pady=10)
        
        # Información del total
        total_frame = ctk.CTkFrame(main_frame, fg_color="#F7FAFC", corner_radius=10)
        total_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            total_frame,
            text="Total a pagar:",
            font=ctk.CTkFont(weight="bold", size=16)
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            total_frame,
            text=f"${self.total_venta:,.0f}",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#2B6CB0"
        ).pack(pady=(5, 15))
        
        # Entrada de monto
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            input_frame,
            text="Monto recibido:",
            font=ctk.CTkFont(weight="bold", size=14)
        ).pack(pady=(0, 10))
        
        self.monto_recibido_var = ctk.StringVar()
        self.monto_entry = ctk.CTkEntry(
            input_frame,
            height=50,
            placeholder_text="Ingrese monto recibido",
            textvariable=self.monto_recibido_var,
            font=ctk.CTkFont(size=18),
            justify="center"
        )
        self.monto_entry.pack(fill="x", pady=(0, 10))
        self.monto_entry.bind("<Return>", lambda e: self.calcular_vuelto())
        self.monto_entry.focus()
        
        # Botón calcular vuelto
        calcular_btn = ctk.CTkButton(
            input_frame,
            text="🔢 CALCULAR VUELTO",
            command=self.calcular_vuelto,
            height=50,
            fg_color="#38A169",
            font=ctk.CTkFont(weight="bold", size=14)
        )
        calcular_btn.pack(fill="x", pady=(0, 15))
        
        # Etiqueta para mostrar vuelto
        self.vuelto_label = ctk.CTkLabel(
            input_frame,
            text="Ingrese monto y calcule vuelto",
            font=ctk.CTkFont(size=16),
            text_color="#718096",
            wraplength=450
        )
        self.vuelto_label.pack(pady=10)
        
        # ✅ BOTONES EN LA PARTE INFERIOR - SIEMPRE VISIBLES
        # Espacio flexible que empuja los botones hacia abajo
        ctk.CTkLabel(main_frame, text="", height=10).pack(fill="x")
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", side="bottom", pady=(20, 0))
        
        # Botones uno al lado del otro
        self.confirmar_efectivo_btn = ctk.CTkButton(
            button_frame,
            text="✅ CONFIRMAR PAGO",
            command=self.confirmar_pago_efectivo,
            height=50,
            fg_color="#2B6CB0",
            font=ctk.CTkFont(weight="bold", size=14),
            state="disabled"
        )
        self.confirmar_efectivo_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        cancelar_btn = ctk.CTkButton(
            button_frame,
            text="❌ CANCELAR",
            command=self.monto_window.destroy,
            height=50,
            fg_color="#E53E3E",
            font=ctk.CTkFont(weight="bold", size=14)
        )
        cancelar_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

    def calcular_vuelto(self):
        """Calcular y mostrar el vuelto"""
        try:
            monto_texto = self.monto_recibido_var.get().strip()
            if not monto_texto:
                self.vuelto_label.configure(
                    text="Ingrese un monto válido",
                    text_color="#E53E3E"
                )
                self.confirmar_efectivo_btn.configure(state="disabled")
                return
                
            # Convertir a número
            monto_texto = monto_texto.replace(',', '').replace('.', '')
            monto_recibido = float(monto_texto)
            vuelto = monto_recibido - self.total_venta
            
            if monto_recibido <= 0:
                self.vuelto_label.configure(
                    text="Monto debe ser mayor a 0",
                    text_color="#E53E3E"
                )
                self.confirmar_efectivo_btn.configure(state="disabled")
            elif vuelto < 0:
                self.vuelto_label.configure(
                    text=f"Faltan: ${abs(vuelto):,.0f}",
                    text_color="#E53E3E",
                    font=ctk.CTkFont(weight="bold")
                )
                self.confirmar_efectivo_btn.configure(state="disabled")
            else:
                self.vuelto_label.configure(
                    text=f"Vuelto: ${vuelto:,.0f}",
                    text_color="#38A169",
                    font=ctk.CTkFont(weight="bold", size=18)
                )
                self.confirmar_efectivo_btn.configure(state="normal")
                
        except ValueError:
            self.vuelto_label.configure(
                text="Monto inválido - use solo números",
                text_color="#E53E3E"
            )
            self.confirmar_efectivo_btn.configure(state="disabled")

    def confirmar_pago_efectivo(self):
        """Confirmar pago en efectivo y registrar venta"""
        try:
            monto_recibido = float(self.monto_recibido_var.get().replace(',', '').replace('.', ''))
            vuelto = monto_recibido - self.total_venta
            
            if vuelto < 0:
                self.mostrar_error("El monto recibido es insuficiente")
                return
                
            # Cerrar ventana de monto
            self.monto_window.destroy()
            
            # Registrar la venta
            self.registrar_venta("EFECTIVO", monto_recibido, vuelto)
            
        except ValueError:
            self.mostrar_error("Monto recibido inválido")

    def confirmar_pago_tarjeta(self, medio_pago):
        """Confirmar pago con tarjeta - VERSIÓN CORREGIDA CON BOTONES VISIBLES"""
        # Mostrar confirmación antes de procesar
        confirm_window = ctk.CTkToplevel(self.window)
        confirm_window.title(f"Confirmar Pago con {medio_pago}")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(confirm_window, width_percent=0.35, min_width=380, min_height=420, parent=self.window)
        confirm_window.transient(self.window)
        confirm_window.grab_set()
        
        # ✅ CONFIGURAR LA VENTANA PARA QUE SEA RESPONSIVA
        confirm_window.grid_columnconfigure(0, weight=1)
        confirm_window.grid_rowconfigure(0, weight=1)
        
        # Frame principal que ocupa toda la ventana
        main_frame = ctk.CTkFrame(confirm_window, fg_color="white")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # ✅ CONFIGURAR GRID RESPONSIVO EN MAIN_FRAME
        main_frame.grid_columnconfigure(0, weight=1)
        # Configurar filas: contenido arriba, espacio flexible, botones abajo
        main_frame.grid_rowconfigure(0, weight=0)  # Título
        main_frame.grid_rowconfigure(1, weight=0)  # Icono
        main_frame.grid_rowconfigure(2, weight=0)  # Total
        main_frame.grid_rowconfigure(3, weight=0)  # Info
        main_frame.grid_rowconfigure(4, weight=1)  # ESPACIO FLEXIBLE (importante)
        main_frame.grid_rowconfigure(5, weight=0)  # Botones (fijos en la parte inferior)
        
        # Título (fila 0)
        ctk.CTkLabel(
            main_frame,
            text=f"💳 PAGO CON {medio_pago}",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#2B6CB0"
        ).grid(row=0, column=0, pady=(0, 15))
        
        # Icono (fila 1)
        icono = "💳" if medio_pago == "CRÉDITO" else "💳"
        ctk.CTkLabel(
            main_frame,
            text=icono,
            font=ctk.CTkFont(size=50)
        ).grid(row=1, column=0, pady=(0, 20))
        
        # Monto total (fila 2)
        total_frame = ctk.CTkFrame(main_frame, fg_color="#F7FAFC", corner_radius=10)
        total_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        total_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            total_frame,
            text="Total a pagar:",
            font=ctk.CTkFont(weight="bold", size=16)
        ).grid(row=0, column=0, pady=(12, 5))
        
        ctk.CTkLabel(
            total_frame,
            text=f"${self.total_venta:,.0f}",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#2B6CB0"
        ).grid(row=1, column=0, pady=(5, 12))
        
        # Información adicional (fila 3)
        info_frame = ctk.CTkFrame(main_frame, fg_color="#EDF2F7", corner_radius=10)
        info_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        info_frame.grid_columnconfigure(0, weight=1)
        
        info_text = f"""
• Productos: {len(self.carrito)}
• Medio de pago: {medio_pago}
• Vendedor: {self.usuario['nombre']}
• Fecha: {datetime.now().strftime('%H:%M:%S')}
"""
        
        ctk.CTkLabel(
            info_frame,
            text=info_text.strip(),
            font=ctk.CTkFont(size=14),
            justify="left"
        ).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # ✅ ESPACIO FLEXIBLE QUE EMPUJA LOS BOTONES HACIA ABAJO (fila 4)
        # Esta fila tiene weight=1 y se expande para ocupar el espacio sobrante
        spacer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        spacer_frame.grid(row=4, column=0, sticky="nsew")
        
        # ✅ BOTONES EN LA PARTE INFERIOR (fila 5) - SIEMPRE VISIBLES
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, sticky="ew", pady=(20, 0))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Botón confirmar (ocupa columna 0)
        confirmar_btn = ctk.CTkButton(
            button_frame,
            text="✅ CONFIRMAR PAGO",
            command=lambda: self.procesar_confirmacion_tarjeta(confirm_window, medio_pago),
            height=50,
            fg_color="#38A169",
            font=ctk.CTkFont(weight="bold", size=14)
        )
        confirmar_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Botón cancelar (ocupa columna 1)
        cancelar_btn = ctk.CTkButton(
            button_frame,
            text="❌ CANCELAR",
            command=confirm_window.destroy,
            height=50,
            fg_color="#E53E3E",
            font=ctk.CTkFont(weight="bold", size=14)
        )
        cancelar_btn.grid(row=0, column=1, sticky="ew", padx=(10, 0))
    def registrar_venta(self, medio_pago, monto_recibido=0, vuelto=0):
        """Registrar la venta en la base de datos"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Registrar venta
            cursor.execute('''
                INSERT INTO ventas (usuario_id, total, iva, medio_pago, monto_recibido, vuelto, fecha_venta)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.usuario['id'], self.total_venta, self.total_venta * self.iva, 
                  medio_pago, monto_recibido, vuelto, datetime.now()))
            
            venta_id = cursor.lastrowid
            
            # Registrar detalles de venta y actualizar stock
            for item in self.carrito:
                cursor.execute('''
                    INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                ''', (venta_id, item['id'], item['cantidad'], item['precio'], item['subtotal']))
                
                # Actualizar stock
                cursor.execute('''
                    UPDATE productos 
                    SET stock_actual = stock_actual - ?, 
                        fecha_ultima_venta = ?
                    WHERE id = ?
                ''', (item['cantidad'], datetime.now(), item['id']))
            
            conn.commit()
            conn.close()
            
            # Mostrar resumen de la venta
            self.mostrar_resumen_venta(medio_pago, monto_recibido, vuelto)
            
        except Exception as e:
            self.mostrar_error(f"Error al procesar venta: {str(e)}")

    def procesar_confirmacion_tarjeta(self, confirm_window, medio_pago):
        """Procesar la confirmación de pago con tarjeta"""
        confirm_window.destroy()
        self.registrar_venta(medio_pago, self.total_venta, 0)

    def mostrar_resumen_venta(self, medio_pago, monto_recibido=0, vuelto=0):
        """Mostrar resumen completo de la venta - LAYOUT CON PACK"""
        resumen_window = ctk.CTkToplevel(self.window)
        resumen_window.title("Resumen de Venta")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(resumen_window, width_percent=0.4, min_width=450, min_height=550, parent=self.window)
        resumen_window.transient(self.window)
        resumen_window.grab_set()
        
        # ✅ CONFIGURACIÓN CON PACK
        main_frame = ctk.CTkFrame(resumen_window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            title_frame,
            text="✅ VENTA EXITOSA",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#38A169"
        ).pack(pady=10)
        
        # Frame de detalles principales
        detalles_frame = ctk.CTkFrame(main_frame, fg_color="#F7FAFC", corner_radius=10)
        detalles_frame.pack(fill="x", pady=(0, 15))
        
        # Información de la venta
        info_text = f"""
📦 Productos vendidos: {len(self.carrito)}
💰 Total venta: ${self.total_venta:,.0f}
📊 IVA (19%): ${self.total_venta * self.iva:,.0f}
💳 Medio de pago: {medio_pago}
"""
        
        if medio_pago == "EFECTIVO":
            info_text += f"""
💵 Monto recibido: ${monto_recibido:,.0f}
🔄 Vuelto: ${vuelto:,.0f}
"""
        
        info_text += f"""
👤 Vendedor: {self.usuario['nombre']}
🕒 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        ctk.CTkLabel(
            detalles_frame,
            text=info_text.strip(),
            font=ctk.CTkFont(size=14),
            justify="left"
        ).pack(padx=20, pady=20, fill="x")
        
        # Detalle de productos
        productos_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        productos_container.pack(fill="both", expand=True, pady=(0, 15))
        
        ctk.CTkLabel(
            productos_container,
            text="📋 DETALLE DE PRODUCTOS:",
            font=ctk.CTkFont(weight="bold", size=14),
            text_color="#2D3748"
        ).pack(anchor="w", pady=(0, 10))
        
        # Frame scrollable para productos
        productos_scroll = ctk.CTkScrollableFrame(
            productos_container, 
            fg_color="#EDF2F7", 
            corner_radius=10,
            height=200  # ✅ Altura fija para el área de productos
        )
        productos_scroll.pack(fill="both", expand=True)
        
        for item in self.carrito:
            producto_frame = ctk.CTkFrame(productos_scroll, fg_color="white", corner_radius=5)
            producto_frame.pack(fill="x", pady=2, padx=5)
            
            producto_text = f"• {item['nombre']} - {item['cantidad']} {item['unidad_medida']} x ${item['precio']:,.0f} = ${item['subtotal']:,.0f}"
            ctk.CTkLabel(
                producto_frame,
                text=producto_text,
                font=ctk.CTkFont(size=12),
                text_color="#4A5568"
            ).pack(padx=10, pady=5, anchor="w")
        
        # ✅ BOTONES EN LA PARTE INFERIOR - SIEMPRE VISIBLES
        # Espacio flexible que empuja los botones hacia abajo
        ctk.CTkLabel(main_frame, text="", height=10).pack(fill="x")
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", side="bottom", pady=(20, 0))
        
        # Botones en columna
        imprimir_btn = ctk.CTkButton(
            button_frame,
            text="🖨️ IMPRIMIR TICKET",
            command=lambda: self.imprimir_ticket(medio_pago, monto_recibido, vuelto),
            height=45,
            fg_color="#2B6CB0",
            font=ctk.CTkFont(weight="bold", size=14)
        )
        imprimir_btn.pack(fill="x", pady=5)
        
        nueva_venta_btn = ctk.CTkButton(
            button_frame,
            text="🔄 NUEVA VENTA",
            command=lambda: self.finalizar_venta(resumen_window),
            height=45,
            fg_color="#38A169",
            font=ctk.CTkFont(weight="bold", size=14)
        )
        nueva_venta_btn.pack(fill="x", pady=5)
        
        reportes_btn = ctk.CTkButton(
            button_frame,
            text="📊 VER REPORTES",
            command=self.abrir_reportes,
            height=45,
            fg_color="#D69E2E",
            font=ctk.CTkFont(weight="bold", size=14)
        )
        reportes_btn.pack(fill="x", pady=5)
        
        cerrar_btn = ctk.CTkButton(
            button_frame,
            text="❌ CERRAR",
            command=resumen_window.destroy,
            height=40,
            fg_color="#718096",
            font=ctk.CTkFont(weight="bold")
        )
        cerrar_btn.pack(fill="x", pady=5)

    def finalizar_venta(self, resumen_window):
        """Finalizar venta y limpiar todo"""
        resumen_window.destroy()
        self.limpiar_carrito()

    def imprimir_ticket(self, medio_pago, monto_recibido, vuelto):
        """Imprimir ticket de venta"""
        try:
            # Crear contenido del ticket
            ticket_content = f"""
{'='*40}
          PANADERÍA RUSTIGONE
{'='*40}
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Vendedor: {self.usuario['nombre']}
{'='*40}
PRODUCTOS:
"""
            
            for item in self.carrito:
                ticket_content += f"{item['nombre'][:20]:20} {item['cantidad']:>4} {item['unidad_medida']:>3} ${item['subtotal']:>7,.0f}\n"
            
            ticket_content += f"""
{'='*40}
Subtotal: ${self.total_venta:,.0f}
IVA (19%): ${self.total_venta * self.iva:,.0f}
Medio pago: {medio_pago}
"""
            
            if medio_pago == "EFECTIVO":
                ticket_content += f"""
Monto recibido: ${monto_recibido:,.0f}
Vuelto: ${vuelto:,.0f}
"""
            
            ticket_content += f"""
{'='*40}
     ¡GRACIAS POR SU COMPRA!
{'='*40}
"""
            
            # Guardar ticket en archivo
            filename = f"ticket_venta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(ticket_content)
            
            self.mostrar_exito(f"Ticket guardado como: {filename}\nPuede imprimirlo desde el archivo.")
            
        except Exception as e:
            self.mostrar_error(f"Error al generar ticket: {str(e)}")

    def abrir_reportes(self):
        """Abrir módulo de reportes"""
        self.mostrar_info("Reportes", "Redirigiendo al módulo de reportes...")

    def limpiar_carrito(self):
        """Limpiar todo el carrito"""
        self.carrito = []
        self.actualizar_carrito_tree()
        self.actualizar_totales()
        self.limpiar_producto()

    def mostrar_error(self, mensaje):
        """Mostrar mensaje de error"""
        error_window = ctk.CTkToplevel(self.window)
        error_window.title("Error")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(error_window, width_percent=0.25, min_width=300, min_height=150, parent=self.window)
        error_window.transient(self.window)
        error_window.grab_set()
        
        ctk.CTkLabel(error_window, text="❌ " + mensaje, 
                    font=ctk.CTkFont(weight="bold")).pack(expand=True, pady=20)
        ctk.CTkButton(error_window, text="Aceptar", 
                     command=error_window.destroy).pack(pady=10)

    def mostrar_exito(self, mensaje):
        """Mostrar mensaje de éxito"""
        exito_window = ctk.CTkToplevel(self.window)
        exito_window.title("Éxito")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(exito_window, width_percent=0.25, min_width=300, min_height=150, parent=self.window)
        exito_window.transient(self.window)
        exito_window.grab_set()
        
        ctk.CTkLabel(exito_window, text="✅ " + mensaje, 
                    font=ctk.CTkFont(weight="bold")).pack(expand=True, pady=20)
        ctk.CTkButton(exito_window, text="Aceptar", 
                     command=exito_window.destroy).pack(pady=10)

    def mostrar_info(self, titulo, mensaje):
        """Mostrar mensaje informativo"""
        info_window = ctk.CTkToplevel(self.window)
        info_window.title(titulo)
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(info_window, width_percent=0.25, min_width=300, min_height=150, parent=self.window)
        info_window.transient(self.window)
        info_window.grab_set()
        
        ctk.CTkLabel(info_window, text="ℹ️ " + mensaje,
                    font=ctk.CTkFont(weight="bold")).pack(expand=True, pady=20)
        ctk.CTkButton(info_window, text="Aceptar",
                     command=info_window.destroy).pack(pady=10)