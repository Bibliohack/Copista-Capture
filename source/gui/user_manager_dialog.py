#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import getpass
import hashlib
from datetime import datetime
import platform

class UserManager:
    def __init__(self, parent=None, data_file="users.json"):
        self.parent = parent
        self.data_file = data_file
        self.current_user = None
        self.users_data = {}
        
        # Información del usuario del sistema
        self.system_user = getpass.getuser()
        self.system_name = self._get_system_display_name()
        
        # Cargar datos existentes
        self.load_users_data()
        
        # Crear ventana si no hay parent
        if parent is None:
            self.root = tk.Tk()
            self.root.title("Gestión de Usuarios")
        else:
            self.root = tk.Toplevel(parent)
            self.root.title("Gestión de Usuarios")
            self.root.transient(parent)
            self.root.grab_set()
        
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.center_window()
        
        # Estado de la interfaz
        self.current_view = "login"
        
        # Crear interfaz
        self.create_widgets()
        self.show_login_view()
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"400x500+{x}+{y}")
    
    def _get_system_display_name(self):
        """Obtener nombre de display del usuario del sistema"""
        try:
            if platform.system() == "Linux":
                # Intentar obtener el nombre real del usuario
                import pwd
                user_info = pwd.getpwnam(self.system_user)
                full_name = user_info.pw_gecos.split(',')[0]
                return full_name if full_name else self.system_user.title()
            else:
                return self.system_user.title()
        except:
            return self.system_user.title()
    
    def load_users_data(self):
        """Cargar datos de usuarios desde archivo JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.users_data = json.load(f)
            else:
                self.users_data = {}
        except Exception as e:
            print(f"Error cargando usuarios: {e}")
            self.users_data = {}
    
    def save_users_data(self):
        """Guardar datos de usuarios a archivo JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.users_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando usuarios: {e}")
            return False
    
    def hash_password(self, password):
        """Hash simple de contraseña (no seguro para producción)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_widgets(self):
        """Crear widgets principales"""
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        self.title_label = ttk.Label(self.main_frame, text="", font=('Arial', 16, 'bold'))
        self.title_label.pack(pady=(0, 20))
        
        # Frame de contenido (se cambiará según la vista)
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
    
    def clear_content(self):
        """Limpiar contenido actual"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_login_view(self):
        """Mostrar vista de login"""
        self.current_view = "login"
        self.clear_content()
        self.title_label.config(text="Iniciar Sesión")
        
        # Opción 1: Usuario del sistema
        system_frame = ttk.LabelFrame(self.content_frame, text="Acceso Rápido")
        system_frame.pack(fill=tk.X, pady=(0, 20))
        
        system_info = ttk.Label(
            system_frame, 
            text=f"Usuario actual: {self.system_name}\n({self.system_user})",
            justify=tk.CENTER
        )
        system_info.pack(pady=10)
        
        system_button = ttk.Button(
            system_frame,
            text="Ingresar como Usuario del Sistema",
            command=self.login_as_system_user
        )
        system_button.pack(pady=(0, 10))
        
        # Separador
        ttk.Separator(self.content_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Opción 2: Login con cuenta personalizada
        login_frame = ttk.LabelFrame(self.content_frame, text="Cuenta Personalizada")
        login_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Usuario
        ttk.Label(login_frame, text="Usuario:").pack(anchor='w', pady=(10, 5))
        self.login_username = ttk.Entry(login_frame, width=30)
        self.login_username.pack(fill=tk.X, padx=5)
        
        # Contraseña
        ttk.Label(login_frame, text="Contraseña:").pack(anchor='w', pady=(10, 5))
        self.login_password = ttk.Entry(login_frame, show="*", width=30)
        self.login_password.pack(fill=tk.X, padx=5)
        self.login_password.bind('<Return>', lambda e: self.login_user())
        
        # Botones
        button_frame = ttk.Frame(login_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Iniciar Sesión", command=self.login_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Crear Cuenta", command=self.show_register_view).pack(side=tk.LEFT)
        
        # Lista de usuarios existentes (para desarrollo/debug)
        if self.users_data:
            users_frame = ttk.LabelFrame(self.content_frame, text="Usuarios Registrados")
            users_frame.pack(fill=tk.X, pady=(10, 0))
            
            users_list = ", ".join(self.users_data.keys())
            ttk.Label(users_frame, text=users_list, foreground='gray').pack(pady=5)
    
    def show_register_view(self):
        """Mostrar vista de registro"""
        self.current_view = "register"
        self.clear_content()
        self.title_label.config(text="Crear Cuenta")
        
        # Campos de registro
        ttk.Label(self.content_frame, text="Nombre de usuario:").pack(anchor='w', pady=(0, 5))
        self.reg_username = ttk.Entry(self.content_frame, width=30)
        self.reg_username.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.content_frame, text="Nombre completo:").pack(anchor='w', pady=(0, 5))
        self.reg_fullname = ttk.Entry(self.content_frame, width=30)
        self.reg_fullname.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.content_frame, text="Email (opcional):").pack(anchor='w', pady=(0, 5))
        self.reg_email = ttk.Entry(self.content_frame, width=30)
        self.reg_email.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.content_frame, text="Contraseña:").pack(anchor='w', pady=(0, 5))
        self.reg_password = ttk.Entry(self.content_frame, show="*", width=30)
        self.reg_password.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.content_frame, text="Confirmar contraseña:").pack(anchor='w', pady=(0, 5))
        self.reg_password_confirm = ttk.Entry(self.content_frame, show="*", width=30)
        self.reg_password_confirm.pack(fill=tk.X, pady=(0, 20))
        self.reg_password_confirm.bind('<Return>', lambda e: self.register_user())
        
        # Botones
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Crear Cuenta", command=self.register_user).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancelar", command=self.show_login_view).pack(side=tk.LEFT)
    
    def show_profile_view(self):
        """Mostrar vista de perfil/gestión"""
        self.current_view = "profile"
        self.clear_content()
        self.title_label.config(text=f"Perfil de {self.current_user['display_name']}")
        
        # Información del usuario
        info_frame = ttk.LabelFrame(self.content_frame, text="Información del Usuario")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        info_text = f"""
Usuario: {self.current_user['username']}
Nombre: {self.current_user['display_name']}
Email: {self.current_user.get('email', 'No especificado')}
Tipo: {self.current_user['type']}
Último acceso: {self.current_user['last_login']}
        """.strip()
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(pady=10, padx=10)
        
        # Opciones de gestión
        if self.current_user['type'] == 'custom':
            # Solo usuarios personalizados pueden editar perfil
            edit_frame = ttk.LabelFrame(self.content_frame, text="Editar Perfil")
            edit_frame.pack(fill=tk.X, pady=(0, 20))
            
            ttk.Label(edit_frame, text="Nombre completo:").pack(anchor='w', pady=(10, 5))
            self.edit_fullname = ttk.Entry(edit_frame, width=30)
            self.edit_fullname.pack(fill=tk.X, padx=10)
            self.edit_fullname.insert(0, self.current_user['display_name'])
            
            ttk.Label(edit_frame, text="Email:").pack(anchor='w', pady=(10, 5))
            self.edit_email = ttk.Entry(edit_frame, width=30)
            self.edit_email.pack(fill=tk.X, padx=10)
            self.edit_email.insert(0, self.current_user.get('email', ''))
            
            ttk.Button(edit_frame, text="Guardar Cambios", command=self.save_profile_changes).pack(pady=10)
        
        # Botones de acción
        action_frame = ttk.Frame(self.content_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="Cerrar Sesión", command=self.logout).pack(side=tk.LEFT)
        
        if self.parent:
            ttk.Button(action_frame, text="Continuar", command=self.close_manager).pack(side=tk.RIGHT)
    
    def login_as_system_user(self):
        """Iniciar sesión como usuario del sistema"""
        username = f"system_{self.system_user}"
        
        # Crear o actualizar usuario del sistema
        if username not in self.users_data:
            self.users_data[username] = {
                'username': username,
                'display_name': self.system_name,
                'email': '',
                'type': 'system',
                'created': datetime.now().isoformat(),
                'last_login': datetime.now().isoformat()
            }
        else:
            self.users_data[username]['last_login'] = datetime.now().isoformat()
        
        self.current_user = self.users_data[username]
        self.save_users_data()
        self.close_manager()
        #self.show_profile_view()
    
    def login_user(self):
        """Iniciar sesión con usuario personalizado"""
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        if username not in self.users_data:
            messagebox.showerror("Error", "Usuario no encontrado")
            return
        
        user_data = self.users_data[username]
        if user_data.get('password_hash') != self.hash_password(password):
            messagebox.showerror("Error", "Contraseña incorrecta")
            return
        
        # Login exitoso
        user_data['last_login'] = datetime.now().isoformat()
        self.current_user = user_data
        self.save_users_data()
        
        self.show_profile_view()
    
    def register_user(self):
        """Registrar nuevo usuario"""
        username = self.reg_username.get().strip()
        fullname = self.reg_fullname.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_password.get()
        password_confirm = self.reg_password_confirm.get()
        
        # Validaciones
        if not username or not fullname or not password:
            messagebox.showerror("Error", "Por favor complete los campos obligatorios")
            return
        
        if password != password_confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        if username in self.users_data:
            messagebox.showerror("Error", "El usuario ya existe")
            return
        
        # Crear usuario
        self.users_data[username] = {
            'username': username,
            'display_name': fullname,
            'email': email,
            'password_hash': self.hash_password(password),
            'type': 'custom',
            'created': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat()
        }
        
        if self.save_users_data():
            self.current_user = self.users_data[username]
            messagebox.showinfo("Éxito", "Cuenta creada exitosamente")
            self.show_profile_view()
    
    def save_profile_changes(self):
        """Guardar cambios del perfil"""
        if self.current_user['type'] != 'custom':
            return
        
        new_fullname = self.edit_fullname.get().strip()
        new_email = self.edit_email.get().strip()
        
        if not new_fullname:
            messagebox.showerror("Error", "El nombre no puede estar vacío")
            return
        
        # Actualizar datos
        self.current_user['display_name'] = new_fullname
        self.current_user['email'] = new_email
        
        username = self.current_user['username']
        self.users_data[username] = self.current_user
        
        if self.save_users_data():
            messagebox.showinfo("Éxito", "Perfil actualizado correctamente")
            self.show_profile_view()  # Refrescar vista
    
    def logout(self):
        """Cerrar sesión"""
        self.current_user = None
        self.show_login_view()
    
    def close_manager(self):
        """Cerrar el gestor de usuarios"""
        if self.parent:
            self.root.grab_release()
        self.root.destroy()
    
    def get_current_user(self):
        """Obtener usuario actual (para usar desde la aplicación principal)"""
        return self.current_user
    
    def show(self):
        """Mostrar el gestor y retornar usuario autenticado"""
        if self.parent is None:
            self.root.mainloop()
        else:
            self.root.wait_window()
        return self.current_user

# Función de conveniencia para usar desde otras aplicaciones
def authenticate_user(parent=None, data_file="users.json"):
    """
    Función simple para autenticar usuario.
    Retorna información del usuario autenticado o None si se cancela.
    """
    manager = UserManager(parent, data_file)
    return manager.show()

# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo 1: Usar como aplicación independiente
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    user = authenticate_user()
    
    if user:
        print(f"Usuario autenticado: {user['display_name']} ({user['username']})")
        
        # Crear ventana principal de la aplicación
        root.deiconify()
        root.title("Mi Aplicación")
        
        welcome_label = ttk.Label(root, text=f"Bienvenido, {user['display_name']}!", 
                                 font=('Arial', 16))
        welcome_label.pack(pady=50)
        
        root.mainloop()
    else:
        print("Autenticación cancelada")

# Función para integrar con tu ImageViewer
def integrate_with_image_viewer():
    """
    Ejemplo de cómo integrar con tu ImageViewer
    """
    return '''
    # En el __init__ de tu ImageViewer, antes de crear la interfaz:
    
    def __init__(self, root):
        self.root = root
        
        # Autenticar usuario
        self.current_user = authenticate_user(self.root, "image_viewer_users.json")
        
        if not self.current_user:
            # Si cancela la autenticación, cerrar aplicación
            self.root.quit()
            return
        
        # Actualizar título con nombre de usuario
        self.root.title(f"Visor de Imágenes - Usuario: {self.current_user['display_name']}")
        
        # Continuar con la inicialización normal...
        self.bundles = []
        # etc...
    '''
