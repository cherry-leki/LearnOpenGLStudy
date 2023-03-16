# -*- coding: utf-8 -*-
import os, sys
import glfw
from glm import ortho
import imgui
import OpenGL.GL as gl

from PIL import Image
from imgui.integrations.glfw import GlfwRenderer
from shader import *
from utils import *
from primitives import *
from func import *

import numpy as np
import argparse


def main(args):
    imgui.create_context()
    window = impl_glfw_init(args.window_size)
    impl = GlfwRenderer(window)


    # control flags
    primitive_type = 2
    viewpoint      = 0
    cam_roll       = 0
    cam_yaw        = 0
    cam_pitch      = 0
    enable_polygon = False
    task           = 0

    obj_positions = [ 
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


    # render loop
    while not glfw.window_should_close(window):
        glfw.poll_events()
        process_input(window)
        impl.process_inputs()

        # imgui setting
        imgui.new_frame()

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("Menu", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )

                if clicked_quit:
                    exit(1)

                imgui.end_menu()
            imgui.end_main_menu_bar()

        # inspector setting
        inspector_win_size = [300, 300]
        imgui.set_next_window_size(inspector_win_size[0], inspector_win_size[1])
        imgui.set_next_window_position(args.window_size[0] - inspector_win_size[0], 20)
        imgui.begin("Inspector", True)

        imgui.begin_group()
        imgui.text_colored("Play setting", 0.2, 1., 0.)
        _, task = imgui.combo(
            "Task", task, ["one", "rotate", "multiple"]
        )

        _, primitive_type = imgui.combo(
            "Primitive", primitive_type, ["tri", "rect", "box"]
        )

        _, enable_polygon = imgui.checkbox("Polygon mode", enable_polygon)
        imgui.end_group()

        imgui.dummy(0, 10)

        imgui.begin_group()
        imgui.text_colored("Cam setting", 0.2, 1., 0.)
        _, viewpoint = imgui.combo(
            "Viewpoint", viewpoint, ["Perspective", "Orthogonal"]
        )
        imgui.text("Cam rotation")
        _, cam_roll  = imgui.slider_float('Roll',  cam_roll,  -360.0, 360.0, '%.2f', 1.0)
        _, cam_yaw   = imgui.slider_float('Yaw',   cam_yaw,   -360.0, 360.0, '%.2f', 1.0)
        _, cam_pitch = imgui.slider_float('Pitch', cam_pitch, -360.0, 360.0, '%.2f', 1.0)
        reset_rot    = imgui.small_button("reset")
        if reset_rot:
            cam_roll  = 0
            cam_yaw   = 0
            cam_pitch = 0
        imgui.end_group()

        imgui.end()


        # opengl render
        gl.glEnable(GL_DEPTH_TEST)

        shader_program = Shader(args.vtx_shader, args.frag_shader)

        primitive_program = Primitive()
        vertices, indices = primitive_program.get_primitive(primitive_type)
        if (vertices is None) and (indices is None):
            print("Please write target primitive ('triangle', 'rect', 'rect')")
            exit()
            
        # set up vertex data (and buffer(s)) and configure vertex attributes
        VAO = set_VAO(vertices, indices)

        # set polygon mode
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if enable_polygon else GL_FILL)
        
        # render
        glClearColor(0.2, 0.3, 0.3, 1.0)                    # background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # also clear the depth buffer now


        # textures
        # load and create a texture
        # bind textures on corresponding texture units        
        texture_list = []
        for i in range(np.size(args.img_file_path)):
            texture_list.append([load_texture(args.img_file_path[i]), "texture" + str(i + 1)])

        # tell opengl for each sampler to which texture unit it belongs to (only has to be done once)
        shader_program.use()    # don't forget to activate/use the shader before setting uniforms!
        for i in range(0, len(texture_list)):
            shader_program.set_int(texture_list[i][1], i)

        for i in range(len(texture_list)):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, texture_list[i][0])


        # create transformations
        ratio     = args.window_size[0] / args.window_size[1]
        proj_mat  = (glm.perspective(glm.radians(45.0), ratio, 0.1, 100.0) if viewpoint == 0 
                    else glm.ortho(-2.0, 2.0, -2.0 / ratio, 2.0 / ratio, -1000.0, 1000.0))

        view_mat  = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, -3.0))
        view_mat  = glm.rotate(view_mat, glm.radians(cam_roll),  glm.vec3(1.0, 0.0, 0.0))
        view_mat  = glm.rotate(view_mat, glm.radians(cam_yaw),   glm.vec3(0.0, 1.0, 0.0))
        view_mat  = glm.rotate(view_mat, glm.radians(cam_pitch), glm.vec3(0.0, 0.0, 1.0))

        # pass transformation matrices to the shader
        shader_program.set_mat4("projection", proj_mat)
        shader_program.set_mat4("view",       view_mat)

        # render container
        glBindVertexArray(VAO)

        model_mat = []
        if task == 0:
            model_mat.append(glm.rotate(glm.mat4(1.0), glm.radians(-55.0), glm.vec3(1.0, 0.0, 0.0)))
        elif task == 1:
            model_mat.append(glm.rotate(glm.mat4(1.0), glfw.get_time() * glm.radians(50.0), glm.vec3(0.5, 1.0, 0.0)))
        elif task == 2:            
            for i in range(len(obj_positions)):
                angle = glm.radians(20.0 * i)
                
                tmp_model_mat = glm.translate(glm.mat4(1.0), obj_positions[i])
                tmp_model_mat = glm.rotate(tmp_model_mat, angle, glm.vec3(1.0, 0.3, 0.5))

                model_mat.append(tmp_model_mat)   
        else:
            print("Select task type")
            exit()

        for i in range(len(model_mat)):
            shader_program.set_mat4("model", model_mat[i])

            if indices is None:
                glDrawArrays(GL_TRIANGLES, 0, 36 if primitive_type == 2 else 3)
            if indices is not None:
                glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, ctypes.c_void_p(0))    


        # render and swap buffers
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file_path", nargs='+', dest="img_file_path", default=["./test_img/container.jpg", "./test_img/awesomeface.png"])
    
    parser.add_argument("-w", "--window_size",  dest="window_size", default=[1280, 720])
    
    parser.add_argument("-vs", "--vtx_shader",  dest="vtx_shader",  default="shader/vtx_shader.vs")
    parser.add_argument("-fs", "--frag_shader", dest="frag_shader", default="shader/frag_shader.fs")

    args = parser.parse_args()

    main(args)