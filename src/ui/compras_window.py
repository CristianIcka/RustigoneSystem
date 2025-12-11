import customtkinter as ctk
from datetime import datetime
import sqlite3
from ui.responsive import set_window_size_and_center


class ComprasWindow:
    def __init__(self, parent, db, usuario, inventario_window=None):
        self.parent = parent
        self.db = db
        self.usuario = usuario
        self.inventario_window = inventario_window
        self.productos_factura = []
        self.producto_actual = None

        # ---------------- VENTANA PRINCIPAL ----------------
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Compras — RustiGone")
        set_window_size_and_center(
            self.window, width_percent=0.70, min_width=900, min_height=600, parent=parent
        )
        self.window.transient(parent)
        self.window.grab_set()

        # Botón maximizar
        self._is_maximized = False
        self.maximize_btn = ctk.CTkButton(
            self.window, text="🗖", width=35, height=28,
            command=self.toggle_maximize,
            fg_color="#38A169", text_color="white"
        )
        self.maximize_btn.place(relx=0.98, rely=0.015, anchor="ne")
        self.window.after(100, self.maximize_btn.lift)

        # Crear widgets
        self.create_widgets()

    def toggle_maximize(self):
        if not self._is_maximized:
            self.window.state("zoomed")
            self._is_maximized = True
            self.maximize_btn.configure(text="🗗")
        else:
            self.window.state("normal")
            self._is_maximized = False
            self.maximize_btn.configure(text="🗖")

    # ===================================================================
    #                           UI PRINCIPAL
    # ===================================================================

    def create_widgets(self):

        # Frame general
        main = ctk.CTkFrame(self.window, fg_color="white")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        ctk.CTkLabel(
            main,
            text="🛒 Registro de Compras",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#D69E2E"
        ).pack(pady=(0, 14))

        # ===================== SECCIÓN FACTURA =====================
        factura = ctk.CTkFrame(main, fg_color="white")
        factura.pack(fill="x", pady=8)

        self._add_factura_fields(factura)

        # ===================== SECCIÓN BÚSQUEDA =====================
        search = ctk.CTkFrame(main, fg_color="white")
        search.pack(fill="x", pady=8)

        self._add_search_fields(search)

        # ===================== DIVISIÓN IZQUIERDA / DERECHA =====================
        body = ctk.CTkFrame(main, fg_color="white")
        body.pack(fill="both", expand=True, pady=(6, 0))

        # IZQUIERDA → Producto + Lista
        left = ctk.CTkFrame(body, fg_color="white")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self._add_product_info(left)
        self._add_product_list(left)

        # DERECHA → Totales + Botones
        right = ctk.CTkFrame(body, fg_color="white", width=260)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        self._add_totals(right)
        self._add_buttons(right)

    # ===================================================================
    #                      SUB-SECCIONES DE LA UI
    # ===================================================================

    # -------- CAMPOS FACTURA --------
    def _add_factura_fields(self, parent):

        title = ctk.CTkLabel(
            parent,
            text="Datos de la Factura",
            font=ctk.CTkFont(weight="bold", size=14),
            text_color="#4A5568"
        )
        title.pack(anchor="w", padx=4, pady=(0, 6))

        grid = ctk.CTkFrame(parent, fg_color="white")
        grid.pack(fill="x")

        # Labels y entradas
        labels = ["N° Factura", "Proveedor", "RUT", "Fecha"]
        self.factura_entry = ctk.CTkEntry(grid, width=140)
        self.proveedor_entry = ctk.CTkEntry(grid, width=200)
        self.rut_entry = ctk.CTkEntry(grid, width=140)
        self.fecha_entry = ctk.CTkEntry(grid, width=140)
        self.fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        widgets = [
            self.factura_entry,
            self.proveedor_entry,
            self.rut_entry,
            self.fecha_entry
        ]

        for i, (lbl, w) in enumerate(zip(labels, widgets)):
            ctk.CTkLabel(grid, text=lbl + ":", font=ctk.CTkFont(size=12)).grid(
                row=i // 2, column=(i % 2) * 2, sticky="w", pady=4, padx=(6, 8)
            )
            w.grid(row=i // 2, column=(i % 2) * 2 + 1, sticky="w", pady=4)

    # -------- BUSCADOR DE PRODUCTO --------
    def _add_search_fields(self, parent):

        ctk.CTkLabel(
            parent,
            text="Código de Barras:",
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=0, padx=(4, 8), pady=6, sticky="w")

        self.codigo_entry = ctk.CTkEntry(parent, width=220)
        self.codigo_entry.grid(row=0, column=1, pady=6)
        self.codigo_entry.bind("<Return>", self.buscar_producto)

        ctk.CTkButton(
            parent, text="Buscar",
            width=90,
            fg_color="#2B6CB0",
            command=self.buscar_producto
        ).grid(row=0, column=2, padx=8)

    # -------- DATOS DEL PRODUCTO --------
    def _add_product_info(self, parent):

        ctk.CTkLabel(
            parent,
            text="Producto Seleccionado",
            font=ctk.CTkFont(weight="bold", size=14),
            text_color="#4A5568"
        ).pack(anchor="w", padx=4, pady=(0, 4))

        frame = ctk.CTkFrame(parent, fg_color="#F7FAFC", corner_radius=10)
        frame.pack(fill="x", padx=4, pady=4)

        self.producto_label = ctk.CTkLabel(frame, text="-", text_color="#2D3748")
        self.precio_actual_label = ctk.CTkLabel(frame, text="$0", text_color="#2B6CB0")
        self.precio_anterior_label = ctk.CTkLabel(frame, text="$0", text_color="#D69E2E")

        self.valor_entry = ctk.CTkEntry(frame, placeholder_text="Precio Factura", width=150)
        self.cantidad_entry = ctk.CTkEntry(frame, placeholder_text="Cantidad", width=150)

        labels = [
            "Producto:",
            "Precio Venta Actual:",
            "Último Precio Compra:",
            "Valor Factura:",
            "Cantidad:"
        ]

        widgets = [
            self.producto_label,
            self.precio_actual_label,
            self.precio_anterior_label,
            self.valor_entry,
            self.cantidad_entry
        ]

        for i, (lbl, w) in enumerate(zip(labels, widgets)):
            ctk.CTkLabel(frame, text=lbl, font=ctk.CTkFont(size=12, weight="bold")).grid(
                row=i, column=0, sticky="w", padx=8, pady=4
            )
            w.grid(row=i, column=1, sticky="w", padx=8, pady=4)

        ctk.CTkButton(
            frame,
            text="Agregar",
            fg_color="#38A169",
            height=34,
            width=120,
            command=self.agregar_a_factura
        ).grid(row=5, column=0, columnspan=2, pady=8)

    # -------- LISTA DE PRODUCTOS EN FACTURA --------
    def _add_product_list(self, parent):

        ctk.CTkLabel(
            parent,
            text="Productos Agregados",
            font=ctk.CTkFont(weight="bold", size=14),
            text_color="#4A5568"
        ).pack(anchor="w", padx=4, pady=(4, 2))

        self.lista_factura_frame = ctk.CTkScrollableFrame(parent, fg_color="white")
        self.lista_factura_frame.pack(fill="both", expand=True, padx=4, pady=(0, 6))

    # -------- RESUMEN + TOTALES --------
    def _add_totals(self, parent):

        ctk.CTkLabel(
            parent,
            text="Resumen",
            font=ctk.CTkFont(weight="bold", size=16),
            text_color="#4A5568"
        ).pack(pady=10)

        frame = ctk.CTkFrame(parent, fg_color="white")
        frame.pack(fill="x", padx=8)

        labels = ["Subtotal:", "IVA (19%):", "Otros Impuestos:", "TOTAL:"]
        self.subtotal_label = ctk.CTkLabel(frame, text="$0")
        self.iva_label = ctk.CTkLabel(frame, text="$0")
        self.otros_impuestos_entry = ctk.CTkEntry(frame, width=100)
        self.total_label = ctk.CTkLabel(frame, text="$0", text_color="#D69E2E")

        widgets = [
            self.subtotal_label,
            self.iva_label,
            self.otros_impuestos_entry,
            self.total_label
        ]

        for i, (lbl, w) in enumerate(zip(labels, widgets)):
            ctk.CTkLabel(frame, text=lbl, font=ctk.CTkFont(size=12, weight="bold")).grid(
                row=i, column=0, sticky="w", pady=4
            )
            w.grid(row=i, column=1, sticky="e", pady=4)

        self.otros_impuestos_entry.bind("<KeyRelease>", self.calcular_totales)

    # -------- BOTONES DERECHA --------
    def _add_buttons(self, parent):

        frame = ctk.CTkFrame(parent, fg_color="white")
        frame.pack(pady=20)

        ctk.CTkButton(
            frame, text="Guardar Compra",
            fg_color="#38A169",
            width=180,
            height=38,
            command=self.guardar_compra
        ).pack(pady=6)

        ctk.CTkButton(
            frame, text="Limpiar",
            fg_color="#2B6CB0",
            width=180,
            height=34,
            command=self.limpiar_factura
        ).pack(pady=4)

        ctk.CTkButton(
            frame, text="Cancelar",
            fg_color="#E53E3E",
            width=180,
            height=34,
            command=self.window.destroy
        ).pack(pady=4)

# Lógica, operaciones y diálogos

    def buscar_producto(self, event=None):
        """Buscar producto por código de barras en la base de datos."""
        codigo = self.codigo_entry.get().strip()
        if not codigo:
            self.mostrar_error("Ingrese un código de barras")
            return

        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.*, c.nombre as categoria_nombre
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                WHERE p.codigo_barras = ? AND p.activo = 1
                """,
                (codigo,),
            )
            producto = cursor.fetchone()
            conn.close()

            if producto:
                # Intentar convertir a dict si row_factory está activo
                try:
                    self.producto_actual = dict(producto)
                except Exception:
                    # fallback por índices (ajustar según tu esquema)
                    self.producto_actual = {
                        "id": producto[0],
                        "codigo_barras": producto[1],
                        "nombre": producto[2],
                        "precio_compra": producto[4] if len(producto) > 4 else 0,
                        "precio_venta": producto[5] if len(producto) > 5 else 0,
                    }
                self.mostrar_producto(self.producto_actual)
            else:
                # Preguntar si crear producto (diálogo custom)
                self._confirm_dialog(
                    title="Producto No Encontrado",
                    message=f"El producto con código {codigo} no existe.\n¿Desea crearlo ahora?",
                    on_confirm=lambda: self.crear_nuevo_producto(codigo),
                )

        except Exception as e:
            self.mostrar_error(f"Error al buscar producto: {str(e)}")

    def mostrar_producto(self, producto):
        """Actualizar campos con la info del producto encontrado."""
        self.producto_label.configure(text=producto.get("nombre", "-"))
        self.precio_actual_label.configure(text=f"${producto.get('precio_venta', 0):,.0f}")
        self.precio_anterior_label.configure(text=f"${producto.get('precio_compra', 0):,.0f}")
        # limpiar entradas para nuevo valor/cantidad
        self.valor_entry.delete(0, "end")
        self.cantidad_entry.delete(0, "end")
        self.valor_entry.focus()

    def crear_nuevo_producto(self, codigo):
        """Placeholder: mostrar mensaje. Podrías abrir CrearProductoWindow aquí."""
        self.mostrar_mensaje("Crear Producto", f"Función para crear producto {codigo} en desarrollo")

    def agregar_a_factura(self):
        """Agregar el producto actual a la lista de factura (validando datos)."""
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

            item = {
                "id": self.producto_actual.get("id"),
                "codigo": self.producto_actual.get("codigo_barras"),
                "nombre": self.producto_actual.get("nombre"),
                "valor": valor,
                "cantidad": cantidad,
                "subtotal": subtotal,
            }

            self.productos_factura.append(item)
            self.actualizar_lista_factura()
            self.calcular_totales()
            self.limpiar_producto()
        except ValueError:
            self.mostrar_error("Valor y cantidad deben ser números válidos")

    def actualizar_lista_factura(self):
        """Renderizar la lista de productos agregados en el scrollable frame."""
        for w in self.lista_factura_frame.winfo_children():
            w.destroy()

        if not self.productos_factura:
            ctk.CTkLabel(
                self.lista_factura_frame,
                text="No hay productos en la factura",
                text_color="#718096"
            ).pack(expand=True, pady=12)
            return

        for idx, item in enumerate(self.productos_factura):
            item_frame = ctk.CTkFrame(self.lista_factura_frame, fg_color="white")
            item_frame.pack(fill="x", pady=6, padx=6)

            # Nombre + detalle
            ctk.CTkLabel(item_frame, text=item["nombre"], font=ctk.CTkFont(weight="bold", size=12), text_color="#2D3748").pack(side="left", padx=8)
            ctk.CTkLabel(item_frame, text=f"{item['cantidad']} x ${item['valor']:,.0f} = ${item['subtotal']:,.0f}", text_color="#4A5568").pack(side="right", padx=8)

            # Botón eliminar pequeño
            def _rem(i=idx):
                try:
                    del self.productos_factura[i]
                    self.actualizar_lista_factura()
                    self.calcular_totales()
                except Exception:
                    pass

            ctk.CTkButton(item_frame, text="Eliminar", width=80, height=26, fg_color="#E53E3E", command=_rem).pack(side="right", padx=(0,8))

    def calcular_totales(self, event=None):
        """Calcular subtotal, IVA y total (incluye 'otros impuestos')."""
        try:
            subtotal = sum(item["subtotal"] for item in self.productos_factura)
            iva = subtotal * 0.19
            otros = float(self.otros_impuestos_entry.get() or 0)
            total = subtotal + iva + otros

            self.subtotal_label.configure(text=f"${subtotal:,.0f}")
            self.iva_label.configure(text=f"${iva:,.0f}")
            self.total_label.configure(text=f"${total:,.0f}")
        except ValueError:
            # Si 'otros impuestos' no es número, ignorar
            pass

    def guardar_compra(self):
        """Confirmar antes de guardar la compra en BD."""
        if not self.productos_factura:
            self.mostrar_error("No hay productos en la factura")
            return

        self._confirm_dialog(
            title="Confirmar Compra",
            message="¿Desea guardar la compra?",
            on_confirm=self._guardar_compra_db
        )

    def _guardar_compra_db(self):
        """Persistir compra y detalle en la base de datos y actualizar stocks."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()

            total_val = float(self.total_label.cget("text").replace("$", "").replace(",", ""))

            cursor.execute(
                """
                INSERT INTO compras (numero_factura, proveedor, rut_proveedor, fecha_compra, total, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    self.factura_entry.get(),
                    self.proveedor_entry.get(),
                    self.rut_entry.get(),
                    self.fecha_entry.get(),
                    total_val,
                    self.usuario.get("id"),
                )
            )

            compra_id = cursor.lastrowid

            for item in self.productos_factura:
                cursor.execute(
                    """
                    INSERT INTO detalle_compras (compra_id, producto_id, cantidad, precio_compra, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (compra_id, item["id"], item["cantidad"], item["valor"], item["subtotal"])
                )

                # Actualizar producto: precio_compra, stock y fecha_ultima_compra
                cursor.execute(
                    """
                    UPDATE productos
                    SET precio_compra = ?, stock_actual = stock_actual + ?, fecha_ultima_compra = ?
                    WHERE id = ?
                    """,
                    (item["valor"], item["cantidad"], datetime.now(), item["id"])
                )

            conn.commit()
            conn.close()

            self.mostrar_exito("Compra registrada exitosamente")
            self.limpiar_factura()

            # Si se pasó referencia a ventana inventario, refrescar
            if self.inventario_window:
                try:
                    self.inventario_window.refrescar_lista()
                except Exception:
                    pass

        except Exception as e:
            self.mostrar_error(f"Error al guardar compra: {str(e)}")

    def limpiar_producto(self):
        """Limpiar campos relacionados al producto actualmente seleccionado."""
        self.producto_actual = None
        try:
            self.producto_label.configure(text="-")
            self.precio_actual_label.configure(text="$0")
            self.precio_anterior_label.configure(text="$0")
            self.valor_entry.delete(0, "end")
            self.cantidad_entry.delete(0, "end")
            self.codigo_entry.delete(0, "end")
            self.codigo_entry.focus()
        except Exception:
            pass

    def limpiar_factura(self):
        """Resetear toda la factura (lista y campos)."""
        self.productos_factura = []
        self.actualizar_lista_factura()
        self.calcular_totales()
        self.limpiar_producto()
        try:
            self.factura_entry.delete(0, "end")
            self.proveedor_entry.delete(0, "end")
            self.rut_entry.delete(0, "end")
            self.otros_impuestos_entry.delete(0, "end")
        except Exception:
            pass

    # ---------------------- DIÁLOGOS CUSTOM ----------------------

    def _confirm_dialog(self, title, message, on_confirm=None):
        """Diálogo modal estilo CustomTkinter con Sí / No."""
        dialog = ctk.CTkToplevel(self.window)
        dialog.title(title)
        set_window_size_and_center(dialog, width_percent=0.30, min_width=380, min_height=150, parent=self.window)
        dialog.transient(self.window)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=message, wraplength=340).pack(expand=True, pady=(16, 8), padx=12)

        btns = ctk.CTkFrame(dialog, fg_color="white")
        btns.pack(pady=(6, 12))

        def _yes():
            dialog.destroy()
            if on_confirm:
                on_confirm()

        def _no():
            dialog.destroy()

        ctk.CTkButton(btns, text="Sí", width=90, height=30, fg_color="#38A169", command=_yes).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="No", width=90, height=30, fg_color="#E53E3E", command=_no).pack(side="left", padx=8)

    def mostrar_error(self, mensaje):
        """Ventana de error simple (modal)."""
        win = ctk.CTkToplevel(self.window)
        win.title("Error")
        set_window_size_and_center(win, width_percent=0.35, min_width=380, min_height=140, parent=self.window)
        win.transient(self.window)
        win.grab_set()

        ctk.CTkLabel(win, text="❌ " + mensaje, wraplength=340).pack(expand=True, pady=16, padx=12)
        ctk.CTkButton(win, text="Aceptar", width=120, command=win.destroy).pack(pady=(8, 12))

    def mostrar_exito(self, mensaje):
        """Ventana de éxito simple (modal)."""
        win = ctk.CTkToplevel(self.window)
        win.title("Éxito")
        set_window_size_and_center(win, width_percent=0.35, min_width=380, min_height=140, parent=self.window)
        win.transient(self.window)
        win.grab_set()

        ctk.CTkLabel(win, text="✅ " + mensaje, wraplength=340).pack(expand=True, pady=16, padx=12)
        ctk.CTkButton(win, text="Aceptar", width=120, command=win.destroy).pack(pady=(8, 12))

    def mostrar_mensaje(self, titulo, mensaje):
        """Ventana informativa genérica."""
        win = ctk.CTkToplevel(self.window)
        win.title(titulo)
        set_window_size_and_center(win, width_percent=0.38, min_width=380, min_height=160, parent=self.window)
        win.transient(self.window)
        win.grab_set()

        ctk.CTkLabel(win, text=mensaje, wraplength=360).pack(expand=True, pady=14, padx=12)
        ctk.CTkButton(win, text="Aceptar", width=120, command=win.destroy).pack(pady=(8, 12))
