# ui/inventario_window.py - VERSIÓN CON BOTONES ALINEADOS
import customtkinter as ctk
from datetime import datetime
import sqlite3
from tkinter import messagebox

class InventarioWindow:
    def __init__(self, parent, db, usuario):
        self.parent = parent
        self.db = db
        self.usuario = usuario
        self.producto_seleccionado = None
        self._after_ids = []

        # Crear ventana de inventario
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Gestión de Inventario - RUSTIGONE")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(self.window, width_percent=0.75, min_width=800, min_height=650, parent=parent)
        self.window.transient(parent)
        self.window.grab_set()
        
        # ✅ Manejar cierre de ventana
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # PRIMERO crear widgets
        self.create_widgets()
        # LUEGO cargar datos
        self.actualizar_lista_productos()
        # Estado de maximización
        self._is_maximized = False
        # Botón maximizar/restaurar
        self.maximize_btn = ctk.CTkButton(self.window, text="🗖", width=40, height=30, command=self.toggle_maximize, fg_color="#38A169", text_color="white")
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
        
    def _on_close(self):
        """Manejar el cierre correcto de la ventana"""
        # ✅ Cancelar todos los eventos programados
        for after_id in self._after_ids:
            self.window.after_cancel(after_id)
        self._after_ids.clear()
        
        # ✅ Destruir ventana
        self.window.destroy()

    def schedule_task(self, delay_ms, func, *args):
        """Programar tarea de forma segura"""
        after_id = self.window.after(delay_ms, func, *args)
        self._after_ids.append(after_id)
        return after_id
    def create_widgets(self):
        """Crear interfaz completa de inventario"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 10))
        
        title = ctk.CTkLabel(
            title_frame,
            text="📦 GESTIÓN DE INVENTARIO",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#38A169"
        )
        title.pack(pady=10)
        
        # ✅ CORREGIDO: Frame de búsqueda y acciones - BOTONES PERFECTAMENTE ALINEADOS
        search_frame = ctk.CTkFrame(main_frame, fg_color="#F7FAFC", corner_radius=10)
        search_frame.pack(fill="x", pady=(0, 10))
        
        # Configurar grid principal con 2 columnas: búsqueda (izq) y acciones (der)
        search_frame.grid_columnconfigure(0, weight=1)  # Columna búsqueda
        search_frame.grid_columnconfigure(1, weight=0)  # Columna acciones
        
        # LEFT: Búsqueda
        left_search = ctk.CTkFrame(search_frame, fg_color="transparent")
        left_search.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Búsqueda en línea horizontal
        ctk.CTkLabel(
            left_search, 
            text="Buscar:",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            left_search,
            placeholder_text="Código, nombre, categoría..."
        )
        self.search_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
        self.search_entry.bind("<Return>", self.buscar_productos)
        
        self.buscar_btn = ctk.CTkButton(
            left_search,
            text="Buscar",
            command=self.buscar_productos,
            fg_color="#2B6CB0"
        )
        self.buscar_btn.pack(side="left", padx=(0, 10))
        
        self.limpiar_btn = ctk.CTkButton(
            left_search,
            text="Limpiar",
            command=self.limpiar_busqueda,
            fg_color="#718096"
        )
        self.limpiar_btn.pack(side="left")
        
        # RIGHT: Botones de acción - TODOS EN LA MISMA FILA
        right_actions = ctk.CTkFrame(search_frame, fg_color="transparent")
        right_actions.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        # ✅ TODOS LOS BOTONES EN LA MISMA LÍNEA SIN TOOLTIPS DEBAJO
        self.crear_btn = ctk.CTkButton(
            right_actions,
            text="➕ CREAR PRODUCTO",
            command=self.crear_producto,
            fg_color="#38A169",
            font=ctk.CTkFont(weight="bold")
        )
        self.crear_btn.pack(side="left", padx=5)

        self.modificar_btn = ctk.CTkButton(
            right_actions,
            text="✏️ MODIFICAR",
            command=self.modificar_producto,
            fg_color="#D69E2E",
            font=ctk.CTkFont(weight="bold"),
            state="disabled"
        )
        self.modificar_btn.pack(side="left", padx=5)

        self.corregir_btn = ctk.CTkButton(
            right_actions,
            text="🔧 CORREGIR STOCK",
            command=self.corregir_stock,
            fg_color="#3182CE",
            font=ctk.CTkFont(weight="bold"),
            state="disabled"
        )
        self.corregir_btn.pack(side="left", padx=5)
        
        # ✅ Tooltips removidos para mejor alineación (se pueden mostrar en status bar si es necesario)
        
        # Frame principal dividido
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # Left frame - Lista de productos
        left_frame = ctk.CTkFrame(content_frame, fg_color="white")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Header de la lista
        list_header = ctk.CTkFrame(left_frame, fg_color="#EDF2F7", height=40)
        list_header.pack(fill="x", pady=(0, 5))
        list_header.pack_propagate(False)

        # Configurar grid del header
        list_header.grid_columnconfigure(0, weight=1, minsize=150)
        list_header.grid_columnconfigure(1, weight=3, minsize=300)
        list_header.grid_columnconfigure(2, weight=1, minsize=120)
        list_header.grid_columnconfigure(3, weight=1, minsize=120)
        list_header.grid_columnconfigure(4, weight=1, minsize=150)
        
        headers = [
            ("Código", "w"),
            ("Nombre", "w"), 
            ("Stock", "ew"),
            ("Precio", "ew"),
            ("Categoría", "ew")
        ]
        
        for i, (header_text, sticky_val) in enumerate(headers):
            label = ctk.CTkLabel(
                list_header,
                text=header_text,
                font=ctk.CTkFont(weight="bold", size=12),
                text_color="#2D3748"
            )
            label.grid(row=0, column=i, padx=8, pady=10, sticky=sticky_val)
        
        # Lista frame
        self.lista_frame = ctk.CTkScrollableFrame(
            left_frame, 
            fg_color="white",
            scrollbar_button_color="#3182CE",
            scrollbar_button_hover_color="#2B6CB0"
        )
        self.lista_frame.pack(fill="both", expand=True)
        left_frame.pack_propagate(True)
        
        # Right frame - Información detallada
        self.info_frame = ctk.CTkFrame(content_frame, fg_color="#F7FAFC", width=400)
        self.info_frame.pack(side="right", fill="y", padx=(5, 0))
        self.info_frame.pack_propagate(False)
        
        # Información del producto seleccionado
        self.mostrar_info_vacia()

    # ... (el resto de los métodos se mantienen igual - mostrar_info_vacia, mostrar_info_producto, actualizar_lista_productos, etc.)

    def mostrar_info_vacia(self):
        """Mostrar información vacía cuando no hay producto seleccionado"""
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(
            self.info_frame,
            text="ℹ️ SELECCIONE UN PRODUCTO",
            font=ctk.CTkFont(weight="bold", size=16),
            text_color="#718096"
        ).pack(expand=True)

    def mostrar_info_producto(self, producto):
        """Mostrar información detallada del producto seleccionado"""
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        # Título
        ctk.CTkLabel(
            self.info_frame,
            text="📋 INFORMACIÓN DEL PRODUCTO",
            font=ctk.CTkFont(weight="bold", size=18),
            text_color="#2D3748"
        ).pack(pady=20)
        
        # Frame de información
        info_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=20)
        
        # Datos del producto
        datos = [
            ("Código:", producto['codigo_barras']),
            ("Nombre:", producto['nombre']),
            ("Descripción:", producto['descripcion'] or "Sin descripción"),
            ("Precio Compra:", f"${producto['precio_compra']:,.0f}"),
            ("Precio Venta:", f"${producto['precio_venta']:,.0f}"),
            ("% Ganancia:", f"{producto['porcentaje_ganancia']}%"),
            ("Stock Actual:", f"{producto['stock_actual']} {producto['unidad_medida']}"),
            ("Stock Mínimo:", f"{producto['stock_minimo']} {producto['unidad_medida']}"),
            ("Categoría:", producto['categoria_nombre']),
            ("Última Compra:", producto['fecha_ultima_compra'] or "Nunca"),
            ("Última Venta:", producto['fecha_ultima_venta'] or "Nunca")
        ]
        
        for i, (label, value) in enumerate(datos):
            ctk.CTkLabel(
                info_frame,
                text=label,
                font=ctk.CTkFont(weight="bold")
            ).grid(row=i, column=0, sticky="w", pady=5, padx=(0, 10))
            
            ctk.CTkLabel(
                info_frame,
                text=value,
                text_color="#4A5568"
            ).grid(row=i, column=1, sticky="w", pady=5)
        
        # Alertas de stock
        if producto['stock_actual'] <= producto['stock_minimo']:
            alert_frame = ctk.CTkFrame(info_frame, fg_color="#FED7D7", corner_radius=5)
            alert_frame.grid(row=len(datos), column=0, columnspan=2, sticky="ew", pady=10)
            ctk.CTkLabel(
                alert_frame,
                text="⚠️ STOCK BAJO - Necesita reposición",
                text_color="#C53030",
                font=ctk.CTkFont(weight="bold")
            ).pack(padx=10, pady=5)

    def actualizar_lista_productos(self, productos=None):
        """Actualizar la lista de productos"""
        # Verificar que lista_frame existe
        if not hasattr(self, 'lista_frame'):
            print("❌ lista_frame no existe")
            return
            
        # Limpiar lista actual
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        
        if productos is None:
            # Obtener todos los productos activos
            try:
                conn = self.db.connect()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.*, c.nombre as categoria_nombre 
                    FROM productos p 
                    LEFT JOIN categorias c ON p.categoria_id = c.id 
                    WHERE p.activo = 1
                    ORDER BY p.nombre
                ''')
                productos = [dict(row) for row in cursor.fetchall()]
                conn.close()
                print(f"✅ Cargados {len(productos)} productos")
            except Exception as e:
                print(f"❌ Error al cargar productos: {e}")
                productos = []
        
        if not productos:
            # Mostrar mensaje de no productos
            ctk.CTkLabel(
                self.lista_frame,
                text="No se encontraron productos",
                text_color="#718096",
                font=ctk.CTkFont(size=14)
            ).pack(expand=True, pady=50)
            return
        
        # Mostrar productos
        for i, producto in enumerate(productos):
            # Frame para cada producto
            product_frame = ctk.CTkFrame(
                self.lista_frame, 
                fg_color="white", 
                height=45,
                corner_radius=5
            )
            product_frame.pack(fill="x", pady=2, padx=5)
            product_frame.pack_propagate(False)
            
            # Color de fondo alternado para mejor legibilidad
            if i % 2 == 0:
                product_frame.configure(fg_color="#F7FAFC")
            
            # Hacer que el frame completo sea clickeable
            product_frame.bind("<Button-1>", lambda e, p=producto: self.seleccionar_producto(p))
            product_frame.configure(cursor="hand2")
            
            # Color del stock según nivel
            stock_color = "#38A169"  # Normal
            if producto['stock_actual'] <= producto['stock_minimo']:
                stock_color = "#E53E3E"  # Bajo
            elif producto['stock_actual'] <= producto['stock_minimo'] * 2:
                stock_color = "#D69E2E"  # Medio
            
            # Frame interno para contenido
            inner_frame = ctk.CTkFrame(product_frame, fg_color="transparent")
            inner_frame.pack(fill="both", expand=True, padx=15, pady=8)
            
            # Configurar columnas (mismo layout que el header)
            inner_frame.grid_columnconfigure(0, weight=1, minsize=150)
            inner_frame.grid_columnconfigure(1, weight=3, minsize=300) 
            inner_frame.grid_columnconfigure(2, weight=1, minsize=120)
            inner_frame.grid_columnconfigure(3, weight=1, minsize=120)
            inner_frame.grid_columnconfigure(4, weight=1, minsize=150)
            
            # Código de barras
            codigo_label = ctk.CTkLabel(
                inner_frame,
                text=producto['codigo_barras'] or "Sin código",
                text_color="#4A5568",
                cursor="hand2",
                anchor="w"
            )
            codigo_label.grid(row=0, column=0, sticky="w")
            
            # Nombre
            nombre_label = ctk.CTkLabel(
                inner_frame,
                text=producto['nombre'],
                text_color="#2D3748",
                font=ctk.CTkFont(weight="bold"),
                cursor="hand2",
                anchor="w"
            )
            nombre_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
            
            # Stock
            stock_label = ctk.CTkLabel(
                inner_frame,
                text=f"{producto['stock_actual']} {producto['unidad_medida']}",
                text_color=stock_color,
                font=ctk.CTkFont(weight="bold"),
                cursor="hand2"
            )
            stock_label.grid(row=0, column=2, sticky="ew")
            
            # Precio
            precio_label = ctk.CTkLabel(
                inner_frame,
                text=f"${producto['precio_venta']:,.0f}",
                text_color="#2B6CB0",
                cursor="hand2"
            )
            precio_label.grid(row=0, column=3, sticky="ew")
            
            # Categoría
            categoria_label = ctk.CTkLabel(
                inner_frame,
                text=producto['categoria_nombre'] or "Sin categoría",
                text_color="#718096",
                cursor="hand2"
            )
            categoria_label.grid(row=0, column=4, sticky="ew")
            
            # Hacer que todos los labels sean clickeables también
            for widget in inner_frame.winfo_children():
                widget.bind("<Button-1>", lambda e, p=producto: self.seleccionar_producto(p))
                widget.configure(cursor="hand2")

    def seleccionar_producto(self, producto):
        """Seleccionar un producto de la lista"""
        try:
            self.producto_seleccionado = producto
            self.mostrar_info_producto(producto)
            
            # Habilitar botones
            self.modificar_btn.configure(state="normal")
            self.corregir_btn.configure(state="normal")
                
            print(f"✅ Producto seleccionado: {producto['nombre']}")
            
        except Exception as e:
            print(f"❌ Error al seleccionar producto: {e}")

    def buscar_productos(self, event=None):
        """Buscar productos según criterios - VERSIÓN SEGURA"""
        try:
            # ✅ Cancelar búsquedas anteriores pendientes
            if hasattr(self, '_search_after_id'):
                self.window.after_cancel(self._search_after_id)
            
            # ✅ Programar nueva búsqueda con delay (debounce)
            def perform_search():
                criterio = self.search_entry.get().strip()
                
                if not criterio:
                    self.actualizar_lista_productos()
                    return
                
                try:
                    conn = self.db.connect()
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT p.*, c.nombre as categoria_nombre 
                        FROM productos p 
                        LEFT JOIN categorias c ON p.categoria_id = c.id 
                        WHERE p.activo = 1 AND (
                            p.codigo_barras LIKE ? OR 
                            p.nombre LIKE ? OR 
                            c.nombre LIKE ? OR
                            p.descripcion LIKE ?
                        )
                        ORDER BY p.nombre
                    ''', (f'%{criterio}%', f'%{criterio}%', f'%{criterio}%', f'%{criterio}%'))
                    
                    productos = [dict(row) for row in cursor.fetchall()]
                    conn.close()
                    
                    self.actualizar_lista_productos(productos)
                    self.producto_seleccionado = None
                    self.mostrar_info_vacia()
                    self.modificar_btn.configure(state="disabled")
                    self.corregir_btn.configure(state="disabled")
                    
                except Exception as e:
                    print(f"❌ Error en búsqueda: {e}")
            
            # ✅ Usar debounce para evitar múltiples búsquedas rápidas
            self._search_after_id = self.window.after(300, perform_search)
            self._after_ids.append(self._search_after_id)
                
        except Exception as e:
            print(f"❌ Error al buscar productos: {e}")

    def limpiar_busqueda(self):
        """Limpiar búsqueda y mostrar todos los productos"""
        try:
            self.search_entry.delete(0, 'end')
            self.actualizar_lista_productos()
            self.producto_seleccionado = None
            self.mostrar_info_vacia()
            self.modificar_btn.configure(state="disabled")
            self.corregir_btn.configure(state="disabled")
        except Exception as e:
            print(f"❌ Error al limpiar búsqueda: {e}")

    def crear_producto(self):
        """Abrir ventana para crear nuevo producto"""
        try:
            from ui.crear_producto_window import CrearProductoWindow
            CrearProductoWindow(self.window, self.db, self)
        except Exception as e:
            print(f"❌ Error al abrir crear producto: {e}")
            self.mostrar_mensaje("Error", f"Error al abrir creación de producto: {str(e)}")

    def modificar_producto(self):
        """Abrir ventana para modificar producto"""
        try:
            if self.producto_seleccionado:
                print("🔍 Abriendo modificación para:", self.producto_seleccionado['nombre'])
                from ui.modificar_producto_window import ModificarProductoWindow
                ModificarProductoWindow(self.window, self.db, self, self.producto_seleccionado)
            else:
                self.mostrar_mensaje("Modificar Producto", "Primero seleccione un producto")
        except Exception as e:
            print(f"❌ Error al abrir modificar producto: {e}")

    def corregir_stock(self):
        """Abrir ventana para corregir stock"""
        try:
            if self.producto_seleccionado:
                print("🔧 Corrigiendo stock de:", self.producto_seleccionado['nombre'])
                from ui.corregir_stock_window import CorregirStockWindow
                CorregirStockWindow(self.window, self.db, self, self.producto_seleccionado)
            else:
                self.mostrar_mensaje("Corregir Stock", "Primero seleccione un producto")
        except Exception as e:
            print(f"❌ Error al abrir corrección de stock: {e}")

    def mostrar_mensaje(self, titulo, mensaje):
        """Mostrar mensaje de información"""
        messagebox.showinfo(titulo, mensaje)

    def refrescar_lista(self):
        """Refrescar la lista de productos"""
        try:
            print("🔄 Refrescando lista de productos...")
            self.actualizar_lista_productos()
            self.producto_seleccionado = None
            self.mostrar_info_vacia()
            self.modificar_btn.configure(state="disabled")
            self.corregir_btn.configure(state="disabled")
            print("✅ Lista refrescada exitosamente")
        except Exception as e:
            print(f"❌ Error al refrescar lista: {e}")