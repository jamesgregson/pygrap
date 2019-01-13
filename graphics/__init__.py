import os

GRAPHICS_DATA_DIR = os.path.abspath('{}/../data'.format(os.path.dirname(__file__)))

from graphics.io import *
from graphics.core import *
from graphics.geometry import *
from graphics.appearance import *
from graphics.opengl import *