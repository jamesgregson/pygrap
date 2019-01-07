"""About the simplest PyQt OpenGL example with decent interaction"""

import sys

from OpenGL.GL import *

from graphics.core import Transform
from graphics.opengl import Application, SimpleViewer, Shader

width = 800
height = 600
aspect = width/height

vertex_shader = """
    uniform mat4 modelview;
    uniform mat4 projection;

    attribute vec3 aPos;
    
    void main(){
        gl_Position = projection*modelview*vec4(aPos, 1.0); // see how we directly give a vec3 to vec4's constructor
    }
"""

fragment_shader = """    
    void main(){
        gl_FragColor = vec4( 1.0, 1.0, 0.0, 0.0 );
    } 
"""

program = None

def resize( w, h ):
    width = w
    height = h
    aspect = w/h
    glViewport( 0, 0, width, height )

def initialize():
    glEnable(GL_DEPTH_TEST)
    glClearColor( 0.7, 0.7, 1.0, 0.0 )

    program = Shader( vertex_shader, fragment_shader )
    program.get_attributes()
    sys.exit(1)

def render():
    glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

    proj  = Transform().perspective(45.0, aspect, 0.1, 10.0 ).matrix()
    model = Transform().lookat( 0.0, 2.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0 ).matrix()

    glMatrixMode( GL_PROJECTION )
    glLoadMatrixf( proj.transpose() )

    glMatrixMode( GL_MODELVIEW )
    glLoadMatrixf( model.transpose() )

    glPointSize(5.0)
    glLineWidth(5.0)
    glBegin(GL_LINES)
    glColor3f(  1.0, 0.0, 0.0 )
    glVertex3f( 1.0, 0.0, 0.0 )
    glVertex3f( 0.0, 0.0, 0.0 )
    glColor3f(  0.0, 1.0, 0.0 )
    glVertex3f( 0.0, 1.0, 0.0 )
    glVertex3f( 0.0, 0.0, 0.0 )
    glColor3f(  0.0, 0.0, 1.0 )
    glVertex3f( 0.0, 0.0, 1.0 )
    glVertex3f( 0.0, 0.0, 0.0 )
    glEnd()

def mouse_move( evt ):
    print('Mouse move {}: [{},{}]'.format(evt.button(),evt.x(),evt.y()) )

def mouse_press( evt ):
    print('Mouse press {}: [{},{}]'.format(evt.button(),evt.x(),evt.y()) )    

def mouse_release( evt ):
    print('Mouse release {}: [{},{}]'.format(evt.button(),evt.x(),evt.y()) )

def key_press( evt ):
    print('Key press {}'.format(evt.key()) )

def key_release( evt ):
    print('Key release {}'.format(evt.key()) )

# create the QApplication
app = Application()

# set up the display
viewer = SimpleViewer()
viewer.resize_cb.connect( resize )
viewer.initialize_cb.connect( initialize )
viewer.render_cb.connect( render )

# keyboard & mouse interactions
viewer.key_press_cb.connect( key_press )
viewer.key_release_cb.connect( key_release )
viewer.mouse_press_cb.connect( mouse_press )
viewer.mouse_release_cb.connect( mouse_release )
viewer.mouse_move_cb.connect( mouse_move )

# resize the window
viewer.resize( width, height )
viewer.show()

# main loop
try:
    sys.exit(app.exec_())
except SystemExit:
    pass
