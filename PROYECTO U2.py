# -*- coding: utf-8 -*-
"""
Created on Sun Apr  6 14:57:51 2025

@author: DADG
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.style as mplstyle
# No necesitamos 'time' ahora

mplstyle.use('ggplot')

class AplicacionCalculadoraRaices:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Raíces - Métodos Numéricos")
        self.root.geometry("1000x800") # Tamaño inicial
        self.root.minsize(800, 600) # Tamaño mínimo permitido
        self.root.configure(bg="#f5f5f5")

        # --- Atributos ---
        self.raiz_calculada = False
        self.datos_iteraciones = []
        self.metodo_seleccionado = tk.StringVar(value="biseccion")
        self.iter_markers = []
        self.calculo_en_curso = False # Flag para saber si hay un cálculo activo
        self._after_id = None # Para guardar el ID de root.after y poder cancelar
        self.delay_ms = tk.IntVar(value=200) # Variable para el delay (ms)

        self.configurar_estilo()
        self.crear_interfaz()
        # Asegurar que la UI se ajuste al cambiar tamaño de ventana
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)


    def configurar_estilo(self):
        # ... (sin cambios) ...
        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure(".", background="#f5f5f5", foreground="#2c3e50")
        estilo.configure("TFrame", background="#f5f5f5")
        estilo.configure("Header.TLabel", font=("Helvetica", 14, "bold"), background="#f5f5f5")
        estilo.configure("TLabel", font=("Helvetica", 11), background="#f5f5f5")
        estilo.configure("Bold.TLabel", font=("Helvetica", 11, "bold"), background="#f5f5f5")
        estilo.configure("TEntry", font=("Helvetica", 11), padding=5)
        estilo.configure("Primary.TButton", font=("Helvetica", 11, "bold"), background="#3498db", foreground="white")
        estilo.map("Primary.TButton", background=[('active', '#2980b9')])
        estilo.configure("Success.TButton", font=("Helvetica", 11, "bold"), background="#2ecc71", foreground="white")
        estilo.map("Success.TButton", background=[('active', '#27ae60')])
        estilo.configure("Warning.TButton", font=("Helvetica", 11, "bold"), background="#e67e22", foreground="white")
        estilo.map("Warning.TButton", background=[('active', '#d35400')])
        estilo.configure("Danger.TButton", font=("Helvetica", 11, "bold"), background="#e74c3c", foreground="white") # Estilo para Detener
        estilo.map("Danger.TButton", background=[('active', '#c0392b')])
        estilo.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="#3498db", foreground="white")
        estilo.configure("Treeview", background="white", rowheight=28, fieldbackground="white")
        estilo.map("Treeview", background=[('selected', '#bdc3c7')])
        # Estilo para el Scale
        estilo.configure("Horizontal.TScale", background="#f5f5f5")


    def crear_interfaz(self):
        # Usar grid para el main_frame para que se expanda correctamente
        main_frame = ttk.Frame(self.root, padding="15 15 15 15") # Añadido padding
        main_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Configurar pesos de las filas/columnas de main_frame
        main_frame.rowconfigure(3, weight=1) # Fila de área central
        main_frame.rowconfigure(4, weight=1) # Fila de historial
        main_frame.columnconfigure(0, weight=1)


        titulo_frame = ttk.Frame(main_frame)
        # Usar grid también para mejor control
        titulo_frame.grid(row=0, column=0, sticky=tk.EW, pady=(0, 10))
        ttk.Label(titulo_frame, text="Calculadora de Raíces", style="Header.TLabel").pack(side=tk.LEFT)

        entrada_frame = ttk.LabelFrame(main_frame, text="Datos de Entrada", padding=10)
        entrada_frame.grid(row=1, column=0, sticky=tk.EW, pady=5)
        entrada_frame.columnconfigure(1, weight=1) # Permitir que entry de función expanda
        entrada_frame.columnconfigure(3, weight=1) # Permitir que ejemplos no se compriman tanto


        # ... (Widgets de Método, Función, Ejemplos, Parámetros, Tol/Iter sin cambios en su creación interna, solo su posicionamiento con grid) ...
        # Método de Selección
        metodo_frame = ttk.Frame(entrada_frame)
        metodo_frame.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=5)
        ttk.Label(metodo_frame, text="Método:", style="Bold.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        metodos = [("Bisección", "biseccion"), ("Falsa Posición", "falsa_posicion"),
                   ("Secante", "secante"), ("Newton-Raphson", "newton_raphson")]
        for texto, valor in metodos:
            rb = ttk.Radiobutton(metodo_frame, text=texto, variable=self.metodo_seleccionado, value=valor, command=self.update_ui_for_method)
            rb.pack(side=tk.LEFT, padx=3) # Menos padding horizontal

        # Función y Ayuda
        ttk.Label(entrada_frame, text="Función f(x):", style="Bold.TLabel").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.funcion_entry = ttk.Entry(entrada_frame, width=40)
        self.funcion_entry.grid(row=1, column=1, sticky=tk.EW, padx=5)
        self.funcion_entry.insert(0, "x**3 - x - 2")
        ttk.Button(entrada_frame, text="?", width=2, command=self.mostrar_ayuda_funciones).grid(row=1, column=2, padx=5)

        # Ejemplos
        ejemplos_frame = ttk.Frame(entrada_frame)
        ejemplos_frame.grid(row=1, column=3, sticky=tk.E, padx=5)
        ejemplos = [("x³-x-2", "x**3 - x - 2"), ("cos(x)-x", "np.cos(x) - x"), ("eˣ-3x", "np.exp(x) - 3*x")]
        for texto, comando in ejemplos:
            btn = ttk.Button(ejemplos_frame, text=texto, width=10, command=lambda c=comando: self.funcion_entry.delete(0, tk.END) or self.funcion_entry.insert(0, c))
            btn.pack(side=tk.LEFT, padx=2)

        # Contenedor para parámetros que cambian
        self.params_frame = ttk.Frame(entrada_frame)
        self.params_frame.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=5, padx=5)
        self.intervalo_label = ttk.Label(self.params_frame, text="Intervalo [a, b]:", style="Bold.TLabel")
        self.a_label = ttk.Label(self.params_frame, text=" a =")
        self.a_entry = ttk.Entry(self.params_frame, width=10)
        self.b_label = ttk.Label(self.params_frame, text=" b =")
        self.b_entry = ttk.Entry(self.params_frame, width=10)
        self.x0_label = ttk.Label(self.params_frame, text="Punto inicial x0:", style="Bold.TLabel")
        self.x0_entry = ttk.Entry(self.params_frame, width=12)
        self.x1_label = ttk.Label(self.params_frame, text=" Punto inicial x1:", style="Bold.TLabel")
        self.x1_entry = ttk.Entry(self.params_frame, width=12)
        # Valores iniciales
        self.a_entry.insert(0, "1"); self.b_entry.insert(0, "2")
        self.x0_entry.insert(0, "1"); self.x1_entry.insert(0, "1.5")

        # Tolerancia e Iteraciones
        tol_iter_frame = ttk.Frame(entrada_frame)
        tol_iter_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=5, padx=5)
        ttk.Label(tol_iter_frame, text="Tolerancia:", style="Bold.TLabel").grid(row=0, column=0, sticky=tk.W)
        self.tolerancia_entry = ttk.Entry(tol_iter_frame, width=12); self.tolerancia_entry.grid(row=0, column=1, sticky=tk.W, padx=5); self.tolerancia_entry.insert(0, "0.0001")
        ttk.Label(tol_iter_frame, text=" Iteraciones máx:", style="Bold.TLabel").grid(row=0, column=2, sticky=tk.W)
        self.max_iter_entry = ttk.Entry(tol_iter_frame, width=12); self.max_iter_entry.grid(row=0, column=3, sticky=tk.W, padx=5); self.max_iter_entry.insert(0, "50")


        # --- Botones de Acción y Control de Animación ---
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, sticky=tk.EW, pady=5)

        ttk.Button(control_frame, text="Verificar", style="Primary.TButton", command=self.verificar_condiciones).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Calcular", style="Success.TButton", command=self.calcular_raiz).pack(side=tk.LEFT, padx=5)
        # Botón Detener (inicialmente deshabilitado)
        self.stop_button = ttk.Button(control_frame, text="Detener", style="Danger.TButton", command=self.detener_calculo, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Limpiar", style="Warning.TButton", command=self.limpiar_campos).pack(side=tk.LEFT, padx=5)

        # Control de velocidad
        ttk.Label(control_frame, text="  Velocidad de animación del cálculo (ms):").pack(side=tk.LEFT, padx=(15, 5))
        self.velocidad_scale = ttk.Scale(control_frame, from_=0, to=1000, orient=tk.HORIZONTAL, length=150, variable=self.delay_ms, style="Horizontal.TScale")
        self.velocidad_scale.pack(side=tk.LEFT, padx=5)
        self.velocidad_label = ttk.Label(control_frame, textvariable=self.delay_ms, width=4)
        self.velocidad_label.pack(side=tk.LEFT)


        # --- Área Central: Gráfica y Resultados ---
        centro_frame = ttk.Frame(main_frame)
        centro_frame.grid(row=3, column=0, sticky=tk.NSEW, pady=5)
        centro_frame.columnconfigure(0, weight=3)
        centro_frame.columnconfigure(1, weight=1)
        centro_frame.rowconfigure(0, weight=1)

        grafica_frame = ttk.LabelFrame(centro_frame, text="Gráfica", padding=5) # Padding reducido
        grafica_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 5))
        grafica_frame.rowconfigure(0, weight=1)
        grafica_frame.columnconfigure(0, weight=1)

        self.fig = Figure(figsize=(5, 4), dpi=90) # Ajustar tamaño/dpi si es necesario
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=grafica_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        # Usar grid para el canvas widget también
        self.canvas_widget.grid(row=0, column=0, sticky=tk.NSEW)
        self.fig.tight_layout()

        resultados_frame = ttk.LabelFrame(centro_frame, text="Resultados", padding=10)
        resultados_frame.grid(row=0, column=1, sticky=tk.NSEW)
        # ... (métricas y labels sin cambios) ...
        metricas = [("Raíz aprox:", "raiz_label"),("f(raíz):", "fxraiz_label"),
                    ("Iteraciones:", "iteraciones_label"),("Error final:", "error_label"),
                    ("Estado:", "estado_label")]
        for i, (texto, var) in enumerate(metricas):
            ttk.Label(resultados_frame, text=texto, style="Bold.TLabel").grid(row=i, column=0, sticky=tk.W, pady=3, padx=5)
            label = ttk.Label(resultados_frame, text="", width=18, anchor="w")
            label.grid(row=i, column=1, sticky=tk.EW, pady=3, padx=5)
            setattr(self, var, label)
        resultados_frame.columnconfigure(1, weight=1)


        # --- Historial de Iteraciones ---
        historial_frame = ttk.LabelFrame(main_frame, text="Historial de Iteraciones", padding=5)
        historial_frame.grid(row=4, column=0, sticky=tk.NSEW, pady=(5, 0)) # NSEW
        historial_frame.rowconfigure(0, weight=1)
        historial_frame.columnconfigure(0, weight=1)

        columns = ("iter", "...") # Columnas iniciales genéricas
        self.historial_tree = ttk.Treeview(historial_frame, columns=columns, show="headings", height=5)

        vsb = ttk.Scrollbar(historial_frame, orient="vertical", command=self.historial_tree.yview)
        hsb = ttk.Scrollbar(historial_frame, orient="horizontal", command=self.historial_tree.xview)
        self.historial_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Usar grid para el treeview y scrollbars
        self.historial_tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)


        self.historial_tree.tag_configure('even', background='#f8f9fa')
        self.historial_tree.tag_configure('odd', background='#ffffff')

        # --- Barra de Estado ---
        self.barra_estado = ttk.Label(main_frame, text="Listo.", relief=tk.SUNKEN, anchor=tk.W, padding=(5, 3))
        self.barra_estado.grid(row=5, column=0, sticky=tk.EW, pady=(5, 0))

        # Configurar UI inicial
        self.update_ui_for_method()


    # ... (evaluar_funcion, evaluar_derivada, mostrar_ayuda_funciones, verificar_condiciones sin cambios) ...
    def evaluar_funcion(self, x):
        """Evalúa la función en el punto x"""
        try:
            expresion = self.funcion_entry.get()
            allowed_names = {'np': np, 'x': x, 'sin': np.sin, 'cos': np.cos, 'tan': np.tan,'exp': np.exp, 'log': np.log, 'log10': np.log10, 'sqrt': np.sqrt,'abs': np.abs, 'pi': np.pi, 'e': np.e}
            return eval(expresion, {"__builtins__": {}}, allowed_names)
        except Exception as e: messagebox.showerror("Error Evaluación", f"f({x}) inválido.\n{str(e)}"); return None
    def evaluar_derivada(self, x):
        """Evalúa la derivada numérica."""
        try:
            f = self.evaluar_funcion; h = 1e-7
            f_ph, f_mh = f(x + h), f(x - h)
            if f_ph is None or f_mh is None: return None
            if abs(h)<1e-15: return None
            return (f_ph - f_mh) / (2*h)
        except: return None
    def mostrar_ayuda_funciones(self):
        """Muestra ayuda sobre cómo ingresar funciones"""
        ayuda = ("Operaciones: +, -, *, /, ** (potencia)\nConstantes: pi, e\nFunciones: sin, cos, tan, exp, log (nat), log10, sqrt, abs\nUsar 'np.' es opcional.\n\nEj: x**3 - x - 2, np.cos(x) - x")
        messagebox.showinfo("Ayuda - Funciones", ayuda)
    def verificar_condiciones(self):
        # ... (sin cambios, ya era robusto) ...
        metodo = self.metodo_seleccionado.get()
        try:
            funcion_str = self.funcion_entry.get();
            if not funcion_str: messagebox.showwarning("Advertencia", "Ingrese f(x)."); return False
            test_val = 1.0
            try:
                if metodo in ["biseccion", "falsa_posicion"]: test_val = float(self.a_entry.get())
                elif metodo in ["secante", "newton_raphson"]: test_val = float(self.x0_entry.get())
            except ValueError: test_val=0.0
            if self.evaluar_funcion(test_val) is None: return False # Error ya mostrado
            if metodo in ["biseccion", "falsa_posicion"]:
                a = float(self.a_entry.get()); b = float(self.b_entry.get())
                if a >= b: messagebox.showwarning("Advertencia", "a < b requerido."); return False
                fa = self.evaluar_funcion(a); fb = self.evaluar_funcion(b)
                if fa is None or fb is None: return False
                if fa * fb >= 0: messagebox.showwarning("Condiciones", f"f(a) * f(b) >= 0.\nf({a:.4g})={fa:.4g}, f({b:.4g})={fb:.4g}"); return False
            elif metodo == "secante":
                x0 = float(self.x0_entry.get()); x1 = float(self.x1_entry.get())
                f0 = self.evaluar_funcion(x0); f1 = self.evaluar_funcion(x1)
                if f0 is None or f1 is None: return False
                if x0 == x1: messagebox.showwarning("Advertencia", "x0 != x1 requerido."); return False
                if abs(f1 - f0) < 1e-10: messagebox.showwarning("Advertencia", f"f(x1) ≈ f(x0).")
            elif metodo == "newton_raphson":
                x0 = float(self.x0_entry.get()); f0 = self.evaluar_funcion(x0)
                if f0 is None: return False
                df0 = self.evaluar_derivada(x0)
                if df0 is None: messagebox.showwarning("Advertencia", "No se pudo calcular f'(x0)."); return False
                if abs(df0) < 1e-10: messagebox.showwarning("Advertencia", f"f'({x0:.4g}) ≈ {df0:.2e} (cercana a 0)."); return False
            messagebox.showinfo("Condiciones Verificadas", "Condiciones iniciales OK."); return True
        except ValueError: messagebox.showerror("Error Entrada", "Valores numéricos inválidos."); return False
        except Exception as e: messagebox.showerror("Error", f"Verificación fallida: {str(e)}"); return False


    def graficar_funcion(self, a_vis, b_vis, raiz=None, iter_data=None, plot_function=True):
        # ... (Graficar función SIN CAMBIOS respecto a la versión anterior) ...
        #      (Ya limpiaba marcadores y dibujaba los de iter_data)
        try:
            if self.iter_markers:
                for marker in self.iter_markers:
                    try: marker.remove()
                    except: pass
            self.iter_markers = []
            if plot_function:
                self.ax.clear(); funcion_str = self.funcion_entry.get()
                x_vals = np.linspace(a_vis, b_vis, 400); y_vals = []; valid_points_x = []
                for x in x_vals:
                    y = self.evaluar_funcion(x)
                    if y is not None and np.isfinite(y): y_vals.append(y); valid_points_x.append(x)
                    else:
                        if valid_points_x: self.ax.plot(valid_points_x, y_vals, 'b-', linewidth=1.5, alpha=0.8)
                        y_vals = []; valid_points_x = []
                if valid_points_x: self.ax.plot(valid_points_x, y_vals, 'b-', linewidth=1.5, alpha=0.8, label=f'f(x)')
                self.ax.axhline(y=0, color='k', linestyle='-', linewidth=0.8, alpha=0.5)
                self.ax.set_xlabel('x'); self.ax.set_ylabel('f(x)'); self.ax.set_title('Gráfica de f(x)')
                self.ax.grid(True, linestyle='--', alpha=0.6)
            if iter_data:
                metodo = self.metodo_seleccionado.get()
                if metodo in ["biseccion", "falsa_posicion"] and all(k in iter_data for k in ['a','b','c','fa','fb','fc']):
                    a, b, c = iter_data['a'], iter_data['b'], iter_data['c']
                    fa, fb, fc = iter_data['fa'], iter_data['fb'], iter_data['fc']
                    l_a, = self.ax.plot([a, a], [0, fa], 'r:', lw=1); l_b, = self.ax.plot([b, b], [0, fb], 'g:', lw=1)
                    p_a, = self.ax.plot(a, fa, 'ro', ms=6, alpha=0.7); p_b, = self.ax.plot(b, fb, 'go', ms=6, alpha=0.7)
                    p_c, = self.ax.plot(c, fc, 'mo', ms=8, label=f'c≈{c:.4f}'); l_c, = self.ax.plot([c, c], [0, fc], 'm--', lw=1, alpha=0.7)
                    self.iter_markers.extend([l_a, l_b, p_a, p_b, p_c, l_c])
                    if metodo == "falsa_posicion": l_fp, = self.ax.plot([a, b], [fa, fb], 'k--', lw=1, alpha=0.5); self.iter_markers.append(l_fp)
                elif metodo == "secante" and all(k in iter_data for k in ['x0','x1','x2','f0','f1']):
                    x0, x1, x2 = iter_data['x0'], iter_data['x1'], iter_data['x2']
                    f0, f1 = iter_data['f0'], iter_data['f1']; f2 = self.evaluar_funcion(x2); f2 = 0 if f2 is None else f2
                    l_sec, = self.ax.plot([x0, x1], [f0, f1], 'k--', lw=1, alpha=0.6)
                    p0, = self.ax.plot(x0, f0, 'co', ms=6, alpha=0.7); p1, = self.ax.plot(x1, f1, 'yo', ms=6, alpha=0.7)
                    p2, = self.ax.plot(x2, f2, 'mo', ms=8, label=f'x₂≈{x2:.4f}'); l_x2, = self.ax.plot([x2, x2], [0, f2], 'm--', lw=1, alpha=0.7)
                    self.iter_markers.extend([l_sec, p0, p1, p2, l_x2])
                elif metodo == "newton_raphson" and all(k in iter_data for k in ['x0','x1','f0','df0']):
                    x0, x1 = iter_data['x0'], iter_data['x1']; f0, df0 = iter_data['f0'], iter_data['df0']; f1 = self.evaluar_funcion(x1); f1 = 0 if f1 is None else f1
                    tan_x = np.array([x0 - 0.5, x1 + 0.5]); tan_y = df0 * (tan_x - x0) + f0 # Mejor rango para tangente
                    l_tan, = self.ax.plot(tan_x, tan_y, 'k--', lw=1, alpha=0.6)
                    p0, = self.ax.plot(x0, f0, 'co', ms=6, alpha=0.7)
                    p1, = self.ax.plot(x1, f1, 'mo', ms=8, label=f'x₁≈{x1:.4f}'); l_x1, = self.ax.plot([x1, x1], [0, f1], 'm--', lw=1, alpha=0.7)
                    self.iter_markers.extend([l_tan, p0, p1, l_x1])
            if raiz is not None:
                fraiz = self.evaluar_funcion(raiz)
                if fraiz is not None and np.isfinite(fraiz):
                    self.ax.plot(raiz, fraiz, 'b*', ms=10, label=f'Raíz≈{raiz:.6f}')
                    self.ax.axvline(x=raiz, color='b', linestyle=':', lw=1.5, alpha=0.8)
            if plot_function or self.ax.has_data():
                handles, labels = self.ax.get_legend_handles_labels()
                unique_labels = {};
                for h, l in zip(handles, labels):
                    if l not in unique_labels: unique_labels[l] = h
                if unique_labels: self.ax.legend(unique_labels.values(), unique_labels.keys(), fontsize=8, loc='best')
            self.fig.tight_layout()
        except Exception as e: print(f"Error graficar: {str(e)}")


    def calcular_raiz(self):
        """Inicia el proceso de cálculo de raíz de forma iterativa."""
        if self.calculo_en_curso:
            messagebox.showwarning("Cálculo en Progreso", "Ya hay un cálculo en curso. Deténgalo primero.")
            return

        if not self.verificar_condiciones():
            self.barra_estado.config(text="Verificación fallida.")
            return

        try:
            metodo = self.metodo_seleccionado.get()
            tolerancia = float(self.tolerancia_entry.get())
            max_iter = int(self.max_iter_entry.get())
            if tolerancia <= 0 or max_iter <= 0: raise ValueError("Tol/Iter deben ser > 0")

            # Limpieza inicial
            for item in self.historial_tree.get_children(): self.historial_tree.delete(item)
            self.datos_iteraciones = []
            for label in [self.raiz_label, self.fxraiz_label, self.iteraciones_label, self.error_label, self.estado_label]: label.config(text="-")
            self.barra_estado.config(text=f"Iniciando {metodo}...")
            self.calculo_en_curso = True
            self.stop_button.config(state=tk.NORMAL) # Habilitar botón Detener
            self.root.update_idletasks()

            # Determinar rango visual
            a_vis, b_vis = self._get_visual_range()
            if a_vis is None: return # Error en _get_visual_range

            # Graficar función base
            self.graficar_funcion(a_vis, b_vis, plot_function=True)
            self.canvas.draw()
            self.root.update_idletasks()

            # Seleccionar y crear el generador apropiado
            generator = None
            if metodo == "biseccion":
                generator = self.metodo_biseccion_generator(tolerancia, max_iter, a_vis, b_vis)
            elif metodo == "falsa_posicion":
                generator = self.metodo_falsa_posicion_generator(tolerancia, max_iter, a_vis, b_vis)
            elif metodo == "secante":
                generator = self.metodo_secante_generator(tolerancia, max_iter, a_vis, b_vis)
            elif metodo == "newton_raphson":
                generator = self.metodo_newton_raphson_generator(tolerancia, max_iter, a_vis, b_vis)
            else:
                messagebox.showerror("Error", f"Método '{metodo}' no implementado para ejecución iterativa.")
                self.finalizar_calculo("Error método")
                return

            # Iniciar la ejecución paso a paso
            self._ejecutar_paso_iteracion(generator)

        except ValueError:
             messagebox.showerror("Error Entrada", "Tol/Iter deben ser números > 0.")
             self.finalizar_calculo("Error Params")
        except Exception as e:
            messagebox.showerror("Error Cálculo", f"Error inesperado al iniciar:\n{str(e)}")
            self.finalizar_calculo("Error Inicio")
            import traceback; traceback.print_exc()

    def _get_visual_range(self):
        """Determina un rango [a, b] adecuado para la visualización inicial."""
        metodo = self.metodo_seleccionado.get()
        try:
            if metodo in ["biseccion", "falsa_posicion"]:
                a = float(self.a_entry.get()); b = float(self.b_entry.get())
            elif metodo == "secante":
                x0 = float(self.x0_entry.get()); x1 = float(self.x1_entry.get())
                a = min(x0, x1); b = max(x0, x1)
            elif metodo == "newton_raphson":
                x0 = float(self.x0_entry.get()); a = x0 - 1; b = x0 + 1 # Rango inicial arbitrario
            else: a = 0; b = 1

            rango = abs(b - a)
            if rango < 1e-6: rango = 2.0 # Evitar rango cero
            a_vis = a - rango * 0.5 # Más margen
            b_vis = b + rango * 0.5
            return a_vis, b_vis
        except ValueError:
            messagebox.showerror("Error", "Valores iniciales inválidos para graficar.")
            return None, None

    def _ejecutar_paso_iteracion(self, generator):
        """Ejecuta un paso del generador y programa el siguiente."""
        if not self.calculo_en_curso: return # Detenido por el usuario

        try:
            # Ejecutar la lógica de una iteración (hasta el yield)
            next(generator)

            # Programar la siguiente ejecución después del delay
            delay = self.delay_ms.get()
            self._after_id = self.root.after(delay, self._ejecutar_paso_iteracion, generator)

        except StopIteration as e:
            # El generador terminó (encontró raíz, max iter, error)
            # El valor de retorno del generador (si lo hay) está en e.value
            resultado_final = e.value if e.value else {} # Capturar diccionario final
            self.finalizar_calculo(resultado_final.get("estado", "Completado"), resultado_final)
        except Exception as e:
            # Error inesperado durante la ejecución del generador
            messagebox.showerror("Error en Iteración", f"Error durante la iteración:\n{str(e)}")
            self.finalizar_calculo("Error Iteración")
            import traceback; traceback.print_exc()

    def detener_calculo(self):
        """Detiene el cálculo en curso cancelando la llamada 'after'."""
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        self.finalizar_calculo("Detenido por usuario")

    def finalizar_calculo(self, estado_final, resultados=None):
        """Tareas comunes al finalizar o detener un cálculo."""
        self.calculo_en_curso = False
        self.stop_button.config(state=tk.DISABLED) # Deshabilitar Detener
        self._after_id = None # Limpiar ID de after

        # Actualizar UI con el estado final
        self.barra_estado.config(text=f"Cálculo finalizado ({estado_final}).")
        if resultados: # Si el generador retornó resultados finales
             raiz = resultados.get('raiz')
             f_raiz = resultados.get('f_raiz')
             iter_count = resultados.get('iter_count')
             error = resultados.get('error')

             if raiz is not None: self.raiz_label.config(text=f"{raiz:.8f}")
             if f_raiz is not None: self.fxraiz_label.config(text=f"{f_raiz:.2e}")
             if iter_count is not None: self.iteraciones_label.config(text=f"{iter_count}")
             if error is not None: self.error_label.config(text=f"{error:.2e}" if error != float('inf') else "N/A")
             self.estado_label.config(text=estado_final)

             # Marcar la raíz final en la gráfica
             a_vis, b_vis = self._get_visual_range()
             if a_vis is not None and raiz is not None:
                  self.graficar_funcion(a_vis, b_vis, raiz=raiz, plot_function=False)
                  self.canvas.draw()
        else:
            # Si no hay resultados (detenido, error), solo actualizar estado
            self.estado_label.config(text=estado_final)

        # Auto-scroll al final del Treeview
        if self.historial_tree.get_children():
             last_item = self.historial_tree.get_children()[-1]
             self.historial_tree.see(last_item)

    # --- Métodos Generadores ---

    def metodo_biseccion_generator(self, tolerancia, max_iter, a_vis, b_vis):
        """Generador para Bisección."""
        a = float(self.a_entry.get()); b = float(self.b_entry.get())
        iteracion = 0; error = float('inf'); c_ant = a; c = a
        estado = "Calculando"; raiz_final, fc_final = None, None

        fa = self.evaluar_funcion(a); fb = self.evaluar_funcion(b)
        if fa is None or fb is None:
            self.barra_estado.config(text="Error eval inicial f(a)/f(b)")
            return {"estado": "Error Eval"} # Termina el generador

        while iteracion < max_iter:
            c = (a + b) / 2
            fc = self.evaluar_funcion(c)
            if fc is None: estado = "Error Eval f(c)"; break

            if iteracion > 0: error = abs(c - c_ant)
            else: error = float('inf')

            tag = 'even' if iteracion % 2 == 0 else 'odd'
            self.historial_tree.insert("", "end", values=(iteracion + 1, f"{a:.7f}", f"{b:.7f}", f"{c:.7f}", f"{fc:.3e}", f"{error:.3e}" if error != float('inf') else "---"), tags=(tag,))

            iter_data = {'a':a, 'b':b, 'c':c, 'fa':fa, 'fb':fb, 'fc':fc}
            self.graficar_funcion(a_vis, b_vis, iter_data=iter_data, plot_function=False)
            self.canvas.draw()
            self.barra_estado.config(text=f"Iter: {iteracion+1}, c={c:.5f}, Err:{error:.2e}")

            yield # Pausar aquí para permitir delay y actualización de UI

            if error < tolerancia or abs(fc) < 1e-12: estado = "Convergencia"; break

            if fa * fc < 0: b = c; fb = fc
            else: a = c; fa = fc
            c_ant = c; iteracion += 1
        else: # Si terminó por max_iter
            estado = "Max iteraciones"

        # Preparar resultados finales
        raiz_final, fc_final = c, self.evaluar_funcion(c) if 'fc' not in locals() else fc
        if abs(fc_final) < 1e-12 and estado != "Max iteraciones": estado = "Raíz casi exacta"
        return {"raiz": raiz_final, "f_raiz": fc_final, "iter_count": iteracion + 1, "error": error, "estado": estado}

    def metodo_falsa_posicion_generator(self, tolerancia, max_iter, a_vis, b_vis):
        """Generador para Falsa Posición."""
        a = float(self.a_entry.get()); b = float(self.b_entry.get())
        iteracion = 0; error = float('inf'); c_ant = a; c = a
        estado = "Calculando"; raiz_final, fc_final = None, None

        fa = self.evaluar_funcion(a); fb = self.evaluar_funcion(b)
        if fa is None or fb is None: return {"estado": "Error Eval"}

        while iteracion < max_iter:
            if abs(fb - fa) < 1e-15: estado = "Estancamiento"; fc_final=self.evaluar_funcion(c); break

            c = (a * fb - b * fa) / (fb - fa)
            fc = self.evaluar_funcion(c)
            if fc is None: estado = "Error Eval f(c)"; break

            if iteracion > 0: error = abs(c - c_ant)
            else: error = float('inf')

            tag = 'even' if iteracion % 2 == 0 else 'odd'
            self.historial_tree.insert("", "end", values=(iteracion + 1, f"{a:.7f}", f"{b:.7f}", f"{c:.7f}", f"{fc:.3e}", f"{error:.3e}" if error != float('inf') else "---"), tags=(tag,))

            iter_data = {'a':a, 'b':b, 'c':c, 'fa':fa, 'fb':fb, 'fc':fc}
            self.graficar_funcion(a_vis, b_vis, iter_data=iter_data, plot_function=False)
            self.canvas.draw()
            self.barra_estado.config(text=f"Iter: {iteracion+1}, c={c:.5f}, Err:{error:.2e}")

            yield

            if error < tolerancia or abs(fc) < 1e-12: estado = "Convergencia"; break

            test_fa = fa; test_fb = fb
            if fa * fc < 0: b = c; fb = fc; #if fa == test_fa: fa /= 2.0 # Simple anti-stagnation
            else: a = c; fa = fc; #if fb == test_fb: fb /= 2.0
            c_ant = c; iteracion += 1
        else: estado = "Max iteraciones"

        if 'fc_final' not in locals(): fc_final = self.evaluar_funcion(c)
        raiz_final = c
        if abs(fc_final) < 1e-12 and estado not in ["Max iteraciones", "Estancamiento"]: estado = "Raíz casi exacta"
        return {"raiz": raiz_final, "f_raiz": fc_final, "iter_count": iteracion + 1, "error": error, "estado": estado}


    def metodo_secante_generator(self, tolerancia, max_iter, a_vis, b_vis):
        """Generador para Secante."""
        x0 = float(self.x0_entry.get()); x1 = float(self.x1_entry.get())
        iteracion = 0; error = float('inf'); x2 = x1
        estado = "Calculando"; raiz_final, f_raiz_final = None, None

        f0 = self.evaluar_funcion(x0); f1 = self.evaluar_funcion(x1)
        if f0 is None or f1 is None: return {"estado": "Error Eval"}

        # Graficar estado inicial
        iter_data = {'x0':x0, 'x1':x1, 'x2':x1, 'f0':f0, 'f1':f1}
        self.graficar_funcion(a_vis, b_vis, iter_data=iter_data, plot_function=False)
        self.canvas.draw()
        self.barra_estado.config(text=f"Iter: 0, x1={x1:.5f}")
        yield # Pausa inicial

        while iteracion < max_iter:
            if abs(f1 - f0) < 1e-15: estado = "Estancamiento"; raiz_final=x1; f_raiz_final=f1; break

            x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
            f2 = self.evaluar_funcion(x2)
            if f2 is None: estado = "Error Eval f(x2)"; raiz_final=x1; f_raiz_final=f1; break

            error = abs(x2 - x1)

            tag = 'even' if iteracion % 2 == 0 else 'odd'
            self.historial_tree.insert("", "end", values=(iteracion + 1, f"{x0:.7f}", f"{x1:.7f}", f"{x2:.7f}", f"{f2:.3e}", f"{error:.3e}"), tags=(tag,))

            iter_data = {'x0':x0, 'x1':x1, 'x2':x2, 'f0':f0, 'f1':f1}
            self.graficar_funcion(a_vis, b_vis, iter_data=iter_data, plot_function=False)
            self.canvas.draw()
            self.barra_estado.config(text=f"Iter: {iteracion+1}, x2={x2:.5f}, Err:{error:.2e}")

            yield

            # Parar si f(xi) está cerca de 0 o error es pequeño
            if error < tolerancia or abs(f1) < 1e-12: estado = "Convergencia"; break

            x0, f0 = x1, f1
            x1, f1 = x2, f2
            iteracion += 1
        else: estado = "Max iteraciones"

        if raiz_final is None: raiz_final = x1 # Usar x1 (último xi válido)
        if f_raiz_final is None: f_raiz_final = self.evaluar_funcion(raiz_final)

        if abs(f_raiz_final) < 1e-12 and estado not in ["Max iteraciones", "Estancamiento"]: estado = "Raíz casi exacta"
        return {"raiz": raiz_final, "f_raiz": f_raiz_final, "iter_count": iteracion + 1, "error": error, "estado": estado}


    def metodo_newton_raphson_generator(self, tolerancia, max_iter, a_vis, b_vis):
        """Generador para Newton-Raphson."""
        x0 = float(self.x0_entry.get()); iteracion = 0; error = float('inf'); x1 = x0
        estado = "Calculando"; raiz_final, f_raiz_final = None, None

        while iteracion < max_iter:
            f0 = self.evaluar_funcion(x0)
            df0 = self.evaluar_derivada(x0)

            if f0 is None: estado = "Error Eval f(xi)"; break
            if df0 is None: estado = "Error Eval f'(xi)"; break
            if abs(df0) < 1e-15: estado = "Derivada cero"; break

            x1 = x0 - f0 / df0
            error = abs(x1 - x0)

            tag = 'even' if iteracion % 2 == 0 else 'odd'
            self.historial_tree.insert("", "end", values=(iteracion + 1, f"{x0:.7f}", f"{f0:.3e}", f"{df0:.3e}", f"{x1:.7f}", f"{error:.3e}"), tags=(tag,))

            iter_data = {'x0':x0, 'x1':x1, 'f0':f0, 'df0':df0}
            self.graficar_funcion(a_vis, b_vis, iter_data=iter_data, plot_function=False)
            self.canvas.draw()
            self.barra_estado.config(text=f"Iter: {iteracion+1}, x1={x1:.5f}, Err:{error:.2e}")

            yield

            # Parar si f(xi) está cerca de 0 o error es pequeño
            if error < tolerancia or abs(f0) < 1e-12: estado = "Convergencia"; break

            x0 = x1
            iteracion += 1
        else: estado = "Max iteraciones"

        raiz_final = x1 # x1 es la última aproximación calculada
        f_raiz_final = self.evaluar_funcion(raiz_final)

        if abs(f0) < 1e-12 and estado not in ["Max iteraciones", "Derivada cero"]: estado = "Raíz casi exacta"
        return {"raiz": raiz_final, "f_raiz": f_raiz_final, "iter_count": iteracion + 1, "error": error, "estado": estado}


    def limpiar_campos(self):
        # ... (sin cambios, ya limpiaba bien) ...
        if self.calculo_en_curso: self.detener_calculo() # Detener si está corriendo
        self.funcion_entry.delete(0, tk.END); self.funcion_entry.insert(0, "x**3 - x - 2")
        self.a_entry.delete(0, tk.END); self.a_entry.insert(0, "1")
        self.b_entry.delete(0, tk.END); self.b_entry.insert(0, "2")
        self.x0_entry.delete(0, tk.END); self.x0_entry.insert(0, "1")
        self.x1_entry.delete(0, tk.END); self.x1_entry.insert(0, "1.5")
        self.tolerancia_entry.delete(0, tk.END); self.tolerancia_entry.insert(0, "0.0001")
        self.max_iter_entry.delete(0, tk.END); self.max_iter_entry.insert(0, "50")
        self.delay_ms.set(200) # Resetear delay

        for label_name in ["raiz_label", "fxraiz_label", "iteraciones_label", "error_label", "estado_label"]:
            if hasattr(self, label_name): getattr(self, label_name).config(text="")
        self.estado_label.config(text="Esperando datos")

        for item in self.historial_tree.get_children(): self.historial_tree.delete(item)
        self.datos_iteraciones = []

        self.ax.clear(); self.iter_markers = []
        self.ax.set_title('Gráfica de f(x)'); self.ax.set_xlabel('x'); self.ax.set_ylabel('f(x)')
        self.ax.grid(True, linestyle='--', alpha=0.7); self.canvas.draw()

        self.raiz_calculada = False; self.barra_estado.config(text="Campos reiniciados.")
        self.metodo_seleccionado.set("biseccion"); self.update_ui_for_method()


    def update_ui_for_method(self, *args):
        # ... (sin cambios, ya funcionaba bien) ...
        metodo = self.metodo_seleccionado.get()
        for widget in self.params_frame.winfo_children(): widget.grid_remove()
        if metodo in ["biseccion", "falsa_posicion"]:
            self.intervalo_label.grid(row=0, column=0, sticky=tk.W, padx=(0,5)); self.a_label.grid(row=0, column=1, sticky=tk.W)
            self.a_entry.grid(row=0, column=2, sticky=tk.W, padx=5); self.b_label.grid(row=0, column=3, sticky=tk.W)
            self.b_entry.grid(row=0, column=4, sticky=tk.W); cols = ("iter", "a", "b", "c", "f(c)", "error")
        elif metodo == "secante":
            self.x0_label.grid(row=0, column=0, sticky=tk.W, padx=(0,5)); self.x0_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
            self.x1_label.grid(row=0, column=2, sticky=tk.W, padx=5); self.x1_entry.grid(row=0, column=3, sticky=tk.W)
            cols = ("iter", "xi-1", "xi", "xi+1", "f(xi+1)", "error")
        elif metodo == "newton_raphson":
            self.x0_label.grid(row=0, column=0, sticky=tk.W, padx=(0,5)); self.x0_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
            cols = ("iter", "xi", "f(xi)", "f'(xi)", "xi+1", "error")
        else: # Default
             self.intervalo_label.grid(row=0, column=0, sticky=tk.W, padx=(0,5)); self.a_label.grid(row=0, column=1, sticky=tk.W)
             self.a_entry.grid(row=0, column=2, sticky=tk.W, padx=5); self.b_label.grid(row=0, column=3, sticky=tk.W)
             self.b_entry.grid(row=0, column=4, sticky=tk.W); cols = ("iter", "a", "b", "c", "f(c)", "error")

        for item in self.historial_tree.get_children(): self.historial_tree.delete(item)
        self.historial_tree.configure(columns=cols, show="headings")
        for col in cols:
            header_text = col.replace("i-1","ᵢ₋₁").replace("i+1","ᵢ₊₁").replace("i","ᵢ").capitalize()
            self.historial_tree.heading(col, text=header_text); self.historial_tree.column(col, width=80, anchor="center", stretch=tk.NO)

        if args: # Limpiar solo si fue llamado por cambio de método (args no vacío)
             for label_name in ["raiz_label", "fxraiz_label", "iteraciones_label", "error_label", "estado_label"]:
                  if hasattr(self, label_name): getattr(self, label_name).config(text="")
             self.estado_label.config(text="Esperando datos"); self.barra_estado.config(text=f"Método: {metodo.replace('_',' ').capitalize()}.")
             self.raiz_calculada = False


    def mostrar_error(self, mensaje):
        messagebox.showerror("Error", mensaje)
        self.barra_estado.config(text=f"Error: {mensaje[:60]}...")

# --- Función Main ---
def main():
    root = tk.Tk()
    try:
        style = ttk.Style(root); themes = style.theme_names()
        if 'clam' in themes: style.theme_use('clam')
    except tk.TclError: pass
    app = AplicacionCalculadoraRaices(root)
    root.mainloop()

if __name__ == "__main__":
    main()