import os, sys
import glfw
import numpy as np
from OpenGL.GL import *
from PIL import Image

from viewer import GLContent
from visualizer.shader     import Shader
from visualizer.utils      import *

def load_texture(file_path):
    texture = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, texture)   # all upcoming GL_TEXTURE_2D operations now have effect on this texture object
    
    # set the texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)    # set texture wrapping to GL_REPEAT (default wrapping method)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # set texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    img = Image.open(file_path)
    img_w, img_h, img_data = img.size[0], img.size[1], img.tobytes("raw", "RGBA", 0, -1)
    if(img_data):
        # Note that 7th parameter(color type) is same as the img's color type
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_w, img_h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
    else:
        print("Failed to load texture")
    
    return texture

# vertices, indices setting
def set_triangle():
    vertices = [
                 -0.5, -0.5,  0.0,   1.0, 0.0, 0.0,   0.0, 0.0,
                  0.5, -0.5,  0.0,   0.0, 1.0, 0.0,   1.0, 0.0,
                  0.0,  0.5,  0.0,   0.0, 0.0, 1.0,   0.5, 1.0
               ]
    vertices = np.array(vertices, dtype=np.float32)

    return vertices, None

def set_rectangle():
    vertices = [  # positions        # colors         # texture coords
                  0.5,  0.5,  0.0,   1.0, 0.0, 0.0,   1.0, 1.0,   # top right
                  0.5, -0.5,  0.0,   0.0, 1.0, 0.0,   1.0, 0.0,   # bottom right
                 -0.5, -0.5,  0.0,   0.0, 0.0, 1.0,   0.0, 0.0,   # bottom left
                 -0.5,  0.5,  0.0,   1.0, 1.0, 1.0,   0.0, 1.0    # top left
               ]
    vertices = np.array(vertices, dtype=np.float32)

    indices = [ 0, 1, 3,
                1, 2, 3 ]
    indices = np.array(indices, dtype=np.uint32)

    return vertices, indices


class Content(GLContent):
    def __init__(self, window, viewport, camera, file_path):
        super().__init__(window, viewport, camera, file_path)

        self.primitive = 0
        self.img1 = 0
        self.img2 = 0

        self.img_path_list, self.img_name_list = get_img_list(self.file_path)
        self.texture_img_list = []

    
    def inspector(self):
        imgui.begin_group()
    
        changed_img1, self.img1 = imgui.combo(
            " Image 1", self.img1, self.img_name_list
        )
        if changed_img1:
            if self.img1 == 0:
                self.img2 = 0
                self.texture_img_list = []
            else:
                self.texture_img_list = [self.img_path_list[self.img1-1]]

        if (self.img1 != 0):
            changed_img2, self.img2 = imgui.combo(
                " Image 2", self.img2, self.img_name_list
            )

            if changed_img2:
                if self.img2 == 0:
                    self.texture_img_list = [self.img_path_list[self.img1-1]]
                else:
                    self.texture_img_list.append(self.img_path_list[self.img2-1])
        else:
            self.img2 = 0


        imgui.dummy(0, 5)
        imgui.push_item_width(100)
        _, self.primitive = imgui.combo(
            " Primitive", self.primitive, ["tri", "rect"]
        )
        imgui.pop_item_width()

        imgui.end_group()

    def render(self):
        self.shader = Shader(os.path.join(self.file_path, '04_vtx_shader.vs'),
                             os.path.join(self.file_path, '04_frag_shader.fs'))
        
        # select primitive type
        if self.primitive == 0:
            vertices, indices = set_triangle()
        elif self.primitive == 1:
            vertices, indices = set_rectangle()
        else:
            print("Please write target primitive ('triangle', 'rect')")
            exit()

        # set up vertex data (and buffer(s)) and configure vertex attributes
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

        # position attribute
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        # color attribute
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(3 * sizeof(GLfloat)))
        glEnableVertexAttribArray(1)
        # texture coord attribute
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(6 * sizeof(GLfloat)))
        glEnableVertexAttribArray(2)

        # load and create a texture
        texture_list = []
        for i in range(np.size(self.texture_img_list)):
            texture_list.append([load_texture(self.texture_img_list[i]), "texture" + str(i + 1)])
        # texture1 = load_texture(self.texture_img_list[0])
        # texture2 = load_texture(self.texture_img_list[1])

        # tell opengl for each sampler to which texture unit it belongs to (only has to be done once)
        self.shader.use()    # don't forget to activate/use the shader before setting uniforms!
        self.shader.set_int("textureNum", len(texture_list))
        for i in range(0, len(texture_list)):
            self.shader.set_int(texture_list[i][1], i)
        # either set it manually like so:
        # glUniform1i(glGetUniformLocation(self.shader.id, "texture1"), 0)
        # self.shader.set_int("texture1", 0)
        # # or set it via the texture class
        # self.shader.set_int("texture2", 1)

        # Binding 0 as a buffer resets the currently bound buffer to a NULL-like state
        # note that this is allowed, the call to glVertexAttribPointer registered self.VBO
        # as the vertex attribute's bound vertex bound object so afterwards we can safely unbind
        # glBindBuffer(GL_ARRAY_BUFFER, 0)
        

        # render
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # bind texture
        for i in range(len(texture_list)):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, texture_list[i][0])
        # glActiveTexture(GL_TEXTURE0)
        # glBindTexture(GL_TEXTURE_2D, texture_list[0][0])
        # glActiveTexture(GL_TEXTURE1)
        # glBindTexture(GL_TEXTURE_2D, texture_list[1][0])

        # draw
        self.shader.use()
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