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
        img_path = file_path.split(chapter_name)[0] + "test_img"
        self.img_path_list, self.img_name_list = get_img_list(img_path)
        self.texture_img_list = [self.img_path_list[self.img1-1], self.img_path_list[self.img2-1]]

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
        
        self.camera = Camera(self.window)
        # Binding 0 as a buffer resets the currently bound buffer to a NULL-like state
        # note that this is allowed, the cafrom inspect import currentframe
        # variables for camera setting
        self.camera_pos   = glm.vec3(0.0, 0.0, 3.0)
        self.camera_front = glm.vec3(0.0, 0.0, -1.0)
        self.camera_up    = glm.vec3(0.0, 1.0, 0.0)
        self.delta_time   = 0                            # time between current frame and last frame
        self.last_frame   = 0                            # time of last frame
        glfw.set_scroll_callback(window, self.camera.get_fov)

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
            " Task", self.task, ["1", "2", "3"]
        )
        imgui.pop_item_width()

        imgui.push_item_width(100)
        _, self.primitive = imgui.combo(
            " Primitive", self.primitive, ["tri", "rect", "box"]
        )
        imgui.pop_item_width()

        imgui.end_group()


    def render(self):
        # set shader program
        shader = Shader(os.path.join(self.file_path, '07_vtx_shader.vs'),
                        os.path.join(self.file_path, '07_frag_shader.fs'))


        # select primitive type
        if self.primitive == 0:
            vertices, indices = Primitive.triangle()
        elif self.primitive == 1:
            vertices, indices = Primitive.rectangle()
        elif self.primitive == 2:
            vertices, indices = Primitive.box()
        else:
            print("Please write target primitive ('triangle', 'rect', 'box)")
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

        if self.primitive == 2:
        # position attribute
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
            # texture coord attribute
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(6 * sizeof(GLfloat)))
            glEnableVertexAttribArray(1)
        else:
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

        # task 1
        # radius = 10.0
        # camX = np.sin(glfw.get_time()) * radius
        # camZ = np.cos(glfw.get_time()) * radius
        # view_mat = glm.lookAt(glm.vec3(camX, 0, camZ), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
        # task 2
        self.current_frame = glfw.get_time()
        self.delta_time    = self.current_frame - self.last_frame
        self.last_frame    = self.current_frame

        if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_RIGHT):
            mouse_x, mouse_y = glfw.get_cursor_pos(self.window)
            self.camera_front = self.camera.rotate(mouse_x, mouse_y)
        else:
            self.camera.first_mouse = True
        self.camera_pos = self.camera.translate(self.camera_pos, self.camera_front, self.camera_up, self.delta_time)
        view_mat   = glm.lookAt(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)

        proj_mat  = glm.perspective(glm.radians(self.camera.fov), self.viewport[0] / self.viewport[1], 0.1, 100.0)

        # retrieve the matrix uniform locations
        view_location  = glGetUniformLocation(shader.id, "view")

        # note: currently we set the projection matrix each frame,
        # but since the projection matrix rarely changes,
        # it's often best practice to set it outside the main loop only once.
        shader.set_mat4("projection", proj_mat)
        
        # pass them to the shaders
        glUniformMatrix4fv(view_location, 1, GL_FALSE, glm.value_ptr(view_mat))

        # render container
        glBindVertexArray(self.VAO)

        # create transformations
        model_mat_list = []

        if self.task == 0:
            model_mat = glm.mat4(1.0)   # make sure to initialize matrix to identity matrix first
            model_mat = glm.rotate(model_mat, glm.radians(-55.0), glm.vec3(1.0, 0.0, 0.0))

            model_mat_list.append(model_mat)

        elif self.task == 1:
            model_mat = glm.mat4(1.0)
            model_mat = glm.rotate(model_mat, glfw.get_time() * glm.radians(50.0), glm.vec3(0.5, 1.0, 0.0))
            model_mat_list.append(model_mat)

        elif self.task == 2:
            for i in range(len(self.cube_positions)):
                tmp_mat = glm.mat4(1.0)
                tmp_mat = glm.translate(tmp_mat, self.cube_positions[i])
                angle = 20.0 * i
                tmp_mat = glm.rotate(tmp_mat, glm.radians(angle), glm.vec3(1.0, 0.3, 0.5))
                model_mat_list.append(tmp_mat)


        for i in range(len(model_mat_list)):
            shader.set_mat4("model", model_mat_list[i])
            
            if self.EBO is None:
                glDrawArrays(GL_TRIANGLES, 0, 36 if self.primitive == 2 else 3)
            if self.EBO is not None:
                glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, ctypes.c_void_p(0)) # last argument is indices that specifies an offset in a buffer
                                                                                        # or a pointer to the location where the indices are stored


    def destroy(self):
        glDeleteVertexArrays(1, self.VAO)
        glDeleteBuffers(1, self.VBO)
        if self.EBO is not None:
            glDeleteBuffers(1, self.EBO)

class Camera:
    def __init__(self, window):
        self.window = window

        self.first_mouse = True

        self.last_x = glfw.get_window_size(window)[0] / 2.0
        self.last_y = glfw.get_window_size(window)[1] / 2.0

        self.yaw   = -90.0
        self.pitch = 0.0
        self.fov   = 45.0

    def translate(self, camera_pos, camera_front, camera_up, delta_time):
        camera_speed = 2.5 * delta_time     # constant speed of 2.5 units per second

        if (glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS):
            return camera_pos + camera_speed * glm.normalize(camera_front)
        if (glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS):
            return camera_pos - camera_speed * glm.normalize(camera_front)
        if (glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS):
            return camera_pos - glm.normalize(glm.cross(camera_front, camera_up)) * camera_speed
        if (glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS):
            return camera_pos + glm.normalize(glm.cross(camera_front, camera_up)) * camera_speed
        
        return camera_pos

    def rotate(self, mouse_x, mouse_y):
        if (self.first_mouse):
            self.last_x = mouse_x
            self.last_y = mouse_y
            self.first_mouse = False
        
        x_offset = mouse_x - self.last_x
        y_offset = self.last_y  - mouse_y
        self.last_x = mouse_x
        self.last_y = mouse_y

        sensitivity = 0.1
        x_offset = sensitivity * x_offset
        y_offset = sensitivity * y_offset

        self.yaw   = self.yaw   + x_offset
        self.pitch = self.pitch + y_offset
        self.pitch = np.clip(self.pitch, -89.0, 89.0)

        front   = glm.vec3()
        front.x = np.cos(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        front.y = np.sin(glm.radians(self.pitch))
        front.z = np.sin(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))

        return glm.normalize(front)

    def get_fov(self, window, x_offset, y_offset):
        self.fov = self.fov - y_offset

        self.fov = np.clip(self.fov, 1.0, 45.0)
        
        return self.fov