import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import numpy as np
import argparse
from PIL import Image

import glfw
from OpenGL.GL import *
import glm
from shader import Shader
from utils import *

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

# vertices, indices setting
def set_triangle():
    vertices = [  # positions        # texture coords
                 -0.5, -0.5,  0.0,   0.0, 0.0,
                  0.5, -0.5,  0.0,   1.0, 0.0,
                  0.0,  0.5,  0.0,   0.5, 1.0
               ]
    vertices = np.array(vertices, dtype=np.float32)

    return vertices, None

def set_rectangle():
    vertices = [  # positions        # texture coords
                  0.5,  0.5,  0.0,   1.0, 1.0,   # top right
                  0.5, -0.5,  0.0,   1.0, 0.0,   # bottom right
                 -0.5, -0.5,  0.0,   0.0, 0.0,   # bottom left
                 -0.5,  0.5,  0.0,   0.0, 1.0    # top left
               ]
    vertices = np.array(vertices, dtype=np.float32)

    indices = [ 0, 1, 3,
                1, 2, 3 ]
    indices = np.array(indices, dtype=np.uint32)

    return vertices, indices

def set_box():
    vertices = [
                -0.5, -0.5, -0.5,  0.0, 0.0,
                 0.5, -0.5, -0.5,  1.0, 0.0,
                 0.5,  0.5, -0.5,  1.0, 1.0,
                 0.5,  0.5, -0.5,  1.0, 1.0,
                -0.5,  0.5, -0.5,  0.0, 1.0,
                -0.5, -0.5, -0.5,  0.0, 0.0,

                -0.5, -0.5,  0.5,  0.0, 0.0,
                 0.5, -0.5,  0.5,  1.0, 0.0,
                 0.5,  0.5,  0.5,  1.0, 1.0,
                 0.5,  0.5,  0.5,  1.0, 1.0,
                -0.5,  0.5,  0.5,  0.0, 1.0,
                -0.5, -0.5,  0.5,  0.0, 0.0,

                -0.5,  0.5,  0.5,  1.0, 0.0,
                -0.5,  0.5, -0.5,  1.0, 1.0,
                -0.5, -0.5, -0.5,  0.0, 1.0,
                -0.5, -0.5, -0.5,  0.0, 1.0,
                -0.5, -0.5,  0.5,  0.0, 0.0,
                -0.5,  0.5,  0.5,  1.0, 0.0,

                 0.5,  0.5,  0.5,  1.0, 0.0,
                 0.5,  0.5, -0.5,  1.0, 1.0,
                 0.5, -0.5, -0.5,  0.0, 1.0,
                 0.5, -0.5, -0.5,  0.0, 1.0,
                 0.5, -0.5,  0.5,  0.0, 0.0,
                 0.5,  0.5,  0.5,  1.0, 0.0,

                -0.5, -0.5, -0.5,  0.0, 1.0,
                 0.5, -0.5, -0.5,  1.0, 1.0,
                 0.5, -0.5,  0.5,  1.0, 0.0,
                 0.5, -0.5,  0.5,  1.0, 0.0,
                -0.5, -0.5,  0.5,  0.0, 0.0,
                -0.5, -0.5, -0.5,  0.0, 1.0,

                -0.5,  0.5, -0.5,  0.0, 1.0,
                 0.5,  0.5, -0.5,  1.0, 1.0,
                 0.5,  0.5,  0.5,  1.0, 0.0,
                 0.5,  0.5,  0.5,  1.0, 0.0,
                -0.5,  0.5,  0.5,  0.0, 0.0,
                -0.5,  0.5, -0.5,  0.0, 1.0
                ]

    vertices = np.array(vertices, dtype=np.float32)

    return vertices, None


cube_positions = [ 
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



### main
def main(args):
    # initialize GLFW
    glfw.init()

    # glfw configuration
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    if (sys.platform == "darwin"):  # for Mac OS. forward compatibility
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
 
    # glfw window creation
    window = glfw.create_window(args.window_width, args.window_height, "LearnOpenGL", None, None)
    if window is None:
        print("Failed to create GLFW window")
        glfw.terminate()
        return
    
    camera = Camera(window)

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    # configure global opengl state
    glEnable(GL_DEPTH_TEST)

    # set shader program
    shader_program = Shader('07_camera/07_vtx_shader.vs', '07_camera/07_frag_shader.fs')


    # select primitive type
    if args.primitive == "tri":
        vertices, indices = set_triangle()
    elif args.primitive == "rect":
        vertices, indices = set_rectangle()
    elif args.primitive == "box":
        vertices, indices = set_box()
    else :
        print("Please write target primitive ('triangle', 'rect')")
        exit()
    

    # set up vertex data (and buffer(s)) and configure vertex attributes
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1) if indices is not None else None

    # bind the Vertex Array Object first, then bind and set vertex buffer(s),
    # and then configure vertex attribute(s)
    glBindVertexArray(VAO)

    # copy vertices array in a buffer for OpenGL to use
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

    if EBO is not None:
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices, GL_STATIC_DRAW)

    # position attribute
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    # texture coord attribute
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), ctypes.c_void_p(3 * sizeof(GLfloat)))
    glEnableVertexAttribArray(1)


    # load and create a texture
    texture_list = []
    for i in range(np.size(args.img_file_path)):
        texture_list.append([load_texture(args.img_file_path[i]), "texture" + str(i + 1)])

    # tell opengl for each sampler to which texture unit it belongs to (only has to be done once)
    shader_program.use()    # don't forget to activate/use the shader before setting uniforms!
    shader_program.set_int("textureNum", len(texture_list))
    for i in range(0, len(texture_list)):
        shader_program.set_int(texture_list[i][1], i)

    # Binding 0 as a buffer resets the currently bound buffer to a NULL-like state
    # note that this is allowed, the cafrom inspect import currentframe
    # variables for camera setting
    camera_pos   = glm.vec3(0.0, 0.0, 3.0)
    camera_front = glm.vec3(0.0, 0.0, -1.0)
    camera_up    = glm.vec3(0.0, 1.0, 0.0)
    delta_time   = 0                            # time between current frame and last frame
    last_frame   = 0                            # time of last frame

    # render loop
    while not glfw.window_should_close(window):
        # input
        process_input(window)

        # render
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # also clear the depth buffer now

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
        current_frame = glfw.get_time()
        delta_time    = current_frame - last_frame
        last_frame    = current_frame

        if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT):
            mouse_x, mouse_y = glfw.get_cursor_pos(window)
            camera_front = camera.rotate(mouse_x, mouse_y)
        else:
            camera.first_mouse = True
        camera_pos = camera.translate(camera_pos, camera_front, camera_up, delta_time)
        view_mat   = glm.lookAt(camera_pos, camera_pos + camera_front, camera_up)

        proj_mat  = glm.perspective(glm.radians(45.0), args.window_width / args.window_height, 0.1, 100.0)

        # retrieve the matrix uniform locations
        view_location  = glGetUniformLocation(shader_program.id, "view")

        # note: currently we set the projection matrix each frame,
        # but since the projection matrix rarely changes,
        # it's often best practice to set it outside the main loop only once.
        shader_program.set_mat4("projection", proj_mat)
        
        # pass them to the shaders
        glUniformMatrix4fv(view_location, 1, GL_FALSE, glm.value_ptr(view_mat))

        # render container
        glBindVertexArray(VAO)

        # create transformations
        model_mat_list = []

        if args.task == 1:
            model_mat = glm.mat4(1.0)   # make sure to initialize matrix to identity matrix first
            model_mat = glm.rotate(model_mat, glm.radians(-55.0), glm.vec3(1.0, 0.0, 0.0))

            model_mat_list.append(model_mat)

        elif args.task == 2:
            model_mat = glm.mat4(1.0)
            model_mat = glm.rotate(model_mat, glfw.get_time() * glm.radians(50.0), glm.vec3(0.5, 1.0, 0.0))
            model_mat_list.append(model_mat)

        elif args.task == 3:
            for i in range(len(cube_positions)):
                tmp_mat = glm.mat4(1.0)
                tmp_mat = glm.translate(tmp_mat, cube_positions[i])
                angle = 20.0 * i
                tmp_mat = glm.rotate(tmp_mat, glm.radians(angle), glm.vec3(1.0, 0.3, 0.5))
                model_mat_list.append(tmp_mat)


        for i in range(len(model_mat_list)):
            shader_program.set_mat4("model", model_mat_list[i])
            
            if EBO is None:
                glDrawArrays(GL_TRIANGLES, 0, 36 if args.primitive == "box" else 3)
            if EBO is not None:
                glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, ctypes.c_void_p(0)) # last argument is indices that specifies an offset in a buffer
                                                                                        # or a pointer to the location where the indices are stored


        # check and call events and swap the buffers
        glfw.swap_buffers(window)
        glfw.poll_events()

    glDeleteVertexArrays(1, VAO)
    glDeleteBuffers(1, VBO)
    if EBO is not None:
        glDeleteBuffers(1, EBO)

    # clear all previously allocated GLFW resources
    glfw.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--task", dest="task", default=3, type=float)
    parser.add_argument("-p", "--primitive", dest="primitive",     default="box")
    parser.add_argument("-m", "--mode",      dest="polygon_mode",  default="fill")
    parser.add_argument("-f", "--file_path", nargs='+', dest="img_file_path", default=["../test_img/container.jpg", "../test_img/awesomeface.png"])

    parser.add_argument("-ww", "--window_width",  dest="window_width",  default=800)
    parser.add_argument("-wh", "--window_height", dest="window_height", default=600)

    args = parser.parse_args()

    main(args)