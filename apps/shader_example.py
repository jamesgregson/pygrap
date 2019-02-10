"""About the simplest PyQt OpenGL example with decent interaction"""


import sys
import numpy

from OpenGL.GL import *
from OpenGL.GLU import *

import graphics
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

class State:
    def __init__( self ):
        pass

state = State()
state.width  = 800
state.height = 600
state.aspect = state.width/state.height
state.frame  = 0

def resize_cb( w, h ):
    state.width = w
    state.height = h
    state.aspect = w/h
    glViewport( 0, 0, state.width, state.height )

def initialize_cb():
    glEnable(GL_DEPTH_TEST)
    glClearColor( 0.7, 0.7, 1.0, 0.0 )

    state.vao = glGenVertexArrays(1)
    glBindVertexArray( state.vao )

    state.shader = Shader( vtx_shader, frg_shader )
    print( 'Uniforms:')
    print( state.shader.uniforms() )
    print( ' ' )
    print( 'Attributes:' )
    print( state.shader.attributes() )

    positions = numpy.array([
        [0.0,0.0,0.0],[1.0,0.0,0.0],
        [0.0,0.0,0.0],[0.0,1.0,0.0],
        [0.0,0.0,0.0],[0.0,0.0,1.0]], dtype=numpy.float32)
    colors = numpy.array([
        [1.0,0.0,0.0],[1.0,0.0,0.0],
        [0.0,1.0,0.0],[0.0,1.0,0.0],
        [0.0,0.0,1.0],[0.0,0.0,1.0]], dtype=numpy.float32 )

    state.shader.use()
    state.shader['position']   = positions.ravel()
    state.shader['color']      = colors.ravel()

    # load a mesh and materials
    state.mesh, materials = graphics.io.load_obj('{}/cube.obj'.format(graphics.GRAPHICS_DATA_DIR) )
    state.materials = { mat.name: mat for mat in materials }

    glBindVertexArray(0)


def render_cb():
    state.frame += 1
    glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

    projection = Transform().lookat(1.0,-1.0,4.0,0.0,0.0,0.0,0.0,1.0,0.0).perspective( 45.0, state.aspect, 0.1, 10.0 )
    modelview  = Transform().rotate( state.frame, 0.0, 1.0, 0.0 )

    state.shader.use()
    state.shader['modelview']  = modelview.matrix()
    state.shader['projection'] = projection.matrix()

    state.shader['position'] = state.mesh.vertices
    for matname,(start,end) in state.mesh.material_triangles.items():        
        mat = state.materials[matname]
        state.shader['color'] = mat.diffuse
        glDrawArrays( GL_TRIANGLES, start*3, (end-start)*3 )


# create the QApplication
app = SimpleViewer.application()

# set up the display
viewer = SimpleViewer()
viewer.resize_cb.connect( resize_cb )
viewer.initialize_cb.connect( initialize_cb )
viewer.render_cb.connect( render_cb )

# resize the window
viewer.resize( state.width, state.height )
viewer.show()

# main loop
try:
    sys.exit(app.exec_())
except SystemExit:
    pass
