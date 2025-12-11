# ui/crear_producto_window.py
import customtkinter as ctk
import sqlite3
from ui.responsive import set_window_size_and_center


class CrearProductoWindow:
    
    def __init__(self, parent, db, inventario_window):
        self.parent = parent
        self.db = db
        self.inventario_window = inventario_window
        
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Crear Producto - RUSTIGONE")

        # Ventana mucho más compacta
        set_window_size_and_center(
            self.window,
            width_percent=0.40,
            min_width=480,
            min_height=530,   # ← antes 850
            parent=parent
        )

        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()

        # Botón maximizar
        self._is_maximized = False
        self.maximize_btn = ctk.CTkButton(
            self.window, text="🗖", width=35, height=28,
            command=self.toggle_maximize,
            fg_color="#38A169", text_color="white"
        )
        self.maximize_btn.place(relx=0.98, rely=0.015, anchor="ne")


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
        main_frame = ctk.CTkFrame(self.window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Título compacto
        ctk.CTkLabel(
            main_frame,
            text="➕ Crear Nuevo Producto",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#38A169"
        ).pack(pady=10)

        # Formulario
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True)
        form_frame.grid_columnconfigure(1, weight=1)

        # Helper para reducir repetición
        def add_row(row, label, widget):
            ctk.CTkLabel(form_frame, text=label, font=ctk.CTkFont(weight="bold")).grid(
                row=row, column=0, sticky="w", pady=4
            )
            widget.grid(row=row, column=1, sticky="ew", pady=4, padx=(8, 0))

        # Campos
        self.codigo_entry = ctk.CTkEntry(form_frame)
        add_row(0, "Código de Barras:", self.codigo_entry)

        self.nombre_entry = ctk.CTkEntry(form_frame)
        add_row(1, "Nombre:", self.nombre_entry)

        self.descripcion_entry = ctk.CTkEntry(form_frame)
        add_row(2, "Descripción:", self.descripcion_entry)

        self.precio_compra_entry = ctk.CTkEntry(form_frame, placeholder_text="0")
        add_row(3, "Precio Compra:", self.precio_compra_entry)

        self.ganancia_entry = ctk.CTkEntry(form_frame, placeholder_text="30")
        add_row(4, "% Ganancia:", self.ganancia_entry)

        self.precio_venta_entry = ctk.CTkEntry(form_frame, placeholder_text="Auto")
        add_row(5, "Precio Venta:", self.precio_venta_entry)

        self.stock_entry = ctk.CTkEntry(form_frame, placeholder_text="0")
        add_row(6, "Stock Inicial:", self.stock_entry)

        self.stock_min_entry = ctk.CTkEntry(form_frame, placeholder_text="1")
        add_row(7, "Stock Mínimo:", self.stock_min_entry)

        # Combos
        self.unidad_combo = ctk.CTkComboBox(form_frame, values=["unidad","kg","g","l","ml"])
        self.unidad_combo.set("unidad")
        add_row(8, "Unidad Medida:", self.unidad_combo)

        categorias = self.obtener_categorias()
        self.categoria_combo = ctk.CTkComboBox(form_frame, values=categorias)
        if categorias:
            self.categoria_combo.set(categorias[0])
        add_row(9, "Categoría:", self.categoria_combo)

        # Botón nueva categoría más pequeño
        ctk.CTkButton(
            form_frame,
            text="➕ Nueva Categoría",
            command=self.crear_nueva_categoria,
            fg_color="#718096",
            height=28,
            font=ctk.CTkFont(size=13)
        ).grid(row=10, column=1, sticky="w", pady=(4, 10), padx=(8, 0))

        # Botones de acción compactos
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=11, column=0, columnspan=2, pady=(10, 0))

        ctk.CTkButton(
            button_frame,
            text="Guardar",
            command=self.guardar_producto,
            fg_color="#38A169",
            font=ctk.CTkFont(weight="bold"),
            width=120
        ).grid(row=0, column=0, padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.window.destroy,
            fg_color="#E53E3E",
            font=ctk.CTkFont(weight="bold"),
            width=120
        ).grid(row=0, column=1, padx=5)


    def obtener_categorias(self):
        """Obtener lista de categorías de la base de datos"""
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM categorias ORDER BY nombre")
        categorias = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categorias
    
    def crear_nueva_categoria(self):
        """Crear nueva categoría"""
        dialog = ctk.CTkInputDialog(text="Ingrese nombre de la nueva categoría:", title="Nueva Categoría")
        nueva_categoria = dialog.get_input()
        
        if nueva_categoria and nueva_categoria.strip():
            conn = self.db.connect()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES (?)", (nueva_categoria.strip(),))
                conn.commit()
                
                # Actualizar combobox
                categorias = self.obtener_categorias()
                self.categoria_combo.configure(values=categorias)
                self.categoria_combo.set(nueva_categoria.strip())
                
                self.mostrar_exito("Categoría creada exitosamente")
            except Exception as e:
                self.mostrar_error(f"Error al crear categoría: {str(e)}")
            finally:
                conn.close()
    
    def calcular_precio_venta(self):
        """Calcular precio de venta automáticamente"""
        try:
            precio_compra = float(self.precio_compra_entry.get() or 0)
            ganancia = float(self.ganancia_entry.get() or 30)
            
            precio_venta = precio_compra * (1 + ganancia/100)
            self.precio_venta_entry.delete(0, 'end')
            self.precio_venta_entry.insert(0, f"{precio_venta:.0f}")
        except ValueError:
            pass
    
    def guardar_producto(self):
        """Guardar nuevo producto en la base de datos"""
        try:
            # Validar campos obligatorios
            if not self.nombre_entry.get().strip():
                self.mostrar_error("El nombre del producto es obligatorio")
                return
            
            if not self.precio_compra_entry.get().strip():
                self.mostrar_error("El precio de compra es obligatorio")
                return
            
            # Obtener datos del formulario
            codigo_barras = self.codigo_entry.get().strip() or None
            nombre = self.nombre_entry.get().strip()
            descripcion = self.descripcion_entry.get().strip() or None
            precio_compra = float(self.precio_compra_entry.get())
            porcentaje_ganancia = float(self.ganancia_entry.get() or 30)
            precio_venta = float(self.precio_venta_entry.get() or precio_compra * 1.3)
            stock_actual = float(self.stock_entry.get() or 0)
            stock_minimo = float(self.stock_min_entry.get() or 1)
            unidad_medida = self.unidad_combo.get()
            categoria_nombre = self.categoria_combo.get()
            
            # Obtener ID de categoría
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM categorias WHERE nombre = ?", (categoria_nombre,))
            categoria_result = cursor.fetchone()
            categoria_id = categoria_result[0] if categoria_result else None
            
            # Insertar producto
            cursor.execute('''
                INSERT INTO productos 
                (codigo_barras, nombre, descripcion, precio_compra, porcentaje_ganancia, 
                 precio_venta, stock_actual, stock_minimo, categoria_id, unidad_medida)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (codigo_barras, nombre, descripcion, precio_compra, porcentaje_ganancia,
                  precio_venta, stock_actual, stock_minimo, categoria_id, unidad_medida))
            
            conn.commit()
            conn.close()
            
            self.mostrar_exito("Producto creado exitosamente")
            self.inventario_window.refrescar_lista()
            self.window.destroy()
            
        except ValueError as e:
            self.mostrar_error("Error en los valores numéricos. Verifique los precios y stocks.")
        except Exception as e:
            self.mostrar_error(f"Error al guardar producto: {str(e)}")
    
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