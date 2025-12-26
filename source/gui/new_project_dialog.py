#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import uuid
import re
from slugify import slugify

class NewProjectDialog:
    """Diálogo para crear un nuevo proyecto"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.result = None  # Almacenará el resultado del diálogo
        self.dialog = None
        
        # Variables de los campos
        self.title_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.identifier_var = tk.StringVar()
        
        # Generar ID único por defecto
        self.generate_unique_id()
        
    def generate_unique_id(self):
        """Genera un identificador único automáticamente"""
        new_id = str(uuid.uuid4())[:8].upper()  # 8 caracteres del UUID
        self.identifier_var.set(f"PRE_{new_id}")
    
    def validate_identifier(self, identifier):
        """Valida que el identificador cumpla con el formato requerido"""
        # Solo letras, números y guiones bajos, no espacios
        pattern = re.compile(r'^[A-Za-z0-9_-]+$')
        return bool(pattern.match(identifier)) and len(identifier) >= 3
    
    def validate_fields(self):
        """Valida todos los campos del formulario"""
        title = self.title_var.get().strip()
        description = self.description_var.get().strip()
        identifier = self.identifier_var.get().strip()
        
        errors = []
        
        # Validar título
        if not title:
            errors.append("El título es obligatorio")
        elif len(title) < 3:
            errors.append("El título debe tener al menos 3 caracteres")
        
        # Validar descripción (opcional pero recomendada)
        if description and len(description) < 5:
            errors.append("La descripción debe tener al menos 5 caracteres")
        
        # Validar identificador
        if not identifier:
            errors.append("El identificador es obligatorio")
        elif not self.validate_identifier(identifier):
            errors.append("El identificador solo puede contener letras, números, guiones y guiones bajos")
        elif len(identifier) < 3:
            errors.append("El identificador debe tener al menos 3 caracteres")
        
        return errors
    
    def on_title_changed(self, *args):
        """Genera automáticamente el ID basado en el título"""
        title = self.title_var.get()
        if title:
            # Generar ID basado en el título
            #id_base = re.sub(r'[^a-zA-Z0-9]', '_', titulo).upper()[:15]
            id_base = re.sub('-', '_', slugify(title)).upper()[:25]
            if id_base:
                self.identifier_var.set(f"{id_base}")
                #self.identifier_var.set(f"{id_base}_{uuid.uuid4().hex[:4].upper()}")
    
    def create_widgets(self):
        """Crear todos los widgets del diálogo"""
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título del diálogo
        dialog_title = ttk.Label(main_frame, text="Crear Nuevo Proyecto", 
                                 font=('Arial', 14, 'bold'))
        dialog_title.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)
        
        # Campo: Título del proyecto
        ttk.Label(main_frame, text="Título del Proyecto:").grid(row=1, column=0, sticky=tk.W, pady=5)
        title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=40)
        title_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Bind para generar ID automáticamente
        self.title_var.trace('w', self.on_title_changed)
        
        # Etiqueta de ayuda para título
        title_help = ttk.Label(main_frame, text="Ej: Mi Proyecto de Fotografía", 
                               foreground='gray', font=('Arial', 8))
        title_help.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Campo: Descripción
        ttk.Label(main_frame, text="Descripción:").grid(row=3, column=0, sticky=(tk.W, tk.N), pady=(15, 5))
        desc_frame = ttk.Frame(main_frame)
        desc_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(15, 5))
        desc_frame.columnconfigure(0, weight=1)
        
        # Text widget con scrollbar
        desc_text = tk.Text(desc_frame, height=4, width=40, wrap=tk.WORD)
        desc_scrollbar = ttk.Scrollbar(desc_frame, orient="vertical", command=desc_text.yview)
        desc_text.configure(yscrollcommand=desc_scrollbar.set)
        
        desc_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        desc_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Conectar Text widget con StringVar
        def on_desc_change(*args):
            content = desc_text.get('1.0', 'end-1c')
            self.description_var.set(content)
        
        desc_text.bind('<KeyRelease>', on_desc_change)
        self.desc_text = desc_text  # Guardar referencia
        
        # Etiqueta de ayuda para descripción
        desc_help = ttk.Label(main_frame, text="Descripción detallada del proyecto (opcional)", 
                              foreground='gray', font=('Arial', 8))
        desc_help.grid(row=4, column=1, sticky=tk.W, padx=(10, 0))
        
        # Campo: Identificador único
        ttk.Label(main_frame, text="Identificador Único:").grid(row=5, column=0, sticky=tk.W, pady=(15, 5))
        
        id_frame = ttk.Frame(main_frame)
        id_frame.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(15, 5))
        id_frame.columnconfigure(0, weight=1)
        
        id_entry = ttk.Entry(id_frame, textvariable=self.identifier_var, width=35)
        id_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Botón para generar nuevo ID
        btn_generate_id = ttk.Button(id_frame, text="🔄", width=3,
                                   command=self.generate_unique_id)
        btn_generate_id.grid(row=0, column=1, padx=(5, 0))
        
        # Etiqueta de ayuda para identificador
        id_help = ttk.Label(main_frame, text="Solo letras, números, guiones y guiones bajos. Ej: PROJ_ABC123", 
                            foreground='gray', font=('Arial', 8))
        id_help.grid(row=6, column=1, sticky=tk.W, padx=(10, 0))
        
        # Separador
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        # Frame para botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=8, column=0, columnspan=3, sticky=tk.E)
        
        # Botones
        btn_cancel = ttk.Button(btn_frame, text="Cancelar", 
                                 command=self.cancel)
        btn_cancel.pack(side=tk.RIGHT, padx=(10, 0))
        
        btn_create = ttk.Button(btn_frame, text="Crear Proyecto", 
                              command=self.create_project)
        btn_create.pack(side=tk.RIGHT)
        
        # Establecer botón por defecto
        self.dialog.bind('<Return>', lambda e: self.create_project())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Focus inicial en el campo título
        title_entry.focus_set()
        
        return title_entry
    
    def create_project(self):
        """Procesar la creación del proyecto"""
        errors = self.validate_fields()
        
        if errors:
            error_message = "Por favor corrige los siguientes errores:\n\n" + "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("Errores de validación", error_message, parent=self.dialog)
            return
        
        # Si todo está bien, crear el resultado
        self.result = {
            'title': self.title_var.get().strip(),
            'description': self.description_var.get().strip(),
            'identifier': self.identifier_var.get().strip(),
            'created': True
        }
        
        # Cerrar el diálogo
        self.dialog.destroy()
    
    def cancel(self):
        """Cancelar la creación del proyecto"""
        self.result = {
            'created': False
        }
        self.dialog.destroy()
    
    def open(self):
        """Abrir el diálogo y devolver el resultado"""
        # Crear ventana del diálogo
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Nuevo Proyecto")
        self.dialog.geometry("500x450")
        self.dialog.resizable(True, False)
        
        # Configurar como diálogo modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centrar en pantalla
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Crear widgets
        self.create_widgets()
        
        # Configurar comportamiento de cierre
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        
        # Esperar hasta que se cierre el diálogo
        self.dialog.wait_window()
        
        return self.result

# ===============================================
# FUNCIONES DE CONVENIENCIA
# ===============================================

def create_new_project(parent=None):
    """
    Función de conveniencia para crear un nuevo proyecto.
    
    Args:
        parent: Ventana padre (opcional)
    
    Returns:
        dict: Información del proyecto creado o None si se canceló
        {
            'title': str,
            'description': str,
            'identifier': str,
            'created': bool
        }
    """
    dialog = NewProjectDialog(parent)
    result = dialog.open()
    
    if result and result.get('created'):
        return {
            'title': result['title'],
            'description': result['description'],
            'identifier': result['identifier']
        }
    return None

# ===============================================
# EJEMPLO DE USO
# ===============================================

class ExampleApplication:
    """Aplicación de ejemplo que usa el diálogo"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ejemplo - Gestor de Proyectos")
        self.root.geometry("600x400")
        
        self.projects = []  # Lista de proyectos
        
        self.create_interface()
    
    def create_interface(self):
        """Crear la interfaz principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="Gestor de Proyectos", 
                          font=('Arial', 16, 'bold'))
        title.pack(pady=(0, 20))
        
        # Botón para crear nuevo proyecto
        btn_new = ttk.Button(main_frame, text="➕ Crear Nuevo Proyecto", 
                              command=self.create_new_project,
                              style='Accent.TButton')
        btn_new.pack(pady=10)
        
        # Lista de proyectos
        ttk.Label(main_frame, text="Proyectos:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(20, 5))
        
        # Frame para la lista
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para mostrar proyectos
        columns = ('ID', 'Título', 'Descripción')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        # Configurar columnas
        self.tree.heading('ID', text='Identificador')
        self.tree.heading('Título', text='Título')
        self.tree.heading('Descripción', text='Descripción')
        
        self.tree.column('ID', width=120)
        self.tree.column('Título', width=200)
        self.tree.column('Descripción', width=300)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview y scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_new_project(self):
        """Abrir diálogo para crear nuevo proyecto"""
        result = create_new_project(self.root)
        
        if result:
            # Agregar proyecto a la lista
            self.projects.append(result)
            
            # Agregar a la vista
            self.tree.insert('', tk.END, values=(
                result['identifier'],
                result['title'],
                result['description'][:50] + "..." if len(result['description']) > 50 else result['description']
            ))
            
            # Mostrar mensaje de confirmación
            messagebox.showinfo("Proyecto Creado", 
                              f"Proyecto '{result['title']}' creado exitosamente\n"
                              f"ID: {result['identifier']}", 
                              parent=self.root)
    
    def run(self):
        """Ejecutar la aplicación"""
        self.root.mainloop()

# ===============================================
# EJECUTAR EJEMPLO
# ===============================================

if __name__ == "__main__":
    # Ejemplo 1: Usar solo la función de conveniencia
    print("=== Ejemplo 1: Función simple ===")
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    result = create_new_project()
    if result:
        print(f"Proyecto creado:")
        print(f"  Título: {result['title']}")
        print(f"  Descripción: {result['description']}")
        print(f"  ID: {result['identifier']}")
    else:
        print("Creación cancelada")
    
    root.destroy()
    
    # Ejemplo 2: Aplicación completa
    print("\n=== Ejemplo 2: Aplicación completa ===")
    app = ExampleApplication()
    app.run()
