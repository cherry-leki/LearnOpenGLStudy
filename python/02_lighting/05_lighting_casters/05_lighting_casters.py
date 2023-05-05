import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import numpy as np
import argparse
from PIL import Image

import glfw
from OpenGL.GL import *
import glm
from shader import Shader
from camera import Camera
from utils import *


### Primitives
def set_box():
    vertices = [
                -0.5, -0.5, -0.5,   0.0, 0.0, -1.0,   0.0, 0.0,
                 0.5, -0.5, -0.5,   0.0, 0.0, -1.0,   1.0, 0.0, 
                 0.5,  0.5, -0.5,   0.0, 0.0, -1.0,   1.0, 1.0, 
                 0.5,  0.5, -0.5,   0.0, 0.0, -1.0,   1.0, 1.0, 
                -0.5,  0.5, -0.5,   0.0, 0.0, -1.0,   0.0, 1.0, 
                -0.5, -0.5, -0.5,   0.0, 0.0, -1.0,   0.0, 0.0, 

                -0.5, -0.5,  0.5,   0.0, 0.0, 1.0,    0.0, 0.0,
                 0.5, -0.5,  0.5,   0.0, 0.0, 1.0,    1.0, 0.0,
                 0.5,  0.5,  0.5,   0.0, 0.0, 1.0,    1.0, 1.0,
                 0.5,  0.5,  0.5,   0.0, 0.0, 1.0,    1.0, 1.0,
                -0.5,  0.5,  0.5,   0.0, 0.0, 1.0,    0.0, 1.0,
                -0.5, -0.5,  0.5,   0.0, 0.0, 1.0,    0.0, 0.0,

                -0.5,  0.5,  0.5,  -1.0, 0.0, 0.0,    1.0, 0.0,
                -0.5,  0.5, -0.5,  -1.0, 0.0, 0.0,    1.0, 1.0,
                -0.5, -0.5, -0.5,  -1.0, 0.0, 0.0,    0.0, 1.0,
                -0.5, -0.5, -0.5,  -1.0, 0.0, 0.0,    0.0, 1.0,
                -0.5, -0.5,  0.5,  -1.0, 0.0, 0.0,    0.0, 0.0,
                -0.5,  0.5,  0.5,  -1.0, 0.0, 0.0,    1.0, 0.0,

                 0.5,  0.5,  0.5,   1.0, 0.0, 0.0,    1.0, 0.0,
                 0.5,  0.5, -0.5,   1.0, 0.0, 0.0,    1.0, 1.0,
                 0.5, -0.5, -0.5,   1.0, 0.0, 0.0,    0.0, 1.0,
                 0.5, -0.5, -0.5,   1.0, 0.0, 0.0,    0.0, 1.0,
                 0.5, -0.5,  0.5,   1.0, 0.0, 0.0,    0.0, 0.0,
                 0.5,  0.5,  0.5,   1.0, 0.0, 0.0,    1.0, 0.0,

                -0.5, -0.5, -0.5,   0.0, -1.0, 0.0,   0.0, 1.0,
                 0.5, -0.5, -0.5,   0.0, -1.0, 0.0,   1.0, 1.0,
                 0.5, -0.5,  0.5,   0.0, -1.0, 0.0,   1.0, 0.0,
                 0.5, -0.5,  0.5,   0.0, -1.0, 0.0,   1.0, 0.0,
                -0.5, -0.5,  0.5,   0.0, -1.0, 0.0,   0.0, 0.0,
                -0.5, -0.5, -0.5,   0.0, -1.0, 0.0,   0.0, 1.0,

                -0.5,  0.5, -0.5,   0.0, 1.0, 0.0,    0.0, 1.0,
                 0.5,  0.5, -0.5,   0.0, 1.0, 0.0,    1.0, 1.0,
                 0.5,  0.5,  0.5,   0.0, 1.0, 0.0,    1.0, 0.0,
                 0.5,  0.5,  0.5,   0.0, 1.0, 0.0,    1.0, 0.0,
                -0.5,  0.5,  0.5,   0.0, 1.0, 0.0,    0.0, 0.0,
                -0.5,  0.5, -0.5,   0.0, 1.0, 0.0,    0.0, 1.0,
                ]

    vertices = np.array(vertices, dtype=np.float32)

    return vertices, None


### Textures
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



### experiments variables
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
light_position = glm.vec3(1.2, 1.0, 2.0)


### main
def main(args):
    # glfw: initialize and configure
    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    if (sys.platform == "darwin"):  # for Mac OS. forward compatibility
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    ### camera
    camera = Camera(args.window_width, args.window_height, glm.vec3(0.0, 0.0, 3.0))
 
    # glfw window creation
    window = glfw.create_window(args.window_width, args.window_height, "LearnOpenGL", None, None)
    if window is None:
        print("Failed to create GLFW window")
        glfw.terminate()
        return   

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_cursor_pos_callback(window, camera.mouse_callback)
    glfw.set_scroll_callback(window, camera.zoom)

    # tell glfw to capture mouse
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    # configure global opengl state
    glEnable(GL_DEPTH_TEST)

    # set shader program
    light_caster_names = ['directionallight', 'pointlight', 'spotlight', 'spotlight']
    light_shader       = Shader('05_lighting_casters/05_light.vs', '05_lighting_casters/05_light_{}.fs'.format(light_caster_names[args.task]))
    lamp_shader        = Shader('05_lighting_casters/05_lamp.vs',  '05_lighting_casters/05_lamp.fs')


    # set vertices and indices
    vertices, _ = set_box()
    

    # configure the VBO(EBO)
    VBO = glGenBuffers(1)

    # copy vertices array in a buffer for OpenGL to use
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

    # configure the object's VAO
    light_VAO = glGenVertexArrays(1)
    glBindVertexArray(light_VAO)
    # position attribute
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    # normal attribute
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(3 * sizeof(GLfloat)))
    glEnableVertexAttribArray(1)
    # texture coord attribute
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(6 * sizeof(GLfloat)))
    glEnableVertexAttribArray(2)

    # configure the lamp's VAO (VBO is the same)
    lamp_VAO = glGenVertexArrays(1)
    glBindVertexArray(lamp_VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    # note that we update the lamp's position attribute's stride to reflect the updated buffer data
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # load and create a texture
    diffuse_map  = load_texture("/media/cl/D:/Dooo/FUN/LearnOpenGLStudy/python/02_lighting/test_img/container2.png")
    specular_map = load_texture("/media/cl/D:/Dooo/FUN/LearnOpenGLStudy/python/02_lighting/test_img/container2_specular.png")
 
    light_shader.use()
    light_shader.set_int("material.diffuse",  0)
    light_shader.set_int("material.specular", 1)

    # render loop
    while not glfw.window_should_close(window):
        # per-frame time logic
        current_frame = glfw.get_time()
        camera.delta_time = current_frame - camera.last_frame
        camera.last_frame = current_frame
        camera.translate(window)

        # input
        process_input(window)

        # render
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # light shader
        # be sure to activate shader when setting uniforms/drawing objects
        light_shader.use()
        light_shader.set_vec3("viewPos", camera.position)

        # material properties
        light_shader.set_float("material.shininess", 32)

        # light properties
        # Task 1: Directional light (e.g. sun)
        if args.task == 0:
            # no need to have position because every object has the same light intensity regardless of distance b/w light and itself. 
            light_shader.set_vec3("light.direction", -0.2, -1.0, -0.3)
            
            light_shader.set_vec3("light.ambient",  glm.vec3(0.2))
            light_shader.set_vec3("light.diffuse",  glm.vec3(0.5))
            light_shader.set_vec3("light.specular", glm.vec3(1.0))
        # Task 2: Point light (e.g. light bulbs and torches)
        elif args.task == 1:
            light_shader.set_vec3("light.position", light_position)
            
            light_shader.set_vec3("light.ambient",  glm.vec3(0.2))
            light_shader.set_vec3("light.diffuse",  glm.vec3(0.5))
            light_shader.set_vec3("light.specular", glm.vec3(1.0))

            # attenuation
            light_shader.set_float("light.constant",  1.0)      # distance of 50
            light_shader.set_float("light.linear",    0.09)
            light_shader.set_float("light.quadratic", 0.032)
        # Task 3: Spot light (e.g. street lamp and flashlight)
        elif args.task == 2:
            light_shader.set_vec3("light.position",  camera.position)
            light_shader.set_vec3("light.direction", camera.front)
            light_shader.set_float("light.cutOff",      glm.cos(glm.radians(12.5))) # compare cosine values instead of angle
            light_shader.set_float("light.outerCutOff", glm.cos(glm.radians(12.5)))

            # we configure the diffuse intensity slightly higher
            # the right lighting conditions differ with each lighting method and environment
            # each environment and lighting type requires some tweaking to get the best out of your environment
            light_shader.set_vec3("light.ambient",  glm.vec3(0.1))
            light_shader.set_vec3("light.diffuse",  glm.vec3(0.8))
            light_shader.set_vec3("light.specular", glm.vec3(1.0))

            light_shader.set_float("light.constant",  1.0)
            light_shader.set_float("light.linear",    0.09)
            light_shader.set_float("light.quadratic", 0.032)
        # Task 4: Spot light with smooth/soft edges
        elif args.task == 3:
            light_shader.set_vec3("light.position",  camera.position)
            light_shader.set_vec3("light.direction", camera.front)
            light_shader.set_float("light.cutOff",      glm.cos(glm.radians(12.5))) # compare cosine values instead of angle
            light_shader.set_float("light.outerCutOff", glm.cos(glm.radians(17.5)))

            # we configure the diffuse intensity slightly higher
            # the right lighting conditions differ with each lighting method and environment
            # each environment and lighting type requires some tweaking to get the best out of your environment
            light_shader.set_vec3("light.ambient",  glm.vec3(0.1))
            light_shader.set_vec3("light.diffuse",  glm.vec3(0.8))
            light_shader.set_vec3("light.specular", glm.vec3(1.0))

            light_shader.set_float("light.constant",  1.0)
            light_shader.set_float("light.linear",    0.09)
            light_shader.set_float("light.quadratic", 0.032)
        else:
            raise TypeError("Wrong task number")

        # render container
        glBindVertexArray(light_VAO)        

        # view properties for object shader           
        proj_mat = glm.perspective(glm.radians(camera.fov), args.window_width / args.window_height, 0.1, 100.0)
        view_mat = camera.get_view_matrix()
        light_shader.set_mat4("projection", proj_mat)
        light_shader.set_mat4("view", view_mat)


        # objects
        # texture
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, diffuse_map)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, specular_map)

        # draw
        glBindVertexArray(light_VAO)
        for i in range(len(cube_positions)):
            model = glm.mat4(1.0)
            model = glm.translate(model, cube_positions[i])
            angle = 20.0 * i
            model = glm.rotate(model, glm.radians(angle), glm.vec3(1.0, 0.3, 0.5))
            light_shader.set_mat4("model", model)
            
            glDrawArrays(GL_TRIANGLES, 0, 36)
      
        # draw light cube
        if args.task == 1:
            lamp_shader.use()
            lamp_shader.set_mat4("projection", proj_mat)
            lamp_shader.set_mat4("view", view_mat)

            model_mat = glm.mat4(1.0)
            model_mat = glm.translate(model_mat, light_position)
            model_mat = glm.scale(model_mat, glm.vec3(0.2))
            lamp_shader.set_mat4("model", model_mat)

            lamp_shader.set_vec3("color", glm.vec3(1.0))

            glBindVertexArray(lamp_VAO)
            glDrawArrays(GL_TRIANGLES, 0, 36)
        

        # check and call events and swap the buffers
        glfw.swap_buffers(window)
        glfw.poll_events()

    glDeleteVertexArrays(1, light_VAO)
    glDeleteVertexArrays(1, lamp_VAO)
    glDeleteBuffers(1, VBO)

    # clear all previously allocated GLFW resources
    glfw.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--task", dest="task", default=0, type=int)
    parser.add_argument("-m", "--mode",           dest="polygon_mode",  default="fill")

    parser.add_argument("-ww", "--window_width",  dest="window_width",  default=800)
    parser.add_argument("-wh", "--window_height", dest="window_height", default=600)

    args = parser.parse_args()

    main(args)