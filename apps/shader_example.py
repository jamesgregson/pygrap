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
 
in vec3 in_position;
in vec3 in_normal;

out vec3 position;
out vec3 normal;

void main(){
    vec4 pos  = modelview*vec4(in_position,1.0);
    vec4 npos = modelview*vec4(in_position+in_normal,1.0);

    normal      = npos.xyz-pos.xyz;
    position    = pos.xyz;
    gl_Position = projection*pos;
}
"""

frg_shader = """
#version 150

// lighting information
uniform vec3  light_pos = vec3(10.0,10.0,10.0);
uniform vec3  diffuse   = vec3(1.0,1.0,1.0);
uniform vec3  ambient   = vec3(0.0,0.0,0.0);
uniform vec3  specular  = vec3(0.0,0.0,0.0);
uniform float spec_exp  = 10.0;

// geometry
in vec3 normal;
in vec3 position;

// output fragment color
out vec3 result;
 
void main(){
    vec3 frag_nor  = normalize(normal);
    vec3 light_dir = normalize(light_pos-position);
    float cos_theta = max( 0.0, dot( frag_nor, light_dir ) );
    result = diffuse*cos_theta + ambient + specular*pow( cos_theta, spec_exp );
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

    # Useful?
    # state.vao = glGenVertexArrays(1)
    # glBindVertexArray( state.vao )

    state.shader = Shader( vtx_shader, frg_shader )
    state.shader.use()

    print( 'Uniforms:')
    print( state.shader.uniforms() )
    print( ' ' )
    print( 'Attributes:' )
    print( state.shader.attributes() )

    # load a mesh and materials
    state.mesh, materials = graphics.io.load_obj('{}/cube.obj'.format(graphics.GRAPHICS_DATA_DIR) )
    state.materials = { mat.name: mat for mat in materials }

    glBindVertexArray(0)


def render_cb():
    state.frame += 1
    glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

    projection = Transform().lookat(1.0,2.0,4.0,0.0,0.0,0.0,0.0,1.0,0.0).perspective( 45.0, state.aspect, 0.1, 10.0 )
    modelview  = Transform().rotate( state.frame, 0.0, 1.0, 0.0 )

    # 
    state.shader.use()
    state.shader['modelview']  = modelview.matrix()
    state.shader['projection'] = projection.matrix()

    state.shader['light_pos'] = (1.0,1.0,4.0)

    state.shader['in_normal']   = state.mesh.normals
    state.shader['in_position'] = state.mesh.vertices
    for matname,(start,end) in state.mesh.material_triangles.items():        
        mat = state.materials[matname]
        state.shader['diffuse']  = mat.diffuse
        state.shader['ambient']  = (0.1,0.1,0.1)
        state.shader['specular'] = (0.3,0.3,0.3)
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
