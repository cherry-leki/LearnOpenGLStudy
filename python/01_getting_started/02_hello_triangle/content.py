import os, sys

import glfw
from OpenGL.GL import *
import imgui

from visualizer.primitives import Primitive
from visualizer.utils      import *
from viewer                import GLContent


### shaders
vertex_shader_source = """
#version 330 core

layout (location = 0) in vec3 aPos;

void main()
{
    gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);
}
"""

fragment_shader_source = """
#version 330 core

out vec4 FragColor;

void main()
{
    FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);
}
"""

# set shader program
def set_shader_program():
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_shader_source) # in pyopengl, we don't need to how many strings we passing as src code
    glCompileShader(vertex_shader)

    # check for shader compile errors
    success = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
    if not success:
        info_log = glGetShaderInfoLog(vertex_shader)
        print("ERROR:SHADER::VERTEX::COMPILATION_FAILED ", info_log)

    # fragment shader
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_shader_source)
    glCompileShader(fragment_shader)

    # check for shader compile errors
    success = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
    if not success:
        info_log = glGetShaderInfoLog(fragment_shader)
        print("ERROR:SHADER::FRAGMENT::COMPILATION_FAILED ", info_log)

    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)
    
    success = glGetProgramiv(shader_program, GL_LINK_STATUS)
    if not success:
        info_log = glGetProgramInfoLog(shader_program)
        print("ERROR::SHADER::PROGRAM::LINKING_FAILED ", info_log)

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return shader_program


class Content(GLContent):
    def __init__(self, window, viewport, camera, file_path):
        super().__init__(window, viewport, camera, file_path)
        
        self.primitive = 0

    def inspector(self):
        imgui.begin_group()

        imgui.push_item_width(100)
        clicked, self.primitive = imgui.combo(
            " Primitive", self.primitive, ["tri", "rect"]
        )
        imgui.pop_item_width()

        imgui.end_group()

    ### main
    def render(self):
        # set shader program
        self.shader = set_shader_program()

        # select primitive type
        if self.primitive == 0:
            vertices, indices = Primitive.triangle()
        elif self.primitive == 1:
            vertices, indices = Primitive.rectangle()
        else:
            print("Please write target primitive ('triangle', 'rect')")
            exit()
        
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1) if indices is not None else None

        # bind the Vertex Array Object first, then bind and set vertex buffer(s),
        # and then configure vertex attribute(s)
        glBindVertexArray(self.VAO)

        # copy vertices array in a buffer for OpenGL to use
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

        if self.EBO is not None:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices, GL_STATIC_DRAW)

        # set the vertex attributes pointers
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)    # specify the index of the vertex attribute to be enabled

        # render
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw
        glUseProgram(self.shader)

        glBindVertexArray(self.VAO)
        if self.EBO is None:
            glDrawArrays(GL_TRIANGLES, 0, 3)
        if self.EBO is not None:
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, ctypes.c_void_p(0)) # last argument is indices that specifies an offset in a buffer
                                                                                    # or a pointer to the location where the indices are stored

    def destroy(self):
        glDeleteVertexArrays(1, self.VAO)
        glDeleteBuffers(1, self.VBO)
        if self.EBO is not None:
            glDeleteBuffers(1, self.EBO)

        glDeleteProgram(self.shader)