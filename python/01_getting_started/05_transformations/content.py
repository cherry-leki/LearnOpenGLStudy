import os, sys
import glm
import glfw
import numpy as np
from OpenGL.GL import *
from PIL import Image

from viewer import GLContent
from visualizer.shader     import Shader
from visualizer.primitives import Primitive
from visualizer.utils      import *


class Content(GLContent):
    def __init__(self, window, viewport, camera, file_path):
        super().__init__(window, viewport, camera, file_path)

        self.task = 0
        self.primitive = 0

        self.img1, self.img2 = 1, 3
        chapter_name = file_path.split("/")[-1]
        img_path = file_path.split(chapter_name)[0] + "/test_img"
        self.img_path_list, self.img_name_list = get_img_list(img_path)
        self.texture_img_list = [self.img_path_list[self.img1-1], self.img_path_list[self.img2-1]]

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
        
        imgui.push_item_width(100)
        _, self.task = imgui.combo(
            " Task", self.task, ["1", "2", "3", "4"]
        )
        imgui.pop_item_width()

        imgui.push_item_width(100)
        _, self.primitive = imgui.combo(
            " Primitive", self.primitive, ["tri", "rect"]
        )
        imgui.pop_item_width()

        imgui.end_group()


    def render(self):
        # set shader program
        shader = Shader(os.path.join(self.file_path, '05_vtx_shader.vs'),
                        os.path.join(self.file_path, '05_frag_shader.fs'))


        # select primitive type
        if self.primitive == 0:
            vertices, indices = Primitive.triangle()
        elif self.primitive == 1:
            vertices, indices = Primitive.rectangle()
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
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        # texture coord attribute
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), ctypes.c_void_p(3 * sizeof(GLfloat)))
        glEnableVertexAttribArray(1)


        # load and create a texture
        texture_list = []
        for i in range(np.size(self.texture_img_list)):
            texture_list.append([load_texture(self.texture_img_list[i]), "texture" + str(i + 1)])

        # tell opengl for each sampler to which texture unit it belongs to (only has to be done once)
        shader.use()    # don't forget to activate/use the shader before setting uniforms!
        shader.set_int("textureNum", len(texture_list))
        for i in range(0, len(texture_list)):
            shader.set_int(texture_list[i][1], i)

        
        # render
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # bind textures on corresponding texture units
        for i in range(len(texture_list)):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, texture_list[i][0])

        # create transformations
        trf_mat = glm.mat4(1.0)   # make sure to initialize matrix to identity matrix first
        
        # translate
        if self.task == 0:
            trf_mat = glm.translate(trf_mat, glm.vec3(1.0, 1.0, 0.0))
        # rotate & scale
        elif self.task == 1:
            trf_mat = glm.rotate(trf_mat, glm.radians(90), glm.vec3(0.0, 0.0, 1.0))
            trf_mat = glm.scale(trf_mat, glm.vec3(0.5, 0.5, 0.5))
        # translate & rotate every timestep
        elif self.task == 2 or self.task == 3:        
            trf_mat = glm.translate(trf_mat, glm.vec3(0.5, -0.5, 0.0))
            trf_mat = glm.rotate(trf_mat, float(glfw.get_time()), glm.vec3(0.0, 0.0, 1.0))

        # draw
        trf_location = glGetUniformLocation(shader.id, "transform")
        glUniformMatrix4fv(trf_location, 1, GL_FALSE, glm.value_ptr(trf_mat))

        # render container
        glBindVertexArray(self.VAO)
        if self.EBO is None:
            glDrawArrays(GL_TRIANGLES, 0, 3)
        else:
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, ctypes.c_void_p(0)) # last argument is indices that specifies an offset in a buffer
                                                                                    # or a pointer to the location where the indices are stored

        if self.task == 3:
            # second transform
            trf_mat = glm.mat4(1.0)
            trf_mat = glm.translate(trf_mat, glm.vec3(-0.5, 0.5, 0.0))
            scale_amount = float(np.sin(glfw.get_time()))
            trf_mat = glm.scale(trf_mat, glm.vec3(scale_amount, scale_amount, scale_amount))
            glUniformMatrix4fv(trf_location, 1, GL_FALSE, glm.value_ptr(trf_mat))

            if self.EBO is None:
                glDrawArrays(GL_TRIANGLES, 0, 3)
            else:
                glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, ctypes.c_void_p(0)) # last argument is indices that specifies an offset in a buffer
                                                                                    # or a pointer to the location where the indices are stored


    def destroy(self):
        glDeleteVertexArrays(1, self.VAO)
        glDeleteBuffers(1, self.VBO)
        if self.EBO is not None:
            glDeleteBuffers(1, self.EBO)