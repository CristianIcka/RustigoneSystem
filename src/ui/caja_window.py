# ui/caja_window.py
import customtkinter as ctk
from datetime import datetime, date
import sqlite3
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CajaWindow:
    def __init__(self, parent, db, usuario):
        self.parent = parent
        self.db = db
        self.usuario = usuario
        self.caja_abierta = None
        self.movimientos = []
        
        # Crear ventana de caja
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Gestión de Caja - RUSTIGONE")
        # Ajustar tamaño centrado usando helper centralizado
        try:
            from ui.responsive import set_window_size_and_center
            set_window_size_and_center(self.window, width_percent=0.7, min_width=750, min_height=650, parent=parent)
        except Exception as e:
            print(f"⚠️ No se pudo usar helper responsive en CajaWindow: {e}")
            self.window.geometry("1200x800")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Verificar estado de caja
        self.verificar_estado_caja()
        
        # Crear widgets
        self.create_widgets()
        self.actualizar_resumen()
        
    def verificar_estado_caja(self):
        """Verificar si hay caja abierta"""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM caja 
            WHERE fecha_cierre IS NULL 
            ORDER BY fecha_apertura DESC 
            LIMIT 1
        ''')
        
        caja = cursor.fetchone()
        if caja:
            self.caja_abierta = dict(caja)
        
        conn.close()
    
    def create_widgets(self):
        """Crear interfaz de gestión de caja"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 10))
        
        title = ctk.CTkLabel(
            title_frame,
            text="💰 GESTIÓN DE CAJA",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#38A169"
        )
        title.pack(pady=10)
        
        # Estado de caja
        self.estado_frame = ctk.CTkFrame(main_frame, fg_color="#F7FAFC", corner_radius=10)
        self.estado_frame.pack(fill="x", pady=(0, 10))
        
        self.actualizar_estado_caja()
        
        # Botones principales
        botones_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        botones_frame.pack(fill="x", pady=(0, 10))
        
        if not self.caja_abierta:
            self.apertura_btn = ctk.CTkButton(
                botones_frame,
                text="📂 ABRIR CAJA",
                command=self.abrir_caja,
                width=150,
                height=45,
                fg_color="#38A169",
                font=ctk.CTkFont(weight="bold", size=14)
            )
            self.apertura_btn.pack(side="left", padx=5)
        else:
            self.cierre_btn = ctk.CTkButton(
                botones_frame,
                text="🔒 CERRAR CAJA",
                command=self.cerrar_caja,
                width=150,
                height=45,
                fg_color="#E53E3E",
                font=ctk.CTkFont(weight="bold", size=14)
            )
            self.cierre_btn.pack(side="left", padx=5)
            
            self.movimiento_btn = ctk.CTkButton(
                botones_frame,
                text="💸 MOVIMIENTO",
                command=self.registrar_movimiento,
                width=150,
                height=45,
                fg_color="#3182CE",
                font=ctk.CTkFont(weight="bold", size=14)
            )
            self.movimiento_btn.pack(side="left", padx=5)
        
        self.reporte_btn = ctk.CTkButton(
            botones_frame,
            text="📊 REPORTES",
            command=self.mostrar_reportes,
            width=150,
            height=45,
            fg_color="#D69E2E",
            font=ctk.CTkFont(weight="bold", size=14)
        )
        self.reporte_btn.pack(side="left", padx=5)
        
        # Frame de contenido
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # Resumen de ventas
        resumen_frame = ctk.CTkFrame(content_frame, fg_color="#F7FAFC")
        resumen_frame.pack(fill="both", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(
            resumen_frame,
            text="📈 RESUMEN DEL DÍA",
            font=ctk.CTkFont(weight="bold", size=16),
            text_color="#2D3748"
        ).pack(pady=10)
        
        self.resumen_text = ctk.CTkTextbox(
            resumen_frame,
            fg_color="white",
            text_color="#4A5568",
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        self.resumen_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Movimientos recientes
        movimientos_frame = ctk.CTkFrame(content_frame, fg_color="#F7FAFC", width=400)
        movimientos_frame.pack(side="right", fill="y", padx=(5, 0))
        movimientos_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            movimientos_frame,
            text="📋 MOVIMIENTOS RECIENTES",
            font=ctk.CTkFont(weight="bold", size=16),
            text_color="#2D3748"
        ).pack(pady=10)
        
        self.movimientos_lista = ctk.CTkTextbox(
            movimientos_frame,
            fg_color="white",
            text_color="#4A5568",
            font=ctk.CTkFont(size=11),
            wrap="word"
        )
        self.movimientos_lista.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.actualizar_movimientos()
    
    def actualizar_estado_caja(self):
        """Actualizar display del estado de caja"""
        for widget in self.estado_frame.winfo_children():
            widget.destroy()
        
        if self.caja_abierta:
            estado_text = f"🟢 CAJA ABIERTA - Inicio: {self.caja_abierta['fecha_apertura']}"
            estado_color = "#38A169"
        else:
            estado_text = "🔴 CAJA CERRADA"
            estado_color = "#E53E3E"
        
        ctk.CTkLabel(
            self.estado_frame,
            text=estado_text,
            font=ctk.CTkFont(weight="bold", size=16),
            text_color=estado_color
        ).pack(pady=10)
    
    def abrir_caja(self):
        """Abrir ventana para apertura de caja"""
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Apertura de Caja")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(dialog, width_percent=0.35, min_width=400, min_height=300, parent=self.window)
        dialog.transient(self.window)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="📂 APERTURA DE CAJA",
            font=ctk.CTkFont(weight="bold", size=18)
        ).pack(pady=20)
        
        ctk.CTkLabel(dialog, text="Monto Inicial en Efectivo:").pack(pady=5)
        monto_entry = ctk.CTkEntry(dialog, width=200)
        monto_entry.pack(pady=5)
        monto_entry.insert(0, "0")
        
        ctk.CTkLabel(dialog, text="Observaciones:").pack(pady=5)
        obs_entry = ctk.CTkTextbox(dialog, width=200, height=80)
        obs_entry.pack(pady=5)
        
        def confirmar():
            try:
                monto_inicial = float(monto_entry.get())
                observaciones = obs_entry.get("1.0", "end-1c").strip()
                
                conn = self.db.connect()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO caja (usuario_id, monto_inicial, observaciones_apertura)
                    VALUES (?, ?, ?)
                ''', (self.usuario['id'], monto_inicial, observaciones))
                
                conn.commit()
                conn.close()
                
                self.verificar_estado_caja()
                self.actualizar_estado_caja()
                self.create_widgets()
                
                dialog.destroy()
                messagebox.showinfo("Éxito", "Caja abierta correctamente")
                
            except ValueError:
                messagebox.showerror("Error", "Monto inicial debe ser un número válido")
            except Exception as e:
                messagebox.showerror("Error", f"Error al abrir caja: {str(e)}")
        
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Confirmar",
            command=confirmar,
            fg_color="#38A169"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="#718096"
        ).pack(side="left", padx=10)
    
    def cerrar_caja(self):
        """Cerrar caja y realizar arqueo"""
        if not self.caja_abierta:
            return
        
        # Calcular totales
        conn = self.db.connect()
        cursor = conn.cursor()
        
        # Obtener ventas del día
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN medio_pago = 'EFECTIVO' THEN total ELSE 0 END) as total_efectivo,
                SUM(CASE WHEN medio_pago = 'DÉBITO' THEN total ELSE 0 END) as total_debito,
                SUM(CASE WHEN medio_pago = 'CRÉDITO' THEN total ELSE 0 END) as total_credito,
                COUNT(*) as total_ventas
            FROM ventas 
            WHERE DATE(fecha_venta) = DATE('now')
        ''')
        
        ventas = cursor.fetchone()
        total_efectivo = ventas[0] or 0
        total_debito = ventas[1] or 0
        total_credito = ventas[2] or 0
        total_ventas = ventas[3] or 0
        
        # Obtener movimientos de caja
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN tipo = 'INGRESO' THEN monto ELSE 0 END) as ingresos,
                SUM(CASE WHEN tipo = 'EGRESO' THEN monto ELSE 0 END) as egresos
            FROM movimientos_caja 
            WHERE caja_id = ?
        ''', (self.caja_abierta['id'],))
        
        movimientos = cursor.fetchone()
        total_ingresos = movimientos[0] or 0
        total_egresos = movimientos[1] or 0
        
        # Calcular total esperado en efectivo
        total_esperado = (self.caja_abierta['monto_inicial'] + 
                         total_efectivo + total_ingresos - total_egresos)
        
        conn.close()
        
        # Mostrar diálogo de cierre
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Cierre de Caja - Arqueo")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(dialog, width_percent=0.45, min_width=500, min_height=600, parent=self.window)
        dialog.transient(self.window)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="🔒 CIERRE DE CAJA - ARQUEO",
            font=ctk.CTkFont(weight="bold", size=18)
        ).pack(pady=20)
        
        # Resumen
        resumen_frame = ctk.CTkFrame(dialog, fg_color="#F7FAFC")
        resumen_frame.pack(fill="x", padx=20, pady=10)
        
        datos = [
            ("Monto Inicial:", f"${self.caja_abierta['monto_inicial']:,.0f}"),
            ("Ventas Efectivo:", f"${total_efectivo:,.0f}"),
            ("Ventas Débito:", f"${total_debito:,.0f}"),
            ("Ventas Crédito:", f"${total_credito:,.0f}"),
            ("Ingresos Extra:", f"${total_ingresos:,.0f}"),
            ("Egresos:", f"${total_egresos:,.0f}"),
            ("", ""),
            ("TOTAL ESPERADO:", f"${total_esperado:,.0f}")
        ]
        
        for i, (label, valor) in enumerate(datos):
            ctk.CTkLabel(
                resumen_frame,
                text=label,
                font=ctk.CTkFont(weight="bold")
            ).grid(row=i, column=0, sticky="w", padx=10, pady=2)
            
            ctk.CTkLabel(
                resumen_frame,
                text=valor,
                text_color="#2B6CB0",
                font=ctk.CTkFont(weight="bold")
            ).grid(row=i, column=1, sticky="e", padx=10, pady=2)
        
        ctk.CTkLabel(dialog, text="Efectivo Contado:").pack(pady=5)
        efectivo_entry = ctk.CTkEntry(dialog, width=200)
        efectivo_entry.pack(pady=5)
        efectivo_entry.insert(0, str(total_esperado))
        
        ctk.CTkLabel(dialog, text="Observaciones:").pack(pady=5)
        obs_entry = ctk.CTkTextbox(dialog, width=200, height=100)
        obs_entry.pack(pady=5)
        
        def confirmar_cierre():
            try:
                efectivo_contado = float(efectivo_entry.get())
                observaciones = obs_entry.get("1.0", "end-1c").strip()
                diferencia = efectivo_contado - total_esperado
                
                conn = self.db.connect()
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE caja SET 
                        fecha_cierre = CURRENT_TIMESTAMP,
                        monto_final_efectivo = ?,
                        total_ventas_efectivo = ?,
                        total_ventas_debito = ?,
                        total_ventas_credito = ?,
                        total_ingresos_extra = ?,
                        total_egresos = ?,
                        diferencia = ?,
                        observaciones_cierre = ?
                    WHERE id = ?
                ''', (efectivo_contado, total_efectivo, total_debito, total_credito,
                     total_ingresos, total_egresos, diferencia, observaciones, 
                     self.caja_abierta['id']))
                
                conn.commit()
                conn.close()
                
                self.caja_abierta = None
                self.actualizar_estado_caja()
                self.create_widgets()
                
                dialog.destroy()
                messagebox.showinfo("Éxito", "Caja cerrada correctamente")
                
            except ValueError:
                messagebox.showerror("Error", "Monto debe ser un número válido")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cerrar caja: {str(e)}")
        
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Confirmar Cierre",
            command=confirmar_cierre,
            fg_color="#E53E3E"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="#718096"
        ).pack(side="left", padx=10)
    
    def registrar_movimiento(self):
        """Registrar movimiento de caja (ingreso/egreso)"""
        if not self.caja_abierta:
            return
        
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Registrar Movimiento")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(dialog, width_percent=0.35, min_width=400, min_height=400, parent=self.window)
        dialog.transient(self.window)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="💸 REGISTRAR MOVIMIENTO",
            font=ctk.CTkFont(weight="bold", size=18)
        ).pack(pady=20)
        
        ctk.CTkLabel(dialog, text="Tipo:").pack(pady=5)
        tipo_var = ctk.StringVar(value="INGRESO")
        tipo_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        tipo_frame.pack(pady=5)
        
        ctk.CTkRadioButton(
            tipo_frame,
            text="Ingreso",
            variable=tipo_var,
            value="INGRESO"
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            tipo_frame,
            text="Egreso",
            variable=tipo_var,
            value="EGRESO"
        ).pack(side="left", padx=10)
        
        ctk.CTkLabel(dialog, text="Monto:").pack(pady=5)
        monto_entry = ctk.CTkEntry(dialog, width=200)
        monto_entry.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Concepto:").pack(pady=5)
        concepto_entry = ctk.CTkEntry(dialog, width=200)
        concepto_entry.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Descripción:").pack(pady=5)
        descripcion_entry = ctk.CTkTextbox(dialog, width=200, height=80)
        descripcion_entry.pack(pady=5)
        
        def confirmar_movimiento():
            try:
                monto = float(monto_entry.get())
                concepto = concepto_entry.get().strip()
                descripcion = descripcion_entry.get("1.0", "end-1c").strip()
                
                if not concepto:
                    messagebox.showerror("Error", "El concepto es obligatorio")
                    return
                
                conn = self.db.connect()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO movimientos_caja 
                    (caja_id, tipo, monto, concepto, descripcion)
                    VALUES (?, ?, ?, ?, ?)
                ''', (self.caja_abierta['id'], tipo_var.get(), monto, concepto, descripcion))
                
                conn.commit()
                conn.close()
                
                self.actualizar_movimientos()
                self.actualizar_resumen()
                
                dialog.destroy()
                messagebox.showinfo("Éxito", "Movimiento registrado correctamente")
                
            except ValueError:
                messagebox.showerror("Error", "Monto debe ser un número válido")
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar movimiento: {str(e)}")
        
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Registrar",
            command=confirmar_movimiento,
            fg_color="#3182CE"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="#718096"
        ).pack(side="left", padx=10)
    
    def actualizar_resumen(self):
        """Actualizar resumen del día"""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        # Obtener estadísticas del día
        cursor.execute('''
            SELECT 
                COUNT(*) as total_ventas,
                SUM(total) as total_ventas_monto,
                SUM(CASE WHEN medio_pago = 'EFECTIVO' THEN total ELSE 0 END) as efectivo,
                SUM(CASE WHEN medio_pago = 'DÉBITO' THEN total ELSE 0 END) as debito,
                SUM(CASE WHEN medio_pago = 'CRÉDITO' THEN total ELSE 0 END) as credito
            FROM ventas 
            WHERE DATE(fecha_venta) = DATE('now')
        ''')
        
        stats = cursor.fetchone()
        
        resumen_text = f"""📊 RESUMEN DEL DÍA - {date.today().strftime('%d/%m/%Y')}

🛒 VENTAS:
• Total Ventas: {stats[0] or 0}
• Monto Total: ${stats[1] or 0:,.0f}

💳 FORMAS DE PAGO:
• Efectivo: ${stats[2] or 0:,.0f}
• Débito: ${stats[3] or 0:,.0f}
• Crédito: ${stats[4] or 0:,.0f}

📈 PRODUCTOS MÁS VENDIDOS:
"""
        
        # Obtener productos más vendidos
        cursor.execute('''
            SELECT p.nombre, SUM(dv.cantidad) as total_vendido
            FROM detalle_ventas dv
            JOIN productos p ON dv.producto_id = p.id
            JOIN ventas v ON dv.venta_id = v.id
            WHERE DATE(v.fecha_venta) = DATE('now')
            GROUP BY p.id
            ORDER BY total_vendido DESC
            LIMIT 5
        ''')
        
        productos_top = cursor.fetchall()
        
        for i, producto in enumerate(productos_top, 1):
            resumen_text += f"{i}. {producto[0]}: {producto[1]} unidades\n"
        
        conn.close()
        
        self.resumen_text.delete("1.0", "end")
        self.resumen_text.insert("1.0", resumen_text)
    
    def actualizar_movimientos(self):
        """Actualizar lista de movimientos"""
        if not self.caja_abierta:
            self.movimientos_lista.delete("1.0", "end")
            self.movimientos_lista.insert("1.0", "Caja cerrada - No hay movimientos")
            return
        
        conn = self.db.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tipo, monto, concepto, descripcion, fecha_creacion
            FROM movimientos_caja 
            WHERE caja_id = ?
            ORDER BY fecha_creacion DESC
            LIMIT 10
        ''', (self.caja_abierta['id'],))
        
        movimientos = cursor.fetchall()
        conn.close()
        
        texto = "📋 ÚLTIMOS MOVIMIENTOS:\n\n"
        
        for mov in movimientos:
            tipo_emoji = "⬆️" if mov[0] == "INGRESO" else "⬇️"
            color = "🟢" if mov[0] == "INGRESO" else "🔴"
            texto += f"{tipo_emoji} {mov[2]}: ${mov[1]:,.0f}\n"
            texto += f"   {mov[3] or 'Sin descripción'}\n"
            texto += f"   {mov[4][:16]}\n\n"
        
        self.movimientos_lista.delete("1.0", "end")
        self.movimientos_lista.insert("1.0", texto)
    
    def mostrar_reportes(self):
        """Mostrar ventana de reportes"""
        reportes_window = ctk.CTkToplevel(self.window)
        reportes_window.title("Reportes de Caja")
        from ui.responsive import set_window_size_and_center
        set_window_size_and_center(reportes_window, width_percent=0.8, min_width=1000, min_height=700, parent=self.window)
        reportes_window.transient(self.window)
        reportes_window.grab_set()
        
        # Notebook para pestañas
        tabview = ctk.CTkTabview(reportes_window)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña de resumen diario
        tab_diario = tabview.add("Resumen Diario")
        self.crear_reporte_diario(tab_diario)
        
        # Pestaña de histórico
        tab_historico = tabview.add("Histórico")
        self.crear_reporte_historico(tab_historico)
        
        # Pestaña de cierres
        tab_cierres = tabview.add("Cierres de Caja")
        self.crear_reporte_cierres(tab_cierres)
    
    def crear_reporte_diario(self, parent):
        """Crear reporte diario"""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        # Obtener datos del día
        cursor.execute('''
            SELECT 
                strftime('%H', fecha_venta) as hora,
                COUNT(*) as ventas,
                SUM(total) as monto
            FROM ventas 
            WHERE DATE(fecha_venta) = DATE('now')
            GROUP BY hora
            ORDER BY hora
        ''')
        
        ventas_por_hora = cursor.fetchall()
        conn.close()
        
        # Crear gráfico
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        if ventas_por_hora:
            horas = [f"{int(h[0]):02d}:00" for h in ventas_por_hora]
            ventas = [h[1] for h in ventas_por_hora]
            montos = [h[2] for h in ventas_por_hora]
            
            ax1.bar(horas, ventas, color='skyblue', alpha=0.7)
            ax1.set_title('Ventas por Hora')
            ax1.set_xlabel('Hora')
            ax1.set_ylabel('N° de Ventas')
            ax1.tick_params(axis='x', rotation=45)
            
            ax2.bar(horas, montos, color='lightgreen', alpha=0.7)
            ax2.set_title('Monto por Hora')
            ax2.set_xlabel('Hora')
            ax2.set_ylabel('Monto ($)')
            ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Embedder gráfico en Tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def crear_reporte_historico(self, parent):
        """Crear reporte histórico"""
        text_widget = ctk.CTkTextbox(parent, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        conn = self.db.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                DATE(fecha_venta) as fecha,
                COUNT(*) as ventas,
                SUM(total) as monto,
                AVG(total) as promedio
            FROM ventas 
            GROUP BY DATE(fecha_venta)
            ORDER BY fecha DESC
            LIMIT 30
        ''')
        
        historico = cursor.fetchall()
        conn.close()
        
        texto = "📅 HISTÓRICO DE VENTAS (Últimos 30 días)\n\n"
        texto += "Fecha       | Ventas | Total     | Promedio\n"
        texto += "-" * 50 + "\n"
        
        for fila in historico:
            texto += f"{fila[0]} | {fila[1]:6d} | ${fila[2]:8,.0f} | ${fila[3]:7,.0f}\n"
        
        text_widget.delete("1.0", "end")
        text_widget.insert("1.0", texto)
    
    def crear_reporte_cierres(self, parent):
        """Crear reporte de cierres de caja"""
        text_widget = ctk.CTkTextbox(parent, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        conn = self.db.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                c.fecha_apertura,
                c.fecha_cierre,
                u.nombre as usuario,
                c.monto_inicial,
                c.monto_final_efectivo,
                c.total_ventas_efectivo,
                c.total_ventas_debito,
                c.total_ventas_credito,
                c.diferencia
            FROM caja c
            JOIN usuarios u ON c.usuario_id = u.id
            WHERE c.fecha_cierre IS NOT NULL
            ORDER BY c.fecha_cierre DESC
            LIMIT 20
        ''')
        
        cierres = cursor.fetchall()
        conn.close()
        
        texto = "🔒 HISTÓRICO DE CIERRES DE CAJA\n\n"
        
        for cierre in cierres:
            texto += f"Fecha: {cierre[0][:16]} - {cierre[1][:16]}\n"
            texto += f"Usuario: {cierre[2]}\n"
            texto += f"Inicial: ${cierre[3]:,.0f} | Final: ${cierre[4]:,.0f}\n"
            texto += f"Ventas - Efectivo: ${cierre[5]:,.0f} | Débito: ${cierre[6]:,.0f} | Crédito: ${cierre[7]:,.0f}\n"
            texto += f"Diferencia: ${cierre[8]:,.0f}\n"
            texto += "-" * 50 + "\n\n"
        
        text_widget.delete("1.0", "end")
        text_widget.insert("1.0", texto)