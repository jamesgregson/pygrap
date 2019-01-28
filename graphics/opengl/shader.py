import ctypes
import numpy
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
    def __init__(self, vertex, fragment):
        self.program_id = glCreateProgram()
        vs_id = self.add_shader(vertex, GL_VERTEX_SHADER)
        frag_id = self.add_shader(fragment, GL_FRAGMENT_SHADER)

        glAttachShader(self.program_id, vs_id)
        glAttachShader(self.program_id, frag_id)
        glLinkProgram(self.program_id)

        if glGetProgramiv(self.program_id, GL_LINK_STATUS) != GL_TRUE:
            info = glGetProgramInfoLog(self.program_id)
            glDeleteProgram(self.program_id)
            glDeleteShader(vs_id)
            glDeleteShader(frag_id)
            raise RuntimeError('Error linking program: %s' % (info))

        info = glGetProgramInfoLog(self.program_id)
        print( info )

        glDeleteShader(vs_id)
        glDeleteShader(frag_id)

        self.__glattributes = self.__get_glattributes()
        self.__gluniforms   = self.__get_gluniforms()

        self.__vbos = {}
        for attr in self.__glattributes:
            self.__vbos[attr] = glGenBuffers(1)

    def add_shader(self, source, shader_type):
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

    def use( self ):
        glUseProgram( self.program_id )

    def release( self ):
        glUseProgram( 0 )

    def uniforms(self):
        return self.__gluniforms

    def attributes(self):
        return self.__glattributes

    def __setitem__( self, key, val ):
        if key in self.__gluniforms:
            uni = self.__gluniforms[key]
            if uni[-1] in SHADER_MATRIX_TYPES:
                SHADER_UNIFORM_FUNC[uni[-1]]( 
                    glGetUniformLocation(self.program_id,key), 
                    uni[1],
                    True, # transpose from row to column major
                    val.ravel() )
            else:
                SHADER_UNIFORM_FUNC[uni[-1]](
                    glGetUniformLocation(self.program_id,key),
                    uni[1],
                    val.ravel().astype(uni[2]) )
        elif key in self.__glattributes:
            attr = self.__glattributes[key]
            loc  = glGetAttribLocation(self.program_id,key)
            if len(val) == attr[0]:
                SHADER_ATTRIBUTE_FUNC[attr[-1]](
                    loc, val
                )
            else:
                glBindBuffer(GL_ARRAY_BUFFER, self.__vbos[key])
                glBufferData( GL_ARRAY_BUFFER, val.itemsize*val.size, val.astype(attr[2]), GL_STATIC_DRAW )
                glVertexAttribPointer( loc, attr[0], SHADER_GLTYPE[attr[-1]], GL_FALSE, 0, None )
                glEnableVertexAttribArray( loc )


    def __get_gluniforms( self ):
        results = {}
        num_uniforms = glGetProgramiv( self.program_id, GL_ACTIVE_UNIFORMS )
        for i in range(num_uniforms):
            name, size, vtype = glGetActiveUniform( self.program_id, i )
            results[name.decode('utf-8')] = (SHADER_COMPONENTS[vtype],size,SHADER_TYPE[vtype],vtype)
        return results

    def __get_glattributes( self ):
        def active_attributes( program, index ):
            bufsize = 256
            length = (ctypes.c_int*1)()
            size = (ctypes.c_int*1)()
            type = (ctypes.c_uint*1)()
            name = ctypes.create_string_buffer(bufsize)
            # pyopengl has a bug, this is a patch
            glGetActiveAttrib(program, index, bufsize, length, size, type, name)
            name = name[:length[0]].decode('utf-8')
            return name, size[0], type[0]

        results = {}
        num_attribs = glGetProgramiv( self.program_id, GL_ACTIVE_ATTRIBUTES )
        for i in range(num_attribs):
            name, size, vtype = active_attributes( self.program_id, i )
            results[name] = (SHADER_COMPONENTS[vtype],size,SHADER_TYPE[vtype],vtype)
        return results

    def uniform_location(self, name):
        return glGetUniformLocation(self.program_id, name)

    def attribute_location(self, name):
        return glGetAttribLocation(self.program_id, name)

SHADER_UNIFORM_FUNC = {
    GL_FLOAT:               glUniform1fv,
    GL_FLOAT_VEC2:          glUniform2fv,
    GL_FLOAT_VEC3:          glUniform3fv,
    GL_FLOAT_VEC4:          glUniform4fv,
    GL_DOUBLE:              glUniform1dv,
    GL_DOUBLE_VEC2:         glUniform2dv,
    GL_DOUBLE_VEC3:         glUniform3dv,
    GL_DOUBLE_VEC4:         glUniform4dv,
    GL_INT:                 glUniform1iv,
    GL_INT_VEC2:            glUniform2iv,
    GL_INT_VEC3:            glUniform3iv,
    GL_INT_VEC4:            glUniform4iv,
    GL_UNSIGNED_INT:        glUniform1uiv,
    GL_UNSIGNED_INT_VEC2:   glUniform2uiv,
    GL_UNSIGNED_INT_VEC3:   glUniform3uiv,
    GL_UNSIGNED_INT_VEC4:   glUniform4uiv,
    # GL_BOOL:                None,
    # GL_BOOL_VEC2:           None,
    # GL_BOOL_VEC3:           None,
    # GL_BOOL_VEC4:           None,
    GL_FLOAT_MAT2:          glUniformMatrix2fv,
    GL_FLOAT_MAT3:          glUniformMatrix3fv,
    GL_FLOAT_MAT4:          glUniformMatrix4fv,
    GL_FLOAT_MAT2x3:        glUniformMatrix2x3fv,
    GL_FLOAT_MAT3x2:        glUniformMatrix3x2fv,
    GL_FLOAT_MAT4x2:        glUniformMatrix4x2fv,
    GL_FLOAT_MAT2x4:        glUniformMatrix2x4fv,
    GL_FLOAT_MAT4x3:        glUniformMatrix4x3fv,
    GL_FLOAT_MAT3x4:        glUniformMatrix3x4fv,

    GL_FLOAT_MAT2:          glUniformMatrix2fv,
    GL_FLOAT_MAT3:          glUniformMatrix3fv,
    GL_FLOAT_MAT4:          glUniformMatrix4fv,
    GL_FLOAT_MAT2x3:        glUniformMatrix2x3fv,
    GL_FLOAT_MAT3x2:        glUniformMatrix3x2fv,
    GL_FLOAT_MAT4x2:        glUniformMatrix4x2fv,
    GL_FLOAT_MAT2x4:        glUniformMatrix2x4fv,
    GL_FLOAT_MAT4x3:        glUniformMatrix4x3fv,
    GL_FLOAT_MAT3x4:        glUniformMatrix3x4fv,

    GL_SAMPLER_1D:          glUniform1iv,
    GL_SAMPLER_2D:          glUniform1iv,
    GL_SAMPLER_3D:          glUniform1iv
}

SHADER_ATTRIBUTE_FUNC = {
    GL_FLOAT:               glVertexAttrib1fv,
    GL_FLOAT_VEC2:          glVertexAttrib2fv,
    GL_FLOAT_VEC3:          glVertexAttrib3fv,
    GL_FLOAT_VEC4:          glVertexAttrib4fv,
    GL_DOUBLE:              glVertexAttrib1dv,
    GL_DOUBLE_VEC2:         glVertexAttrib2dv,
    GL_DOUBLE_VEC3:         glVertexAttrib3dv,
    GL_DOUBLE_VEC4:         glVertexAttrib4dv,
    # # GL_INT:                 None,
    # # GL_INT_VEC2:            glUniform2iv,
    # # GL_INT_VEC3:            glUniform3iv,
    # # GL_INT_VEC4:            glUniform4iv,
    # # GL_UNSIGNED_INT:        glUniform1uiv,
    # # GL_UNSIGNED_INT_VEC2:   glUniform2uiv,
    # # GL_UNSIGNED_INT_VEC3:   glUniform3uiv,
    # # GL_UNSIGNED_INT_VEC4:   glUniform4uiv,
    # # # GL_BOOL:                None,
    # # # GL_BOOL_VEC2:           None,
    # # # GL_BOOL_VEC3:           None,
    # # # GL_BOOL_VEC4:           None,
    # # GL_FLOAT_MAT2:          glUniformMatrix2fv,
    # # GL_FLOAT_MAT3:          glUniformMatrix3fv,
    # # GL_FLOAT_MAT4:          glUniformMatrix4fv,
    # # GL_FLOAT_MAT2x3:        glUniformMatrix2x3fv,
    # # GL_FLOAT_MAT3x2:        glUniformMatrix3x2fv,
    # # GL_FLOAT_MAT4x2:        glUniformMatrix4x2fv,
    # # GL_FLOAT_MAT2x4:        glUniformMatrix2x4fv,
    # # GL_FLOAT_MAT4x3:        glUniformMatrix4x3fv,
    # # GL_FLOAT_MAT3x4:        glUniformMatrix3x4fv,

    # # GL_FLOAT_MAT2:          glUniformMatrix2fv,
    # # GL_FLOAT_MAT3:          glUniformMatrix3fv,
    # # GL_FLOAT_MAT4:          glUniformMatrix4fv,
    # # GL_FLOAT_MAT2x3:        glUniformMatrix2x3fv,
    # # GL_FLOAT_MAT3x2:        glUniformMatrix3x2fv,
    # # GL_FLOAT_MAT4x2:        glUniformMatrix4x2fv,
    # # GL_FLOAT_MAT2x4:        glUniformMatrix2x4fv,
    # # GL_FLOAT_MAT4x3:        glUniformMatrix4x3fv,
    # # GL_FLOAT_MAT3x4:        glUniformMatrix3x4fv,

    # GL_SAMPLER_1D:          glUniform1iv,
    # GL_SAMPLER_2D:          glUniform1iv,
    # GL_SAMPLER_3D:          glUniform1iv
}

SHADER_GLTYPE = {
    GL_FLOAT:               GL_FLOAT,
    GL_FLOAT_VEC2:          GL_FLOAT,
    GL_FLOAT_VEC3:          GL_FLOAT,
    GL_FLOAT_VEC4:          GL_FLOAT,
    GL_DOUBLE:              GL_DOUBLE,
    GL_DOUBLE_VEC2:         GL_DOUBLE,
    GL_DOUBLE_VEC3:         GL_DOUBLE,
    GL_DOUBLE_VEC4:         GL_DOUBLE,
    GL_INT:                 GL_INT,
    GL_INT_VEC2:            GL_INT,
    GL_INT_VEC3:            GL_INT,
    GL_INT_VEC4:            GL_INT,
    GL_UNSIGNED_INT:        GL_UNSIGNED_INT,
    GL_UNSIGNED_INT_VEC2:   GL_UNSIGNED_INT,
    GL_UNSIGNED_INT_VEC3:   GL_UNSIGNED_INT,
    GL_UNSIGNED_INT_VEC4:   GL_UNSIGNED_INT,
    # GL_BOOL:                None,
    # GL_BOOL_VEC2:           None,
    # GL_BOOL_VEC3:           None,
    # GL_BOOL_VEC4:           None,
    # GL_FLOAT_MAT2:          glUniformMatrix2fv,
    # GL_FLOAT_MAT3:          glUniformMatrix3fv,
    # GL_FLOAT_MAT4:          glUniformMatrix4fv,
    # GL_FLOAT_MAT2x3:        glUniformMatrix2x3fv,
    # GL_FLOAT_MAT3x2:        glUniformMatrix3x2fv,
    # GL_FLOAT_MAT4x2:        glUniformMatrix4x2fv,
    # GL_FLOAT_MAT2x4:        glUniformMatrix2x4fv,
    # GL_FLOAT_MAT4x3:        glUniformMatrix4x3fv,
    # GL_FLOAT_MAT3x4:        glUniformMatrix3x4fv,

    # GL_FLOAT_MAT2:          glUniformMatrix2fv,
    # GL_FLOAT_MAT3:          glUniformMatrix3fv,
    # GL_FLOAT_MAT4:          glUniformMatrix4fv,
    # GL_FLOAT_MAT2x3:        glUniformMatrix2x3fv,
    # GL_FLOAT_MAT3x2:        glUniformMatrix3x2fv,
    # GL_FLOAT_MAT4x2:        glUniformMatrix4x2fv,
    # GL_FLOAT_MAT2x4:        glUniformMatrix2x4fv,
    # GL_FLOAT_MAT4x3:        glUniformMatrix4x3fv,
    # GL_FLOAT_MAT3x4:        glUniformMatrix3x4fv,

    # GL_SAMPLER_1D:          glUniform1iv,
    # GL_SAMPLER_2D:          glUniform1iv,
    # GL_SAMPLER_3D:          glUniform1iv
}

SHADER_COMPONENTS = {
    GL_FLOAT:               1,
    GL_FLOAT_VEC2:          2,
    GL_FLOAT_VEC3:          3,
    GL_FLOAT_VEC4:          4,
    GL_DOUBLE:              1,
    GL_DOUBLE_VEC2:         2,
    GL_DOUBLE_VEC3:         3,
    GL_DOUBLE_VEC4:         4,
    GL_INT:                 1,
    GL_INT_VEC2:            2,
    GL_INT_VEC3:            3,
    GL_INT_VEC4:            4,
    GL_UNSIGNED_INT:        1,
    GL_UNSIGNED_INT_VEC2:   2,
    GL_UNSIGNED_INT_VEC3:   3,
    GL_UNSIGNED_INT_VEC4:   4,
    # GL_BOOL:                1,
    # GL_BOOL_VEC2:           2,
    # GL_BOOL_VEC3:           3,
    # GL_BOOL_VEC4:           4,
    GL_FLOAT_MAT2:          (2,2),
    GL_FLOAT_MAT3:          (3,3),
    GL_FLOAT_MAT4:          (4,4),
    GL_FLOAT_MAT2x3:        (2,3),
    GL_FLOAT_MAT3x2:        (3,2),
    GL_FLOAT_MAT4x2:        (4,2),
    GL_FLOAT_MAT2x4:        (2,4),
    GL_FLOAT_MAT4x3:        (3,4),
    GL_FLOAT_MAT3x4:        (4,3),

    GL_DOUBLE_MAT2:         (2,2),
    GL_DOUBLE_MAT3:         (3,3),
    GL_DOUBLE_MAT4:         (4,4),
    GL_DOUBLE_MAT2x3:       (2,3),
    GL_DOUBLE_MAT3x2:       (3,2),
    GL_DOUBLE_MAT4x2:       (4,2),
    GL_DOUBLE_MAT2x4:       (2,4),
    GL_DOUBLE_MAT4x3:       (3,4),
    GL_DOUBLE_MAT3x4:       (4,3),

    GL_SAMPLER_1D:          1,
    GL_SAMPLER_2D:          1,
    GL_SAMPLER_3D:          1
}

SHADER_MATRIX_TYPES = {
    GL_FLOAT_MAT2,
    GL_FLOAT_MAT3,
    GL_FLOAT_MAT4,
    GL_FLOAT_MAT2x3,
    GL_FLOAT_MAT3x2,
    GL_FLOAT_MAT4x2,
    GL_FLOAT_MAT2x4,
    GL_FLOAT_MAT4x3,
    GL_FLOAT_MAT3x4,

    GL_DOUBLE_MAT2,
    GL_DOUBLE_MAT3,
    GL_DOUBLE_MAT4,
    GL_DOUBLE_MAT2x3,
    GL_DOUBLE_MAT3x2,
    GL_DOUBLE_MAT4x2,
    GL_DOUBLE_MAT2x4,
    GL_DOUBLE_MAT4x3,
    GL_DOUBLE_MAT3x4
}

SHADER_TYPE = {
    GL_FLOAT:               numpy.float32,
    GL_FLOAT_VEC2:          numpy.float32,
    GL_FLOAT_VEC3:          numpy.float32,
    GL_FLOAT_VEC4:          numpy.float32,
    GL_DOUBLE:              numpy.float64,
    GL_DOUBLE_VEC2:         numpy.float64,
    GL_DOUBLE_VEC3:         numpy.float64,
    GL_DOUBLE_VEC4:         numpy.float64,
    GL_INT:                 numpy.int32,
    GL_INT_VEC2:            numpy.int32,
    GL_INT_VEC3:            numpy.int32,
    GL_INT_VEC4:            numpy.int32,
    GL_UNSIGNED_INT:        numpy.uint32,
    GL_UNSIGNED_INT_VEC2:   numpy.uint32,
    GL_UNSIGNED_INT_VEC3:   numpy.uint32,
    GL_UNSIGNED_INT_VEC4:   numpy.uint32,
    # GL_BOOL:                None,
    # GL_BOOL_VEC2:           None,
    # GL_BOOL_VEC3:           None,
    # GL_BOOL_VEC4:           None,
    GL_FLOAT_MAT2:          numpy.float32,
    GL_FLOAT_MAT3:          numpy.float32,
    GL_FLOAT_MAT4:          numpy.float32,
    GL_FLOAT_MAT2x3:        numpy.float32,
    GL_FLOAT_MAT3x2:        numpy.float32,
    GL_FLOAT_MAT4x2:        numpy.float32,
    GL_FLOAT_MAT2x4:        numpy.float32,
    GL_FLOAT_MAT4x3:        numpy.float32,
    GL_FLOAT_MAT3x4:        numpy.float32,

    GL_DOUBLE_MAT2:         numpy.float64,
    GL_DOUBLE_MAT3:         numpy.float64,
    GL_DOUBLE_MAT4:         numpy.float64,
    GL_DOUBLE_MAT2x3:       numpy.float64,
    GL_DOUBLE_MAT3x2:       numpy.float64,
    GL_DOUBLE_MAT4x2:       numpy.float64,
    GL_DOUBLE_MAT2x4:       numpy.float64,
    GL_DOUBLE_MAT4x3:       numpy.float64,
    GL_DOUBLE_MAT3x4:       numpy.float64,

    GL_SAMPLER_1D:          numpy.uint32,
    GL_SAMPLER_2D:          numpy.uint32,
    GL_SAMPLER_3D:          numpy.uint32
}