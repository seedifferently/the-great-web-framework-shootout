import os, sys
here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here)

from flask_app import app as application
