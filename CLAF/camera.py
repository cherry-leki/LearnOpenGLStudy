import glm
from enum import Enum

class CAMERA_MOVE(Enum):
    FORWARD  = 1
    BACKWARD = 2 
    LEFT     = 3
    RIGHT    = 4


class Camera:
    def __init__(self, position=glm.vec3(0.0, 0.0, 0.0), up=(0.0, 1.0, 0.0), front=glm.vec3(0.0, 0.0, -1.0),
                 yaw=-90, pitch=0.0, movement_speed=2.5, mouse_sensitivity=0.1, fov=45.0):
        self.position    = position
        self.front       = front
        self.up          = up
        self.right       = glm.vec3()
        self.world_up    = up

        # euler angles
        self.yaw         = yaw
        self.pitch       = pitch

        # camera options
        self.speed       = movement_speed
        self.sensitivity = mouse_sensitivity
        self.fov         = fov


    def update_camera_vectors(self):
        front = glm.vec3()
        front.x = glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.yaw))
        front.y = glm.sin(glm.radians(self.pitch))
        front.z = glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))

        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up    = glm.normalize(glm.cross(self.right, self.front))


    def get_view_mat(self):
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def move(self, camera_move, delta_time):
        velocity = self.speed * delta_time
        if (camera_move == CAMERA_MOVE.FORWARD):
            self.position = self.position + (self.front * velocity)
        if (camera_move == CAMERA_MOVE.BACKWARD):
            self.position = self.position - (self.front * velocity)
        if (camera_move == CAMERA_MOVE.LEFT):
            self.position = self.position - (self.right * velocity)
        if (camera_move == CAMERA_MOVE.RIGHT):
            self.position = self.position + (self.right * velocity)

    def rotate(self, x_offset, y_offset, constrain_pitch = True):
        x_offset = x_offset * self.sensitivity
        y_offset = y_offset * self.sensitivity

        self.yaw   = self.yaw   + x_offset
        self.pitch = self.pitch + y_offset

        if (constrain_pitch):
            self.pitch = glm.clamp(self.pitch, -89.0, 89.0)
        
        self.update_camera_vectors()

    def zoom(self, y_offset):
        self.fov = self.fov - y_offset

        self.fov = glm.clamp(self.fov, 1.0, 45.0)

