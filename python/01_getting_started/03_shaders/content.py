import os, sys
import glfw
import numpy as np
from OpenGL.GL import *
from PIL import Image

from viewer import GLContent
from visualizer.shader     import Shader
from visualizer.utils      import *


# vertices, indices setting
def set_triangle():
    vertices = [  # positions      # colors
                  0.5, -0.5, 0.0,  1.0, 0.0, 0.0,  # bottom right
                 -0.5, -0.5, 0.0,  0.0, 1.0, 0.0,  # bottom left
                  0.0,  0.5, 0.0,  0.0, 0.0, 1.0]  # top
    vertices = np.array(vertices, dtype=np.float32)

    return vertices, None

def set_rectangle():
    vertices = [ -0.5,  0.5,  0.0,  1.0, 0.0, 0.0, # top-left
                  0.5,  0.5,  0.0,  0.0, 1.0, 0.0, # top-right
                  0.5, -0.5,  0.0,  0.0, 0.0, 1.0, # bottom-right
                 -0.5, -0.5,  0.0,  1.0, 1.0, 1.0] # bottom-left
                
    vertices = np.array(vertices, dtype=np.float32)

    indices = [ 0, 1, 2,
                2, 3, 0 ]
    indices = np.array(indices, dtype=np.uint32)

    return vertices, indices
    

class Content(GLContent):
    def __init__(self, window, viewport, camera, file_path):
        super().__init__(window, viewport, camera, file_path)

        self.task = 0
        self.primitive = 0
        self.translate_offset = [0, 0, 0]

        self.folder_path = ['0301_shaders_uniform_variable', '0301_shaders_uniform_variable', '0302_shaders_color_vertex_array']
        self.vtx_path    = ['0301_vtx_shader.vs', '0301_vtx_shader.vs', '0302_vtx_shader.vs']
        self.frag_path   = ['0301_frag_shader.fs', '0301_uniform_frag_shader.fs', '0302_frag_shader.fs']
        self.shader = Shader(os.path.join(file_path, self.folder_path[0], self.vtx_path[0]),
                             os.path.join(file_path, self.folder_path[0], self.frag_path[0]))
    
    def inspector(self):
        imgui.begin_group()
        imgui.push_item_width(100)
        changed_task, self.task = imgui.combo(
            " Task", self.task, ["1", "2", "3"]
        )
        if changed_task:
            self.shader = Shader(os.path.join(self.file_path,
                                              self.folder_path[self.task],
                                              self.vtx_path[self.task]),
                                 os.path.join(self.file_path,
                                              self.folder_path[self.task],
                                              self.frag_path[self.task]))
        imgui.pop_item_width()

        imgui.dummy(0, 5)
        imgui.push_item_width(100)
        _, self.primitive = imgui.combo(
            " Primitive", self.primitive, ["tri", "rect"]
        )
        imgui.pop_item_width()


        if self.task == 1:
            imgui.dummy(0, 5)
            _, self.translate_offset = imgui.input_float3("translate offset", *self.translate_offset)

        imgui.end_group()

    def render(self):
        # select primitive type
        if self.primitive == 0:
            vertices, indices = set_triangle()
        elif self.primitive == 1:
            vertices, indices = set_rectangle()
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
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)    # specify the index of the vertex attribute to be enabled
        if self.task == 2:
            # color attribute
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), ctypes.c_void_p(3 * sizeof(GLfloat)))
            glEnableVertexAttribArray(1)

        # Binding 0 as a buffer resets the currently bound buffer to a NULL-like state
        # note that this is allowed, the call to glVertexAttribPointer registered VBO
        # as the vertex attribute's bound vertex bound object so afterwards we can safely unbind
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        
        # do NOT unbine the EBO while a VAO is active as the bound element buffer is stored in the VAO; keep the EBO bound
        # VAO store the glBindBuffer calls when the target is GL_ELEMENT_ARRAY_BUFFER, which menas it stores its unbind calls
        # if EBO is not None:
        #     glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        # bind vertex array object
        #  Any subsequent VBO, EBO, glVertexAttribPointer, and glEnalbeVertexAttribArray calls will be stored inside the VAO.
        #  The role of VAO is just for managing vertex attributes, and we can use VBO only by calling glEnableVertexAttribArray.
        #  (see how to use VBO without VAO in 02_hello_triangle_noVAO.py)
        #  So, we don't need to use glBindVertexArray function here and in the while loop to run this simple triangle example.
        glBindVertexArray(0)


        # render
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.shader.use()

        if self.task == 1:
            horizontal_offset = glGetUniformLocation(self.shader.id, "offsetPos")
            glUniform3f(horizontal_offset, self.translate_offset[0], self.translate_offset[1], self.translate_offset[2])

            # update the uniform color
            time_value = glfw.get_time()
            green_value = np.sin(time_value) / 2.0 + 0.5
            vertex_color_location = glGetUniformLocation(self.shader.id, "ourColor")
            glUniform4f(vertex_color_location, 0, green_value, 0, 1)

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