# Config file
import os, sys
from sys import getwindowsversion


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


FILE_PATHS = {'INI': resource_path('dependencies\\initialization.ini'),
              'MAIN_UI': resource_path('ui_elements\\main.ui'),
              'SPLASH_UI': resource_path('ui_elements\\splash_screen.ui'),
              '1D_DATA': resource_path('data\\1D\\')
              }
