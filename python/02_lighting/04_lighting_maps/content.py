import os, sys
import glm
import glfw
import numpy as np
from OpenGL.GL import *

from viewer import GLContent
from visualizer.shader     import Shader
from visualizer.primitives import Primitive
from visualizer.utils      import *


class Content(GLContent):
    def __init__(self, window, viewport, camera, file_path):
        super().__init__(window, viewport, camera, file_path)

        # textures
        img_file_path = file_path.split(file_path.split("/")[-1])[0] + "test_img"    # chapter name
        self.texture_list, self.img_name_list = get_texture_list(img_file_path)
        self.diff_map, self.spec_map = 4, 5

        # flags
        self.task = 0

        # task variables
        self.mat_shininess    = 5
        self.light_position   = glm.vec3(1.2, 1.0, 2.0)

        # variables for rendering
        # set shader program
        self.obj_shader   = Shader(os.path.join(self.file_path, '04_object.vs'),
                                   os.path.join(self.file_path, '04_object.fs'))
        self.light_shader = Shader(os.path.join(self.file_path, '04_lighting.vs'),
                                   os.path.join(self.file_path, '04_lighting.fs'))

    def inspector(self):
        imgui.begin_group()

        _, self.diff_map = imgui.combo(
            " Diffuse map", self.diff_map, self.img_name_list
        )
        _, self.spec_map = imgui.combo(
            " Specular map", self.spec_map, self.img_name_list
        )

        imgui.dummy(0, 5)        
        imgui.push_item_width(100)
        _, self.task = imgui.combo(
            " Task", self.task, ["1", "2"]
        )
        imgui.pop_item_width()
            
        imgui.dummy(0, 5)
        imgui.text('Material')
        _, self.mat_shininess = imgui.slider_int("shininess", self.mat_shininess,
                                                 min_value=1, max_value=8, format="2^%d")

        imgui.text('Light')
        imgui.text('Light position')
        imgui.push_item_width(250)
        _, self.light_position = imgui.drag_float3('', *self.light_position,
                                                    0.01, -10.0, 10.0, "%.2f")
        imgui.pop_item_width()
        imgui.end_group()


    def render(self):
        # select primitive type
        vertices, indices = Primitive.box()

        # configure the VBO and EBO
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1) if indices is not None else None
        # copy vertices array in a buffer for OpenGL to use
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)
        if self.EBO is not None:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices, GL_STATIC_DRAW)

        # configure the object's VAO
        self.obj_VAO = glGenVertexArrays(1)
        glBindVertexArray(self.obj_VAO)
        # position attribute
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        # normal attribute
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(3 * sizeof(GLfloat)))
        glEnableVertexAttribArray(1)
        # texture coord attribute
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(6 * sizeof(GLfloat)))
        glEnableVertexAttribArray(2)

        # configure the light's VAO (VBO is the same)
        self.light_VAO = glGenVertexArrays(1)
        glBindVertexArray(self.light_VAO)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)


        # load and create a texture
        diffuse_map  = self.texture_list[self.diff_map-1]
        specular_map = self.texture_list[self.spec_map-1]

        self.obj_shader.use()
        self.obj_shader.set_int("material.diffuse",  0)
        self.obj_shader.set_int("material.specular", 1)

        # Task 1: diffuse map texture
        if self.task == 0:
            # bind diffuse map
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, diffuse_map)
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, diffuse_map)      
        # Task 2: diffuse map & specular map
        elif self.task == 1:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, diffuse_map)
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, specular_map)
        else:
            raise TypeError("Wrong task number")
       
        
        # render
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # camera control
        current_frame = glfw.get_time()
        self.camera.delta_time = current_frame - self.camera.last_frame
        self.camera.last_frame = current_frame
        self.camera.translate(self.window)

        # render container
        glBindVertexArray(self.obj_VAO)

        # object shader
        self.obj_shader.use()    
        self.obj_shader.set_vec3("viewPos",        *self.camera.position)   # cam properties
        self.obj_shader.set_vec3("light.position", *self.light_position)    # light properties
        self.obj_shader.set_vec3("light.ambient",  glm.vec3(0.2))
        self.obj_shader.set_vec3("light.diffuse",  glm.vec3(0.5))
        self.obj_shader.set_vec3("light.specular", glm.vec3(1.0))
        self.obj_shader.set_float("material.shininess", pow(self.mat_shininess, 2)) # material properties       

        # view properties for object shader     
        proj_mat = glm.perspective(glm.radians(self.camera.fov), self.viewport[0] / self.viewport[1], 0.1, 100.0)
        view_mat = self.camera.get_view_matrix()
        self.obj_shader.set_mat4("projection", proj_mat)
        self.obj_shader.set_mat4("view", view_mat)

        
        # create transformations
        model_mat_list = [glm.mat4(1.0)]

        # draw
        for i in range(len(model_mat_list)):
            self.obj_shader.set_mat4("model", model_mat_list[i])
            
            if self.EBO is None:
                glDrawArrays(GL_TRIANGLES, 0, 36)
            if self.EBO is not None:
                glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, ctypes.c_void_p(0)) # last argument is indices that specifies an offset in a buffer
                                                                                        # or a pointer to the location where the indices are stored
        
        # draw light cube
        self.light_shader.use()
        self.light_shader.set_mat4("projection", proj_mat)
        self.light_shader.set_mat4("view", view_mat)
        
        model_mat = glm.mat4(1.0)
        model_mat = glm.translate(model_mat, self.light_position)
        model_mat = glm.scale(model_mat, glm.vec3(0.2))
        self.light_shader.set_mat4("model", model_mat)

        glBindVertexArray(self.light_VAO)
        glDrawArrays(GL_TRIANGLES, 0, 36)


    def destroy(self):
        glDeleteVertexArrays(1, self.obj_VAO)
        glDeleteVertexArrays(1, self.light_VAO)
        glDeleteBuffers(1, self.VBO)
        if self.EBO is not None:
            glDeleteBuffers(1, self.EBO)