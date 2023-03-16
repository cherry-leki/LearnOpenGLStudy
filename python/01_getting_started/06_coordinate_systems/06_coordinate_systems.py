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
    window = glfw.create_window(800, 600, "LearnOpenGL", None, None)
    if window is None:
        print("Failed to create GLFW window")
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    # configure global opengl state
    glEnable(GL_DEPTH_TEST)

    # set shader program
    shader_program = Shader('06_coordinate_systems/06_vtx_shader.vs', '06_coordinate_systems/06_frag_shader.fs')


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
    # note that this is allowed, the call to glVertexAttribPointer registered VBO
    # as the vertex attribute's bound vertex bound object so afterwards we can safely unbind
    # glBindBuffer(GL_ARRAY_BUFFER, 0)

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if args.polygon_mode == "wire" else GL_FILL)


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
        
        view_mat  = glm.mat4(1.0)
        view_mat  = glm.translate(view_mat, glm.vec3(0.0, 0.0, -3.0))

        proj_mat  = glm.mat4(1.0)
        proj_mat  = glm.perspective(glm.radians(45.0), 800.0 / 600.0, 0.1, 100.0)

        # retrieve the matrix uniform locations
        view_location  = glGetUniformLocation(shader_program.id, "view")

        # note: currently we set the projection matrix each frame,
        # but since the projection matrix rarely changes,
        # it's often best practice to set it outside the main loop only once.
        shader_program.set_mat4("projection", proj_mat)
        
        # pass them to the shaders
        glUniformMatrix4fv(view_location, 1, GL_FALSE, glm.value_ptr(view_mat))

        # create transformations
        model_mat = glm.mat4(1.0)   # make sure to initialize matrix to identity matrix first
        if args.task == 1:
            model_mat = glm.rotate(model_mat, glm.radians(-55.0), glm.vec3(1.0, 0.0, 0.0))

            model_location = glGetUniformLocation(shader_program.id, "model")
            glUniformMatrix4fv(model_location, 1, GL_FALSE, glm.value_ptr(model_mat))

            
            # render container
            glBindVertexArray(VAO)
            if EBO is None:
                glDrawArrays(GL_TRIANGLES, 0, 36 if args.primitive == "box" else 3)
            if EBO is not None:
                glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, ctypes.c_void_p(0)) # last argument is indices that specifies an offset in a buffer
                                                                                    # or a pointer to the location where the indices are stored
        elif args.task == 2:
            model_mat = glm.rotate(model_mat, glfw.get_time() * glm.radians(50.0), glm.vec3(0.5, 1.0, 0.0))

            model_location = glGetUniformLocation(shader_program.id, "model")
            glUniformMatrix4fv(model_location, 1, GL_FALSE, glm.value_ptr(model_mat))

            
            # render container
            glBindVertexArray(VAO)
            if EBO is None:
                glDrawArrays(GL_TRIANGLES, 0, 36 if args.primitive == "box" else 3)
            if EBO is not None:
                glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, ctypes.c_void_p(0)) # last argument is indices that specifies an offset in a buffer
                                                                                    # or a pointer to the location where the indices are stored
        elif args.task == 3:
            cube_position = [ 
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

            # render container
            glBindVertexArray(VAO)

            for i in range(10):
                model = glm.mat4(1)
                model = glm.translate(model, cube_position[i])
                angle = 20.0 * i
                model = glm.rotate(model, glm.radians(angle), glm.vec3(1.0, 0.3, 0.5))
                shader_program.set_mat4("model", model)

                
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

    parser.add_argument("--task", dest="task", default=1, type=float)
    parser.add_argument("-p", "--primitive", dest="primitive",     default="tri")
    parser.add_argument("-m", "--mode",      dest="polygon_mode",  default="fill")
    parser.add_argument("-f", "--file_path", nargs='+', dest="img_file_path", default=["../test_img/container.jpg", "../test_img/awesomeface.png"])

    args = parser.parse_args()

    main(args)