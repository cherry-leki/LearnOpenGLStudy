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
        self.mat_shininess       = 5
        self.light_position      = glm.vec3(1.2, 1.0, 2.0)
        self.light_direction     = glm.vec3(-0.2, -1.0, -0.3)
        self.light_cut_off       = 12.5
        self.light_outer_cut_off = 12.5


        # variables for rendering
        self.light_caster_names = ['directionallight', 'pointlight', 'spotlight', 'spotlight']
        # set shader program
        self.light_shader= Shader(os.path.join(self.file_path, '05_light.vs'),
                                  os.path.join(self.file_path, '05_light_{}.fs'.format(self.light_caster_names[self.task])))
        self.lamp_shader = Shader(os.path.join(self.file_path, '05_lamp.vs'),
                                  os.path.join(self.file_path, '05_lamp.fs'))

        self.cube_positions = [ 
                                glm.vec3( 0.0,  0.0,   0.0),
                                glm.vec3( 2.0,  5.0, -15.0),
                                glm.vec3(-1.5, -2.2,  -2.5),
                                glm.vec3(-3.8, -2.0, -12.3),
                                glm.vec3( 2.4, -0.4,  -3.5),
                                glm.vec3(-1.7,  3.0,  -7.5),
                                glm.vec3( 1.3, -2.0,  -2.5),
                                glm.vec3( 1.5,  2.0,  -2.5),
                                glm.vec3( 1.5,  0.2,  -1.5),
                                glm.vec3(-1.3,  1.0,  -1.5),
                              ]

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
        changed_task, self.task = imgui.combo(
            " Task", self.task, ["1", "2", "3"]
        )
        if (changed_task):
            self.light_shader = Shader(os.path.join(self.file_path, '05_light.vs'),
                                     os.path.join(self.file_path,
                                                  '05_light_{}.fs'.format(
                                                  self.light_caster_names[self.task])))
        imgui.pop_item_width()
            
        imgui.dummy(0, 5)
        imgui.text('Material')
        _, self.mat_shininess = imgui.slider_int("shininess", self.mat_shininess,
                                                 min_value=1, max_value=8, format="2^%d")

        imgui.text('Light')
        if self.task != 1:
            imgui.text('Light position')
            imgui.push_item_width(250)
            _, self.light_position = imgui.drag_float3('pos', *self.light_position,
                                                        0.01, -10.0, 10.0, "%.2f")
            imgui.pop_item_width()
        if self.task != 0:
            imgui.text('Light direction')
            imgui.push_item_width(250)
            _, self.light_direction = imgui.drag_float3('dir', *self.light_direction,
                                                        0.01, -10.0, 10.0, "%.2f")
            imgui.pop_item_width()
        if self.task == 2:
            imgui.push_item_width(100)
            _, self.light_cut_off = imgui.drag_float('cut off', self.light_cut_off, 0.01, 0)
            _, self.light_outer_cut_off = imgui.drag_float('outer cut off', self.light_outer_cut_off, 0.01, 0)
            imgui.pop_item_width()
            self.light_cut_off = glm.clamp(self.light_cut_off, 0, self.light_outer_cut_off)
        imgui.end_group()


    def render(self):
        # select primitive type
        vertices, _ = Primitive.box()

        # configure the VBO and EBO
        self.VBO = glGenBuffers(1)
        # copy vertices array in a buffer for OpenGL to use
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

        # configure the object's VAO
        self.light_VAO = glGenVertexArrays(1)
        glBindVertexArray(self.light_VAO)
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
        self.lamp_VAO = glGenVertexArrays(1)
        glBindVertexArray(self.lamp_VAO)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)


        # load and create a texture
        diffuse_map  = self.texture_list[self.diff_map-1]
        specular_map = self.texture_list[self.spec_map-1]

        self.light_shader.use()
        self.light_shader.set_int("material.diffuse",  0)
        self.light_shader.set_int("material.specular", 1)

        
        # render
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # camera control
        current_frame = glfw.get_time()
        self.camera.delta_time = current_frame - self.camera.last_frame
        self.camera.last_frame = current_frame
        self.camera.translate(self.window)

        # light shader
        # be sure to activate shader when setting uniforms/drawing objects
        self.light_shader.use()
        self.light_shader.set_vec3("viewPos", *self.camera.position)

        # material properties
        self.light_shader.set_float("material.shininess", 32)

        # light properties
        # Task 1: Directional light (e.g. sun)
        if self.task == 0:
            # no need to have position because every object has the same light intensity regardless of distance b/w light and itself. 
            self.light_shader.set_vec3("light.direction", *self.light_direction)
            
            self.light_shader.set_vec3("light.ambient",  glm.vec3(0.2))
            self.light_shader.set_vec3("light.diffuse",  glm.vec3(0.5))
            self.light_shader.set_vec3("light.specular", glm.vec3(1.0))
        # Task 2: Point light (e.g. light bulbs and torches)
        elif self.task == 1:
            self.light_shader.set_vec3("light.position", *self.light_position)
            
            self.light_shader.set_vec3("light.ambient",  glm.vec3(0.2))
            self.light_shader.set_vec3("light.diffuse",  glm.vec3(0.5))
            self.light_shader.set_vec3("light.specular", glm.vec3(1.0))

            # attenuation
            self.light_shader.set_float("light.constant",  1.0)      # distance of 50
            self.light_shader.set_float("light.linear",    0.09)
            self.light_shader.set_float("light.quadratic", 0.032)
        # Task 3: Spot light (e.g. street lamp and flashlight)
        elif self.task == 2:
            self.light_shader.set_vec3("light.position",     *self.camera.position)
            self.light_shader.set_vec3("light.direction",    *self.camera.front)
            self.light_shader.set_float("light.cutOff",      glm.cos(glm.radians(self.light_cut_off))) # compare cosine values instead of angle
            self.light_shader.set_float("light.outerCutOff", glm.cos(glm.radians(self.light_outer_cut_off))) # for smooth/soft edges

            # we configure the diffuse intensity slightly higher
            # the right lighting conditions differ with each lighting method and environment
            # each environment and lighting type requires some tweaking to get the best out of your environment
            self.light_shader.set_vec3("light.ambient",  glm.vec3(0.1))
            self.light_shader.set_vec3("light.diffuse",  glm.vec3(0.8))
            self.light_shader.set_vec3("light.specular", glm.vec3(1.0))

            self.light_shader.set_float("light.constant",  1.0)
            self.light_shader.set_float("light.linear",    0.09)
            self.light_shader.set_float("light.quadratic", 0.032)
        else:
            raise TypeError("Wrong task number")

        # render container
        glBindVertexArray(self.light_VAO)        

        # view properties for object shader           
        proj_mat = glm.perspective(glm.radians(self.camera.fov), self.viewport[0]/self.viewport[1], 0.1, 100.0)
        view_mat = self.camera.get_view_matrix()
        self.light_shader.set_mat4("projection", proj_mat)
        self.light_shader.set_mat4("view", view_mat)


        # objects
        # texture
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, diffuse_map)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, specular_map)

        # draw
        glBindVertexArray(self.light_VAO)
        for i in range(len(self.cube_positions)):
            model = glm.mat4(1.0)
            model = glm.translate(model, self.cube_positions[i])
            angle = 20.0 * i
            model = glm.rotate(model, glm.radians(angle), glm.vec3(1.0, 0.3, 0.5))
            self.light_shader.set_mat4("model", model)
            
            glDrawArrays(GL_TRIANGLES, 0, 36)
      
        # draw light cube
        if self.task == 1:
            self.lamp_shader.use()
            self.lamp_shader.set_mat4("projection", proj_mat)
            self.lamp_shader.set_mat4("view", view_mat)

            model_mat = glm.mat4(1.0)
            model_mat = glm.translate(model_mat, self.light_position)
            model_mat = glm.scale(model_mat, glm.vec3(0.2))
            self.lamp_shader.set_mat4("model", model_mat)

            self.lamp_shader.set_vec3("color", glm.vec3(1.0))

            glBindVertexArray(self.lamp_VAO)
            glDrawArrays(GL_TRIANGLES, 0, 36)


    def destroy(self):
        glDeleteVertexArrays(1, self.light_VAO)
        glDeleteVertexArrays(1, self.lamp_VAO)
        glDeleteBuffers(1, self.VBO)