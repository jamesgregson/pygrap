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
 
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
 
in vec3 in_position;
in vec3 in_normal;

out vec3 position;
out vec3 normal;

void main(){
    vec4 pos  = model*vec4(in_position,1.0);
    vec4 npos = model*vec4(in_position+in_normal,1.0);

    normal      = npos.xyz-pos.xyz;
    position    = pos.xyz;
    gl_Position = projection*view*pos;
}
"""

frg_shader = """
#version 150

// camera position
uniform vec3 camera_pos = vec3(0.0,0.0,0.0);

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
    vec3 view_dir  = normalize(camera_pos-position);
    float spec     = max( 0.0, -dot( reflect(light_dir,frag_nor), view_dir ));
    float cos_theta = max( 0.0, dot( frag_nor, light_dir ) );
    result = diffuse*cos_theta + ambient + specular*pow( spec, spec_exp );
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

    # Shader stuff
    state.shader = Shader( vtx_shader, frg_shader )
    state.shader.use()

    print( 'Uniforms:')
    print( state.shader.uniforms() )
    print( ' ' )
    print( 'Attributes:' )
    print( state.shader.attributes() )

    # view stuff
    state.azimuth   = 0.0
    state.elevation = 0.0

    # load a mesh and materials
    state.mesh, materials = graphics.io.load_obj('{}/cube.obj'.format(graphics.GRAPHICS_DATA_DIR) )
    state.materials = { mat.name: mat for mat in materials }

    # unbind any vertex arrays
    glBindVertexArray(0)


def render_cb():
    state.frame += 1
    glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

    projection = Transform().perspective( 45.0, state.aspect, 0.1, 10.0 )
    view       = Transform().lookat(0.0,0.0,4.0,0.0,0.0,0.0,0.0,1.0,0.0)
    model      = Transform().rotate( state.azimuth, 0.0, 1.0, 0.0 ).rotate( state.elevation, 1.0, 0.0, 0.0 )
    cam_pos    = view.inverse()*(0.0, 0.0, 0.0)

    # enable the shader 
    state.shader.use()

    # view and projection matricies
    state.shader['view']       = view.matrix()
    state.shader['projection'] = projection.matrix()
    state.shader['camera_pos'] = cam_pos

    # world-space lighting
    state.shader['light_pos']  = (1.0,10.0,4.0)

    # per object/material stuff
    state.shader['model']      =  model.matrix()
    state.shader['in_normal']   = state.mesh.normals
    state.shader['in_position'] = state.mesh.vertices

    # draw each material individually with its
    # specific (hacked a bit here) materials
    for matname,(start,end) in state.mesh.material_triangles.items():        
        mat = state.materials[matname]
        state.shader['diffuse']  = mat.diffuse
        state.shader['ambient']  = mat.diffuse*0.25
        state.shader['specular'] = (1.0,1.0,1.0)
        state.shader['spec_exp'] = 70.0
        glDrawArrays( GL_TRIANGLES, start*3, (end-start)*3 )

def mouse_move_cb( evt ):
    state.azimuth = evt.x()
    state.elevation = evt.y()


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
