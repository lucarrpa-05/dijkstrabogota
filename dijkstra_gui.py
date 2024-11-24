import pandas as pd
import numpy as np
import heapq
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import os

class AplicacionDijkstra:
    def __init__(self, root):
        self.root = root
        self.root.title('Lucas Carrasquilla, Lucas Durán, Juan Esteban Ardila')
        self.root.geometry("1200x800")
        
        # Set the theme
        self.root.set_theme("arc")
        
        # Configure colors and styles
        self.colors = {
            'primary': '#5294e2',
            'secondary': '#ffffff',
            'text': '#2d323d',
            'success': '#2eb398',
            'warning': '#f08437'
        }
        
        # Configure styles
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'))
        style.configure('Subtitle.TLabel', font=('Segoe UI', 12))
        style.configure('Route.TLabel', font=('Segoe UI', 11))
        style.configure('Custom.TButton', font=('Segoe UI', 11))
        
        # Cargar datos
        try:
            self.cargar_datos()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar los datos: {str(e)}")
            root.destroy()
            return
        
        # Crear interfaz
        self.crear_interfaz()
        
    def cargar_datos(self):
        """Carga la matriz de adyacencia del archivo Excel"""
        # Cargar archivo
        ruta_archivo = 'data_transmi.xlsx'
        
        # Leer matriz de adyacencia
        self.matriz_pesos = pd.read_excel(ruta_archivo, index_col=0)
        self.matriz_pesos.index = self.matriz_pesos.index.str.strip()
        self.matriz_pesos.columns = self.matriz_pesos.columns.str.strip()
        
        # Lista de estaciones
        self.estaciones = sorted(list(self.matriz_pesos.index))
                    
    def crear_interfaz(self):
        """Crea la interfaz gráfica de usuario"""
        # Container principal
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, 
                 text="Simulador de Dijkstra", 
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        # Split view container
        content_frame = ttk.Frame(self.main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo (Entrada de datos)
        left_panel = ttk.LabelFrame(content_frame, text="Selección de Ruta", padding="20")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Estación de inicio
        inicio_frame = ttk.Frame(left_panel)
        inicio_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(inicio_frame, text="Estación de Inicio:", 
                 style='Subtitle.TLabel').pack(anchor=tk.W)
        
        self.combo_inicio = ttk.Combobox(inicio_frame, values=self.estaciones, 
                                       state="readonly", font=('Segoe UI', 11))
        self.combo_inicio.pack(fill=tk.X, pady=(5, 0))
        
        # Estación de destino
        destino_frame = ttk.Frame(left_panel)
        destino_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(destino_frame, text="Estación de Destino:", 
                 style='Subtitle.TLabel').pack(anchor=tk.W)
        
        self.combo_destino = ttk.Combobox(destino_frame, values=self.estaciones, 
                                        state="readonly", font=('Segoe UI', 11))
        self.combo_destino.pack(fill=tk.X, pady=(5, 0))
        
        # Botón calcular
        self.btn_calcular = ttk.Button(left_panel, text="Simular", 
                                     command=self.calcular_ruta, style='Custom.TButton')
        self.btn_calcular.pack(fill=tk.X, ipady=10)
        
        # Panel derecho (Resultados)
        right_panel = ttk.LabelFrame(content_frame, text="Resultados", padding="20")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame para los resultados
        results_container = ttk.Frame(right_panel)
        results_container.pack(fill=tk.BOTH, expand=True)
        
        # Texto para mostrar resultados
        self.texto_resultados = tk.Text(results_container, wrap=tk.WORD, 
                                      font=('Segoe UI', 11), bd=0,
                                      bg=self.colors['secondary'])
        self.texto_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_container, orient=tk.VERTICAL, 
                                command=self.texto_resultados.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.texto_resultados.configure(yscrollcommand=scrollbar.set)
        
        # Configurar tags para formato de texto
        self.texto_resultados.tag_configure('header', 
                                          font=('Segoe UI', 14, 'bold'),
                                          foreground=self.colors['primary'])
        self.texto_resultados.tag_configure('subheader', 
                                          font=('Segoe UI', 12),
                                          foreground=self.colors['text'])
        self.texto_resultados.tag_configure('route', 
                                          font=('Segoe UI', 11),
                                          foreground=self.colors['success'])
        
    def dijkstra(self, nodo_inicio, nodo_fin):
        """Implementación del algoritmo de Dijkstra"""
        nodos = list(self.matriz_pesos.index)
        distancias = {nodo: float('inf') for nodo in nodos}
        nodos_previos = {nodo: None for nodo in nodos}
        distancias[nodo_inicio] = 0
        cola_prioridad = [(0, nodo_inicio)]
        
        while cola_prioridad:
            distancia_actual, nodo_actual = heapq.heappop(cola_prioridad)
            if distancia_actual > distancias[nodo_actual]:
                continue
            for vecino, peso in self.matriz_pesos.loc[nodo_actual].items():
                if peso == float('inf'):
                    continue
                distancia = distancia_actual + peso
                if distancia < distancias[vecino]:
                    distancias[vecino] = distancia
                    nodos_previos[vecino] = nodo_actual
                    heapq.heappush(cola_prioridad, (distancia, vecino))
        
        # Reconstruir la ruta
        ruta = []
        actual = nodo_fin
        while actual:
            ruta.insert(0, actual)
            actual = nodos_previos[actual]
            
        return ruta, distancias[nodo_fin]
        
    def calcular_ruta(self):
        """Maneja el cálculo de la ruta y muestra los resultados"""
        # Obtener estaciones seleccionadas
        inicio = self.combo_inicio.get()
        destino = self.combo_destino.get()
        
        # Validar selección
        if not inicio or not destino:
            messagebox.showwarning("Advertencia", 
                                 "Por favor seleccione las estaciones de inicio y destino.")
            return
            
        if inicio == destino:
            messagebox.showinfo("Información", 
                              "La estación de inicio y destino son la misma.")
            return
        
        # Desactivar botón mientras se calcula
        self.btn_calcular.configure(state='disabled')
        self.root.update()
            
        try:
            # Calcular ruta
            ruta, distancia = self.dijkstra(inicio, destino)
            
            # Mostrar resultados
            self.texto_resultados.delete(1.0, tk.END)
            
            # Título
            self.texto_resultados.insert(tk.END, "Caminata Óptima Encontrada\n\n", 'header')
            
            # Detalles del viaje
            self.texto_resultados.insert(tk.END, "Detalles del Viaje:\n", 'subheader')
            self.texto_resultados.insert(tk.END, f"• Desde: {inicio}\n")
            self.texto_resultados.insert(tk.END, f"• Hasta: {destino}\n")
            self.texto_resultados.insert(tk.END, f"• Distancia: {distancia:.2f} km\n")
            self.texto_resultados.insert(tk.END, f"• Número de estaciones: {len(ruta)}\n\n")
            
            # Ruta detallada
            self.texto_resultados.insert(tk.END, "Caminata:\n", 'subheader')
            ruta_texto = " → ".join(ruta)
            self.texto_resultados.insert(tk.END, f"{ruta_texto}\n", 'route')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error de cálculo: {str(e)}")
        finally:
            # Reactivar botón
            self.btn_calcular.configure(state='normal')

# Iniciar aplicación
if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = AplicacionDijkstra(root)
    root.mainloop()
