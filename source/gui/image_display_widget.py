#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os


def create_default_image_display(app, parent, image_path):
    """Crear un display compuesto con imagen y botón"""
    # Container principal del display
    display_container = ttk.Frame(parent, relief='ridge', borderwidth=1)
    display_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    
    # Frame para la imagen (parte superior del display)
    image_frame = ttk.Frame(display_container)
    image_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    try:
        # Cargar y redimensionar imagen
        pil_image = Image.open(image_path)
        
        # Redimensionar manteniendo proporción
        display_width = 350
        display_height = 400
        
        # (compatible con versiones antiguas de Pillow)
        try:
            pil_image.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)
        except AttributeError:
            # Para versiones anteriores de Pillow
            pil_image.thumbnail((display_width, display_height), Image.LANCZOS)
        
        # Convertir para tkinter
        photo = ImageTk.PhotoImage(pil_image)
        
        # Label para mostrar imagen
        image_label = ttk.Label(image_frame, image=photo)
        image_label.image = photo  # Mantener referencia
        image_label.pack(expand=True)
        
        # Label con nombre de archivo (pequeño, debajo de la imagen)
        name_label = ttk.Label(image_frame, text=os.path.basename(image_path), font=('Arial', 8), foreground='gray')
        name_label.pack(pady=(5, 0))
        
    except Exception as e:
        # Si hay error cargando la imagen, mostrar placeholder
        error_label = ttk.Label(
            image_frame, 
            text=f"Error cargando:\n{image_path}\n{str(e)[:50]}...",
            justify=tk.CENTER,
            foreground='red'
        )
        error_label.pack(expand=True)
    
    # Botón del display (parte inferior del display compuesto)
    display_button = ttk.Button(
        display_container,
        text="Capture",
        command=lambda: app.image_function(image_path)
    )
    display_button.pack(fill=tk.X, padx=5, pady=(0, 5))

