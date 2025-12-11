# ui/reportes_window.py
import customtkinter as ctk
from datetime import datetime, timedelta
import sqlite3
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import date

class ReportesWindow:
    def __init__(self, parent, db, usuario):
        self.parent = parent
        self.db = db
        self.usuario = usuario
        
        # Crear ventana
        self.window = ctk.CTkToplevel(parent)
        self.window.title("📊 Reportes Gerenciales - RUSTIGONE")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(self.window, width_percent=0.8, min_width=850, min_height=700, parent=parent)
        self.window.transient(parent)
        self.window.grab_set()
        # Estado de maximización
        self._is_maximized = False
        # Botón maximizar/restaurar
        self.maximize_btn = ctk.CTkButton(self.window, text="🗖", width=40, height=30, command=self.toggle_maximize, fg_color="#2C3E50", text_color="white")
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
        
        # Hacer responsiva
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Crear interfaz de reportes gerenciales"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.window, fg_color="white")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="#2C3E50")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="📊 REPORTES GERENCIALES",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title.pack(pady=15)
        
        # Controles de filtros
        filters_frame = ctk.CTkFrame(main_frame, fg_color="#F7FAFC")
        filters_frame.grid(row=1, column=0, sticky="nsew")
        filters_frame.grid_columnconfigure(1, weight=1)
        
        # Fila 1: Fechas
        ctk.CTkLabel(filters_frame, text="Fecha Inicio:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.fecha_inicio = ctk.CTkEntry(filters_frame)
        self.fecha_inicio.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.fecha_inicio.insert(0, (date.today() - timedelta(days=30)).strftime("%Y-%m-%d"))
        
        ctk.CTkLabel(filters_frame, text="Fecha Fin:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.fecha_fin = ctk.CTkEntry(filters_frame)
        self.fecha_fin.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.fecha_fin.insert(0, date.today().strftime("%Y-%m-%d"))
        
        # Fila 2: Filtros adicionales
        ctk.CTkLabel(filters_frame, text="Categoría:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.categoria_var = ctk.StringVar(value="TODAS")
        categorias = ["TODAS", "Pan", "Pastelería", "Bebida", "Materia Prima"]
        self.categoria_combo = ctk.CTkComboBox(filters_frame, values=categorias, variable=self.categoria_var)
        self.categoria_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(filters_frame, text="Tipo Reporte:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.tipo_reporte_var = ctk.StringVar(value="VENTAS")
        tipos = ["VENTAS", "COMPRAS", "PRODUCTOS", "FINANCIERO", "PROVEEDORES"]
        self.tipo_combo = ctk.CTkComboBox(filters_frame, values=tipos, variable=self.tipo_reporte_var)
        self.tipo_combo.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # Botones de acción
        button_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        button_frame.grid(row=0, column=4, rowspan=2, padx=20, pady=5, sticky="e")
        
        # Botones de acción: permitir que se expandan
        btn_generar = ctk.CTkButton(
            button_frame,
            text="🔍 Generar Reporte",
            command=self.generar_reporte,
            fg_color="#3498DB",
        )
        btn_generar.pack(side="left", fill="x", expand=True, padx=5)

        btn_export = ctk.CTkButton(
            button_frame,
            text="💾 Exportar Excel",
            command=self.exportar_excel,
            fg_color="#27AE60",
        )
        btn_export.pack(side="left", fill="x", expand=True, padx=5)
        
        # Área de reportes con pestañas
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        main_frame.grid_rowconfigure(2, weight=1)
        
        # Crear pestañas
        self.tab_resumen = self.tabview.add("📈 Resumen")
        self.tab_detalle = self.tabview.add("📋 Detalle")
        self.tab_graficos = self.tabview.add("📊 Gráficos")
        self.tab_recomendaciones = self.tabview.add("💡 Recomendaciones")
        
        # Configurar áreas de contenido
        self.setup_tab_resumen()
        self.setup_tab_detalle()
        self.setup_tab_graficos()
        self.setup_tab_recomendaciones()
        
        # Generar reporte inicial
        self.generar_reporte()
    
    def setup_tab_resumen(self):
        """Configurar pestaña de resumen"""
        self.resumen_text = ctk.CTkTextbox(self.tab_resumen, wrap="word", font=ctk.CTkFont(size=12))
        self.resumen_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def setup_tab_detalle(self):
        """Configurar pestaña de detalle"""
        self.detalle_text = ctk.CTkTextbox(self.tab_detalle, wrap="word", font=ctk.CTkFont(size=11))
        self.detalle_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def setup_tab_graficos(self):
        """Configurar pestaña de gráficos"""
        self.graficos_frame = ctk.CTkFrame(self.tab_graficos)
        self.graficos_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def setup_tab_recomendaciones(self):
        """Configurar pestaña de recomendaciones"""
        self.recomendaciones_text = ctk.CTkTextbox(self.tab_recomendaciones, wrap="word", font=ctk.CTkFont(size=12))
        self.recomendaciones_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def generar_reporte(self):
        """Generar reporte completo"""
        try:
            fecha_inicio = self.fecha_inicio.get()
            fecha_fin = self.fecha_fin.get()
            categoria = self.categoria_var.get()
            tipo_reporte = self.tipo_reporte_var.get()
            
            conn = self.db.connect()
            
            if tipo_reporte == "VENTAS":
                self.generar_reporte_ventas(conn, fecha_inicio, fecha_fin, categoria)
            elif tipo_reporte == "COMPRAS":
                self.generar_reporte_compras(conn, fecha_inicio, fecha_fin, categoria)
            elif tipo_reporte == "PRODUCTOS":
                self.generar_reporte_productos(conn, fecha_inicio, fecha_fin, categoria)
            elif tipo_reporte == "FINANCIERO":
                self.generar_reporte_financiero(conn, fecha_inicio, fecha_fin)
            elif tipo_reporte == "PROVEEDORES":
                self.generar_reporte_proveedores(conn, fecha_inicio, fecha_fin)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def generar_reporte_ventas(self, conn, fecha_inicio, fecha_fin, categoria):
        """Generar reporte de ventas"""
        cursor = conn.cursor()
        
        # Resumen general de ventas
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
        # Asegurar que los valores agregados NULL se conviertan a 0 para evitar errores de formato
        if not resumen:
            resumen = (0, 0, 0, 0, 0, 0)
        else:
            resumen = tuple(0 if v is None else v for v in resumen)
        
        # Productos más vendidos
        query = '''
            SELECT p.nombre, SUM(dv.cantidad) as cantidad, SUM(dv.subtotal) as total
            FROM detalle_ventas dv
            JOIN productos p ON dv.producto_id = p.id
            JOIN ventas v ON dv.venta_id = v.id
            JOIN categorias c ON p.categoria_id = c.id
            WHERE DATE(v.fecha_venta) BETWEEN ? AND ?
            AND (? = 'TODAS' OR c.nombre = ?)
            GROUP BY p.id
            ORDER BY cantidad DESC
            LIMIT 10
        '''
        cursor.execute(query, (fecha_inicio, fecha_fin, categoria, categoria))
        top_productos = cursor.fetchall()
        
        # Ventas por día
        query = '''
            SELECT DATE(fecha_venta) as fecha, COUNT(*), SUM(total)
            FROM ventas 
            WHERE DATE(fecha_venta) BETWEEN ? AND ?
            GROUP BY DATE(fecha_venta)
            ORDER BY fecha
        '''
        cursor.execute(query, (fecha_inicio, fecha_fin))
        ventas_por_dia = cursor.fetchall()
        
        # Generar texto del reporte
        texto_resumen = f"""
📊 REPORTE DE VENTAS
Período: {fecha_inicio} a {fecha_fin}
Categoría: {categoria}
{'='*50}

📈 RESUMEN GENERAL:
• Total Ventas: {resumen[0]:,}
• Monto Total: ${resumen[1]:,.0f}
• Promedio por Venta: ${resumen[2]:,.0f}

💳 FORMAS DE PAGO:
• Efectivo: ${resumen[3]:,.0f}
• Débito: ${resumen[4]:,.0f}
• Crédito: ${resumen[5]:,.0f}

🏆 PRODUCTOS MÁS VENDIDOS:
"""
        for i, producto in enumerate(top_productos, 1):
            texto_resumen += f"{i}. {producto[0]}: {producto[1]:.1f} unidades (${producto[2]:,.0f})\n"
        
        self.resumen_text.delete("1.0", "end")
        self.resumen_text.insert("1.0", texto_resumen)
        
        # Detalle
        texto_detalle = "📋 DETALLE DE VENTAS POR DÍA:\n\n"
        texto_detalle += "Fecha       | Ventas | Total\n"
        texto_detalle += "-" * 40 + "\n"
        for venta in ventas_por_dia:
            texto_detalle += f"{venta[0]} | {venta[1]:6} | ${venta[2]:8,.0f}\n"
        
        self.detalle_text.delete("1.0", "end")
        self.detalle_text.insert("1.0", texto_detalle)
        
        # Generar gráficos
        self.generar_graficos_ventas(ventas_por_dia, top_productos)
        
        # Generar recomendaciones
        self.generar_recomendaciones_ventas(resumen, top_productos)
    
    def generar_graficos_ventas(self, ventas_por_dia, top_productos):
        """Generar gráficos para ventas"""
        for widget in self.graficos_frame.winfo_children():
            widget.destroy()
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # Gráfico 1: Ventas por día
        if ventas_por_dia:
            fechas = [v[0] for v in ventas_por_dia]
            montos = [v[2] for v in ventas_por_dia]
            ax1.plot(fechas, montos, marker='o', linewidth=2, markersize=4)
            ax1.set_title('Evolución de Ventas Diarias')
            ax1.set_ylabel('Monto ($)')
            ax1.tick_params(axis='x', rotation=45)
        
        # Gráfico 2: Productos más vendidos
        if top_productos:
            productos = [p[0][:15] + '...' if len(p[0]) > 15 else p[0] for p in top_productos]
            cantidades = [p[1] for p in top_productos]
            ax2.barh(productos, cantidades, color='skyblue')
            ax2.set_title('Top 10 Productos Más Vendidos')
            ax2.set_xlabel('Cantidad Vendida')
        
        # Gráfico 3: Distribución por forma de pago
        # (Aquí necesitarías los datos de formas de pago)
        
        # Gráfico 4: Tendencia semanal
        # (Podrías agregar análisis de tendencias)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.graficos_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def generar_recomendaciones_ventas(self, resumen, top_productos):
        """Generar recomendaciones basadas en ventas"""
        texto = "💡 RECOMENDACIONES ESTRATÉGICAS\n\n"
        
        # Análisis de promedio de venta
        promedio_venta = resumen[2] or 0
        if promedio_venta < 5000:
            texto += "• ⚠️  El promedio de venta es bajo. Considere estrategias de up-selling\n"
        elif promedio_venta > 15000:
            texto += "• ✅ Excelente promedio de venta. Mantenga las estrategias actuales\n"
        
        # Análisis de productos top
        if top_productos:
            texto += f"\n📦 GESTIÓN DE INVENTARIO:\n"
            texto += f"• Producto estrella: {top_productos[0][0]} ({top_productos[0][1]:.0f} unidades)\n"
            
            # Recomendación de stock
            if top_productos[0][1] > 100:
                texto += "• 🔥 Alta rotación. Mantenga stock suficiente para demanda\n"
        
        # Recomendaciones generales
        texto += "\n🎯 ACCIONES SUGERIDAS:\n"
        texto += "• Analizar productos de baja rotación para posibles descuentos\n"
        texto += "• Promocionar productos complementarios a los más vendidos\n"
        texto += "• Evaluar horarios pico para optimizar personal\n"
        
        self.recomendaciones_text.delete("1.0", "end")
        self.recomendaciones_text.insert("1.0", texto)
    

    def generar_reporte_compras(self, conn, fecha_inicio, fecha_fin, categoria):
        """Generar reporte de compras"""
        self.resumen_text.delete("1.0", "end")
        self.resumen_text.insert("1.0", "⚠️ El reporte de COMPRAS aún no está implementado.")
        self.detalle_text.delete("1.0", "end")
        self.detalle_text.insert("1.0", "⚠️ El reporte de COMPRAS aún no está implementado.")
        for widget in self.graficos_frame.winfo_children():
            widget.destroy()
        self.recomendaciones_text.delete("1.0", "end")
        self.recomendaciones_text.insert("1.0", "⚠️ El reporte de COMPRAS aún no está implementado.")

    def generar_reporte_productos(self, conn, fecha_inicio, fecha_fin, categoria):
        """Generar reporte de productos"""
        self.resumen_text.delete("1.0", "end")
        self.resumen_text.insert("1.0", "⚠️ El reporte de PRODUCTOS aún no está implementado.")
        self.detalle_text.delete("1.0", "end")
        self.detalle_text.insert("1.0", "⚠️ El reporte de PRODUCTOS aún no está implementado.")
        for widget in self.graficos_frame.winfo_children():
            widget.destroy()
        self.recomendaciones_text.delete("1.0", "end")
        self.recomendaciones_text.insert("1.0", "⚠️ El reporte de PRODUCTOS aún no está implementado.")

    def generar_reporte_financiero(self, conn, fecha_inicio, fecha_fin):
        """Generar reporte financiero"""
        self.resumen_text.delete("1.0", "end")
        self.resumen_text.insert("1.0", "⚠️ El reporte FINANCIERO aún no está implementado.")
        self.detalle_text.delete("1.0", "end")
        self.detalle_text.insert("1.0", "⚠️ El reporte FINANCIERO aún no está implementado.")
        for widget in self.graficos_frame.winfo_children():
            widget.destroy()
        self.recomendaciones_text.delete("1.0", "end")
        self.recomendaciones_text.insert("1.0", "⚠️ El reporte FINANCIERO aún no está implementado.")

    def generar_reporte_proveedores(self, conn, fecha_inicio, fecha_fin):
        """Generar reporte de proveedores"""
        self.resumen_text.delete("1.0", "end")
        self.resumen_text.insert("1.0", "⚠️ El reporte de PROVEEDORES aún no está implementado.")
        self.detalle_text.delete("1.0", "end")
        self.detalle_text.insert("1.0", "⚠️ El reporte de PROVEEDORES aún no está implementado.")
        for widget in self.graficos_frame.winfo_children():
            widget.destroy()
        self.recomendaciones_text.delete("1.0", "end")
        self.recomendaciones_text.insert("1.0", "⚠️ El reporte de PROVEEDORES aún no está implementado.")
    
    def exportar_excel(self):
        """Exportar reporte a Excel"""
        messagebox.showinfo("Exportar", "Funcionalidad de exportación a Excel")