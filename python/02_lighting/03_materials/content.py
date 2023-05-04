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
        self.img1, self.img2 = 0, 0
        img_file_path = file_path.split(file_path.split("/")[-1])[0] + "test_img"    # chapter name
        self.texture_list, self.img_name_list = get_texture_list(img_file_path)
        self.selected_textures = []

        # flags
        self.task = 0

        # task variables
        self.mat_ambient      = glm.vec3(1.0, 0.5, 0.31)
        self.mat_diffuse      = glm.vec3(1.0, 0.5, 0.31)
        self.mat_specular     = glm.vec3(0.5)
        self.mat_shininess    = 5

        self.light_ambient    = glm.vec3(1.0)
        self.light_diffuse    = glm.vec3(1.0)
        self.light_specular   = glm.vec3(1.0)
        self.light_position   = glm.vec3(1.2, 1.0, 2.0)

    def inspector(self):
        imgui.begin_group()

        changed_img1, self.img1 = imgui.combo(
            " Texture 1", self.img1, self.img_name_list
        )
        if changed_img1:
            if self.img1 == 0:
                self.img2 = 0
                self.selected_textures = []
            else:
                self.selected_textures = [self.texture_list[self.img1-1]]
        if self.img1 != 0:
            changed_img2, self.img2 = imgui.combo(
                " Texture 2", self.img2, self.img_name_list
            )
            if changed_img2:
                if self.img2 == 0:
                    self.selected_textures = [self.texture_list[self.img1-1]]
                else:
                    self.selected_textures = [self.texture_list[self.img1-1],
                                              self.texture_list[self.img2-1]]
        else:
            self.img2 = 0

        imgui.dummy(0, 5)        
        imgui.push_item_width(100)
        changed_task, self.task = imgui.combo(
            " Task", self.task, ["1", "2", "3", "4", "5"]
        )
        if changed_task:
            if self.task == 1:
                self.light_ambient  = glm.vec3(0.2)
                self.light_diffuse  = glm.vec3(0.5)
                self.light_specular = glm.vec3(1.0)
        imgui.pop_item_width()
            
        imgui.dummy(0, 5)
        imgui.text('Material')
        _, self.mat_ambient   = imgui.color_edit3("mat_ambient",  *self.mat_ambient)
        _, self.mat_diffuse   = imgui.color_edit3("mat_diffuse",  *self.mat_diffuse)
        _, self.mat_specular  = imgui.color_edit3("mat_specular", *self.mat_specular)
        _, self.mat_shininess = imgui.slider_int("shininess", self.mat_shininess,
                                                 min_value=1, max_value=8, format="2^%d")

        imgui.text('Light')
        _, self.light_ambient  = imgui.color_edit3("lit_ambient",  *self.light_ambient)
        _, self.light_diffuse  = imgui.color_edit3("lit_diffuse",  *self.light_diffuse)
        _, self.light_specular = imgui.color_edit3("lit_specular", *self.light_specular)
        imgui.text('Light position')
        imgui.push_item_width(250)
        _, self.light_position = imgui.drag_float3('', *self.light_position,
                                                    0.01, -10.0, 10.0, "%.2f")
        imgui.pop_item_width()
        imgui.end_group()


    def render(self):
        # set shader program
        obj_shader   = Shader(os.path.join(self.file_path, '03_object.vs'),
                              os.path.join(self.file_path, '03_object.fs'))
        light_shader = Shader(os.path.join(self.file_path, '03_lighting.vs'),
                              os.path.join(self.file_path, '03_lighting.fs'))


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
        texture_list = []
        for i in range(np.size(self.selected_textures)):
            texture_list.append([self.selected_textures[i], "texture" + str(i + 1)])

        # tell opengl for each sampler to which texture unit it belongs to (only has to be done once)
        obj_shader.use()    # don't forget to activate/use the shader before setting uniforms!
        obj_shader.set_int("textureNum", len(texture_list))
        for i in range(0, len(texture_list)):
            obj_shader.set_int(texture_list[i][1], i)


        # camera control
        current_frame = glfw.get_time()
        self.camera.delta_time = current_frame - self.camera.last_frame
        self.camera.last_frame = current_frame
        self.camera.translate(self.window)

        
        # render
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # bind textures on corresponding texture units
        for i in range(len(texture_list)):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, texture_list[i][0])

        # render container
        glBindVertexArray(self.obj_VAO)

        # create transformations
        model_mat_list = []
        model_mat = glm.mat4(1.0)
        model_mat_list.append(model_mat)

        obj_shader.use()        
        obj_shader.set_vec3("material.ambient",  *self.mat_ambient)
        obj_shader.set_vec3("material.diffuse",  *self.mat_diffuse)
        obj_shader.set_vec3("material.specular", *self.mat_specular)
        obj_shader.set_float("material.shininess", self.mat_shininess)

        obj_shader.set_vec3("light.position", *self.light_position)
        obj_shader.set_vec3("viewPos", *self.camera.position)

        # Task 1: bright color & Task 2: regulating light color
        if self.task <= 1:
            obj_shader.set_vec3("light.ambient",  *self.light_ambient)
            obj_shader.set_vec3("light.diffuse",  *self.light_diffuse)
            obj_shader.set_vec3("light.specular", *self.light_specular)         
        # Task 3: diverse colors with light changing
        elif self.task == 2:
            # the light color directly influcences what colors the obj can reflect
            light_color = glm.vec3()
            light_color.x = glm.sin(glfw.get_time() * 2.0)
            light_color.y = glm.sin(glfw.get_time() * 0.7)
            light_color.z = glm.sin(glfw.get_time() * 1.3)

            diffuse_color = light_color   * glm.vec3(0.5)
            ambient_color = diffuse_color * glm.vec3(0.2)

            obj_shader.set_vec3("light.ambient", ambient_color)
            obj_shader.set_vec3("light.diffuse", diffuse_color)
            obj_shader.set_vec3("light.specular", glm.vec3(1.0))

            self.light_ambient = imgui_ext.convert_color(ambient_color, -1, 1, 0, 1)
            self.light_diffuse = imgui_ext.convert_color(diffuse_color, -1, 1, 0, 1)
        # Task 4: change light cube color
        elif self.task == 3:
            obj_shader.set_vec3("light.ambient",  *self.light_ambient)
            obj_shader.set_vec3("light.diffuse",  *self.light_diffuse)
            obj_shader.set_vec3("light.specular", *self.light_specular)
        # Task 3: diverse colors with light changing
        elif self.task == 4:
            # the light color directly influcences what colors the obj can reflect
            light_color = glm.vec3()
            light_color.x = glm.sin(glfw.get_time() * 2.0)
            light_color.y = glm.sin(glfw.get_time() * 0.7)
            light_color.z = glm.sin(glfw.get_time() * 1.3)

            diffuse_color = light_color   * glm.vec3(0.5)
            ambient_color = diffuse_color * glm.vec3(0.2)

            obj_shader.set_vec3("light.ambient", ambient_color)
            obj_shader.set_vec3("light.diffuse", diffuse_color)
            obj_shader.set_vec3("light.specular", glm.vec3(1.0))

            self.light_ambient = imgui_ext.convert_color(ambient_color, -1, 1, 0, 1)
            self.light_diffuse = imgui_ext.convert_color(diffuse_color, -1, 1, 0, 1)
        else:
            raise TypeError("Wrong task number")

        # draw object     
        proj_mat = glm.perspective(glm.radians(self.camera.fov), self.viewport[0] / self.viewport[1], 0.1, 100.0)
        view_mat = self.camera.get_view_matrix()
        obj_shader.set_mat4("projection", proj_mat)
        obj_shader.set_mat4("view", view_mat)

        # draw
        for i in range(len(model_mat_list)):
            obj_shader.set_mat4("model", model_mat_list[i])
            
            if self.EBO is None:
                glDrawArrays(GL_TRIANGLES, 0, 36)
            if self.EBO is not None:
                glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, ctypes.c_void_p(0)) # last argument is indices that specifies an offset in a buffer
                                                                                        # or a pointer to the location where the indices are stored
        
        # draw light cube
        light_shader.use()
        light_shader.set_mat4("projection", proj_mat)
        light_shader.set_mat4("view", view_mat)
        
        model_mat = glm.mat4(1.0)
        model_mat = glm.translate(model_mat, self.light_position)
        model_mat = glm.scale(model_mat, glm.vec3(0.2))
        light_shader.set_mat4("model", model_mat)

        if self.task >= 3:
            light_shader.set_vec3("color",  *self.light_diffuse)
        else:
            light_shader.set_vec3("color",  glm.vec3(1.0))

        glBindVertexArray(self.light_VAO)
        glDrawArrays(GL_TRIANGLES, 0, 36)


    def destroy(self):
        glDeleteVertexArrays(1, self.obj_VAO)
        glDeleteVertexArrays(1, self.light_VAO)
        glDeleteBuffers(1, self.VBO)
        if self.EBO is not None:
            glDeleteBuffers(1, self.EBO)