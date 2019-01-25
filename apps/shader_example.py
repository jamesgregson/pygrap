"""About the simplest PyQt OpenGL example with decent interaction"""


import sys
import numpy

from OpenGL.GL import *
from OpenGL.GLU import *

from graphics.core import Transform
from graphics.opengl import SimpleViewer
from graphics.opengl import Shader

vtx_shader = """
#version 150
 
uniform mat4 modelview;
uniform mat4 projection;
 
in vec3 position;
in vec3 color;
 
out vec3 Color;
 
void main(){
    Color = color;
    gl_Position = projection*modelview*vec4(position,1.0);
}
"""

frg_shader = """
#version 150
 
in vec3 Color;
out vec4 outputF;
 
void main(){
    outputF = vec4( Color.r, Color.g, Color.b, 0.0 );
}
"""

global shader
width = 800
height = 600
aspect = width/height
shader = None

def resize_cb( w, h ):
    width = w
    height = h
    aspect = w/h
    glViewport( 0, 0, width, height )

def initialize_cb():
    global shader
    glEnable(GL_DEPTH_TEST)
    glClearColor( 0.7, 0.7, 1.0, 0.0 )

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    shader = Shader( vtx_shader, frg_shader )
    print( 'Uniforms:')
    print( shader.uniforms() )
    print( ' ' )
    print( 'Attributes:' )
    print( shader.attributes() )

def render_cb():
    global shader
    glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

    projection = Transform().perspective( 45.0, aspect, 0.1, 10.0 )
    modelview = Transform().lookat(1.0,1.0,4.0,0.0,0.0,0.0,0.0,1.0,0.0)

    positions = numpy.array([
        [0.0,0.0,0.0],[1.0,0.0,0.0],
        [0.0,0.0,0.0],[0.0,1.0,0.0],
        [0.0,0.0,0.0],[0.0,0.0,1.0]], dtype=numpy.float32)
    colors = numpy.array([
        [1.0,0.0,0.0],[1.0,0.0,0.0],
        [0.0,1.0,0.0],[0.0,1.0,0.0],
        [0.0,0.0,1.0],[0.0,0.0,1.0]], dtype=numpy.float32 )

    shader.use()
    shader['modelview']  = modelview.matrix()
    shader['projection'] = projection.matrix()

    shader['position']   = positions.ravel()
    shader['color']      = colors.ravel()

    glLineWidth(4.0)

    glDrawArrays( GL_LINES, 0, 6 )

    shader.release()

# create the QApplication
app = SimpleViewer.application()

# set up the display
viewer = SimpleViewer()
viewer.resize_cb.connect( resize_cb )
viewer.initialize_cb.connect( initialize_cb )
viewer.render_cb.connect( render_cb )

# resize the window
viewer.resize( width, height )
viewer.show()

# main loop
try:
    sys.exit(app.exec_())
except SystemExit:
    pass
