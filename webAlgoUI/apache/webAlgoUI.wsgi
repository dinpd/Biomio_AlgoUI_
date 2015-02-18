import sys
import os
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_ROOT)
os.chdir('..')
APP_ROOT = os.curdir
os.chdir('..')
activate_this = os.path.join(os.curdir, 'venv', 'bin', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))
sys.path.insert(0, APP_ROOT)
from webAlgoUI.webAlgoUI import app as application
