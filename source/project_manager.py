#!/usr/bin/env python3

import json
import os
from slugify import slugify

# cuando mejores las funciones de bundle
#import bundle_types

def is_copista_project(directory):
    """ una confirmacion rapida de que la carpeta es un proyecto copista """
    path_to_check = os.path.join(directory, 'bundles.json')   
    if os.path.isfile(path_to_check):
        return True
    else:
        return False
    
class Project:
    def __init__(self, directory):
        self.directory = directory
        self.project_metadata = {
            "title" : None,
            "description" : None
        }
        self.bundles = []
        self.files = {
            "bundles": os.path.join(self.directory, "bundles.json"),
            "project_metadata": os.path.join(self.directory, "project_metadata.json"),
            "documents_metadata": os.path.join(self.directory, "documents_metadata.json"),
        }
        self.subfolders = {
            "cache_subfolder": os.path.join(self.directory, ".cache"),
            "capture_subfolder": os.path.join(self.directory, ".capture")
        }

    def load_bundles(self):
        result, message, bundles = self.load_from_json(self.files["bundles"], 'bundles')
        if not result:
            return False, message
        self.bundles = bundles
        return True, None

    def save_bundles(self):
        bundles = {"bundles": self.bundles}     
        result, message = self.save_to_json(self.files["bundles"], bundles)
        if not result:
            return False, message
        return True, message

    def load_project_metadata(self):
        result, message, project_metadata = self.load_from_json(self.files["project_metadata"], 'project_metadata')
        if not result:
            return False, message
        self.project_metadata = project_metadata
        return True, None

    def save_project_metadata(self):
        project_metadata = {"project_metadata": self.project_metadata}     
        result, message = self.save_to_json(self.files["project_metadata"], project_metadata)
        if not result:
            return False, message
        return True, message
                
    def load_from_json(self, file, item_name):
        """
        Cargar data desde el archivo JSON
        """
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                item = data.get(item_name, [])
        except FileNotFoundError:
            filename = os.path.basename(file)
            message = ("Error", f"No existe {filename} en el proyecto")
            return False, message, None
        except json.JSONDecodeError:
            filename = os.path.basename(file)
            message = ("Error", "Error al leer {filename}")
            return False, message, None
        except Exception as e:
            message = ("Error", f"Error inesperado: {str(e)}")
            return False, message, None

        message = ("Advertencia", "No se encontro {item_name} en el archivo JSON") if not item else None           
        return True, message, item
        
    def save_to_json(self, file, data):
        """
        Actualiza un archivo json con la data actual
        """
        try:
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            message = ("Error", f"Error actualizando {file}: {str(e)}")
            return False, message
        return True, None
            
    def ensure_subfolders(self):
        """Verifica si las subcarpetas de proyecto estan presentes, sino las crea"""
        for subfolder in self.subfolders.values():        
            try:
                os.makedirs(subfolder, exist_ok=True)
                print(f"Directorio creado o ya existía: {subfolder}")
            except OSError as e:
                message = ("Error", f"Error al crear {subfolder}: {e}")
                return False, message
        return True, None

class ProjectManager:
    def __init__(self, settings):
        self.config = self.load_config(settings)
        self.session = settings
        self.current_project = None

    def load_config(self, settings):
        """ 
        Si existe config.json, cargarlo. Si se necesitan valores por default 
        definirlos aqui.
        """
        # intentar cargar confing desde settings['copista_folder']
        default_config = {
            'base_projects_folder': settings['base_projects_folder'],
            'copista_folder': settings['copista_folder']
        }
        return default_config

    def is_project_valid(self, directory):
        #TODO: por ahora solo deberia verificar que el directorio exista y bundles.json sea valido
        pass

    def create_project(self, title=None, parent_directory=None):
        if not title:
            return False
        slug = slugify(title)
        parent = parent_directory if parent_directory else self.config['base_projects_folder']
        new_directory = os.path.join(parent, slug)
        
        # Si el archivo ya existe, agregar número secuencial
        counter = 1
        while os.path.exists(new_directory):
            alt_slug = f"{slug}_{counter:03d}"
            new_directory = os.path.join(parent, alt_slug)
            counter += 1

        new_project = Project(new_directory)
        new_project.project_metadata["title"] = title
           
        try:
            os.makedirs(new_project.directory, exist_ok=True)
        except OSError as e:
            message = ("Error", f"Error al crear {new_project.directory}: {e}")
            return False, message
            
        result, message = new_project.ensure_subfolders()
        if not result:
            return False, message
        result, message = new_project.save_bundles()
        if not result:
            return False, message
        result, message = new_project.save_project_metadata()
        if not result:
            return False, message
            
        self.current_project = new_project
        return True, None
            
    def load_project(self, directory):
        if not os.path.exists(directory):
            message = ("Error", f"No existe el directorio del proyecto {project.directory}")
            return False, message

        project = Project(directory)
        result, message = project.load_bundles()
        if not result:
            return False, message
        result, message_update = project.ensure_subfolders()
        if not result:
            return False, message
        result, message = project.load_project_metadata()
        if not result:
            return False, message
        
        self.current_project = project
        return True, message

    def _cleanup_copied_files(self, filenames):
        """
        Elimina archivos que fueron copiados (para limpiar en caso de error).
        
        Args:
            filenames (list): Lista de nombres de archivos a eliminar
        """
        for filename in filenames:
            try:
                file_path = os.path.join(self.current_project.directory, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Advertencia: No se pudo eliminar {filename}: {str(e)}")

    def insert_bundle(self, image_paths, bundle_type, index):
        # TODO: copia las imagenes e inserta el bundle en bundle.json
        pass

