# ui/modificar_producto_window.py - VERSIÓN FINAL MEJORADA
import customtkinter as ctk
from ui.responsive import set_window_size_and_center


class ModificarProductoWindow:
    def __init__(self, parent, db, inventario_window, producto):
        self.parent = parent
        self.db = db
        self.inventario_window = inventario_window
        self.producto = producto

        # Ventana principal
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Modificar Producto - RUSTIGONE")

        set_window_size_and_center(
            self.window,
            width_percent=0.40,
            min_width=480,
            min_height=620,
            parent=parent
        )

        self.window.transient(parent)
        self.window.grab_set()

        # Estado de maximización
        self._is_maximized = False

        # Crear interfaz
        self.create_widgets()

    # ==========================
    #   MAXIMIZAR / RESTAURAR
    # ==========================
    def toggle_maximize(self):
        if not self._is_maximized:
            self.window.state("zoomed")
            self._is_maximized = True
            self.maximize_btn.configure(text="🗗")
        else:
            self.window.state("normal")
            self._is_maximized = False
            self.maximize_btn.configure(text="🗖")

    # ==========================
    #  CREAR INTERFAZ
    # ==========================
    def create_widgets(self):

        # Frame principal
        main_frame = ctk.CTkFrame(self.window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # ------------------------
        # Botón Maximizar (ahora visible siempre)
        # ------------------------
        self.maximize_btn = ctk.CTkButton(
            main_frame,
            text="🗖",
            width=35,
            height=28,
            command=self.toggle_maximize,
            fg_color="#D69E2E",
            text_color="white"
        )
        self.maximize_btn.place(relx=0.99, rely=0.01, anchor="ne")

        # ------------------------
        # Título
        # ------------------------
        ctk.CTkLabel(
            main_frame,
            text="✏️ Modificar Producto",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#D69E2E"
        ).pack(pady=10)

        # Contenedor principal del formulario
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True)
        form_frame.grid_columnconfigure(1, weight=1)

        # Helper de filas para evitar repetición
        def add_row(row, label, widget):
            ctk.CTkLabel(
                form_frame,
                text=label,
                font=ctk.CTkFont(weight="bold")
            ).grid(row=row, column=0, sticky="w", pady=4)
            widget.grid(row=row, column=1, sticky="ew", pady=4, padx=(8, 0))

        # ==========================
        #  CAMPOS EDITABLES
        # ==========================

        # Nombre
        self.nombre_entry = ctk.CTkEntry(form_frame)
        self.nombre_entry.insert(0, self.producto["nombre"])
        add_row(0, "Nombre:", self.nombre_entry)

        # Descripción
        self.descripcion_entry = ctk.CTkEntry(form_frame)
        self.descripcion_entry.insert(0, self.producto.get("descripcion", ""))
        add_row(1, "Descripción:", self.descripcion_entry)

        # Precio compra
        self.precio_compra_entry = ctk.CTkEntry(form_frame)
        self.precio_compra_entry.insert(0, str(self.producto["precio_compra"]))
        add_row(2, "Precio Compra:", self.precio_compra_entry)

        # Ganancia
        self.ganancia_entry = ctk.CTkEntry(form_frame)
        self.ganancia_entry.insert(0, str(self.producto["porcentaje_ganancia"]))
        add_row(3, "% Ganancia:", self.ganancia_entry)

        # Precio venta
        self.precio_venta_entry = ctk.CTkEntry(form_frame)
        self.precio_venta_entry.insert(0, str(self.producto["precio_venta"]))
        add_row(4, "Precio Venta:", self.precio_venta_entry)

        # Stock actual
        self.stock_entry = ctk.CTkEntry(form_frame)
        self.stock_entry.insert(0, str(self.producto["stock_actual"]))
        add_row(5, "Stock Actual:", self.stock_entry)

        # Stock mínimo
        self.stock_min_entry = ctk.CTkEntry(form_frame)
        self.stock_min_entry.insert(0, str(self.producto["stock_minimo"]))
        add_row(6, "Stock Mínimo:", self.stock_min_entry)

        # Unidad de medida
        self.unidad_combo = ctk.CTkComboBox(
            form_frame,
            values=["unidad", "kg", "g", "l", "ml"]
        )
        self.unidad_combo.set(self.producto.get("unidad_medida", "unidad"))
        add_row(7, "Unidad Medida:", self.unidad_combo)

        # Categoría
        categorias = self.obtener_categorias()
        self.categoria_combo = ctk.CTkComboBox(form_frame, values=categorias)
        self.categoria_combo.set(self.producto.get("categoria_nombre", categorias[0]))
        add_row(8, "Categoría:", self.categoria_combo)

        # Botón nueva categoría
        ctk.CTkButton(
            form_frame,
            text="➕ Nueva Categoría",
            command=self.crear_nueva_categoria,
            fg_color="#718096",
            height=28,
            font=ctk.CTkFont(size=13)
        ).grid(row=9, column=1, sticky="w", pady=(4, 10), padx=(8, 0))

        # ==========================
        #  INFORMACIÓN (no editable)
        # ==========================
        info_frame = ctk.CTkFrame(main_frame, fg_color="#F7FAFC", corner_radius=10)
        info_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            info_frame,
            text="📊 Información del Sistema",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#4A5568"
        ).pack(pady=5)

        info_text = f"""• Última compra: {self.producto.get('fecha_ultima_compra', 'Nunca')}
• Última venta: {self.producto.get('fecha_ultima_venta', 'Nunca')}
• Fecha creación: {self.producto.get('fecha_creacion', 'Desconocida')}"""

        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=11),
            text_color="#718096",
            justify="left"
        ).pack(padx=15, pady=5)

        # ==========================
        #  BOTONES FINALES
        # ==========================
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        ctk.CTkButton(
            button_frame,
            text="Guardar",
            fg_color="#38A169",
            width=120,
            command=self.guardar_cambios
        ).grid(row=0, column=0, padx=5)

        ctk.CTkButton(
            button_frame,
            text="Calcular",
            fg_color="#2B6CB0",
            width=120,
            command=self.calcular_precio_venta
        ).grid(row=0, column=1, padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            fg_color="#E53E3E",
            width=120,
            command=self.window.destroy
        ).grid(row=0, column=2, padx=5)

        # Auto-cálculo
        self.precio_compra_entry.bind("<KeyRelease>", lambda e: self.calcular_precio_venta())
        self.ganancia_entry.bind("<KeyRelease>", lambda e: self.calcular_precio_venta())

    # ==========================
    #  BASE DE DATOS Y LÓGICA
    # ==========================
    def obtener_categorias(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM categorias ORDER BY nombre")
        categorias = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categorias if categorias else ["General"]

    def crear_nueva_categoria(self):
        dialog = ctk.CTkInputDialog(text="Ingrese nombre de la nueva categoría:", title="Nueva Categoría")
        nueva = dialog.get_input()
        if not nueva:
            return

        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES (?)", (nueva,))
        conn.commit()
        conn.close()

        categorias = self.obtener_categorias()
        self.categoria_combo.configure(values=categorias)
        self.categoria_combo.set(nueva)

    def calcular_precio_venta(self):
        try:
            compra = float(self.precio_compra_entry.get())
            ganancia = float(self.ganancia_entry.get() or 30)
            venta = compra * (1 + ganancia / 100)
            self.precio_venta_entry.delete(0, "end")
            self.precio_venta_entry.insert(0, f"{venta:.0f}")
        except:
            pass

    # ==========================
    #  GUARDAR CAMBIOS
    # ==========================
    def guardar_cambios(self):
        try:
            nombre = self.nombre_entry.get().strip()
            if not nombre:
                self.mostrar_error("El nombre del producto es obligatorio.")
                return

            descripcion = self.descripcion_entry.get().strip()
            precio_compra = float(self.precio_compra_entry.get())
            ganancia = float(self.ganancia_entry.get())
            precio_venta = float(self.precio_venta_entry.get())
            stock_actual = float(self.stock_entry.get())
            stock_minimo = float(self.stock_min_entry.get())
            unidad = self.unidad_combo.get()
            categoria = self.categoria_combo.get()

            conn = self.db.connect()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM categorias WHERE nombre=?", (categoria,))
            categoria_id = cursor.fetchone()[0]

            cursor.execute("""
                UPDATE productos
                SET nombre=?, descripcion=?, precio_compra=?, porcentaje_ganancia=?,
                    precio_venta=?, stock_actual=?, stock_minimo=?, categoria_id=?, unidad_medida=?
                WHERE id=?
            """, (
                nombre, descripcion, precio_compra, ganancia,
                precio_venta, stock_actual, stock_minimo,
                categoria_id, unidad, self.producto["id"]
            ))

            conn.commit()
            conn.close()

            self.inventario_window.refrescar_lista()
            self.mostrar_exito("Producto actualizado exitosamente")
            self.window.destroy()

        except Exception as e:
            self.mostrar_error(f"Error al guardar cambios: {e}")

    # ==========================
    #  MENSAJES
    # ==========================
    def mostrar_error(self, msg):
        win = ctk.CTkToplevel(self.window)
        win.title("Error")
        set_window_size_and_center(win, width_percent=0.35, min_width=400, min_height=150, parent=self.window)
        win.grab_set()
        ctk.CTkLabel(win, text="❌ " + msg).pack(expand=True, pady=20)
        ctk.CTkButton(win, text="Aceptar", command=win.destroy).pack(pady=10)

    def mostrar_exito(self, msg):
        win = ctk.CTkToplevel(self.window)
        win.title("Éxito")
        set_window_size_and_center(win, width_percent=0.35, min_width=400, min_height=150, parent=self.window)
        win.grab_set()
        ctk.CTkLabel(win, text="✅ " + msg).pack(expand=True, pady=20)
        ctk.CTkButton(win, text="Aceptar", command=win.destroy).pack(pady=10)
