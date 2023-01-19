# example of blinking colors and adding offsets with uniform variable
import os
import sys
import numpy as np
import argparse

import glfw
from OpenGL.GL import *


### shaders
vs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "0301_vertex_shader.vs")
# fs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "0301_fragment_shader.fs")
fs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "0301_uniform_fragment_shader.fs")

vertex_shader_source   = open(vs_path, 'r').read()
fragment_shader_source = open(fs_path, 'r').read()


### functions
# whenever the window size changed (by OS or user) this callback function executes
def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)

# process all input
# : query GLFW whether relevant keys are pressed/released this frame and react accordingly
def process_input(window):
    if(glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS):
        glfw.set_window_should_close(window, True)

# set shader program
def set_shader_program():
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_shader_source) # in pyopengl, we don't need to how many strings we passing as src code
    glCompileShader(vertex_shader)

    # check for shader compile errors
    success = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
    if not success:
        info_log = glGetShaderInfoLog(vertex_shader)
        print("ERROR:SHADER::VERTEX::COMPILATION_FAILED ", info_log)

    # fragment shader
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_shader_source)
    glCompileShader(fragment_shader)

    # check for shader compile errors
    success = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
    if not success:
        info_log = glGetShaderInfoLog(fragment_shader)
        print("ERROR:SHADER::FRAGMENT::COMPILATION_FAILED ", info_log)

    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)
    
    success = glGetProgramiv(shader_program, GL_LINK_STATUS)
    if not success:
        info_log = glGetProgramInfoLog(shader_program)
        print("ERROR::SHADER::PROGRAM::LINKING_FAILED ", info_log)

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return shader_program

# vertices, indices setting
def set_triangle():
    vertices = [ -0.5, -0.5,  0.0,
                  0.5, -0.5,  0.0,
                  0.0,  0.5,  0.0 ]
    vertices = np.array(vertices, dtype=np.float32)

    return vertices, None

def set_rectangle():
    vertices = [  0.5,  0.5,  0.0,
                  0.5, -0.5,  0.0,
                 -0.5, -0.5,  0.0,
                 -0.5,  0.5,  0.0 ]
    vertices = np.array(vertices, dtype=np.float32)

    indices = [ 0, 1, 3,
                1, 2, 3 ]
    indices = np.array(indices, dtype=np.uint32)

    return vertices, indices


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


    # set shader program
    shader_program = set_shader_program()


    # set up vertex data (and buffer(s)) and configure vertex attributes
    if args.primitive == "tri":
        vertices, indices = set_triangle()
    elif args.primitive == "rect":
        vertices, indices = set_rectangle()
    else :
        print("Please write target primitive ('triangle', 'rect')")
        exit()
    
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

    # set the vertex attributes pointers
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)    # specify the index of the vertex attribute to be enabled

    # Binding 0 as a buffer resets the currently bound buffer to a NULL-like state
    # note that this is allowed, the call to glVertexAttribPointer registered VBO
    # as the vertex attribute's bound vertex bound object so afterwards we can safely unbind
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    
    # do NOT unbine the EBO while a VAO is active as the bound element buffer is stored in the VAO; keep the EBO bound
    # VAO store the glBindBuffer calls when the target is GL_ELEMENT_ARRAY_BUFFER, which menas it stores its unbind calls
    # if EBO is not None:
    #     glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    # bind vertex array object
    #  Any subsequent VBO, EBO, glVertexAttribPointer, and glEnalbeVertexAttribArray calls will be stored inside the VAO.
    #  The role of VAO is just for managing vertex attributes, and we can use VBO only by calling glEnableVertexAttribArray.
    #  (see how to use VBO without VAO in 02_hello_triangle_noVAO.py)
    #  So, we don't need to use glBindVertexArray function here and in the while loop to run this simple triangle example.
    glBindVertexArray(0)

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if args.polygon_mode == "wire" else GL_FILL)


    # render loop
    while not glfw.window_should_close(window):
        # input
        process_input(window)

        # render
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # draw
        glUseProgram(shader_program)

        horizontal_offset = glGetUniformLocation(shader_program, "offsetPos")
        glUniform3f(horizontal_offset, args.translate_offset[0], args.translate_offset[1], args.translate_offset[2])

        # update the uniform color
        time_value = glfw.get_time()
        green_value = np.sin(time_value) / 2.0 + 0.5
        vertex_color_location = glGetUniformLocation(shader_program, "ourColor")
        glUniform4f(vertex_color_location, 0, green_value, 0, 1)

        glBindVertexArray(VAO)
        if EBO is None:
            glDrawArrays(GL_TRIANGLES, 0, 3)
        if EBO is not None:
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, ctypes.c_void_p(0)) # last argument is indices that specifies an offset in a buffer
                                                                                 # or a pointer to the location where the indices are stored
        # print(ctypes.c_void_p(0))
        glBindVertexArray(0)

        # check and call events and swap the buffers
        glfw.swap_buffers(window)
        glfw.poll_events()

    glDeleteVertexArrays(1, VAO)
    glDeleteBuffers(1, VBO)
    if EBO is not None:
        glDeleteBuffers(1, EBO)
    glDeleteProgram(shader_program)

    # clear all previously allocated GLFW resources
    glfw.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--primitive", dest="primitive", default="tri")
    parser.add_argument("-m", "--mode", dest="polygon_mode", default="fill")
    parser.add_argument("-o", "--offset", dest="translate_offset", default=[0, 0, 0], type=float, nargs=3)

    args = parser.parse_args()

    main(args)