# ui/modificar_producto_window.py - VERSIÓN CORREGIDA
import customtkinter as ctk
import sqlite3
from datetime import datetime

class ModificarProductoWindow:
    def __init__(self, parent, db, inventario_window, producto):
        self.parent = parent
        self.db = db
        self.inventario_window = inventario_window
        self.producto = producto
        
        print("🔄 Iniciando ModificarProductoWindow...")  # Debug
        print("📦 Datos del producto:", producto)  # Debug
        
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Modificar Producto - RUSTIGONE")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(self.window, width_percent=0.45, min_width=500, min_height=650, parent=parent)
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
        """Crear formulario para modificar producto"""
        try:
            main_frame = ctk.CTkFrame(self.window, fg_color="white")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título
            ctk.CTkLabel(
                main_frame,
                text="✏️ MODIFICAR PRODUCTO",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#D69E2E"
            ).pack(pady=20)
            
            # Formulario
            form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            form_frame.pack(fill="both", expand=True)
            
            # Configurar grid para mejor alineación
            form_frame.grid_columnconfigure(1, weight=1)
            
            # Código de barras (no editable)
            ctk.CTkLabel(form_frame, text="Código de Barras:", 
                        font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", pady=10, padx=10)
            codigo_text = self.producto.get('codigo_barras', '') or "Sin código"
            self.codigo_label = ctk.CTkLabel(form_frame, text=codigo_text, text_color="#4A5568")
            self.codigo_label.grid(row=0, column=1, sticky="w", pady=10, padx=10)
            
            # Nombre
            ctk.CTkLabel(form_frame, text="Nombre:", 
                        font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", pady=10, padx=10)
            self.nombre_entry = ctk.CTkEntry(form_frame)
            self.nombre_entry.insert(0, self.producto.get('nombre', ''))
            self.nombre_entry.grid(row=1, column=1, sticky="ew", pady=10, padx=10)
            
            # Descripción
            ctk.CTkLabel(form_frame, text="Descripción:", 
                        font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", pady=10, padx=10)
            self.descripcion_entry = ctk.CTkEntry(form_frame)
            descripcion = self.producto.get('descripcion', '') or ""
            self.descripcion_entry.insert(0, descripcion)
            self.descripcion_entry.grid(row=2, column=1, sticky="ew", pady=10, padx=10)
            
            # Precio Compra
            ctk.CTkLabel(form_frame, text="Precio Compra:", 
                        font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, sticky="w", pady=10, padx=10)
            self.precio_compra_entry = ctk.CTkEntry(form_frame)
            self.precio_compra_entry.insert(0, str(self.producto.get('precio_compra', 0)))
            self.precio_compra_entry.grid(row=3, column=1, sticky="ew", pady=10, padx=10)
            
            # % Ganancia
            ctk.CTkLabel(form_frame, text="% Ganancia:", 
                        font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, sticky="w", pady=10, padx=10)
            self.ganancia_entry = ctk.CTkEntry(form_frame)
            self.ganancia_entry.insert(0, str(self.producto.get('porcentaje_ganancia', 30)))
            self.ganancia_entry.grid(row=4, column=1, sticky="ew", pady=10, padx=10)
            
            # Precio Venta
            ctk.CTkLabel(form_frame, text="Precio Venta:", 
                        font=ctk.CTkFont(weight="bold")).grid(row=5, column=0, sticky="w", pady=10, padx=10)
            self.precio_venta_entry = ctk.CTkEntry(form_frame)
            self.precio_venta_entry.insert(0, str(self.producto.get('precio_venta', 0)))
            self.precio_venta_entry.grid(row=5, column=1, sticky="ew", pady=10, padx=10)
            
            # Stock Actual
            ctk.CTkLabel(form_frame, text="Stock Actual:", 
                        font=ctk.CTkFont(weight="bold")).grid(row=6, column=0, sticky="w", pady=10, padx=10)
            self.stock_entry = ctk.CTkEntry(form_frame)
            self.stock_entry.insert(0, str(self.producto.get('stock_actual', 0)))
            self.stock_entry.grid(row=6, column=1, sticky="ew", pady=10, padx=10)
            
            # Stock Mínimo
            ctk.CTkLabel(form_frame, text="Stock Mínimo:", 
                        font=ctk.CTkFont(weight="bold")).grid(row=7, column=0, sticky="w", pady=10, padx=10)
            self.stock_min_entry = ctk.CTkEntry(form_frame)
            self.stock_min_entry.insert(0, str(self.producto.get('stock_minimo', 1)))
            self.stock_min_entry.grid(row=7, column=1, sticky="ew", pady=10, padx=10)
            
            # Unidad de Medida
            ctk.CTkLabel(form_frame, text="Unidad Medida:", 
                        font=ctk.CTkFont(weight="bold")).grid(row=8, column=0, sticky="w", pady=10, padx=10)
            self.unidad_combo = ctk.CTkComboBox(
                form_frame,
                values=["unidad", "kg", "g", "l", "ml"]
            )
            self.unidad_combo.set(self.producto.get('unidad_medida', 'unidad'))
            self.unidad_combo.grid(row=8, column=1, sticky="ew", pady=10, padx=10)
            
            # Categoría
            ctk.CTkLabel(form_frame, text="Categoría:", 
                        font=ctk.CTkFont(weight="bold")).grid(row=9, column=0, sticky="w", pady=10, padx=10)
            
            # Obtener categorías de la base de datos
            categorias = self.obtener_categorias()
            self.categoria_combo = ctk.CTkComboBox(
                form_frame,
                values=categorias
            )
            
            # Establecer categoría actual si existe
            categoria_actual = self.producto.get('categoria_nombre', '')
            if categoria_actual and categoria_actual in categorias:
                self.categoria_combo.set(categoria_actual)
            elif categorias:
                self.categoria_combo.set(categorias[0])
                
            self.categoria_combo.grid(row=9, column=1, sticky="ew", pady=10, padx=10)
            
            # Botón crear nueva categoría
            ctk.CTkButton(
                form_frame,
                text="➕ Nueva Categoría",
                command=self.crear_nueva_categoria,
                fg_color="#718096"
            ).grid(row=10, column=1, sticky="w", pady=5, padx=10)
            
            # Información no editable
            info_frame = ctk.CTkFrame(main_frame, fg_color="#EDF2F7", corner_radius=10)
            info_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                info_frame,
                text="📊 INFORMACIÓN DEL SISTEMA (No editable)",
                font=ctk.CTkFont(weight="bold", size=12),
                text_color="#4A5568"
            ).pack(pady=10)
            
            # Formatear fechas
            ultima_compra = self.producto.get('fecha_ultima_compra', '') or 'Nunca'
            ultima_venta = self.producto.get('fecha_ultima_venta', '') or 'Nunca'
            fecha_creacion = self.producto.get('fecha_creacion', '') or 'Desconocida'
            
            info_text = f"""• Última compra: {ultima_compra}
• Última venta: {ultima_venta}
• Fecha creación: {fecha_creacion}"""
        
            ctk.CTkLabel(
                info_frame,
                text=info_text.strip(),
                font=ctk.CTkFont(size=11),
                text_color="#718096",
                justify="left"
            ).pack(padx=20, pady=10)
            
            # Botones de acción
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(pady=20)
            
            ctk.CTkButton(
                button_frame,
                text="💾 GUARDAR CAMBIOS",
                command=self.guardar_cambios,
                fg_color="#38A169",
                font=ctk.CTkFont(weight="bold")
            ).pack(side="left", padx=10)
            
            ctk.CTkButton(
                button_frame,
                text="🔄 CALCULAR PRECIO",
                command=self.calcular_precio_venta,
                fg_color="#2B6CB0",
                font=ctk.CTkFont(weight="bold")
            ).pack(side="left", padx=10)
            
            ctk.CTkButton(
                button_frame,
                text="❌ CANCELAR",
                command=self.window.destroy,
                fg_color="#E53E3E",
                font=ctk.CTkFont(weight="bold")
            ).pack(side="left", padx=10)
            
            # Bind eventos para cálculo automático
            self.precio_compra_entry.bind("<KeyRelease>", lambda e: self.calcular_precio_venta())
            self.ganancia_entry.bind("<KeyRelease>", lambda e: self.calcular_precio_venta())
            
            print("✅ Ventana de modificación creada exitosamente")
            
        except Exception as e:
            print(f"❌ Error al crear widgets: {e}")
            self.mostrar_error(f"Error al crear la ventana: {str(e)}")
    
    def obtener_categorias(self):
        """Obtener lista de categorías de la base de datos"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM categorias ORDER BY nombre")
            categorias = [row[0] for row in cursor.fetchall()]
            conn.close()
            return categorias
        except Exception as e:
            print(f"❌ Error al obtener categorías: {e}")
            return ["General"]
    
    def crear_nueva_categoria(self):
        """Crear nueva categoría"""
        try:
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
        except Exception as e:
            self.mostrar_error(f"Error en diálogo: {str(e)}")
    
    def calcular_precio_venta(self):
        """Calcular precio de venta automáticamente"""
        try:
            precio_compra_text = self.precio_compra_entry.get().strip()
            ganancia_text = self.ganancia_entry.get().strip()
            
            if not precio_compra_text:
                return
                
            precio_compra = float(precio_compra_text)
            ganancia = float(ganancia_text) if ganancia_text else 30
            
            precio_venta = precio_compra * (1 + ganancia/100)
            self.precio_venta_entry.delete(0, 'end')
            self.precio_venta_entry.insert(0, f"{precio_venta:.0f}")
        except ValueError:
            # Ignorar errores de conversión
            pass
    
    def guardar_cambios(self):
        """Guardar cambios del producto en la base de datos"""
        try:
            print("💾 Guardando cambios del producto...")
            
            # Validar campos obligatorios
            if not self.nombre_entry.get().strip():
                self.mostrar_error("El nombre del producto es obligatorio")
                return
            
            if not self.precio_compra_entry.get().strip():
                self.mostrar_error("El precio de compra es obligatorio")
                return
            
            # Obtener datos del formulario
            nombre = self.nombre_entry.get().strip()
            descripcion = self.descripcion_entry.get().strip() or None
            precio_compra = float(self.precio_compra_entry.get())
            porcentaje_ganancia = float(self.ganancia_entry.get() or 30)
            precio_venta = float(self.precio_venta_entry.get() or precio_compra * 1.3)
            stock_actual = float(self.stock_entry.get() or 0)
            stock_minimo = float(self.stock_min_entry.get() or 1)
            unidad_medida = self.unidad_combo.get()
            categoria_nombre = self.categoria_combo.get()
            
            print(f"📝 Datos a guardar: {nombre}, {precio_compra}, {precio_venta}")
            
            # Obtener ID de categoría
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM categorias WHERE nombre = ?", (categoria_nombre,))
            categoria_result = cursor.fetchone()
            categoria_id = categoria_result[0] if categoria_result else None
            
            print(f"🔍 Categoría ID: {categoria_id}")
            
            # Actualizar producto
            cursor.execute('''
                UPDATE productos 
                SET nombre = ?, descripcion = ?, precio_compra = ?, porcentaje_ganancia = ?,
                    precio_venta = ?, stock_actual = ?, stock_minimo = ?, categoria_id = ?, unidad_medida = ?
                WHERE id = ?
            ''', (nombre, descripcion, precio_compra, porcentaje_ganancia,
                  precio_venta, stock_actual, stock_minimo, categoria_id, unidad_medida, self.producto['id']))
            
            conn.commit()
            conn.close()
            
            self.mostrar_exito("✅ Producto actualizado exitosamente")
            self.inventario_window.refrescar_lista()
            self.window.destroy()
            
        except ValueError as e:
            print(f"❌ Error de valor: {e}")
            self.mostrar_error("Error en los valores numéricos. Verifique los precios y stocks.")
        except Exception as e:
            print(f"❌ Error general: {e}")
            self.mostrar_error(f"Error al actualizar producto: {str(e)}")
    
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