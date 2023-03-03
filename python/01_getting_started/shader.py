import os
import numpy as np
import argparse

import glfw
from OpenGL.GL import *

#################################################################
# Shader class                                                  #
# - reference: https://gist.github.com/deepankarsharma/3494203  #
#################################################################

class Shader:
    def __init__(self, vertex_path, fragment_path):
        # open vertex shader and fragment shader code files
        abs_path = os.path.dirname(os.path.abspath(__file__))

        vtx_src_code   = open(os.path.join(abs_path, vertex_path), 'r').read()
        frag_src_code  = open(os.path.join(abs_path, fragment_path), 'r').read()

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

    def set_vec2(self, name, value):
        glUniform2fv(glGetUniformLocation(self.id, name), 1, value)

    def set_vec2(self, name, x, y):
        glUniform2f(glGetUniformLocation(self.id, name), x, y)
    