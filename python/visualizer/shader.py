import os
from typing import overload
import numpy as np

import glm
from OpenGL.GL import *

#################################################################
# Shader class                                                  #
# - reference: https://gist.github.com/deepankarsharma/3494203  #
#################################################################

class Shader:
    def __init__(self, vertex_path, fragment_path):
        # open vertex shader and fragment shader code files
        abs_path = os.path.dirname(os.path.abspath(__file__))

        vtx_src_code   = open(vertex_path).read()
        frag_src_code  = open(fragment_path).read()

        # vertex shader and fragment shader
        vtx_shader   = self.add_shader(vtx_src_code, GL_VERTEX_SHADER)
        frag_shader  = self.add_shader(frag_src_code, GL_FRAGMENT_SHADER)

        # shader program
        self.id = glCreateProgram()
        glAttachShader(self.id, vtx_shader)
        glAttachShader(self.id, frag_shader)
        glLinkProgram(self.id)

        if glGetProgramiv(self.id, GL_LINK_STATUS) != GL_TRUE:
            info_log = glGetProgramInfoLog(self.id)
            glDeleteProgram(self.id)
            glDeleteShader(vtx_shader)
            glDeleteShader(frag_shader)
            raise RuntimeError("ERROR::SHADER::PROGRAM::LINKING_FAILED %s ", info_log)
        
        # delete the shaders as they're linked into our program now and no longer necessary
        glDeleteShader(vtx_shader)
        glDeleteShader(frag_shader)

    def add_shader(self, code, shader_type):
        try:
            shader_id = glCreateShader(shader_type)
            glShaderSource(shader_id, code)
            glCompileShader(shader_id)
            if glGetShaderiv(shader_id, GL_COMPILE_STATUS) != GL_TRUE:
                info_log = glGetShaderInfoLog(shader_id)
                raise RuntimeError("ERROR:SHADER::FRAGMENT::COMPILATION_FAILED %s" % (info_log))
            return shader_id
        except:
            glDeleteShader(shader_id)
            raise

    def use(self):
        glUseProgram(self.id)

    def set_bool(self, name, value):
        glUniform1i(glGetUniformLocation(self.id, name), int(value))
    
    def set_int(self, name, value):
        glUniform1i(glGetUniformLocation(self.id, name), value)
    
    def set_float(self, name, value):
        glUniform1f(glGetUniformLocation(self.id, name), value)

    def set_vec2(self, name, *args):
        if len(args) == 1:
            glUniform2fv(glGetUniformLocation(self.id, name), 1, glm.value_ptr(args[0]))
        elif len(args) == 3:
            glUniform2f(glGetUniformLocation(self.id, name), args[0], args[1])
        else:
            raise TypeError("set_vec2()::wrong positional arguments: glm.vec2() or x, y values")

    def set_vec3(self, name, *args):
        if len(args) == 1:
            glUniform3fv(glGetUniformLocation(self.id, name), 1, glm.value_ptr(args[0]))
        elif len(args) == 3:
            glUniform3f(glGetUniformLocation(self.id, name), args[0], args[1], args[2])
        else:
            raise TypeError("set_vec3()::wrong positional arguments: glm.vec3() or x, y, z values")
    
    def set_vec4(self, name, *args):
        if len(args) == 1:
            glUniform4fv(glGetUniformLocation(self.id, name), 1, glm.value_ptr(args[0]))
        elif len(args) == 4:
            glUniform4f(glGetUniformLocation(self.id, name), args[0], args[1], args[2], args[3])
        else:
            raise TypeError("set_vec4()::wrong positional arguments: glm.vec4() or x, y, z, w values")

    def set_mat2(self, name, mat):
        glUniformMatrix2fv(glGetUniformLocation(self.id, name), 1, GL_FALSE, glm.value_ptr(mat))
    
    def set_mat3(self, name, mat):
        glUniformMatrix3fv(glGetUniformLocation(self.id, name), 1, GL_FALSE, glm.value_ptr(mat))

    def set_mat4(self, name, mat):
        glUniformMatrix4fv(glGetUniformLocation(self.id, name), 1, GL_FALSE, glm.value_ptr(mat))
    