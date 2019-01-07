import ctypes
from OpenGL.GL import *

def _glGetActiveAttrib(program, index):
    bufsize = 256
    length = (ctypes.c_int*1)()
    size = (ctypes.c_int*1)()
    type = (ctypes.c_uint*1)()
    name = ctypes.create_string_buffer(bufsize)
    # pyopengl has a bug, this is a patch
    glGetActiveAttrib(program, index, bufsize, length, size, type, name)
    name = name[:length[0]].decode('utf-8')
    return name, size[0], type[0]

class Shader(object):
    """ Helper class for using GLSL shader programs

    adapted from: https://gist.github.com/deepankarsharma/3494203
    """
    def __init__(self, vertex, fragment):
        """
        Parameters
        ----------
        vertex : str
            String containing shader source code for the vertex
            shader
        fragment : str
            String containing shader source code for the fragment
            shader
        """
        self.program_id = glCreateProgram()
        vs_id = self.add_shader(vertex, GL_VERTEX_SHADER)
        frag_id = self.add_shader(fragment, GL_FRAGMENT_SHADER)

        self.attributes = {}
        self.uniforms = {}

        glAttachShader(self.program_id, vs_id)
        glAttachShader(self.program_id, frag_id)
        glLinkProgram(self.program_id)

        if glGetProgramiv(self.program_id, GL_LINK_STATUS) != GL_TRUE:
            info = glGetProgramInfoLog(self.program_id)
            glDeleteProgram(self.program_id)
            glDeleteShader(vs_id)
            glDeleteShader(frag_id)
            raise RuntimeError('Error linking program: %s' % (info))
        glDeleteShader(vs_id)
        glDeleteShader(frag_id)

    def add_shader(self, source, shader_type):
        """ Helper function for compiling a GLSL shader
        Parameters
        ----------
        source : str
            String containing shader source code
        shader_type : valid OpenGL shader type
            Type of shader to compile
        Returns
        -------
        value : int
            Identifier for shader if compilation is successful
        """
        try:
            shader_id = glCreateShader(shader_type)
            glShaderSource(shader_id, source)
            glCompileShader(shader_id)
            if glGetShaderiv(shader_id, GL_COMPILE_STATUS) != GL_TRUE:
                info = glGetShaderInfoLog(shader_id)
                raise RuntimeError('Shader compilation failed: %s' % (info))
            return shader_id
        except:
            glDeleteShader(shader_id)
            raise

    def get_attributes(self):
        count = glGetProgramiv( self.program_id, GL_ACTIVE_ATTRIBUTES )
        for i in range(count):
            ret = _glGetActiveAttrib( self.program_id, i )
            if ret[2] == GL_FLOAT_VEC3:
                print('Vec3')
            print( ret )

    def uniform_location(self, name):
        """ Helper function to get location of an OpenGL uniform variable
        Parameters
        ----------
        name : str
            Name of the variable for which location is to be returned
        Returns
        -------
        value : int
            Integer describing location
        """
        return glGetUniformLocation(self.program_id, name)

    def attribute_location(self, name):
        """ Helper function to get location of an OpenGL attribute variable
        Parameters
        ----------
        name : str
            Name of the variable for which location is to be returned
        Returns
        -------
        value : int
            Integer describing location
        """
        return glGetAttribLocation(self.program_id, name)