import glfw
import glm
from enum import Enum

# Default camera values
YAW         = -90.0
PITCH       = 0.0
SPEED       = 2.5
SENSITIVITY = 0.1
ZOOM        = 45.0

class MOVEMODE(Enum):
    GUI      = 0
    KEYBOARD = 1

class Camera:
    def __init__(self, window_width, window_height,
                       position = glm.vec3(0.0, 0.0, 0.0),
                       up       = glm.vec3(0.0, 1.0, 0.0),
                       yaw      = YAW,
                       pitch    = PITCH):
        self.position = position
        self.front    = glm.vec3(0.0, 0.0, -1.0)
        self.up       = glm.vec3(0.0, 0.0, 0.0)
        self.right    = glm.vec3(0.0, 0.0, 0.0)
        self.world_up = up
        self.yaw      = yaw
        self.pitch    = pitch
        
        self.move_speed = SPEED
        self.move_sense = SENSITIVITY
        self.fov        = ZOOM

        self.first_mouse = True
        self.last_x = window_width  / 2.0
        self.last_y = window_height / 2.0

        self.delta_time  = 0.0
        self.last_frame  = 0.0

        self.move_mode = MOVEMODE.GUI

        self._update_camera_vectors()


    def _update_camera_vectors(self):
        # compute the new front vector
        front = glm.vec3()
        front.x = glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        front.y = glm.sin(glm.radians(self.pitch))
        front.z = glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)

        # re-compute the right and up vector
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up    = glm.normalize(glm.cross(self.right, self.front))
        

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def translate(self, window):
        if (self.move_mode == MOVEMODE.GUI.value): return

        velocity = self.move_speed * self.delta_time
        if (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS):
            self.position += self.front * velocity
        if (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS):
            self.position -= self.front * velocity
        if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS):
            self.position -= self.right * velocity
        if (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS):
            self.position += self.right * velocity
    
    def rotate(self, x_offset, y_offset, contrain_pitch=True):
        if (self.move_mode == MOVEMODE.GUI.value): return

        x_offset *= self.move_sense
        y_offset *= self.move_sense

        self.yaw   += x_offset
        self.pitch += y_offset

        if (contrain_pitch):
            self.pitch = glm.clamp(self.pitch, -89.0, 89.0)

        self._update_camera_vectors()

    def zoom(self, window, x_offset, y_offset):
        if (self.move_mode == MOVEMODE.GUI.value): return

        self.fov -= y_offset
        self.fov = glm.clamp(self.fov, 1.0, 45.0)

    def mouse_callback(self, window, x_pos_in, y_pos_in):
        if (glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT)):
            x_pos = x_pos_in
            y_pos = y_pos_in

            if (self.first_mouse):
                self.last_x = x_pos
                self.last_y = y_pos
                self.first_mouse = False
            
            x_offset = x_pos - self.last_x
            y_offset = self.last_y - y_pos

            self.last_x = x_pos
            self.last_y = y_pos

            
            self.rotate(x_offset, y_offset)
        else:
            self.first_mouse = True

    def set_rotation(self, rotation):
        self.yaw   = rotation[1]
        self.pitch = rotation[0]

        self._update_camera_vectors()