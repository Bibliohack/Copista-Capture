#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import json
import os

import bundle_types
import file_utils
from project_manager import ProjectManager
from dummy_capture import random_dummy_page_builder
from gui.progress_bar_widget import LoadingDialog
from gui.progress_bar_widget import run_with_loading_dialog
from gui.file_selector_dialog import ask_directory_no_hidden
from gui.user_manager_dialog import authenticate_user
from gui.new_project_dialog import create_new_project

class DigitizationDialog(ProjectManager):
    def __init__(self, root, settings):
        ProjectManager.__init__(self, settings)
        self.session = self.load_session(settings)
        # GUI attributes
        self.root = root
        self.root.title("Copista")
        self.root.geometry("1200x800")
        # Autenticar usuario
        self.current_user = authenticate_user(
            self.root, 
            os.path.join(self.config['copista_folder'], "digitization_users.json")
        )       
        if not self.current_user:
            # Si cancela la autenticación, cerrar aplicación
            self.root.quit()
            return
        
        # Actualizar título con nombre de usuario
        self.root.title(f"Copista - Usuario: {self.current_user['username']}")
        
        # Variables
        self.current_bundle_index = 0
        self.last_parent_directory = None # el directorio donde estan los proyectos
        
        # Crear la interfaz
        self.create_widgets()
        
        # ofrecer seleccionar proyecto
        if not self.current_project:
            self.load_project_and_update_dialog()
            
        if self.current_project:
            # Mostrar el primer bundle
            if self.current_project.bundles:
                self.show_current_bundle()
    
    def load_session(self, settings):
        """ 
        Si existe session.json, cargarlo. Si se necesitan valores por default 
        definirlos aqui.
        """
        # intentar cargar session desde settings['copista_folder']
        return {}
    
    def create_widgets(self): #GUI
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame superior para selección de directorio
        directory_frame = ttk.Frame(main_frame)
        directory_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botón para crear proyecto nuevo
        self.new_project_button = ttk.Button(
            directory_frame,
            text="✨ Crear Proyecto",
            command=self.create_project_and_update_dialog
        )
        self.new_project_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para seleccionar directorio
        self.select_dir_button = ttk.Button(
            directory_frame,
            text="📁 Seleccionar Proyecto",
            command=self.load_project_and_update_dialog
        )
        self.select_dir_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Label para mostrar directorio actual
        if self.current_project:
            directory_info = f"Proyecto: {self.current_project.title}"
        else:
            directory_info = f"SIN PROYECTO CARGADO"
            
        self.directory_label = ttk.Label(
            directory_frame,
            text=directory_info,
            foreground='gray'
        )
        self.directory_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Frame para las imágenes
        self.images_frame = ttk.Frame(main_frame)
        self.images_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Frame para controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X)
            
        # Botón anterior
        self.prev_button = ttk.Button(
            controls_frame, 
            text="← Anterior", 
            command=self.previous_bundle
        )
        self.prev_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botones centrales
        center_frame = ttk.Frame(controls_frame)
        center_frame.pack(side=tk.LEFT, expand=True)
        
        self.center_button1 = ttk.Button(
            center_frame,
            text="Importar",
            command=self.center_function1
        )
        self.center_button1.pack(side=tk.LEFT, padx=5)
        
        self.center_button2 = ttk.Button(
            center_frame,
            text="Capturar",
            command=self.center_function2
        )
        self.center_button2.pack(side=tk.LEFT, padx=5)
        
        # Botón siguiente
        self.next_button = ttk.Button(
            controls_frame,
            text="Siguiente →",
            command=self.next_bundle
        )
        self.next_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Label para mostrar información del bundle actual
        self.info_label = ttk.Label(main_frame, text="")
        self.info_label.pack(pady=(10, 0))

        # Si no hay un proyecto cargado desabilitar botones pertinentes
        if not self.current_project:        
            self.prev_button.config(state='disabled')
            self.next_button.config(state='disabled')
            self.center_button1.config(state='disabled')
            self.center_button2.config(state='disabled')

    def select_project(self): #GUI
        if self.last_parent_directory:
            initial_dir = self.last_parent_directory
        else:
            initial_dir = self.config['base_projects_folder']
            
        new_directory = ask_directory_no_hidden(
            parent=self.root,
            title="Seleccionar directorio de proyecto",
            initial_dir=initial_dir,
            base_projects=self.config['base_projects_folder']
        )
        if new_directory:
            return new_directory
        else:
            return False

    def load_project_and_update_dialog(self):
        new_directory = self.select_project()
        if not new_directory:
            return False
        result, message = self.load_project(new_directory)
        if not result:
            messagebox.showerror(*message)
            return False

        self.directory_label.config(text=self.current_project.project_metadata['title'])
        # Reiniciar índice de bundle
        self.current_bundle_index = 0
        # activar botones pertinentes
        self.center_button1.config(state='normal')
        self.center_button2.config(state='normal')
        # fijando el directorio por defecto para cargar siguientes proyectos
        self.last_parent_directory = os.path.dirname(self.current_project.directory) 
        # Mostrar el primer bundle si existe
        if self.current_project.bundles:
            self.show_current_bundle()
        else:
            # Limpiar pantalla si no hay bundles
            for widget in self.images_frame.winfo_children():
                widget.destroy()
            self.update_info_label()
            self.update_navigation_buttons()
        return True

    def create_project_and_update_dialog(self):
        result = create_new_project(self.root)
        if not result:
            #messagebox.showerror("","")
            return False

        # self.last_parent_directory = os.path.dirname(self.current_project.directory) 
        # TODO: definir si el nuevo proyecto se crea en last_parent oi siempre en base!           
        result, message = self.create_project(title=result["title"], parent_directory=None)
        if not result:
            return False, message

        self.directory_label.config(text=self.current_project.project_metadata['title'])
        # Reiniciar índice de bundle
        self.current_bundle_index = -1
        # activar botones pertinentes
        self.center_button1.config(state='normal')
        self.center_button2.config(state='normal')
        # fijando el directorio por defecto para cargar siguientes proyectos

        # Limpiar pantalla 
        for widget in self.images_frame.winfo_children():
            widget.destroy()
        self.update_info_label()
        #self.update_navigation_buttons()
        return True

    """         
    def select_directory(self): #GUI
        # ToDo: separar en dos funciones, seleccionar el directorio y cargar proyecto,
        # tiene que ser posible cargar el ultimo proyecto cargado, que no llegara
        # de seleccionar el directorio
        #new_directory = filedialog.askdirectory(
        #    title="Seleccionar directorio con imágenes",
        #    initialdir=self.directory
        #)
        if self.last_parent_directory:
            initial_dir = self.last_parent_directory
        else:
            initial_dir = self.config['base_projects_folder']
            
        new_directory = ask_directory_no_hidden(
            parent=self.root,
            title="Seleccionar directorio de proyecto",
            initial_dir=initial_dir,
            base_projects=self.config['base_projects_folder']
        )
        
        if new_directory:  # Si el usuario seleccionó un directorio
            result, message, new_bundles_data = self.try_to_load_bundles_data(new_directory)
            if not result:
                messagebox.showerror(*message)
                return False
            
            if message:
                messagebox.showwarning(*message)
            
            
            self.directory = new_directory
            self.directory_label.config(text=f"Directorio: {self.directory}")
            
            # Reiniciar índice de bundle
            self.current_bundle_index = 0
            
            # Cargar bundles del nuevo directorio
            self.load_bundles(new_bundles_data)
            
            # actualizar subfolders
            self.ensure_subfolders()

            # activar botones pertinentes
            print("Activando botones de funcion")
            self.center_button1.config(state='normal')
            self.center_button2.config(state='normal')

            self.last_parent_directory = os.path.dirname(self.directory)           
            
            # Mostrar el primer bundle si existe
            if self.bundles:
                self.show_current_bundle()
            else:
                # Limpiar pantalla si no hay bundles
                for widget in self.images_frame.winfo_children():
                    widget.destroy()
                self.update_info_label()
                self.update_navigation_buttons()
    """
   
    def show_current_bundle(self): #GUI
        """Mostrar el bundle actual"""
        if not self.current_project.bundles:
            return
        
        # Limpiar displays anteriores
        for widget in self.images_frame.winfo_children():
            widget.destroy()
        
        current_bundle = self.current_project.bundles[self.current_bundle_index]
        bundle_type = current_bundle.get('type', 'generic')
        
        # Por ahora solo procesamos bundles genéricos
        if bundle_type == 'generic':
            #self.process_generic_bundle(current_bundle)
            bundle_type_object = bundle_types.BundleGeneric()
            bundle_type_object.create_display(current_bundle, self)
        
        # Actualizar información
        self.update_info_label()
        
        # Actualizar estado de botones
        self.update_navigation_buttons()
    
    def previous_bundle(self): #GUI
        """Ir al bundle anterior"""
        if self.current_project.bundles and self.current_bundle_index > 0:
            self.current_bundle_index -= 1
            self.show_current_bundle()
    
    def next_bundle(self): #GUI
        """Ir al siguiente bundle"""
        if self.current_project.bundles and self.current_bundle_index < len(self.current_project.bundles) - 1:
            self.current_bundle_index += 1
            self.show_current_bundle()
    
    def update_navigation_buttons(self): #GUI
        """Actualizar estado de botones de navegación"""
        if not self.current_project.bundles:
            self.prev_button.config(state='disabled')
            self.next_button.config(state='disabled')
            return
        
        # Botón anterior
        if self.current_bundle_index <= 0:
            self.prev_button.config(state='disabled')
        else:
            self.prev_button.config(state='normal')
        
        # Botón siguiente
        if self.current_bundle_index >= len(self.current_project.bundles) - 1:
            self.next_button.config(state='disabled')
        else:
            self.next_button.config(state='normal')
    
    def update_info_label(self): #GUI
        """Actualizar label de información"""
        if not self.current_project.bundles:
            self.info_label.config(text="No hay bundles cargados")
            return
        
        current_bundle = self.current_project.bundles[self.current_bundle_index]
        bundle_type = current_bundle.get('type', 'generic')
        num_images = len(current_bundle.get('images', []))
        
        info_text = f"Posición {self.current_bundle_index + 1} de {len(self.current_project.bundles)} | Tipo: {bundle_type} | Objetos: {num_images}"
        self.info_label.config(text=info_text)


    def add_bundle_from_images(self, image_paths): #GUI
        # TODO esta funcion mezcla operciones sobre la interfase y el proyecto, 
        # ademas solo inserta un tipo de bundle generic
        """
        Crea un bundle generic a partir de un array de rutas de imágenes (1-3),
        copia las imágenes al directorio, agrega el bundle y avanza la posición.
        
        Args:
            image_paths (list): Lista con 1-3 rutas de archivos de imagen
        
        Returns:
            bool: True si se completó exitosamente, False en caso de error
        """
        if not image_paths or len(image_paths) == 0 or len(image_paths) > 3:
            messagebox.showerror("Error", "Debe proporcionar entre 1 y 3 rutas de imagen")
            return False
        
        try:
            # Copiar imágenes al directorio actual
            copied_filenames = []
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    messagebox.showerror("Error", f"No se encuentra el archivo: {img_path}")
                    return False
                
                filename = file_utils.copy_image_to_directory(img_path, self.current_project.directory)
                if filename:
                    copied_filenames.append(filename)
                else:
                    # Si falla la copia, limpiar archivos ya copiados
                    self._cleanup_copied_files(copied_filenames)
                    return False
            
            # Crear el nuevo bundle
            new_bundle = {
                "type": "generic",
                "images": copied_filenames
            }
            
            # Insertar bundle en la posición siguiente al actual
            insert_position = self.current_bundle_index + 1
            self.current_project.bundles.insert(insert_position, new_bundle)
            
            # Actualizar archivo JSON
            result, message = self.current_project.save_bundles()
            if result:
                # Avanzar a la nueva posición
                self.current_bundle_index = insert_position
                self.show_current_bundle()
                return True
            else:
                # Si falla la actualización del JSON, revertir cambios
                self.current_project.bundles.pop(insert_position)
                self._cleanup_copied_files(copied_filenames)
                messagebox.showerror(*message)
                return False
                
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado al agregar bundle: {str(e)}")
            return False

    def add_bundle_from_file_dialog(self): #GUI
        """
        Función de conveniencia que abre un diálogo para seleccionar imágenes
        y crear un bundle con ellas.
        """
        file_types = [
            ('Imágenes', '*.jpg *.jpeg *.png *.gif *.bmp *.tiff'),
            ('JPEG', '*.jpg *.jpeg'),
            ('PNG', '*.png'),
            ('Todos los archivos', '*.*')
        ]
        
        selected_files = filedialog.askopenfilenames(
            title="Seleccionar imágenes para el bundle (máximo 3)",
            filetypes=file_types,
            initialdir=os.path.expanduser("~")
        )
        
        if selected_files:
            if len(selected_files) > 3:
                messagebox.showwarning("Advertencia", 
                    "Solo se pueden seleccionar máximo 3 imágenes. Se tomarán las primeras 3.")
                selected_files = selected_files[:3]
            
            return self.add_bundle_from_images(list(selected_files))
        
        return False

    def add_bundle_from_dummy(self): #GUI
        if self.current_project.subfolders["capture_subfolder"]:
            path_left  = os.path.join(self.current_project.subfolders["capture_subfolder"], "left.jpg")
            path_right = os.path.join(self.current_project.subfolders["capture_subfolder"], "right.jpg")
            
            def operation():
                # Tu código original aquí
                capture_result = random_dummy_page_builder.get_dummy_capture(path_left, path_right)
                if capture_result:
                    return self.add_bundle_from_images([path_left, path_right])                
                else:
                    return False
                    
            return run_with_loading_dialog(
                self.root,
                operation, 
                "Dummy capture",
                "Capturando imágenes..."
            )

        return False

    # Funciones de placeholder (por ahora vacías)
    def image_function(self, image_name):
        """Función que se ejecuta al hacer clic en botón de imagen"""
        print(f"Función de imagen ejecutada para: {image_name}")
        # TODO: Implementar funcionalidad específica
        pass
    
    def center_function1(self):
        """Primera función central"""
        
        self.add_bundle_from_file_dialog()
        #print("Función central 1 ejecutada")
        # TODO: Implementar funcionalidad específica
        #pass
    
    def center_function2(self):
        """Segunda función central"""
        self.add_bundle_from_dummy()
        #print("Función central 2 ejecutada")
        # TODO: Implementar funcionalidad específica
        #pass

def launch_digitization_app_dialog(settings):
    root = tk.Tk()
    app = DigitizationDialog(root, settings)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario")

