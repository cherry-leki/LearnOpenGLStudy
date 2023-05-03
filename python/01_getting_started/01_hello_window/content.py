import os, sys
import glfw
import numpy as np
from OpenGL.GL import *
from PIL import Image

from viewer import GLContent
from visualizer.shader     import Shader
from visualizer.utils      import *


class Content(GLContent):    
    def inspector(self):
        imgui.begin_group()
        imgui.end_group()

    def render(self):
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
    
    def destroy(self):
        return super().destroy()