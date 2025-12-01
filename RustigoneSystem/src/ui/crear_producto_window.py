# ui/crear_producto_window.py
import customtkinter as ctk
import sqlite3

class CrearProductoWindow:
    def __init__(self, parent, db, inventario_window):
        self.parent = parent
        self.db = db
        self.inventario_window = inventario_window
        
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Crear Nuevo Producto - RUSTIGONE")
        self.window.geometry("600x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear formulario para nuevo producto"""
        main_frame = ctk.CTkFrame(self.window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            main_frame,
            text="➕ CREAR NUEVO PRODUCTO",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#38A169"
        ).pack(pady=20)
        
        # Formulario
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True)
        
        # Código de barras
        ctk.CTkLabel(form_frame, text="Código de Barras:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", pady=10)
        self.codigo_entry = ctk.CTkEntry(form_frame, width=300)
        self.codigo_entry.grid(row=0, column=1, sticky="w", pady=10, padx=(10, 0))
        
        # Nombre
        ctk.CTkLabel(form_frame, text="Nombre:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", pady=10)
        self.nombre_entry = ctk.CTkEntry(form_frame, width=300)
        self.nombre_entry.grid(row=1, column=1, sticky="w", pady=10, padx=(10, 0))
        
        # Descripción
        ctk.CTkLabel(form_frame, text="Descripción:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", pady=10)
        self.descripcion_entry = ctk.CTkEntry(form_frame, width=300)
        self.descripcion_entry.grid(row=2, column=1, sticky="w", pady=10, padx=(10, 0))
        
        # Precio Compra
        ctk.CTkLabel(form_frame, text="Precio Compra:", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, sticky="w", pady=10)
        self.precio_compra_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="0")
        self.precio_compra_entry.grid(row=3, column=1, sticky="w", pady=10, padx=(10, 0))
        
        # % Ganancia
        ctk.CTkLabel(form_frame, text="% Ganancia:", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, sticky="w", pady=10)
        self.ganancia_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="30")
        self.ganancia_entry.grid(row=4, column=1, sticky="w", pady=10, padx=(10, 0))
        
        # Precio Venta (calculado)
        ctk.CTkLabel(form_frame, text="Precio Venta:", font=ctk.CTkFont(weight="bold")).grid(row=5, column=0, sticky="w", pady=10)
        self.precio_venta_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Se calculará automáticamente")
        self.precio_venta_entry.grid(row=5, column=1, sticky="w", pady=10, padx=(10, 0))
        
        # Stock Inicial
        ctk.CTkLabel(form_frame, text="Stock Inicial:", font=ctk.CTkFont(weight="bold")).grid(row=6, column=0, sticky="w", pady=10)
        self.stock_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="0")
        self.stock_entry.grid(row=6, column=1, sticky="w", pady=10, padx=(10, 0))
        
        # Stock Mínimo
        ctk.CTkLabel(form_frame, text="Stock Mínimo:", font=ctk.CTkFont(weight="bold")).grid(row=7, column=0, sticky="w", pady=10)
        self.stock_min_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="1")
        self.stock_min_entry.grid(row=7, column=1, sticky="w", pady=10, padx=(10, 0))
        
        # Unidad de Medida
        ctk.CTkLabel(form_frame, text="Unidad Medida:", font=ctk.CTkFont(weight="bold")).grid(row=8, column=0, sticky="w", pady=10)
        self.unidad_combo = ctk.CTkComboBox(
            form_frame,
            values=["unidad", "kg", "g", "l", "ml"],
            width=300
        )
        self.unidad_combo.set("unidad")
        self.unidad_combo.grid(row=8, column=1, sticky="w", pady=10, padx=(10, 0))
        
        # Categoría
        ctk.CTkLabel(form_frame, text="Categoría:", font=ctk.CTkFont(weight="bold")).grid(row=9, column=0, sticky="w", pady=10)
        
        # Obtener categorías de la base de datos
        categorias = self.obtener_categorias()
        self.categoria_combo = ctk.CTkComboBox(
            form_frame,
            values=categorias,
            width=300
        )
        if categorias:
            self.categoria_combo.set(categorias[0])
        self.categoria_combo.grid(row=9, column=1, sticky="w", pady=10, padx=(10, 0))
        
        # Botón crear nueva categoría
        ctk.CTkButton(
            form_frame,
            text="➕ Nueva Categoría",
            command=self.crear_nueva_categoria,
            width=120,
            fg_color="#718096"
        ).grid(row=10, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Botones de acción
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="💾 GUARDAR PRODUCTO",
            command=self.guardar_producto,
            width=180,
            height=45,
            fg_color="#38A169",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="🔄 CALCULAR PRECIO",
            command=self.calcular_precio_venta,
            width=180,
            height=45,
            fg_color="#2B6CB0",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=1, padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="❌ CANCELAR",
            command=self.window.destroy,
            width=180,
            height=45,
            fg_color="#E53E3E",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=2, padx=10)
        
        # Bind eventos para cálculo automático
        self.precio_compra_entry.bind("<KeyRelease>", lambda e: self.calcular_precio_venta())
        self.ganancia_entry.bind("<KeyRelease>", lambda e: self.calcular_precio_venta())
    
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
        error_window.geometry("400x150")
        error_window.transient(self.window)
        error_window.grab_set()
        
        ctk.CTkLabel(error_window, text="❌ " + mensaje).pack(expand=True, pady=20)
        ctk.CTkButton(error_window, text="Aceptar", command=error_window.destroy).pack(pady=10)
    
    def mostrar_exito(self, mensaje):
        """Mostrar mensaje de éxito"""
        exito_window = ctk.CTkToplevel(self.window)
        exito_window.title("Éxito")
        exito_window.geometry("400x150")
        exito_window.transient(self.window)
        exito_window.grab_set()
        
        ctk.CTkLabel(exito_window, text="✅ " + mensaje).pack(expand=True, pady=20)
        ctk.CTkButton(exito_window, text="Aceptar", command=exito_window.destroy).pack(pady=10)