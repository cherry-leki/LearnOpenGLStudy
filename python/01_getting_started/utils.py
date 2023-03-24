import glfw
import glm
from OpenGL.GL import *
from math import *

### functions
# whenever the window size changed (by OS or user) this callback function executes
def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)

# process all input
# : query GLFW whether relevant keys are pressed/released this frame and react accordingly
def process_input(window):
    if(glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS):
        glfw.set_window_should_close(window, True)


class Camera:
    def __init__(self, window):
        self.window = window

        self.first_mouse = True

        self.last_x = glfw.get_window_size(window)[0] / 2.0
        self.last_y = glfw.get_window_size(window)[1] / 2.0

        self.yaw   = -90.0
        self.pitch = 0.0

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

        if (self.pitch > 89.0):
            self.pitch = 89.0
        if (self.pitch < -89.0):
            self.pitch = -89.0

        front   = glm.vec3()
        front.x = cos(glm.radians(self.yaw)) * cos(glm.radians(self.pitch))
        front.y = sin(glm.radians(self.pitch))
        front.z = sin(glm.radians(self.yaw)) * cos(glm.radians(self.pitch))

        return glm.normalize(front)

    def get_fov(self, x_offset, y_offset):
        fov = fov - y_offset
        if fov < 1.0:
            fov = 1.0
        if fov > 45.:
            fov = 45.0
        
        return fov

        