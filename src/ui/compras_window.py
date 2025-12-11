# ui/compras_window.py
import customtkinter as ctk
from datetime import datetime
import sqlite3

class ComprasWindow:
    def __init__(self, parent, db, usuario):
        self.parent = parent
        self.db = db
        self.usuario = usuario
        self.productos_factura = []
        
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Módulo de Compras - RUSTIGONE")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(self.window, width_percent=0.75, min_width=800, min_height=650, parent=parent)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        # Estado de maximización
        self._is_maximized = False
        # Botón maximizar/restaurar
        self.maximize_btn = ctk.CTkButton(self.window, text="🗖", width=40, height=30, command=self.toggle_maximize, fg_color="#D69E2E", text_color="white")
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
        """Crear interfaz de compras"""
        main_frame = ctk.CTkFrame(self.window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title = ctk.CTkLabel(
            main_frame,
            text="🛒 MÓDULO DE COMPRAS",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#D69E2E"
        )
        title.pack(pady=20)
        
        # Frame de información de factura
        factura_frame = ctk.CTkFrame(main_frame, fg_color="#F7FAFC", corner_radius=10)
        factura_frame.pack(fill="x", pady=(0, 20))
        
        # Información de la factura
        info_frame = ctk.CTkFrame(factura_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(info_frame, text="N° Factura:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.factura_entry = ctk.CTkEntry(info_frame, width=150)
        self.factura_entry.grid(row=0, column=1, sticky="w", pady=5, padx=(10, 30))
        
        ctk.CTkLabel(info_frame, text="Proveedor:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, sticky="w", pady=5)
        self.proveedor_entry = ctk.CTkEntry(info_frame, width=200)
        self.proveedor_entry.grid(row=0, column=3, sticky="w", pady=5, padx=(10, 30))
        
        ctk.CTkLabel(info_frame, text="RUT:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, sticky="w", pady=5)
        self.rut_entry = ctk.CTkEntry(info_frame, width=150)
        self.rut_entry.grid(row=0, column=5, sticky="w", pady=5, padx=(10, 30))
        
        ctk.CTkLabel(info_frame, text="Fecha:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.fecha_entry = ctk.CTkEntry(info_frame, width=150)
        self.fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.fecha_entry.grid(row=1, column=1, sticky="w", pady=5, padx=(10, 30))
        
        # Frame de búsqueda de productos
        busqueda_frame = ctk.CTkFrame(main_frame, fg_color="#EDF2F7", corner_radius=10)
        busqueda_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(busqueda_frame, text="Código de Barras:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        self.codigo_entry = ctk.CTkEntry(busqueda_frame, width=200, height=40)
        self.codigo_entry.grid(row=0, column=1, padx=10, pady=15)
        self.codigo_entry.bind("<Return>", self.buscar_producto)
        
        ctk.CTkButton(
            busqueda_frame,
            text="Buscar Producto",
            command=self.buscar_producto,
            width=120,
            height=40,
            fg_color="#2B6CB0"
        ).grid(row=0, column=2, padx=10, pady=15)
        
        # Frame principal dividido
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # Left - Información del producto
        left_frame = ctk.CTkFrame(content_frame, fg_color="white")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            left_frame,
            text="INFORMACIÓN DEL PRODUCTO",
            font=ctk.CTkFont(weight="bold", size=16),
            text_color="#2D3748"
        ).pack(pady=15)
        
        # Información del producto
        info_producto_frame = ctk.CTkFrame(left_frame, fg_color="#F7FAFC", corner_radius=10)
        info_producto_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(info_producto_frame, text="Producto:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", pady=8, padx=10)
        self.producto_label = ctk.CTkLabel(info_producto_frame, text="-", text_color="#4A5568")
        self.producto_label.grid(row=0, column=1, sticky="w", pady=8, padx=10)
        
        ctk.CTkLabel(info_producto_frame, text="Precio Venta Actual:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", pady=8, padx=10)
        self.precio_actual_label = ctk.CTkLabel(info_producto_frame, text="$0", text_color="#2B6CB0")
        self.precio_actual_label.grid(row=1, column=1, sticky="w", pady=8, padx=10)
        
        ctk.CTkLabel(info_producto_frame, text="Último Precio Compra:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", pady=8, padx=10)
        self.precio_anterior_label = ctk.CTkLabel(info_producto_frame, text="$0", text_color="#D69E2E")
        self.precio_anterior_label.grid(row=2, column=1, sticky="w", pady=8, padx=10)
        
        ctk.CTkLabel(info_producto_frame, text="Valor Factura:", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, sticky="w", pady=8, padx=10)
        self.valor_entry = ctk.CTkEntry(info_producto_frame, width=150, placeholder_text="Precio en factura")
        self.valor_entry.grid(row=3, column=1, sticky="w", pady=8, padx=10)
        
        ctk.CTkLabel(info_producto_frame, text="Cantidad:", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, sticky="w", pady=8, padx=10)
        self.cantidad_entry = ctk.CTkEntry(info_producto_frame, width=150, placeholder_text="Cantidad comprada")
        self.cantidad_entry.grid(row=4, column=1, sticky="w", pady=8, padx=10)
        
        ctk.CTkButton(
            info_producto_frame,
            text="Agregar a Factura",
            command=self.agregar_a_factura,
            width=200,
            height=45,
            fg_color="#38A169",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=5, column=0, columnspan=2, pady=15)
        
        # Lista de productos en factura
        ctk.CTkLabel(
            left_frame,
            text="PRODUCTOS EN FACTURA",
            font=ctk.CTkFont(weight="bold", size=16),
            text_color="#2D3748"
        ).pack(pady=(20, 10))
        
        self.lista_factura_frame = ctk.CTkScrollableFrame(left_frame, fg_color="white")
        self.lista_factura_frame.pack(fill="both", expand=True, padx=20, pady=10)
        left_frame.pack_propagate(True)
        
        # Right - Resumen de factura
        right_frame = ctk.CTkFrame(content_frame, fg_color="#F7FAFC", width=300)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            right_frame,
            text="RESUMEN FACTURA",
            font=ctk.CTkFont(weight="bold", size=18),
            text_color="#2D3748"
        ).pack(pady=20)
        
        # Totales
        totales_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        totales_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(totales_frame, text="Subtotal:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", pady=8)
        self.subtotal_label = ctk.CTkLabel(totales_frame, text="$0", font=ctk.CTkFont(weight="bold"))
        self.subtotal_label.grid(row=0, column=1, sticky="e", pady=8)
        
        ctk.CTkLabel(totales_frame, text="IVA (19%):", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", pady=8)
        self.iva_label = ctk.CTkLabel(totales_frame, text="$0", font=ctk.CTkFont(weight="bold"))
        self.iva_label.grid(row=1, column=1, sticky="e", pady=8)
        
        ctk.CTkLabel(totales_frame, text="Otros Impuestos:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", pady=8)
        self.otros_impuestos_entry = ctk.CTkEntry(totales_frame, width=120, placeholder_text="0")
        self.otros_impuestos_entry.grid(row=2, column=1, sticky="e", pady=8)
        self.otros_impuestos_entry.bind("<KeyRelease>", self.calcular_totales)
        
        ctk.CTkLabel(totales_frame, text="TOTAL:", font=ctk.CTkFont(weight="bold", size=16)).grid(row=3, column=0, sticky="w", pady=12)
        self.total_label = ctk.CTkLabel(totales_frame, text="$0", font=ctk.CTkFont(weight="bold", size=16), text_color="#D69E2E")
        self.total_label.grid(row=3, column=1, sticky="e", pady=12)
        
        # Botones de acción
        button_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="💾 GUARDAR COMPRA",
            command=self.guardar_compra,
            width=200,
            height=50,
            fg_color="#38A169",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="🔄 LIMPIAR",
            command=self.limpiar_factura,
            width=200,
            height=40,
            fg_color="#2B6CB0",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="❌ CANCELAR",
            command=self.window.destroy,
            width=200,
            height=40,
            fg_color="#E53E3E",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)
        
        # Producto actual
        self.producto_actual = None
        
    def buscar_producto(self, event=None):
        """Buscar producto por código de barras"""
        codigo = self.codigo_entry.get().strip()
        if not codigo:
            self.mostrar_error("Ingrese un código de barras")
            return
        
        # Si el producto no existe, preguntar si crear nuevo
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
        else:
            self.preguntar_crear_producto(codigo)
    
    def mostrar_producto(self, producto):
        """Mostrar información del producto"""
        self.producto_label.configure(text=producto['nombre'])
        self.precio_actual_label.configure(text=f"${producto['precio_venta']:,.0f}")
        self.precio_anterior_label.configure(text=f"${producto['precio_compra']:,.0f}")
        self.valor_entry.delete(0, 'end')
        self.cantidad_entry.delete(0, 'end')
        self.valor_entry.focus()
    
    def preguntar_crear_producto(self, codigo):
        """Preguntar si crear nuevo producto"""
        from tkinter import messagebox
        respuesta = messagebox.askyesno(
            "Producto No Encontrado",
            f"El producto con código {codigo} no existe.\n¿Desea crearlo ahora?"
        )
        
        if respuesta:
            self.crear_nuevo_producto(codigo)
        else:
            self.limpiar_producto()
    
    def crear_nuevo_producto(self, codigo):
        """Crear nuevo producto"""
        self.mostrar_mensaje("Crear Producto", f"Función para crear producto {codigo} en desarrollo")
        # Aquí se integraría con el módulo de crear producto
    
    def agregar_a_factura(self):
        """Agregar producto a la factura"""
        if not self.producto_actual:
            self.mostrar_error("No hay producto seleccionado")
            return
        
        try:
            valor = float(self.valor_entry.get())
            cantidad = float(self.cantidad_entry.get())
            
            if valor <= 0 or cantidad <= 0:
                self.mostrar_error("Valor y cantidad deben ser mayores a 0")
                return
            
            subtotal = valor * cantidad
            
            item_factura = {
                'id': self.producto_actual['id'],
                'codigo': self.producto_actual['codigo_barras'],
                'nombre': self.producto_actual['nombre'],
                'valor': valor,
                'cantidad': cantidad,
                'subtotal': subtotal
            }
            
            self.productos_factura.append(item_factura)
            self.actualizar_lista_factura()
            self.calcular_totales()
            self.limpiar_producto()
            
        except ValueError:
            self.mostrar_error("Valor y cantidad deben ser números válidos")
    
    def actualizar_lista_factura(self):
        """Actualizar lista de productos en factura"""
        for widget in self.lista_factura_frame.winfo_children():
            widget.destroy()
        
        if not self.productos_factura:
            ctk.CTkLabel(
                self.lista_factura_frame,
                text="No hay productos en la factura",
                text_color="#718096"
            ).pack(expand=True)
            return
        
        for item in self.productos_factura:
            item_frame = ctk.CTkFrame(self.lista_factura_frame, fg_color="white")
            item_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                item_frame,
                text=item['nombre'],
                text_color="#2D3748",
                font=ctk.CTkFont(weight="bold")
            ).pack(side="left", padx=10, pady=5)
            
            ctk.CTkLabel(
                item_frame,
                text=f"{item['cantidad']} x ${item['valor']:,.0f} = ${item['subtotal']:,.0f}",
                text_color="#4A5568"
            ).pack(side="right", padx=10, pady=5)
    
    def calcular_totales(self, event=None):
        """Calcular totales de la factura"""
        try:
            subtotal = sum(item['subtotal'] for item in self.productos_factura)
            iva = subtotal * 0.19
            otros_impuestos = float(self.otros_impuestos_entry.get() or 0)
            total = subtotal + iva + otros_impuestos
            
            self.subtotal_label.configure(text=f"${subtotal:,.0f}")
            self.iva_label.configure(text=f"${iva:,.0f}")
            self.total_label.configure(text=f"${total:,.0f}")
            
        except ValueError:
            pass
    
    def guardar_compra(self):
        """Guardar la compra en la base de datos"""
        if not self.productos_factura:
            self.mostrar_error("No hay productos en la factura")
            return
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Registrar la compra
            cursor.execute('''
                INSERT INTO compras (numero_factura, proveedor, rut_proveedor, fecha_compra, total, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                self.factura_entry.get(),
                self.proveedor_entry.get(),
                self.rut_entry.get(),
                self.fecha_entry.get(),
                float(self.total_label.cget("text").replace("$", "").replace(",", "")),
                self.usuario['id']
            ))
            
            compra_id = cursor.lastrowid
            
            # Registrar detalles y actualizar productos
            for item in self.productos_factura:
                cursor.execute('''
                    INSERT INTO detalle_compras (compra_id, producto_id, cantidad, precio_compra, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                ''', (compra_id, item['id'], item['cantidad'], item['valor'], item['subtotal']))
                
                # Actualizar producto
                cursor.execute('''
                    UPDATE productos 
                    SET precio_compra = ?, 
                        stock_actual = stock_actual + ?,
                        fecha_ultima_compra = ?
                    WHERE id = ?
                ''', (item['valor'], item['cantidad'], datetime.now(), item['id']))
            
            conn.commit()
            conn.close()
            
            self.mostrar_exito("Compra registrada exitosamente")
            self.limpiar_factura()
            
        except Exception as e:
            self.mostrar_error(f"Error al guardar compra: {str(e)}")
    
    def limpiar_producto(self):
        """Limpiar información del producto actual"""
        self.producto_actual = None
        self.producto_label.configure(text="-")
        self.precio_actual_label.configure(text="$0")
        self.precio_anterior_label.configure(text="$0")
        self.valor_entry.delete(0, 'end')
        self.cantidad_entry.delete(0, 'end')
        self.codigo_entry.delete(0, 'end')
        self.codigo_entry.focus()
    
    def limpiar_factura(self):
        """Limpiar toda la factura"""
        self.productos_factura = []
        self.actualizar_lista_factura()
        self.calcular_totales()
        self.limpiar_producto()
        self.factura_entry.delete(0, 'end')
        self.proveedor_entry.delete(0, 'end')
        self.rut_entry.delete(0, 'end')
        self.otros_impuestos_entry.delete(0, 'end')
    
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
    
    def mostrar_mensaje(self, titulo, mensaje):
        """Mostrar mensaje informativo"""
        message_window = ctk.CTkToplevel(self.window)
        message_window.title(titulo)
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(message_window, width_percent=0.4, min_width=400, min_height=200, parent=self.window)
        message_window.transient(self.window)
        message_window.grab_set()
        
        ctk.CTkLabel(message_window, text=mensaje).pack(expand=True, pady=20)
        ctk.CTkButton(message_window, text="Aceptar", command=message_window.destroy).pack(pady=10)