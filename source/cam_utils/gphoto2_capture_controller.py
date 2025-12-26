#!/usr/bin/env python3

import os
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

try:
    import gphoto2 as gp
except ImportError:
    raise ImportError(
        "gphoto2 library not found. Install with: pip install gphoto2\n"
        "Also ensure libgphoto2 is installed on your system."
    )


class CaptureController:
    """
    Controlador de camara usando gphoto2.
    Permite capturar y descargar imágenes directamente desde la cámara.
    """
    
    def __init__(self, download_folder: str, camera_port: str = "usb:001,059", 
                 use_camera_ram: bool = True):
        """
        Inicializar el controlador de la cámara Canon T7.
        
        Args:
            download_folder (str): Carpeta donde se descargarán las imágenes
            camera_port (str): Puerto USB donde está conectada la cámara
            use_camera_ram (bool): Si True, captura directamente en RAM (no necesita SD card)
                                 Si False, captura en tarjeta SD
        """
        self.download_folder = Path(download_folder)
        self.camera_port = camera_port
        self.use_camera_ram = use_camera_ram
        self.camera = None
        self.context = None
        
        # Configurar logging
        self.logger = self._setup_logging()
        
        # Crear carpeta de descarga si no existe
        self.download_folder.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Canon T7 Controller inicializado")
        self.logger.info(f"Carpeta de descarga: {self.download_folder}")
        self.logger.info(f"Puerto de cámara: {self.camera_port}")
        self.logger.info(f"Modo de captura: {'RAM (sin SD requerida)' if use_camera_ram else 'Tarjeta SD'}")
    
    def _setup_logging(self) -> logging.Logger:
        """Configurar sistema de logging"""
        logger = logging.getLogger('CaptureController')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def connect(self) -> bool:
        """
        Conectar con la cámara Canon T7.
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            self.logger.info("Intentando conectar con la cámara...")
            
            # Crear contexto de gphoto2
            self.context = gp.Context()
            
            # Inicializar cámara
            self.camera = gp.Camera()
            
            # Intentar detectar cámara automáticamente primero
            if not self._try_auto_detect():
                # Si falla detección automática, usar puerto específico
                if self.camera_port:
                    if not self._try_specific_port():
                        return False
                else:
                    self.logger.error("No se pudo detectar la cámara automáticamente")
                    return False
            
            # Inicializar conexión
            self.camera.init(self.context)
            
            # Configurar destino de captura
            self._configure_capture_target()
            
            # Obtener información de la cámara
            camera_info = self._get_camera_info()
            self.logger.info(f"Conectado exitosamente: {camera_info}")
            
            return True
            
        except gp.GPhoto2Error as e:
            self.logger.error(f"Error al conectar con la cámara: {e}")
            self._show_connection_help()
            return False
        except Exception as e:
            self.logger.error(f"Error inesperado al conectar: {e}")
            return False
    
    def _try_auto_detect(self) -> bool:
        """Intentar detectar la cámara automáticamente"""
        try:
            self.logger.info("Intentando detección automática de cámara...")
            
            # Listar cámaras disponibles
            camera_list = gp.check_result(gp.gp_camera_autodetect(self.context))
            
            if not camera_list:
                self.logger.warning("No se detectaron cámaras automáticamente")
                return False
            
            self.logger.info(f"Cámaras detectadas: {len(camera_list)}")
            for i, (name, port) in enumerate(camera_list):
                self.logger.info(f"  {i+1}. {name} en puerto {port}")
            
            # Usar la primera cámara detectada si es Canon
            for name, port in camera_list:
                if 'canon' in name.lower() or 't7' in name.lower():
                    self.logger.info(f"Usando cámara Canon detectada: {name} en {port}")
                    self.camera_port = port
                    return self._try_specific_port()
            
            # Si no encuentra Canon específicamente, usar la primera
            if camera_list:
                name, port = camera_list[0]
                self.logger.info(f"Usando primera cámara detectada: {name} en {port}")
                self.camera_port = port
                return self._try_specific_port()
            
            return False
            
        except gp.GPhoto2Error as e:
            self.logger.warning(f"Error en detección automática: {e}")
            return False
    
    def _try_specific_port(self) -> bool:
        """Intentar conectar usando puerto específico"""
        try:
            self.logger.info(f"Configurando puerto específico: {self.camera_port}")
            port_info_list = gp.PortInfoList()
            port_info_list.load()
            
            # Buscar puerto exacto
            try:
                idx = port_info_list.lookup_path(self.camera_port)
                self.camera.set_port_info(port_info_list[idx])
                return True
            except gp.GPhoto2Error:
                # Si no encuentra puerto exacto, mostrar puertos disponibles
                self.logger.warning(f"Puerto {self.camera_port} no encontrado")
                self._list_available_ports()
                return False
                
        except gp.GPhoto2Error as e:
            self.logger.error(f"Error configurando puerto: {e}")
            return False
    
    def _list_available_ports(self) -> None:
        """Listar puertos disponibles para debugging"""
        try:
            self.logger.info("Puertos USB disponibles:")
            port_info_list = gp.PortInfoList()
            port_info_list.load()
            
            for i in range(port_info_list.count()):
                port_info = port_info_list.get_info(i)
                if 'usb' in port_info.path.lower():
                    self.logger.info(f"  - {port_info.path}")
                    
        except Exception as e:
            self.logger.warning(f"No se pudieron listar puertos: {e}")
    
    def _show_connection_help(self) -> None:
        """Mostrar ayuda para solucionar problemas de conexión"""
        help_msg = """
        ===============================================
        AYUDA PARA SOLUCIONAR PROBLEMAS DE CONEXIÓN:
        ===============================================
        
        1. Verificar que la cámara esté conectada:
           gphoto2 --list-ports
           gphoto2 --auto-detect
        
        2. Verificar permisos USB (agregar usuario a grupo):
           sudo usermod -a -G plugdev $USER
           (luego reiniciar sesión)
        
        3. Crear regla udev para Canon (crear archivo /etc/udev/rules.d/90-libgphoto2.rules):
           SUBSYSTEM=="usb", ATTR{idVendor}=="04a9", MODE="0664", GROUP="plugdev"
        
        4. Reiniciar servicio udev:
           sudo udevadm control --reload-rules
           sudo udevadm trigger
        
        5. Asegurarse de que la cámara esté en modo PTP/MTP:
           - Encender la cámara
           - En menú: Setup > Communication > Set to PTP
        
        6. Probar conexión manual:
           gphoto2 --summary
        """
        print(help_msg)
    
    def disconnect(self) -> None:
        """Desconectar de la cámara y liberar recursos"""
        try:
            if self.camera:
                self.camera.exit(self.context)
                self.logger.info("Cámara desconectada exitosamente")
        except Exception as e:
            self.logger.error(f"Error al desconectar: {e}")
        finally:
            self.camera = None
            self.context = None
    
    def wait_for_camera_ready(self, timeout_seconds: int = 5) -> bool:
        """
        Esperar a que la cámara esté lista para la siguiente operación.
        
        Args:
            timeout_seconds (int): Tiempo máximo de espera en segundos
            
        Returns:
            bool: True si la cámara está lista, False si timeout
        """
        if not self.camera:
            return False
            
        try:
            self.logger.debug("Esperando que la cámara esté lista...")
            start_time = time.time()
            
            while time.time() - start_time < timeout_seconds:
                try:
                    # Esperar eventos con timeout corto
                    event_type, event_data = self.camera.wait_for_event(500, self.context)
                    self.logger.debug(f"Evento detectado: {event_type}")
                    
                    # Si recibimos ciertos eventos, la cámara está lista
                    if event_type in [gp.GP_EVENT_UNKNOWN, gp.GP_EVENT_TIMEOUT]:
                        return True
                        
                except gp.GPhoto2Error:
                    # Si no hay más eventos, probablemente esté lista
                    return True
            
            self.logger.warning(f"Timeout esperando que la cámara esté lista ({timeout_seconds}s)")
            return False
            
        except Exception as e:
            self.logger.error(f"Error esperando cámara lista: {e}")
            return False
    
    def _get_camera_info(self) -> str:
        """Obtener información básica de la cámara"""
        try:
            summary = self.camera.get_summary(self.context)
            return str(summary).split('\n')[0]
        except:
            return "Canon T7 (información no disponible)"
    
    def _configure_capture_target(self) -> None:
        """Configurar el destino de captura (RAM o tarjeta SD)"""
        try:
            config = self.camera.get_config(self.context)
            
            # Buscar el parámetro capturetarget
            capture_target = None
            try:
                capture_target = config.get_child_by_name('capturetarget')
            except gp.GPhoto2Error:
                try:
                    # Algunas cámaras usan 'imagequality' o otro nombre
                    capture_target = config.get_child_by_name('imagequality')
                except gp.GPhoto2Error:
                    self.logger.warning("No se pudo encontrar configuración de destino de captura")
                    return
            
            if capture_target:
                # Obtener las opciones disponibles
                choices = []
                try:
                    choice_count = capture_target.count_choices()
                    for i in range(choice_count):
                        choice = capture_target.get_choice(i)
                        choices.append(choice)
                    self.logger.info(f"Opciones de capturetarget disponibles: {choices}")
                except:
                    pass
                
                if self.use_camera_ram:
                    # Configurar para captura en RAM
                    # Opciones comunes: "Internal RAM", "SDRAM", 0
                    target_values = ["Internal RAM", "SDRAM", "RAM", "0"]
                    for target_value in target_values:
                        try:
                            if target_value in choices:
                                capture_target.set_value(target_value)
                                self.logger.info(f"Configurado capturetarget a: {target_value}")
                                break
                            elif target_value == "0" and len(choices) > 0:
                                capture_target.set_value(choices[0])  # Primer opción disponible
                                self.logger.info(f"Configurado capturetarget a: {choices[0]} (primera opción)")
                                break
                        except gp.GPhoto2Error as e:
                            self.logger.debug(f"No se pudo configurar a {target_value}: {e}")
                            continue
                else:
                    # Configurar para captura en tarjeta SD
                    # Opciones comunes: "Memory card", "SD", 1
                    target_values = ["Memory card", "SD", "Card", "1"]
                    for target_value in target_values:
                        try:
                            if target_value in choices:
                                capture_target.set_value(target_value)
                                self.logger.info(f"Configurado capturetarget a: {target_value}")
                                break
                            elif target_value == "1" and len(choices) > 1:
                                capture_target.set_value(choices[1])  # Segunda opción si existe
                                self.logger.info(f"Configurado capturetarget a: {choices[1]} (segunda opción)")
                                break
                        except gp.GPhoto2Error as e:
                            self.logger.debug(f"No se pudo configurar a {target_value}: {e}")
                            continue
                
                # Aplicar configuración
                try:
                    self.camera.set_config(config, self.context)
                    self.logger.info("Configuración de capturetarget aplicada exitosamente")
                except gp.GPhoto2Error as e:
                    self.logger.warning(f"No se pudo aplicar configuración capturetarget: {e}")
                
        except gp.GPhoto2Error as e:
            self.logger.warning(f"No se pudo configurar destino de captura: {e}")
            if not self.use_camera_ram:
                self.logger.warning("Asegúrate de que la cámara tenga una tarjeta SD insertada")
    
    def capture_and_download(self, filename: Optional[str] = None, 
                           delete_from_camera: bool = True) -> Optional[str]:
        """
        Capturar una imagen y descargarla automáticamente.
        
        Args:
            filename (str, optional): Nombre del archivo. Si no se especifica, 
                                    se genera automáticamente con timestamp
            delete_from_camera (bool): Si eliminar la imagen de la cámara después 
                                     de descargarla
        
        Returns:
            str: Ruta completa del archivo descargado, o None si hubo error
        """
        if not self.camera:
            self.logger.error("No hay conexión con la cámara. Llama a connect() primero.")
            return None
        
        try:
            self.logger.info("Iniciando captura de imagen...")
            
            # SOLUCIÓN PARA ERROR "E/S en curso": Esperar eventos antes de capturar
            self.logger.info("Esperando que la cámara esté lista...")
            try:
                # Esperar eventos por 1 segundo para limpiar el buffer
                event_type, event_data = self.camera.wait_for_event(1000, self.context)
                self.logger.debug(f"Evento recibido: {event_type}")
            except gp.GPhoto2Error as e:
                self.logger.debug(f"No hay eventos pendientes: {e}")
            
            # Pequeña pausa adicional para asegurar que la cámara esté lista
            time.sleep(0.5)
            
            # Capturar imagen
            if self.use_camera_ram:
                # Para captura en RAM, usar capture directo y descargar inmediatamente
                file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE, self.context)
                self.logger.info(f"Imagen capturada en RAM: {file_path.folder}/{file_path.name}")
            else:
                # Para captura en SD, usar captura normal
                file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE, self.context)
                self.logger.info(f"Imagen capturada en SD: {file_path.folder}/{file_path.name}")
            
            # Generar nombre de archivo si no se especifica
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                extension = Path(file_path.name).suffix
                filename = f"canon_eos_1500d_{timestamp}{extension}"
            
            # Ruta completa del archivo de destino
            local_path = self.download_folder / filename
            
            # Descargar imagen
            self.logger.info(f"Descargando imagen a: {local_path}")
            camera_file = self.camera.file_get(
                file_path.folder, file_path.name, 
                gp.GP_FILE_TYPE_NORMAL, self.context
            )
            camera_file.save(str(local_path))
            
            # Eliminar de la cámara si se solicita (y no está en RAM)
            if delete_from_camera and not self.use_camera_ram:
                self.logger.info("Eliminando imagen de la cámara...")
                self.camera.file_delete(file_path.folder, file_path.name, self.context)
            elif self.use_camera_ram:
                self.logger.info("Imagen capturada en RAM - se elimina automáticamente")
            
            # Esperar eventos después de la captura para limpiar el buffer
            try:
                event_type, event_data = self.camera.wait_for_event(500, self.context)
                self.logger.debug(f"Evento post-captura: {event_type}")
            except gp.GPhoto2Error:
                pass  # No hay problema si no hay eventos
            
            self.logger.info(f"Imagen descargada exitosamente: {local_path}")
            return str(local_path)
            
        except gp.GPhoto2Error as e:
            self.logger.error(f"Error de gPhoto2 durante captura: {e}")
            if "I/O in progress" in str(e) or "-110" in str(e):
                self.logger.info("Error E/S en curso - intentando limpiar buffer de eventos...")
                try:
                    # Intentar limpiar el buffer de eventos
                    for _ in range(3):
                        event_type, event_data = self.camera.wait_for_event(1000, self.context)
                        self.logger.debug(f"Limpiando evento: {event_type}")
                except gp.GPhoto2Error:
                    pass
                self.logger.info("Buffer limpiado. Intenta capturar de nuevo en unos segundos.")
            return None
        except Exception as e:
            self.logger.error(f"Error inesperado durante captura: {e}")
            return None
    
    def list_files_on_camera(self) -> List[Dict[str, Any]]:
        """
        Listar todos los archivos disponibles en la cámara.
        
        Returns:
            List[Dict]: Lista de archivos con información (folder, name, size, etc.)
        """
        if not self.camera:
            self.logger.error("No hay conexión con la cámara.")
            return []
        
        files = []
        try:
            # Obtener lista de carpetas en la cámara
            folder_list = self.camera.folder_list_folders('/', self.context)
            
            # Recorrer carpetas recursivamente
            self._scan_folder('/', files)
            
            self.logger.info(f"Se encontraron {len(files)} archivos en la cámara")
            return files
            
        except gp.GPhoto2Error as e:
            self.logger.error(f"Error al listar archivos: {e}")
            return []
    
    def _scan_folder(self, folder_path: str, files_list: List[Dict[str, Any]]) -> None:
        """Escanear una carpeta recursivamente para encontrar archivos"""
        try:
            # Listar archivos en la carpeta actual
            file_list = self.camera.folder_list_files(folder_path, self.context)
            for i in range(file_list.count()):
                filename = file_list.get_name(i)
                file_info = self.camera.file_get_info(folder_path, filename, self.context)
                
                files_list.append({
                    'folder': folder_path,
                    'name': filename,
                    'size': file_info.file.size,
                    'mtime': file_info.file.mtime
                })
            
            # Listar subcarpetas y escanear recursivamente
            folder_list = self.camera.folder_list_folders(folder_path, self.context)
            for i in range(folder_list.count()):
                subfolder = folder_list.get_name(i)
                subfolder_path = f"{folder_path.rstrip('/')}/{subfolder}"
                self._scan_folder(subfolder_path, files_list)
                
        except gp.GPhoto2Error as e:
            self.logger.warning(f"No se pudo escanear carpeta {folder_path}: {e}")
    
    def download_file(self, folder: str, filename: str, 
                     local_filename: Optional[str] = None,
                     delete_from_camera: bool = False) -> Optional[str]:
        """
        Descargar un archivo específico de la cámara.
        
        Args:
            folder (str): Carpeta en la cámara donde está el archivo
            filename (str): Nombre del archivo en la cámara
            local_filename (str, optional): Nombre local del archivo
            delete_from_camera (bool): Si eliminar el archivo de la cámara
        
        Returns:
            str: Ruta del archivo descargado, o None si hubo error
        """
        if not self.camera:
            self.logger.error("No hay conexión con la cámara.")
            return None
        
        try:
            # Usar nombre original si no se especifica otro
            if not local_filename:
                local_filename = filename
            
            local_path = self.download_folder / local_filename
            
            self.logger.info(f"Descargando {folder}/{filename} -> {local_path}")
            
            # Obtener archivo de la cámara
            camera_file = self.camera.file_get(
                folder, filename, gp.GP_FILE_TYPE_NORMAL, self.context
            )
            
            # Guardar localmente
            camera_file.save(str(local_path))
            
            # Eliminar de la cámara si se solicita
            if delete_from_camera:
                self.camera.file_delete(folder, filename, self.context)
                self.logger.info("Archivo eliminado de la cámara")
            
            self.logger.info(f"Archivo descargado: {local_path}")
            return str(local_path)
            
        except gp.GPhoto2Error as e:
            self.logger.error(f"Error al descargar archivo: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error inesperado: {e}")
            return None
    
    def get_camera_config(self) -> Optional[Dict[str, Any]]:
        """
        Obtener configuración actual de la cámara.
        
        Returns:
            Dict: Configuración de la cámara o None si hay error
        """
        if not self.camera:
            self.logger.error("No hay conexión con la cámara.")
            return None
        
        try:
            config = self.camera.get_config(self.context)
            return self._config_to_dict(config)
        except gp.GPhoto2Error as e:
            self.logger.error(f"Error al obtener configuración: {e}")
            return None
    
    def _config_to_dict(self, config) -> Dict[str, Any]:
        """Convertir configuración de gphoto2 a diccionario"""
        result = {}
        for i in range(config.count_children()):
            child = config.get_child(i)
            name = child.get_name()
            try:
                value = child.get_value()
                result[name] = value
            except:
                # Si no se puede obtener el valor, intentar recursivamente
                if child.count_children() > 0:
                    result[name] = self._config_to_dict(child)
                else:
                    result[name] = None
        return result
    
    def __enter__(self):
        """Context manager entry"""
        if self.connect():
            return self
        else:
            raise ConnectionError("No se pudo conectar con la cámara")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# ===============================================
# EJEMPLO DE USO
# ===============================================

def main():
    """Ejemplo de uso del controlador Capture"""
    download_folder = "./captured_images"
    
    print("=== DIAGNÓSTICO DE CONEXIÓN ===")
    print("Ejecutando comandos de diagnóstico...")
    
    # Intentar diagnóstico automático
    import subprocess
    
    try:
        print("\n1. Detectando cámaras disponibles:")
        result = subprocess.run(['gphoto2', '--auto-detect'], 
                              capture_output=True, text=True, timeout=10)
        if result.stdout:
            print(result.stdout)
        else:
            print("   No se detectaron cámaras")
            
        print("\n2. Listando puertos USB:")
        result = subprocess.run(['gphoto2', '--list-ports'], 
                              capture_output=True, text=True, timeout=10)
        if result.stdout:
            print(result.stdout)
            
    except subprocess.TimeoutExpired:
        print("   Timeout - puede que la cámara no responda")
    except FileNotFoundError:
        print("   gphoto2 no está instalado en el sistema")
    except Exception as e:
        print(f"   Error ejecutando diagnóstico: {e}")
    
    print("\n=== INTENTANDO CONEXIÓN ===")
    print("¿Tienes tarjeta SD en la cámara? (s/n): ", end="")
    has_sd = input().lower().startswith('s')
    use_ram = not has_sd  # Si no tiene SD, usar RAM
    
    # Intentar con detección automática (puerto None para auto-detectar)
    camera_port = None  # Cambiar a None para auto-detección
    
    try:
        # Usando context manager (recomendado)
        with CaptureController(download_folder, camera_port, use_camera_ram=use_ram) as camera:
            print("=== Información de la cámara ===")
            config = camera.get_camera_config()
            if config:
                print(f"Configuración obtenida: {len(config)} parámetros")
            
            if not use_ram:  # Solo listar archivos si hay SD card
                print("\n=== Archivos en la cámara ===")
                files = camera.list_files_on_camera()
                for file_info in files[:5]:  # Mostrar solo los primeros 5
                    print(f"📁 {file_info['folder']}/{file_info['name']} "
                          f"({file_info['size']} bytes)")
            
            print(f"\n=== Capturando nueva imagen ===")
            modo = "RAM de la cámara" if use_ram else "tarjeta SD"
            print(f"Modo de captura: {modo}")
            
            # Capturar y descargar automáticamente
            captured_file = camera.capture_and_download(
                filename="mi_foto_canon_t7.jpg",
                delete_from_camera=True
            )
            
            if captured_file:
                print(f"✅ Imagen capturada y guardada: {captured_file}")
                print(f"📸 La imagen se capturó en: {modo}")
            else:
                print("❌ Error al capturar imagen")
    
    except ConnectionError as e:
        print(f"❌ Error de conexión: {e}")
        print("\n💡 Sugerencias:")
        print("1. Asegúrate de que la cámara esté encendida")
        print("2. Verifica que esté en modo PTP (no MTP ni Mass Storage)")  
        print("3. Prueba desconectar y reconectar el cable USB")
        print("4. Ejecuta: sudo gphoto2 --auto-detect")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    # Configurar logging para mostrar más información
    logging.basicConfig(level=logging.INFO)
    
    print("Canon T7 Controller - Ejemplo de uso")
    print("=" * 50)
    main()
