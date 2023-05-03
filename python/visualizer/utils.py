import os, sys
import glob
import glfw
import imgui

from OpenGL.GL import *
from PIL import Image

### functions
# whenever the window size changed (by OS or user) this callback function executes
def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)

# process all input
# : query GLFW whether relevant keys are pressed/released this frame and react accordingly
def process_input(window):
    if(glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS):
        glfw.set_window_should_close(window, True)


def impl_glfw_init(window_size):
    width  = window_size[0]
    height = window_size[1]
    window_name = "visualizer"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE) 
    if (sys.platform == "darwin"):  # for Mac OS. forward compatibility
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
    )
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window


def get_tutorial_file_list():
    path = "../**/**/content.py"

    tutorial_file_list = glob.glob(path)

    file_dir_list  = []
    chap_name_list = []
    for file in tutorial_file_list:        
        chapter_name = file.split("/")[-2]
        folder_name  = file.split("/")[-3]

        file_dir_list.append(os.path.abspath(file.split("content.py")[0]))
        chap_name_list.append(folder_name + "/" + chapter_name)

    return file_dir_list, chap_name_list


def get_img_list(file_path):
    img_path_list = glob.glob(os.path.join(file_path, "*.jpg"))
    img_path_list.extend(glob.glob(os.path.join(file_path, "*.png")))

    img_name_list = ["None"]
    for img in img_path_list:
        img_name_list.append(img.split("/")[-1])

    return img_path_list, img_name_list


def load_texture(file_path):
    texture = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, texture)   # all upcoming GL_TEXTURE_2D operations now have effect on this texture object
    
    # set the texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)    # set texture wrapping to GL_REPEAT (default wrapping method)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # set texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    img = Image.open(file_path)
    img_w, img_h, img_data = img.size[0], img.size[1], img.tobytes("raw", "RGBA", 0, -1)
    if(img_data):
        # Note that 7th parameter(color type) is same as the img's color type
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_w, img_h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
    else:
        print("Failed to load texture")
    
    return texture


class imgui_ext:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def title_bar(text, color = "00BCD499"):
        window_size = imgui.get_window_size()

        draw_list = imgui.get_window_draw_list()
        pos = imgui.get_cursor_screen_pos()
        draw_list.add_rect_filled(pos[0]-10, pos[1],
                                  pos[0] + window_size[0],
                                  pos[1] + 15,
                                  int.from_bytes(bytearray.fromhex(color), byteorder='little'))
        imgui.text(text)