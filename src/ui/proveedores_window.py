# ui/proveedores_window.py - Versión A (mejorada, compacta y con edición activa)
import customtkinter as ctk
from datetime import datetime
import sqlite3

from ui.responsive import set_window_size_and_center


class ProveedoresWindow:
    def __init__(self, parent, db, usuario, inventario_window=None):
        self.parent = parent
        self.db = db
        self.usuario = usuario
        self.inventario_window = inventario_window

        self.proveedor_seleccionado = None

        # Ventana principal
        self.window = ctk.CTkToplevel(parent)
        self.window.title("👥 Proveedores - RUSTIGONE")
        set_window_size_and_center(self.window, width_percent=0.60, min_width=880, min_height=520, parent=parent)
        self.window.transient(parent)
        self.window.grab_set()

        # Botón maximizar (compacto, estilo A)
        self._is_maximized = False
        self.maximize_btn = ctk.CTkButton(
            self.window, text="🗖", width=35, height=28,
            command=self.toggle_maximize, fg_color="#38A169", text_color="white"
        )
        self.maximize_btn.place(relx=0.98, rely=0.015, anchor="ne")
        # Asegurar que quede al frente
        try:
            self.maximize_btn.lift()
        except Exception:
            try:
                self.maximize_btn.tkraise()
            except Exception:
                pass

        self.create_widgets()
        self.actualizar_lista_proveedores()

    def toggle_maximize(self):
        if not self._is_maximized:
            self.window.state("zoomed")
            self._is_maximized = True
            self.maximize_btn.configure(text="🗗")
        else:
            self.window.state("normal")
            self._is_maximized = False
            self.maximize_btn.configure(text="🗖")

    # -------------------- UI --------------------
    def create_widgets(self):
        main = ctk.CTkFrame(self.window, fg_color="white")
        main.pack(fill="both", expand=True, padx=12, pady=10)

        # Título compacto
        ctk.CTkLabel(
            main,
            text="👥 Gestión de Proveedores",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#2D3748"
        ).pack(pady=(6, 10))

        content = ctk.CTkFrame(main, fg_color="transparent")
        content.pack(fill="both", expand=True)

        # Izquierda: buscador + lista
        left = ctk.CTkFrame(content, fg_color="white")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Buscador + acciones compactas
        search_frame = ctk.CTkFrame(left, fg_color="transparent")
        search_frame.pack(fill="x", padx=6, pady=(0, 8))

        ctk.CTkLabel(search_frame, text="Buscar:", font=ctk.CTkFont(weight="bold", size=12)).pack(side="left", padx=(0, 8))
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="RUT, nombre, giro...", width=360)
        self.search_entry.pack(side="left", padx=(0, 8), fill="x", expand=True)
        self.search_entry.bind("<Return>", self.buscar_proveedores)

        ctk.CTkButton(search_frame, text="🔍", width=60, height=30, command=self.buscar_proveedores).pack(side="left", padx=6)
        ctk.CTkButton(search_frame, text="🔄", width=60, height=30, command=self.limpiar_busqueda, fg_color="#718096").pack(side="left", padx=6)

        # Acciones principales
        actions = ctk.CTkFrame(search_frame, fg_color="transparent")
        actions.pack(side="right")
        ctk.CTkButton(actions, text="➕ Nuevo", fg_color="#38A169", width=120, height=30, command=self.crear_proveedor).pack(side="left", padx=6)
        self.editar_btn = ctk.CTkButton(actions, text="✏️ Editar", fg_color="#D69E2E", width=120, height=30, command=self.editar_proveedor, state="disabled")
        self.editar_btn.pack(side="left", padx=6)

        # Lista header (compact)
        header = ctk.CTkFrame(left, fg_color="#EDF2F7", height=36)
        header.pack(fill="x", padx=6, pady=(0, 4))
        header.pack_propagate(False)
        headers = ["RUT", "Nombre", "Giro", "Contacto", "Teléfono", "Estado"]
        # distribute approximate widths using pack side left
        for h in headers:
            ctk.CTkLabel(header, text=h, font=ctk.CTkFont(weight="bold", size=11), text_color="#2D3748").pack(side="left", padx=8)

        # Lista scrollable
        self.lista_proveedores = ctk.CTkScrollableFrame(left, fg_color="white")
        self.lista_proveedores.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        # Derecha: info / detalles (se transformará en formulario cuando edites)
        right = ctk.CTkFrame(content, fg_color="white", width=360)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self.info_frame = right

        self.mostrar_info_vacia()

    # -------------------- Helpers de UI --------------------
    def mostrar_info_vacia(self):
        for w in self.info_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.info_frame, text="ℹ️ Selecciona un proveedor", font=ctk.CTkFont(weight="bold", size=14), text_color="#718096").pack(expand=True, pady=20)

    def mostrar_info_proveedor(self, proveedor):
        """Muestra la info en panel derecho (lectura)."""
        for w in self.info_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.info_frame, text="📋 Información del Proveedor", font=ctk.CTkFont(weight="bold", size=14), text_color="#2D3748").pack(pady=(12, 8))

        info = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        info.pack(fill="both", expand=True, padx=12)

        datos = [
            ("RUT", proveedor.get("rut", "")),
            ("Nombre", proveedor.get("nombre", "")),
            ("Giro", proveedor.get("giro") or "No especificado"),
            ("Dirección", proveedor.get("direccion") or "No especificada"),
            ("Teléfono", proveedor.get("telefono") or "No especificado"),
            ("Email", proveedor.get("email") or "No especificado"),
            ("Contacto", proveedor.get("contacto") or "No especificado"),
            ("Estado", "Activo" if proveedor.get("activo") else "Inactivo"),
            ("Registro", proveedor.get("fecha_registro")[:10] if fornecedor_val(proveedor := proveedor) else "No disponible")
        ]

        # Render filas
        for i, (label, val) in enumerate(datos):
            ctk.CTkLabel(info, text=label + ":", font=ctk.CTkFont(weight="bold", size=11)).grid(row=i, column=0, sticky="w", padx=(0, 6), pady=4)
            ctk.CTkLabel(info, text=val, text_color="#4A5568").grid(row=i, column=1, sticky="w", pady=4)

        # Estadísticas rápidas (consulta)
        stats = self._obtener_estadisticas_proveedor(proveedor.get("id"))
        start_row = len(datos) + 1
        ctk.CTkLabel(info, text="\n📊 Estadísticas", font=ctk.CTkFont(weight="bold", size=12)).grid(row=start_row, column=0, columnspan=2, sticky="w", pady=(12, 6))
        ctk.CTkLabel(info, text="Total Compras:", font=ctk.CTkFont(size=11)).grid(row=start_row+1, column=0, sticky="w", padx=(0,6))
        ctk.CTkLabel(info, text=str(stats.get("total_compras", 0)), text_color="#2B6CB0").grid(row=start_row+1, column=1, sticky="w")
        ctk.CTkLabel(info, text="Monto Total:", font=ctk.CTkFont(size=11)).grid(row=start_row+2, column=0, sticky="w", padx=(0,6))
        ctk.CTkLabel(info, text=f"${stats.get('monto_total', 0):,.0f}", text_color="#2B6CB0").grid(row=start_row+2, column=1, sticky="w")
        ctk.CTkLabel(info, text="Última Compra:", font=ctk.CTkFont(size=11)).grid(row=start_row+3, column=0, sticky="w", padx=(0,6))
        ctk.CTkLabel(info, text=stats.get("ultima_compra") or "Nunca", text_color="#4A5568").grid(row=start_row+3, column=1, sticky="w")

    # -------------------- DB & Lista --------------------
    def _row_to_dict(self, cursor, row):
        """Convierte una fila sqlite (tuple) a dict usando cursor.description."""
        if row is None:
            return None
        desc = [col[0] for col in cursor.description]
        return {k: row[i] for i, k in enumerate(desc)}

    def actualizar_lista_proveedores(self, proveedores=None):
        for w in self.lista_proveedores.winfo_children():
            w.destroy()

        if proveedores is None:
            conn = self.db.connect()
            cur = conn.cursor()
            cur.execute("SELECT * FROM proveedores ORDER BY nombre")
            rows = cur.fetchall()
            proveedores = [self._row_to_dict(cur, r) for r in rows]
            conn.close()

        if not proveedores:
            ctk.CTkLabel(self.lista_proveedores, text="No hay proveedores", text_color="#718096").pack(expand=True, pady=30)
            return

        for i, prov in enumerate(proveedores):
            bg = "#F7FAFC" if i % 2 == 0 else "white"
            prov_frame = ctk.CTkFrame(self.lista_proveedores, fg_color=bg, height=44)
            prov_frame.pack(fill="x", pady=1, padx=6)
            prov_frame.pack_propagate(False)

            inner = ctk.CTkFrame(prov_frame, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=8)

            # Build compact labels (pack left)
            ctk.CTkLabel(inner, text=prov.get("rut", ""), width=110, anchor="w", text_color="#4A5568").pack(side="left", padx=6)
            ctk.CTkLabel(inner, text=prov.get("nombre", ""), width=220, anchor="w", text_color="#2D3748", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=6)
            ctk.CTkLabel(inner, text=prov.get("giro") or "-", width=160, anchor="w", text_color="#4A5568").pack(side="left", padx=6)
            ctk.CTkLabel(inner, text=prov.get("contacto") or "-", width=140, anchor="w", text_color="#4A5568").pack(side="left", padx=6)
            ctk.CTkLabel(inner, text=prov.get("telefono") or "-", width=120, anchor="w", text_color="#4A5568").pack(side="left", padx=6)
            estado_txt = "🟢" if prov.get("activo") else "🔴"
            ctk.CTkLabel(inner, text=estado_txt, width=60, anchor="w", text_color="#38A169" if prov.get("activo") else "#E53E3E").pack(side="left", padx=6)

            # Bind click
            prov_frame.bind("<Button-1>", lambda e, p=prov: self.seleccionar_proveedor(p))
            for child in inner.winfo_children():
                child.bind("<Button-1>", lambda e, p=prov: self.seleccionar_proveedor(p))

    def seleccionar_proveedor(self, proveedor):
        self.proveedor_seleccionado = proveedor
        self.mostrar_info_proveedor(proveedor)
        self.editar_btn.configure(state="normal")

    def _obtener_estadisticas_proveedor(self, proveedor_id):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) as total_compras, IFNULL(SUM(total),0) as monto_total, MAX(fecha_compra) as ultima_compra
            FROM compras WHERE proveedor_id = ?
        """, (proveedor_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            # row might be tuple, map manually
            return {"total_compras": row[0] or 0, "monto_total": row[1] or 0, "ultima_compra": row[2]}
        return {"total_compras": 0, "monto_total": 0, "ultima_compra": None}

    # -------------------- BÚSQUEDA --------------------
    def buscar_proveedores(self, event=None):
        criterio = self.search_entry.get().strip()
        if not criterio:
            self.actualizar_lista_proveedores()
            self.proveedor_seleccionado = None
            self.mostrar_info_vacia()
            self.editar_btn.configure(state="disabled")
            return

        conn = self.db.connect()
        cur = conn.cursor()
        like = f"%{criterio}%"
        cur.execute("""
            SELECT * FROM proveedores
            WHERE rut LIKE ? OR nombre LIKE ? OR giro LIKE ? OR contacto LIKE ?
            ORDER BY nombre
        """, (like, like, like, like))
        rows = cur.fetchall()
        resultados = [self._row_to_dict(cur, r) for r in rows]
        conn.close()
        self.actualizar_lista_proveedores(resultados)
        self.proveedor_seleccionado = None
        self.mostrar_info_vacia()
        self.editar_btn.configure(state="disabled")

    def limpiar_busqueda(self):
        self.search_entry.delete(0, "end")
        self.actualizar_lista_proveedores()
        self.proveedor_seleccionado = None
        self.mostrar_info_vacia()
        self.editar_btn.configure(state="disabled")

    # -------------------- CREAR / EDITAR (Nueva ventana estilo A) --------------------
    def crear_proveedor(self):
        self._open_proveedor_dialog(mode="create")

    def editar_proveedor(self):
        if not self.proveedor_seleccionado:
            return
        self._open_proveedor_dialog(mode="edit", proveedor=self.proveedor_seleccionado)

    def _open_proveedor_dialog(self, mode="create", proveedor=None):
        """Abre un diálogo modal (igual al de 'crear') para crear o editar."""
        dialog = ctk.CTkToplevel(self.window)
        dialog.transient(self.window)
        dialog.grab_set()
        dialog.title("Nuevo Proveedor" if mode == "create" else f"Editar: {proveedor.get('nombre')}")
        set_window_size_and_center(dialog, width_percent=0.45, min_width=520, min_height=520, parent=self.window)

        # Título compacto
        ctk.CTkLabel(dialog, text="➕ Nuevo Proveedor" if mode == "create" else "✏️ Editar Proveedor",
                     font=ctk.CTkFont(weight="bold", size=16)).pack(pady=12)

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=18, pady=8)

        campos = [
            ("RUT*", "rut"),
            ("Nombre*", "nombre"),
            ("Giro", "giro"),
            ("Dirección", "direccion"),
            ("Teléfono", "telefono"),
            ("Email", "email"),
            ("Persona Contacto", "contacto")
        ]

        entries = {}
        for i, (label_text, key) in enumerate(campos):
            ctk.CTkLabel(form, text=label_text + ":", font=ctk.CTkFont(weight="bold", size=12)).grid(row=i, column=0, sticky="w", pady=6, padx=(0,8))
            ent = ctk.CTkEntry(form, width=320)
            ent.grid(row=i, column=1, sticky="w", pady=6)
            entries[key] = ent

        # Estado radio buttons
        ctk.CTkLabel(form, text="Estado:", font=ctk.CTkFont(weight="bold", size=12)).grid(row=len(campos), column=0, sticky="w", pady=8)
        estado_var = ctk.StringVar(value="ACTIVO")
        estado_frame = ctk.CTkFrame(form, fg_color="transparent")
        estado_frame.grid(row=len(campos), column=1, sticky="w", pady=8)
        ctk.CTkRadioButton(estado_frame, text="Activo", value="ACTIVO", variable=estado_var).pack(side="left", padx=8)
        ctk.CTkRadioButton(estado_frame, text="Inactivo", value="INACTIVO", variable=estado_var).pack(side="left", padx=8)

        # Prefill si es editar
        if mode == "edit" and proveedor:
            entries['rut'].insert(0, proveedor.get("rut") or "")
            entries['nombre'].insert(0, proveedor.get("nombre") or "")
            entries['giro'].insert(0, proveedor.get("giro") or "")
            entries['direccion'].insert(0, proveedor.get("direccion") or "")
            entries['telefono'].insert(0, proveedor.get("telefono") or "")
            entries['email'].insert(0, proveedor.get("email") or "")
            entries['contacto'].insert(0, proveedor.get("contacto") or "")
            estado_var.set("ACTIVO" if proveedor.get("activo") else "INACTIVO")

        # Guardar / Cancelar
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=12)

        def _on_save():
            # Validaciones básicas
            rut = entries['rut'].get().strip()
            nombre = entries['nombre'].get().strip()
            if not rut or not nombre:
                self._dialog_error(dialog, "RUT y Nombre son obligatorios")
                return

            try:
                conn = self.db.connect()
                cur = conn.cursor()

                # Verificar duplicado de RUT
                if mode == "create":
                    cur.execute("SELECT id FROM proveedores WHERE rut = ?", (rut,))
                    if cur.fetchone():
                        conn.close()
                        self._dialog_error(dialog, "El RUT ya está registrado")
                        return

                    cur.execute(
                        """
                        INSERT INTO proveedores
                        (rut, nombre, giro, direccion, telefono, email, contacto, activo, fecha_registro)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            rut,
                            nombre,
                            entries['giro'].get() or None,
                            entries['direccion'].get() or None,
                            entries['telefono'].get() or None,
                            entries['email'].get() or None,
                            entries['contacto'].get() or None,
                            estado_var.get() == "ACTIVO",
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                    )
                    conn.commit()
                    conn.close()
                    dialog.destroy()
                    self.actualizar_lista_proveedores()
                    self._dialog_info("Éxito", "Proveedor creado correctamente")
                else:
                    # Edit mode: evitar conflicto de RUT con otros registros
                    cur.execute("SELECT id FROM proveedores WHERE rut = ? AND id != ?", (rut, proveedor.get("id")))
                    if cur.fetchone():
                        conn.close()
                        self._dialog_error(dialog, "El RUT ya está en uso por otro proveedor")
                        return

                    cur.execute(
                        """
                        UPDATE proveedores
                        SET rut = ?, nombre = ?, giro = ?, direccion = ?, telefono = ?, email = ?, contacto = ?, activo = ?
                        WHERE id = ?
                        """,
                        (
                            rut,
                            nombre,
                            entries['giro'].get() or None,
                            entries['direccion'].get() or None,
                            entries['telefono'].get() or None,
                            entries['email'].get() or None,
                            entries['contacto'].get() or None,
                            estado_var.get() == "ACTIVO",
                            proveedor.get("id")
                        )
                    )
                    conn.commit()
                    conn.close()
                    dialog.destroy()
                    self.actualizar_lista_proveedores()
                    # re-seleccionar proveedor actualizado
                    try:
                        # fetch updated row to show
                        conn2 = self.db.connect()
                        cur2 = conn2.cursor()
                        cur2.execute("SELECT * FROM proveedores WHERE id = ?", (proveedor.get("id"),))
                        row = cur2.fetchone()
                        prov = self._row_to_dict(cur2, row) if row else None
                        conn2.close()
                        if prov:
                            self.seleccionar_proveedor(prov)
                    except Exception:
                        pass
                    self._dialog_info("Éxito", "Proveedor actualizado correctamente")

            except Exception as e:
                try:
                    conn.close()
                except Exception:
                    pass
                self._dialog_error(dialog, f"Error al guardar: {str(e)}")

        ctk.CTkButton(btn_frame, text="Guardar", fg_color="#38A169", width=120, height=34, command=_on_save).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="#718096", width=120, height=34, command=dialog.destroy).pack(side="left", padx=8)

    # -------------------- Mensajes / diálogos (custom) --------------------
    def _dialog_error(self, parent, message):
        win = ctk.CTkToplevel(parent if isinstance(parent, ctk.CTk) else self.window)
        win.title("Error")
        set_window_size_and_center(win, width_percent=0.30, min_width=360, min_height=140, parent=parent)
        win.transient(parent)
        win.grab_set()
        ctk.CTkLabel(win, text="❌ " + message, wraplength=320).pack(expand=True, pady=12, padx=12)
        ctk.CTkButton(win, text="Aceptar", width=120, command=win.destroy).pack(pady=8)

    def _dialog_info(self, title, message):
        win = ctk.CTkToplevel(self.window)
        win.title(title)
        set_window_size_and_center(win, width_percent=0.32, min_width=380, min_height=140, parent=self.window)
        win.transient(self.window)
        win.grab_set()
        ctk.CTkLabel(win, text="✅ " + message, wraplength=320).pack(expand=True, pady=12, padx=12)
        ctk.CTkButton(win, text="Aceptar", width=120, command=win.destroy).pack(pady=8)

# Helper function used locally in mostrar_info_proveedor()
def fornecedor_val(proveedor):
    # small helper to avoid NameError if proveedor is None, used when slicing fecha_registro
    return proveedor is not None and isinstance(proveedor, dict)
