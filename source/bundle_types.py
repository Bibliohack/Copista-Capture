#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import os

from gui.image_display_widget import create_default_image_display

class BundleGeneric:
    def create_bundle(self, bundle_content, app):
        pass
        
    def create_display(self, bundle_content, app):
        """Crear el display para un bundle genérico"""
        images = bundle_content.get('images', [])
        num_images = len(images)
        # Crear solo los displays necesarios según cantidad de imágenes
        for i in range(num_images):
            image_path = os.path.join(app.current_project.directory, images[i])
            display_frame = ttk.Frame(app.images_frame)
            display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            create_default_image_display(app, display_frame, image_path)
