import glfw
import glm
import numpy as np

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
        