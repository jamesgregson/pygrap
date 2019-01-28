"""About the simplest PyQt OpenGL example with decent interaction"""


import sys
import numpy

from OpenGL.GL import *
from OpenGL.GLU import *

from graphics.core import Transform
from graphics.opengl import SimpleViewer
from graphics.opengl import Shader

render_vtx_shader = """
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

render_frg_shader = """
#version 150
 
in vec3 Color;
out vec4 outputF;
 
void main(){
    outputF = vec4( Color.r, Color.g, Color.b, 0.0 );
}
"""

select_vtx_shader = """
#version 150

uniform mat4 modelview;
uniform mat4 projection;

in vec3 position;
in float id;

flat out int ID;

void main(){
    ID = int(id+0.5f);
    gl_Position = projection*modelview*vec4(position,1.0);
}
"""

select_frg_shader = """
#version 150

flat in int ID;

out vec4 color;

void main(){
    highp float r = float((ID>>0)&0xff)/255.0f;
    highp float g = float((ID>>8)&0xff)/255.0f;
    highp float b = float((ID>>16)&0xff)/255.0f;
    color = vec4( r, g, b, 0.0 );
}
"""

class State:
    def __init__( self ):
        pass

state = State()
state.width  = 800
state.height = 600
state.aspect = state.width/state.height
state.mouse  = (0,0)

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

    state.positions = numpy.random.standard_normal( size=(5000,3) )
    state.colors    = numpy.random.uniform( size=state.positions.shape )
    state.ids       = numpy.random.randint( low=1, high=2**24-1, size=state.positions.shape[0] )
    state.id_map = { v: k for k,v in enumerate( state.ids ) }

    # the rendering shader
    state.render_shader = Shader( render_vtx_shader, render_frg_shader )
    state.select_shader = Shader( select_vtx_shader, select_frg_shader )

def mouse_move_cb( evt ):
    state.mouse = ( evt.x(), state.height-evt.y() )

def render_cb():
    # camera stuff
    projection = Transform().perspective( 45.0, state.aspect, 0.1, 10.0 )
    modelview = Transform().lookat(4.0,4.0,4.0,0.0,0.0,0.0,0.0,1.0,0.0)

    ## Selection code.
    glClearColor(0.0,0.0,0.0,0.0)
    glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
    state.select_shader.use()
    state.select_shader['modelview']  = modelview.matrix()
    state.select_shader['projection'] = projection.matrix()

    state.select_shader['position'] = state.positions
    state.select_shader['id']       = state.ids

    # draw scene here
    glPointSize( 10.0 )
    glDrawArrays( GL_POINTS, 0, state.positions.shape[0] )
    glFlush()

    # read the pixel under the mouse and convert to an integer,
    # if the result is in the map of ids, mark as selected
    rgb = glReadPixels( state.mouse[0], state.mouse[1], 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, None )
    idx = int(rgb[0]) + int(rgb[1])*256 + int(rgb[2])*65536
    if idx in state.id_map:
        selected = state.id_map[idx]
    else:
        selected = -1

    # Rendering code
    glClearColor( 0.7, 0.7, 1.0, 0.0 )
    glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

    # highlight the selected point in yellow
    tcolors = state.colors.copy()
    if selected >= 0:
        tcolors[selected] = (1.0,1.0,0.0)

    state.render_shader.use()
    state.render_shader['modelview']  = modelview.matrix()
    state.render_shader['projection'] = projection.matrix()

    state.render_shader['position'] = state.positions
    state.render_shader['color'] = tcolors

    glPointSize( 10.0 )
    glDrawArrays( GL_POINTS, 0, state.positions.shape[0] )
    glFlush()



# create the QApplication
app = SimpleViewer.application()

# set up the display
viewer = SimpleViewer()
viewer.resize_cb.connect( resize_cb )
viewer.initialize_cb.connect( initialize_cb )
viewer.mouse_move_cb.connect( mouse_move_cb )
viewer.render_cb.connect( render_cb )

# resize the window
viewer.resize( state.width, state.height )
viewer.show()

# main loop
try:
    sys.exit(app.exec_())
except SystemExit:
    pass
