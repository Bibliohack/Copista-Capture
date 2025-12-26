#!/usr/bin/env python3

import logging
from typing import Optional, Dict, Any, List, Union
from pathlib import Path

try:
    import gphoto2 as gp
except ImportError:
    raise ImportError(
        "gphoto2 library not found. Install with: pip install gphoto2\n"
        "Also ensure libgphoto2 is installed on your system."
    )

# Importar la clase base
from gphoto2_capture import Capture


class ConfigUtils(Capture):
    """
    Controlador extendido con funcionalidades avanzadas de configuración.
    Hereda de Capture y agrega métodos para manipular configuraciones específicas.
    """
    
    def __init__(self, download_folder: str, camera_port: str = "usb:001,059", 
                 use_camera_ram: bool = True):
        """
        Inicializar el controlador extendido.
        
        Args:
            download_folder (str): Carpeta donde se descargarán las imágenes
            camera_port (str): Puerto USB donde está conectada la cámara
            use_camera_ram (bool): Si True, captura directamente en RAM
        """
        super().__init__(download_folder, camera_port, use_camera_ram)
        self.logger.info("Canon T7 Extended Controller inicializado")
    
    def get_all_config_keys(self) -> List[str]:
        """
        Obtener todas las claves de configuración disponibles en la cámara.
        
        Returns:
            List[str]: Lista con todas las claves de configuración disponibles
        """
        if not self.camera:
            self.logger.error("No hay conexión con la cámara.")
            return []
        
        try:
            config = self.camera.get_config(self.context)
            keys = self._extract_config_keys(config)
            self.logger.info(f"Se encontraron {len(keys)} claves de configuración")
            return keys
            
        except gp.GPhoto2Error as e:
            self.logger.error(f"Error al obtener claves de configuración: {e}")
            return []
    
    def _extract_config_keys(self, config, parent_path: str = "") -> List[str]:
        """
        Extraer todas las claves de configuración recursivamente.
        
        Args:
            config: Objeto de configuración de gphoto2
            parent_path (str): Ruta padre para claves anidadas
            
        Returns:
            List[str]: Lista de claves encontradas
        """
        keys = []
        
        try:
            for i in range(config.count_children()):
                child = config.get_child(i)
                child_name = child.get_name()
                
                # Construir la ruta completa de la clave
                if parent_path:
                    full_key = f"{parent_path}.{child_name}"
                else:
                    full_key = child_name
                
                # Agregar la clave actual
                keys.append(full_key)
                
                # Si tiene hijos, extraer recursivamente
                if child.count_children() > 0:
                    child_keys = self._extract_config_keys(child, full_key)
                    keys.extend(child_keys)
                    
        except Exception as e:
            self.logger.debug(f"Error extrayendo claves de {parent_path}: {e}")
        
        return keys
    
    def get_config_value(self, config_key: str) -> Optional[Dict[str, Any]]:
        """
        Obtener el valor y metadatos de una entrada de configuración específica.
        
        Args:
            config_key (str): Clave de configuración (ej: 'iso', 'shutterspeed', 'aperture')
                             Puede usar notación de punto para claves anidadas (ej: 'image.quality')
        
        Returns:
            Dict[str, Any]: Diccionario con información de la configuración:
                - 'key': Clave solicitada
                - 'current_value': Valor actual
                - 'choices': Lista de valores posibles (si aplica)
                - 'type': Tipo de configuración
                - 'readonly': Si es solo lectura
                - 'label': Etiqueta descriptiva
                - 'info': Información adicional
            None si la clave no existe o hay error
        """
        if not self.camera:
            self.logger.error("No hay conexión con la cámara.")
            return None
        
        try:
            config = self.camera.get_config(self.context)
            config_item = self._find_config_item(config, config_key)
            
            if not config_item:
                self.logger.warning(f"Clave de configuración '{config_key}' no encontrada")
                return None
            
            # Obtener información del item de configuración
            result = {
                'key': config_key,
                'current_value': None,
                'choices': [],
                'type': None,
                'readonly': False,
                'label': '',
                'info': ''
            }
            
            try:
                result['current_value'] = config_item.get_value()
            except:
                result['current_value'] = None
            
            try:
                result['type'] = config_item.get_type()
            except:
                pass
            
            try:
                result['label'] = config_item.get_label()
            except:
                pass
            
            try:
                result['info'] = config_item.get_info()
            except:
                pass
            
            try:
                result['readonly'] = config_item.get_readonly()
            except:
                pass
            
            # Obtener opciones disponibles si es un tipo choice
            try:
                choice_count = config_item.count_choices()
                for i in range(choice_count):
                    choice = config_item.get_choice(i)
                    result['choices'].append(choice)
            except:
                pass  # No todos los items tienen choices
            
            self.logger.info(f"Configuración '{config_key}': {result['current_value']}")
            return result
            
        except gp.GPhoto2Error as e:
            self.logger.error(f"Error al obtener configuración '{config_key}': {e}")
            return None
    
    def set_config_value(self, config_key: str, value: Union[str, int, float, Dict[str, Any]]) -> bool:
        """
        Modificar el valor de una entrada de configuración.
        
        Args:
            config_key (str): Clave de configuración a modificar
            value: Nuevo valor a establecer. Puede ser:
                  - str/int/float: Valor directo
                  - Dict: Para configuraciones complejas con múltiples parámetros
        
        Returns:
            bool: True si la configuración se aplicó exitosamente, False en caso contrario
        """
        if not self.camera:
            self.logger.error("No hay conexión con la cámara.")
            return False
        
        try:
            config = self.camera.get_config(self.context)
            config_item = self._find_config_item(config, config_key)
            
            if not config_item:
                self.logger.error(f"Clave de configuración '{config_key}' no encontrada")
                return False
            
            # Verificar si es de solo lectura
            try:
                if config_item.get_readonly():
                    self.logger.error(f"La configuración '{config_key}' es de solo lectura")
                    return False
            except:
                pass  # Si no se puede verificar, intentar continuar
            
            # Obtener valor actual para log
            try:
                current_value = config_item.get_value()
                self.logger.info(f"Cambiando '{config_key}' de '{current_value}' a '{value}'")
            except:
                self.logger.info(f"Estableciendo '{config_key}' a '{value}'")
            
            # Establecer nuevo valor
            if isinstance(value, dict):
                # Para configuraciones complejas, intentar establecer sub-valores
                for sub_key, sub_value in value.items():
                    try:
                        sub_config = config_item.get_child_by_name(sub_key)
                        sub_config.set_value(sub_value)
                        self.logger.debug(f"Sub-configuración '{sub_key}' establecida a '{sub_value}'")
                    except Exception as e:
                        self.logger.warning(f"No se pudo establecer sub-configuración '{sub_key}': {e}")
            else:
                # Valor simple
                config_item.set_value(value)
            
            # Aplicar configuración a la cámara
            self.camera.set_config(config, self.context)
            
            # Verificar que el cambio se aplicó
            new_config = self.camera.get_config(self.context)
            new_config_item = self._find_config_item(new_config, config_key)
            if new_config_item:
                try:
                    actual_value = new_config_item.get_value()
                    if str(actual_value) == str(value) or (isinstance(value, dict) and actual_value):
                        self.logger.info(f"✅ Configuración '{config_key}' aplicada exitosamente: {actual_value}")
                        return True
                    else:
                        self.logger.warning(f"⚠️ Valor aplicado ({actual_value}) difiere del solicitado ({value})")
                        return True  # Aún consideramos exitoso, la cámara puede haber ajustado el valor
                except:
                    self.logger.info(f"✅ Configuración '{config_key}' aplicada (verificación no disponible)")
                    return True
            
            return True
            
        except gp.GPhoto2Error as e:
            self.logger.error(f"Error al establecer configuración '{config_key}': {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error inesperado al configurar '{config_key}': {e}")
            return False
    
    def _find_config_item(self, config, config_key: str):
        """
        Buscar un item de configuración por clave, soportando notación de punto.
        
        Args:
            config: Objeto de configuración base
            config_key (str): Clave a buscar (ej: 'iso' o 'image.quality')
            
        Returns:
            Objeto de configuración encontrado o None
        """
        # Dividir la clave si tiene notación de punto
        key_parts = config_key.split('.')
        current_config = config
        
        try:
            for part in key_parts:
                # Buscar en los hijos del config actual
                found = False
                for i in range(current_config.count_children()):
                    child = current_config.get_child(i)
                    if child.get_name().lower() == part.lower():
                        current_config = child
                        found = True
                        break
                
                if not found:
                    # Intentar búsqueda case-insensitive más exhaustiva
                    for i in range(current_config.count_children()):
                        child = current_config.get_child(i)
                        child_name = child.get_name()
                        if (part.lower() in child_name.lower() or 
                            child_name.lower() in part.lower()):
                            current_config = child
                            found = True
                            self.logger.debug(f"Encontrado match parcial: '{part}' -> '{child_name}'")
                            break
                
                if not found:
                    return None
            
            return current_config
            
        except Exception as e:
            self.logger.debug(f"Error buscando configuración '{config_key}': {e}")
            return None
    
    def get_common_settings(self) -> Dict[str, Any]:
        """
        Obtener configuraciones comunes de fotografía de forma conveniente.
        
        Returns:
            Dict[str, Any]: Diccionario con configuraciones comunes:
                - 'iso': Configuración ISO actual
                - 'shutter_speed': Velocidad de obturación
                - 'aperture': Apertura/f-stop
                - 'white_balance': Balance de blancos
                - 'image_quality': Calidad de imagen
                - 'focus_mode': Modo de enfoque
        """
        common_keys = {
            'iso': ['iso', 'isospeed', 'sensitivity'],
            'shutter_speed': ['shutterspeed', 'shutter', 'speed'],
            'aperture': ['aperture', 'fnumber', 'f-number'],
            'white_balance': ['whitebalance', 'wb'],
            'image_quality': ['imagequality', 'quality'],
            'focus_mode': ['focusmode', 'autofocus', 'af']
        }
        
        result = {}
        
        for setting_name, possible_keys in common_keys.items():
            for key in possible_keys:
                config_info = self.get_config_value(key)
                if config_info:
                    result[setting_name] = config_info
                    break
            
            if setting_name not in result:
                result[setting_name] = None
        
        return result
    
    def set_common_settings(self, settings: Dict[str, Union[str, int, float]]) -> Dict[str, bool]:
        """
        Establecer múltiples configuraciones comunes de una vez.
        
        Args:
            settings (Dict): Diccionario con configuraciones a establecer:
                - 'iso': Valor ISO (ej: 100, 200, 400, 800, 1600, 3200)
                - 'shutter_speed': Velocidad obturación (ej: '1/60', '1/125')
                - 'aperture': Apertura (ej: 'f/2.8', 'f/5.6')
                - 'white_balance': Balance blancos (ej: 'Auto', 'Daylight')
                - 'image_quality': Calidad (ej: 'Fine', 'Normal')
        
        Returns:
            Dict[str, bool]: Resultado de cada configuración aplicada
        """
        common_key_mapping = {
            'iso': ['iso', 'isospeed'],
            'shutter_speed': ['shutterspeed', 'shutter'],
            'aperture': ['aperture', 'fnumber'],
            'white_balance': ['whitebalance', 'wb'],
            'image_quality': ['imagequality', 'quality'],
            'focus_mode': ['focusmode', 'autofocus']
        }
        
        results = {}
        
        for setting_name, value in settings.items():
            if setting_name in common_key_mapping:
                success = False
                for key in common_key_mapping[setting_name]:
                    if self.set_config_value(key, value):
                        success = True
                        break
                results[setting_name] = success
            else:
                # Intentar establecer directamente si no está en el mapeo
                results[setting_name] = self.set_config_value(setting_name, value)
        
        return results
    
    def print_all_configurations(self, filter_pattern: Optional[str] = None) -> None:
        """
        Imprimir todas las configuraciones disponibles de forma organizada.
        
        Args:
            filter_pattern (str, optional): Patrón para filtrar configuraciones
                                          (ej: 'iso', 'focus', 'image')
        """
        print("\n" + "="*60)
        print("CONFIGURACIONES DE CÁMARA CANON T7")
        print("="*60)
        
        keys = self.get_all_config_keys()
        
        if filter_pattern:
            keys = [key for key in keys if filter_pattern.lower() in key.lower()]
            print(f"Filtrado por: '{filter_pattern}' ({len(keys)} resultados)")
            print("-"*60)
        
        for key in sorted(keys):
            config_info = self.get_config_value(key)
            if config_info:
                print(f"\n📷 {key}")
                print(f"   Valor actual: {config_info['current_value']}")
                print(f"   Etiqueta: {config_info['label']}")
                print(f"   Solo lectura: {'Sí' if config_info['readonly'] else 'No'}")
                
                if config_info['choices']:
                    choices_str = ', '.join(map(str, config_info['choices'][:10]))
                    if len(config_info['choices']) > 10:
                        choices_str += f" ... (+{len(config_info['choices']) - 10} más)"
                    print(f"   Opciones: {choices_str}")
                
                if config_info['info']:
                    print(f"   Info: {config_info['info']}")
        
        print(f"\n📊 Total de configuraciones: {len(keys)}")
        print("="*60)


# ===============================================
# EJEMPLO DE USO DE LA CLASE EXTENDIDA
# ===============================================

def example_usage():
    """Ejemplo de uso del controlador extendido"""
    download_folder = "./captured_images"
    
    try:
        with ConfigUtils(download_folder, use_camera_ram=True) as camera:
            print("=== EXPLORANDO CONFIGURACIONES ===")
            
            # Obtener todas las claves disponibles
            all_keys = camera.get_all_config_keys()
            print(f"Total de configuraciones disponibles: {len(all_keys)}")
            
            # Mostrar algunas configuraciones comunes
            print("\n=== CONFIGURACIONES COMUNES ===")
            common = camera.get_common_settings()
            for name, config in common.items():
                if config:
                    print(f"{name}: {config['current_value']} "
                          f"(opciones: {len(config['choices'])})")
                else:
                    print(f"{name}: No disponible")
            
            # Ejemplo: Obtener configuración específica
            print("\n=== CONFIGURACIÓN ESPECÍFICA (ISO) ===")
            iso_config = camera.get_config_value('iso')
            if iso_config:
                print(f"ISO actual: {iso_config['current_value']}")
                print(f"Opciones ISO disponibles: {iso_config['choices']}")
            
            # Ejemplo: Modificar configuración
            print("\n=== MODIFICANDO CONFIGURACIONES ===")
            changes = {
                'iso': '400',
                'image_quality': 'Fine'
            }
            
            results = camera.set_common_settings(changes)
            for setting, success in results.items():
                status = "✅ Exitoso" if success else "❌ Error"
                print(f"{setting}: {status}")
            
            # Mostrar configuraciones filtradas
            print("\n=== CONFIGURACIONES RELACIONADAS CON ISO ===")
            camera.print_all_configurations('iso')
            
            # Capturar imagen con nueva configuración
            print("\n=== CAPTURANDO IMAGEN ===")
            captured = camera.capture_and_download("imagen_configurada.jpg")
            if captured:
                print(f"✅ Imagen capturada: {captured}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    example_usage()
