#!/usr/bin/env python3

from tkinter import messagebox
import shutil
from pathlib import Path
import os

def copy_image_to_directory(source_path, dest_directory):
    """
    Copia una imagen al directorio actual con nombre único si es necesario.
    
    Args:
        source_path (str): Ruta del archivo fuente
        
    Returns:
        str: Nombre del archivo copiado, o None si falla
    """
    try:
        source_file = Path(source_path)
        if not source_file.exists():
            return None
        
        # Generar nombre único en el directorio destino
        base_name = source_file.stem
        extension = source_file.suffix
        dest_filename = f"{base_name}{extension}"
        dest_path = os.path.join(dest_directory, dest_filename)
        
        # Si el archivo ya existe, agregar número secuencial
        counter = 1
        while os.path.exists(dest_path):
            dest_filename = f"{base_name}_{counter:03d}{extension}"
            dest_path = os.path.join(dest_directory, dest_filename)
            counter += 1
        
        # Copiar archivo
        shutil.copy2(source_path, dest_path)
        return dest_filename
        
    except Exception as e:
        messagebox.showerror("Error", f"Error copiando {source_path}: {str(e)}")
        return None
