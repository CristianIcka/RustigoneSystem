# database/database_manager.py - VERSIÓN CORREGIDA
import sqlite3
import os
import bcrypt
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="rustigone.db"):
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        """Conectar a la base de datos"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def init_database(self):
        """Inicializar la base de datos con tablas necesarias - VERSIÓN CORREGIDA"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Tablas existentes (mantener las que ya tienes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nombre TEXT NOT NULL,
                rol TEXT NOT NULL CHECK(rol IN ('admin', 'cajero', 'inventario')),
                activo BOOLEAN DEFAULT 1,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                descripcion TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_barras TEXT UNIQUE,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio_compra REAL NOT NULL,
                porcentaje_ganancia REAL DEFAULT 30,
                precio_venta REAL NOT NULL,
                stock_actual REAL DEFAULT 0,
                stock_minimo REAL DEFAULT 1,
                categoria_id INTEGER,
                unidad_medida TEXT NOT NULL CHECK(unidad_medida IN ('unidad', 'kg', 'g', 'l', 'ml')),
                activo BOOLEAN DEFAULT 1,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_ultima_compra DATETIME,
                fecha_ultima_venta DATETIME,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                total REAL NOT NULL,
                iva REAL NOT NULL,
                medio_pago TEXT NOT NULL CHECK(medio_pago IN ('EFECTIVO', 'DÉBITO', 'CRÉDITO')),
                monto_recibido REAL DEFAULT 0,
                vuelto REAL DEFAULT 0,
                fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad REAL NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')
        
        # NUEVAS TABLAS PARA PROVEEDORES - VERSIÓN CORREGIDA
        self.crear_tablas_proveedores(cursor)
        
        # Insertar datos por defecto
        self._create_default_admin(cursor)
        self._create_default_categories(cursor)
        
        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada correctamente")
        
        # Actualizar esquema si es necesario
        self.update_database_schema()

    def crear_tablas_proveedores(self, cursor):
        """Crear tablas relacionadas con proveedores - VERSIÓN SEGURA"""
        try:
            # Tabla de proveedores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS proveedores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rut TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    giro TEXT,
                    direccion TEXT,
                    telefono TEXT,
                    email TEXT,
                    contacto TEXT,
                    activo BOOLEAN DEFAULT 1,
                    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de documentos (facturas, boletas, guías)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proveedor_id INTEGER NOT NULL,
                    tipo_documento TEXT NOT NULL CHECK(tipo_documento IN ('FACTURA', 'BOLETA', 'GUIA_DESPACHO')),
                    numero_documento TEXT NOT NULL,
                    fecha_emision DATE NOT NULL,
                    fecha_recepcion DATE,
                    monto_total REAL NOT NULL,
                    estado TEXT DEFAULT 'PENDIENTE' CHECK(estado IN ('PENDIENTE', 'PAGADO', 'ANULADO')),
                    observaciones TEXT,
                    archivo_pdf TEXT,
                    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
                    UNIQUE(proveedor_id, tipo_documento, numero_documento)
                )
            ''')
            
            # Verificar si la tabla compras existe y tiene las columnas correctas
            cursor.execute("PRAGMA table_info(compras)")
            compras_columns = [column[1] for column in cursor.fetchall()]
            
            if not compras_columns:
                # Crear tabla compras desde cero
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS compras (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        proveedor_id INTEGER NOT NULL,
                        tipo_documento TEXT NOT NULL CHECK(tipo_documento IN ('FACTURA', 'BOLETA', 'GUIA_DESPACHO')),
                        numero_documento TEXT NOT NULL,
                        fecha_compra DATE NOT NULL,
                        total REAL NOT NULL,
                        usuario_id INTEGER NOT NULL,
                        fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                    )
                ''')
            else:
                # La tabla existe, verificar y agregar columnas faltantes
                if 'proveedor_id' not in compras_columns:
                    cursor.execute('ALTER TABLE compras ADD COLUMN proveedor_id INTEGER DEFAULT 1')
                
                if 'tipo_documento' not in compras_columns:
                    cursor.execute('ALTER TABLE compras ADD COLUMN tipo_documento TEXT DEFAULT "FACTURA"')
                
                # Si existe numero_factura, migrar a numero_documento
                if 'numero_factura' in compras_columns and 'numero_documento' not in compras_columns:
                    cursor.execute('ALTER TABLE compras ADD COLUMN numero_documento TEXT')
                    cursor.execute('UPDATE compras SET numero_documento = numero_factura')
                    
            # Tabla de detalle de compras
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detalle_compras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    compra_id INTEGER NOT NULL,
                    producto_id INTEGER NOT NULL,
                    cantidad REAL NOT NULL,
                    precio_compra REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (compra_id) REFERENCES compras(id),
                    FOREIGN KEY (producto_id) REFERENCES productos(id)
                )
            ''')
            
            # Tabla de caja
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS caja (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    fecha_apertura DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_cierre DATETIME,
                    monto_inicial REAL NOT NULL DEFAULT 0,
                    monto_final_efectivo REAL,
                    total_ventas_efectivo REAL DEFAULT 0,
                    total_ventas_debito REAL DEFAULT 0,
                    total_ventas_credito REAL DEFAULT 0,
                    total_ingresos_extra REAL DEFAULT 0,
                    total_egresos REAL DEFAULT 0,
                    diferencia REAL DEFAULT 0,
                    observaciones_apertura TEXT,
                    observaciones_cierre TEXT,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            ''')
            
            # Tabla de movimientos de caja
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movimientos_caja (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    caja_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL CHECK(tipo IN ('INGRESO', 'EGRESO')),
                    monto REAL NOT NULL,
                    concepto TEXT NOT NULL,
                    descripcion TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (caja_id) REFERENCES caja(id)
                )
            ''')
            
            print("✅ Tablas de proveedores creadas/verificadas correctamente")
            
        except Exception as e:
            print(f"⚠️ Error al crear tablas de proveedores: {e}")

    def update_database_schema(self):
        """Actualizar el esquema de la base de datos si es necesario"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Verificar columnas en ventas
            cursor.execute("PRAGMA table_info(ventas)")
            ventas_columns = [column[1] for column in cursor.fetchall()]
            
            if 'monto_recibido' not in ventas_columns:
                cursor.execute('ALTER TABLE ventas ADD COLUMN monto_recibido REAL DEFAULT 0')
                print("✅ Columna 'monto_recibido' agregada a ventas")
            
            if 'vuelto' not in ventas_columns:
                cursor.execute('ALTER TABLE ventas ADD COLUMN vuelto REAL DEFAULT 0')
                print("✅ Columna 'vuelto' agregada a ventas")
            
            # Insertar proveedor por defecto si no existe
            cursor.execute("SELECT id FROM proveedores WHERE rut = '99999999-9'")
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO proveedores (rut, nombre, giro, activo)
                    VALUES ('99999999-9', 'Proveedor General', 'Varios', 1)
                ''')
                print("✅ Proveedor por defecto creado")
            
            # Actualizar compras existentes para que apunten al proveedor por defecto
            cursor.execute("SELECT COUNT(*) FROM compras WHERE proveedor_id IS NULL")
            compras_sin_proveedor = cursor.fetchone()[0]
            
            if compras_sin_proveedor > 0:
                cursor.execute("UPDATE compras SET proveedor_id = 1 WHERE proveedor_id IS NULL")
                print(f"✅ Actualizadas {compras_sin_proveedor} compras con proveedor por defecto")
            
            conn.commit()
            
        except Exception as e:
            print(f"⚠️ Error actualizando esquema: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def _create_default_admin(self, cursor):
        """Crear usuario administrador por defecto"""
        admin_email = "admin@rustigone.com"
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (admin_email,))
        if not cursor.fetchone():
            password_hash = self.hash_password("Admin123!")
            cursor.execute('''
                INSERT INTO usuarios (email, password_hash, nombre, rol)
                VALUES (?, ?, ?, ?)
            ''', (admin_email, password_hash, "Administrador", "admin"))
    
    def _create_default_categories(self, cursor):
        """Crear categorías básicas"""
        categorias = [
            ("Pan", "Productos de panadería"),
            ("Pastelería", "Tortas y pasteles"),
            ("Bebida", "Bebidas y líquidos"),
            ("Materia Prima", "Ingredientes a granel")
        ]
        
        for nombre, descripcion in categorias:
            cursor.execute('''
                INSERT OR IGNORE INTO categorias (nombre, descripcion)
                VALUES (?, ?)
            ''', (nombre, descripcion))
    
    def hash_password(self, password):
        """Hashear contraseña"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, password_hash):
        """Verificar contraseña"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def get_user_by_email(self, email):
        """Obtener usuario por email"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ? AND activo = 1", (email,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None