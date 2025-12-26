#!/usr/bin/env python3

import json
import os

from gui.digitization_dialog import launch_digitization_app_dialog
# from cli_utils import CopistaCli

class Copista:
    def __init__(self, settings):
        self.settings = settings

    def launch_gui(self):
        launch_digitization_app_dialog(self.settings)
    
def load_settings():
    # declara dict con valores por defecto
    default_settings = {
        'copista_folder' : '../config/',
        'base_projects_folder' : '../example_projects/'
    }
    # determina donde estan los archivos de configuracion
    # cargar algun archivo de configuracion maestro si hace falta con
    # valores que sean generales a todas las utilidades de copista   
    settings = default_settings
    return settings

def main():
    app = Copista(load_settings())
    app.launch_gui()

if __name__ == "__main__":
    main()
