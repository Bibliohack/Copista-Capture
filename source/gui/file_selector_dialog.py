#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import platform

from project_manager import is_copista_project

# Opción 2: Diálogo personalizado con Tkinter
class ProjectSelector:
    def __init__(self, parent, title="Seleccionar Proyecto", initial_dir=None, base_projects=None ):
        self.parent = parent
        self.selected_directory = None
        self.current_path = initial_dir or os.getcwd()
        self.base_projects = base_projects
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.center_window()
        
        # Crear interfaz
        self.create_widgets()
        
        # Cargar directorio inicial
        self.load_directory(self.current_path)
    
    def center_window(self):
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"600x400+{x}+{y}")
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame superior con ruta actual
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(path_frame, text="Directorio actual:").pack(side=tk.LEFT)
        self.path_label = ttk.Label(path_frame, text=self.current_path, foreground='blue')
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Frame para navegación
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.up_button = ttk.Button(nav_frame, text="⬆ Directorio Padre", command=self.go_up)
        self.up_button.pack(side=tk.LEFT)

        if self.base_projects:
            self.home_button = ttk.Button(nav_frame, text="🤖 Proyectos Copista", command=self.go_base_projects)
            self.home_button.pack(side=tk.LEFT, padx=(5, 0))

        self.home_button = ttk.Button(nav_frame, text="🏠 Carpeta personal", command=self.go_home)
        self.home_button.pack(side=tk.LEFT, padx=(5, 0))

        
        # Lista de directorios
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        self.dir_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.dir_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.dir_listbox.bind('<Double-1>', self.on_double_click)
        
        scrollbar.config(command=self.dir_listbox.yview)
        
        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancelar", command=self.cancel).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Cargar Proyecto", command=self.select_selection).pack(side=tk.RIGHT, padx=(0, 5))
    
    def load_directory(self, path):
        """Cargar contenido del directorio, ocultando archivos ocultos"""
        try:
            self.current_path = os.path.abspath(path)
            self.path_label.config(text=self.current_path)
            
            # Limpiar lista
            self.dir_listbox.delete(0, tk.END)
            
            # Obtener contenido
            items = []
            try:
                for item in os.listdir(self.current_path):
                    # FILTRAR ARCHIVOS OCULTOS (que empiezan con punto)
                    if not item.startswith('.'):
                        item_path = os.path.join(self.current_path, item)
                        if os.path.isdir(item_path):
                            items.append(item)
            except PermissionError:
                self.dir_listbox.insert(tk.END, "[Sin permisos para leer este directorio]")
                return
            
            # Ordenar y agregar a la lista
            items.sort()
            for item in items:
                if is_copista_project(os.path.join(self.current_path, item)):
                    self.dir_listbox.insert(tk.END, f"🤖 {item}")
                else:
                    self.dir_listbox.insert(tk.END, f"📁 {item}")
                
        except Exception as e:
            self.dir_listbox.delete(0, tk.END)
            self.dir_listbox.insert(tk.END, f"[Error: {str(e)}]")
    
    def on_double_click(self, event):
        """Manejar doble clic en directorio"""
        selection = self.dir_listbox.curselection()
        if selection:
            item = self.dir_listbox.get(selection[0])
            if item.startswith("📁 "):
                dir_name = item[2:]  # Remover emoji
                new_path = os.path.join(self.current_path, dir_name)
                self.load_directory(new_path)
            elif item.startswith("🤖 "):
                dir_name = item[2:]  # Remover emoji
                self.current_path = os.path.join(self.current_path, dir_name)
                self.select_current()
    
    def go_up(self):
        """Ir al directorio padre"""
        parent_path = os.path.dirname(self.current_path)
        if parent_path != self.current_path:  # No estamos en la raíz
            self.load_directory(parent_path)
    
    def go_home(self):
        """Ir al directorio home"""
        self.load_directory(os.path.expanduser("~"))

    def go_base_projects(self):
        """Ir a base_projects"""
        if self.base_projects:
            self.load_directory(self.base_projects)
                
    def select_selection(self):
        """Seleccionar directorio actual"""
        selection = self.dir_listbox.curselection()
        if selection: 
            item = self.dir_listbox.get(selection[0])
            if item.startswith("🤖 "):
                dir_name = item[2:]  # Remover emoji
                self.current_path = os.path.join(self.current_path, dir_name)
                self.select_current()
            else:
                messagebox.showwarning("Atención", "El item seleccionado no es un Proyecto Copista")
        else:
            messagebox.showwarning("Atención", "No ha seleccionado ningun item")
            
    def select_current(self):
        """Seleccionar directorio actual"""
        self.selected_directory = self.current_path
        self.dialog.destroy()
    
    def cancel(self):
        """Cancelar selección"""
        self.selected_directory = None
        self.dialog.destroy()
    
    def show(self):
        """Mostrar diálogo y retornar directorio seleccionado"""
        self.parent.wait_window(self.dialog)
        return self.selected_directory


def ask_directory_no_hidden(parent=None, title="Seleccionar directorio", initial_dir=None, base_projects=None):
    """
    Seleccionar un directorio de proyecto, sin mostrar archivos ocultos.
    """
    if parent:
        selector = ProjectSelector(parent, title, initial_dir, base_projects)
        return selector.show()

