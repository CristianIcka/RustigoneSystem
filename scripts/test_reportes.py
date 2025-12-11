import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models.database_manager import DatabaseManager
from datetime import date, timedelta

# Conectar a la misma base de datos usada por la aplicación
db = DatabaseManager()
conn = db.connect()
cursor = conn.cursor()

fecha_fin = date.today().strftime("%Y-%m-%d")
fecha_inicio = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")

# Consulta resumen (mismo SQL que usa ReportesWindow)
query = '''
            SELECT 
                COUNT(*) as total_ventas,
                SUM(total) as monto_total,
                AVG(total) as promedio_venta,
                SUM(CASE WHEN medio_pago = 'EFECTIVO' THEN total ELSE 0 END) as efectivo,
                SUM(CASE WHEN medio_pago = 'DÉBITO' THEN total ELSE 0 END) as debito,
                SUM(CASE WHEN medio_pago = 'CRÉDITO' THEN total ELSE 0 END) as credito
            FROM ventas 
            WHERE DATE(fecha_venta) BETWEEN ? AND ?
        '''
cursor.execute(query, (fecha_inicio, fecha_fin))
resumen = cursor.fetchone()
if not resumen:
    resumen = (0, 0, 0, 0, 0, 0)
else:
    resumen = tuple(0 if v is None else v for v in resumen)

print("Resumen (coalesced):", resumen)

# Probar formateo (esto replicará lo que hace la UI)
try:
    texto_resumen = f"""
📊 REPORTE DE VENTAS
Período: {fecha_inicio} a {fecha_fin}
Categoría: TODAS
{'='*50}

📈 RESUMEN GENERAL:
• Total Ventas: {resumen[0]:,}
• Monto Total: ${resumen[1]:,.0f}
• Promedio por Venta: ${resumen[2]:,.0f}

💳 FORMAS DE PAGO:
• Efectivo: ${resumen[3]:,.0f}
• Débito: ${resumen[4]:,.0f}
• Crédito: ${resumen[5]:,.0f}

"""
    print(texto_resumen)
except Exception as e:
    print("Error al formatear resumen:", e)

conn.close()
