# add_test_products.py
from database.database_manager import DatabaseManager

def agregar_productos_prueba():
    db = DatabaseManager()
    conn = db.connect()
    cursor = conn.cursor()
    
    # Productos de panadería de prueba
    productos = [
        {
            'codigo_barras': '1234567890123',
            'nombre': 'Pan Francés',
            'descripcion': 'Pan francés tradicional',
            'precio_compra': 500,
            'porcentaje_ganancia': 50,
            'precio_venta': 750,
            'stock_actual': 50,
            'stock_minimo': 10,
            'categoria_id': 1,  # Pan
            'unidad_medida': 'unidad'
        },
        {
            'codigo_barras': '1234567890124',
            'nombre': 'Torta Chocolate',
            'descripcion': 'Torta de chocolate premium',
            'precio_compra': 8000,
            'porcentaje_ganancia': 40,
            'precio_venta': 11200,
            'stock_actual': 5,
            'stock_minimo': 2,
            'categoria_id': 2,  # Pastelería
            'unidad_medida': 'unidad'
        },
        {
            'codigo_barras': '1234567890125',
            'nombre': 'Harina Trigo',
            'descripcion': 'Harina de trigo especial',
            'precio_compra': 1500,
            'porcentaje_ganancia': 30,
            'precio_venta': 1950,
            'stock_actual': 100,
            'stock_minimo': 20,
            'categoria_id': 4,  # Materia Prima
            'unidad_medida': 'kg'
        },
        {
            'codigo_barras': '1234567890126',
            'nombre': 'Leche Entera',
            'descripcion': 'Leche entera pasteurizada',
            'precio_compra': 1200,
            'porcentaje_ganancia': 35,
            'precio_venta': 1620,
            'stock_actual': 30,
            'stock_minimo': 5,
            'categoria_id': 3,  # Bebida
            'unidad_medida': 'l'
        }
    ]
    
    for producto in productos:
        cursor.execute('''
            INSERT OR IGNORE INTO productos 
            (codigo_barras, nombre, descripcion, precio_compra, porcentaje_ganancia, 
             precio_venta, stock_actual, stock_minimo, categoria_id, unidad_medida)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            producto['codigo_barras'], producto['nombre'], producto['descripcion'],
            producto['precio_compra'], producto['porcentaje_ganancia'], producto['precio_venta'],
            producto['stock_actual'], producto['stock_minimo'], producto['categoria_id'],
            producto['unidad_medida']
        ))
    
    conn.commit()
    conn.close()
    print("✅ Productos de prueba agregados correctamente")

if __name__ == "__main__":
    agregar_productos_prueba()