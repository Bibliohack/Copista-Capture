#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import threading
import time

class LoadingDialog:
    """Ventana de carga simple con mensaje y barra de progreso"""
    
    def __init__(self, parent, title="Cargando...", message="Por favor espere..."):
        self.parent = parent
        
        # Crear ventana modal
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x120")
        self.dialog.resizable(False, False)
        
        # Centrar ventana
        self.center_window()
        
        # Hacer modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Evitar que se cierre con X
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Crear contenido
        self.create_widgets(message)
        
        # Variable para controlar si terminó la operación
        self.finished = False
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (120 // 2)
        self.dialog.geometry(f"300x120+{x}+{y}")
    
    def create_widgets(self, message):
        """Crear widgets de la ventana de carga"""
        # Frame principal
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Mensaje
        self.message_label = ttk.Label(main_frame, text=message, justify=tk.CENTER)
        self.message_label.pack(pady=(0, 15))
        
        # Barra de progreso indeterminada
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        self.progress.start(10)  # Velocidad de animación
    
    def update_message(self, new_message):
        """Actualizar mensaje de la ventana"""
        self.message_label.config(text=new_message)
        self.dialog.update()
    
    def close(self):
        """Cerrar ventana de carga"""
        self.finished = True
        self.progress.stop()
        self.dialog.grab_release()
        self.dialog.destroy()


class SpinnerDialog:
    """Ventana de carga con spinner personalizado"""
    
    def __init__(self, parent, title="Procesando...", message="Trabajando..."):
        self.parent = parent
        self.spinning = True
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("250x100")
        self.dialog.resizable(False, False)
        
        # Centrar y hacer modal
        self.center_window()
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Crear contenido
        self.create_widgets(message)
        
        # Iniciar animación
        self.animate_spinner()
    
    def center_window(self):
        """Centrar ventana"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (250 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (100 // 2)
        self.dialog.geometry(f"250x100+{x}+{y}")
    
    def create_widgets(self, message):
        """Crear widgets con spinner"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame para spinner y mensaje
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(expand=True)
        
        # Spinner (usando caracteres Unicode)
        self.spinner_label = ttk.Label(content_frame, text="⟳", font=('Arial', 20))
        self.spinner_label.pack()
        
        # Mensaje
        self.message_label = ttk.Label(content_frame, text=message)
        self.message_label.pack(pady=(10, 0))
        
        # Caracteres del spinner
        self.spinner_chars = ["⟳", "⟲", "⟳", "⟲"]
        self.spinner_index = 0
    
    def animate_spinner(self):
        """Animar el spinner"""
        if self.spinning:
            char = self.spinner_chars[self.spinner_index]
            self.spinner_label.config(text=char)
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)
            self.dialog.after(200, self.animate_spinner)
    
    def update_message(self, new_message):
        """Actualizar mensaje"""
        self.message_label.config(text=new_message)
        self.dialog.update()
    
    def close(self):
        """Cerrar ventana"""
        self.spinning = False
        self.dialog.grab_release()
        self.dialog.destroy()

def run_with_loading_dialog(parent, operation_func, title="Cargando...", message="Por favor espere..."):
    """
    Ejecuta una operación en segundo plano mientras muestra ventana de carga.
    
    Args:
        parent: Ventana padre
        operation_func: Función a ejecutar (debe ser callable)
        title: Título de la ventana de carga
        message: Mensaje a mostrar
    
    Returns:
        Resultado de operation_func o None si hay error
    """
    result = [None]  # Lista para almacenar resultado (mutable)
    error = [None]   # Lista para almacenar error
    
    def worker():
        """Función que ejecuta la operación en segundo plano"""
        try:
            result[0] = operation_func()
        except Exception as e:
            error[0] = e
        finally:
            # Programar el cierre de la ventana en el hilo principal
            parent.after(0, lambda: loading_dialog.close())
    
    # Crear ventana de carga
    loading_dialog = LoadingDialog(parent, title, message)
    
    # Iniciar operación en hilo separado
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    
    # Esperar hasta que termine la operación
    parent.wait_window(loading_dialog.dialog)
    
    # Verificar si hubo error
    if error[0]:
        raise error[0]
    
    return result[0]
    
def run_with_progress_steps(parent, steps_func, title="Procesando...", total_steps=None):
    """
    Ejecuta operación con pasos definidos y barra de progreso determinada.
    
    Args:
        parent: Ventana padre
        steps_func: Generador que yield mensajes de progreso
        title: Título de la ventana
        total_steps: Número total de pasos (opcional)
    """
    
    class ProgressDialog:
        def __init__(self, parent, title, total_steps):
            self.dialog = tk.Toplevel(parent)
            self.dialog.title(title)
            self.dialog.geometry("350x130")
            self.dialog.resizable(False, False)
            
            # Centrar
            self.dialog.update_idletasks()
            x = (self.dialog.winfo_screenwidth() // 2) - (350 // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (130 // 2)
            self.dialog.geometry(f"350x130+{x}+{y}")
            
            # Modal
            self.dialog.transient(parent)
            self.dialog.grab_set()
            self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
            
            # Widgets
            main_frame = ttk.Frame(self.dialog)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            self.message_label = ttk.Label(main_frame, text="Iniciando...")
            self.message_label.pack(pady=(0, 10))
            
            # Barra de progreso
            if total_steps:
                self.progress = ttk.Progressbar(main_frame, maximum=total_steps, value=0)
            else:
                self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
                self.progress.start(10)
            
            self.progress.pack(fill=tk.X, pady=(0, 10))
            
            # Label de progreso
            self.progress_label = ttk.Label(main_frame, text="")
            self.progress_label.pack()
            
            self.current_step = 0
            self.total_steps = total_steps
        
        def update_progress(self, message):
            self.message_label.config(text=message)
            if self.total_steps:
                self.current_step += 1
                self.progress['value'] = self.current_step
                self.progress_label.config(text=f"{self.current_step}/{self.total_steps}")
            self.dialog.update()
        
        def close(self):
            if not self.total_steps:
                self.progress.stop()
            self.dialog.grab_release()
            self.dialog.destroy()
    
    # Crear ventana de progreso
    progress_dialog = ProgressDialog(parent, title, total_steps)
    
    def worker():
        try:
            # Ejecutar pasos
            for step_message in steps_func():
                parent.after(0, lambda msg=step_message: progress_dialog.update_progress(msg))
                time.sleep(0.1)  # Pequeña pausa para ver el progreso
        except Exception as e:
            parent.after(0, lambda: progress_dialog.close())
            raise e
        finally:
            parent.after(0, lambda: progress_dialog.close())
    
    # Ejecutar en hilo separado
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    
    # Esperar
    parent.wait_window(progress_dialog.dialog)





# Ejemplos de uso para tu visor de imágenes:

"""

def example_long_operation():
    #Simula operación larga (copiar archivos, procesar imágenes, etc.)
    time.sleep(3)  # Simular trabajo
    return "Operación completada exitosamente"

def example_with_steps():
    #Generador que simula operación con pasos
    steps = [
        "Verificando archivos...",
        "Copiando imagen 1...", 
        "Copiando imagen 2...",
        "Copiando imagen 3...",
        "Actualizando bundles.json...",
        "Finalizando..."
    ]
    
    for step in steps:
        yield step
        time.sleep(0.5)  # Simular trabajo de cada paso

# Funciones de integración para tu ImageViewer:

def add_bundle_with_loading(self, image_paths):
    #Versión con carga de tu función add_bundle_from_images
    
    def operation():
        return self.add_bundle_from_images_original(image_paths)
    
    try:
        result = run_with_loading_dialog(
            self.root, 
            operation,
            "Agregando Bundle",
            "Copiando imágenes y actualizando..."
        )
        return result
    except Exception as e:
        messagebox.showerror("Error", f"Error agregando bundle: {str(e)}")
        return False

def add_bundle_with_progress(self, image_paths):
    #Versión con progreso paso a paso
    
    def steps():
        yield "Validando imágenes..."
        # Aquí validarías las imágenes
        
        for i, path in enumerate(image_paths, 1):
            yield f"Copiando imagen {i} de {len(image_paths)}..."
            # Aquí copiarías cada imagen
        
        yield "Creando bundle..."
        # Aquí crearías el bundle
        
        yield "Actualizando bundles.json..."
        # Aquí actualizarías el JSON
        
        yield "Completado!"
    
    try:
        run_with_progress_steps(
            self.root,
            steps,
            "Agregando Bundle",
            total_steps=len(image_paths) + 3
        )
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")
        return False
        
"""
