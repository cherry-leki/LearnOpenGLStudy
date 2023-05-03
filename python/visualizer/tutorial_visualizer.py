# -*- coding: utf-8 -*-
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import argparse
import importlib

import glfw
import imgui
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer

from camera import *
from utils import *
from func import *


def main(args):
    # create window
    imgui.create_context()
    window = impl_glfw_init(args.window_size)
    viewport_size = [args.window_size[0] - 300, args.window_size[1]]
    impl   = GlfwRenderer(window)


    # Variables
    # camera
    cam = Camera(args.window_size[0], args.window_size[1], glm.vec3(0.0, 0.0, 3.0))
    glfw.set_cursor_pos_callback(window, cam.mouse_callback)
    glfw.set_scroll_callback(window, cam.zoom)
    cam_mode = 0
    cam_pos = [0, 0, 0]
    cam_rot = [0, 0, 0]

    # visualize
    wire_mode = False

    # tutorial file list and currently rendered file
    file_dir_list, file_chap_list = get_tutorial_file_list()
    chapter      = 0
    chapter_name = "01_getting_started/01_hellow_window"
    file_dir     = file_dir_list[chapter]
    cur_file     = importlib.import_module("01_getting_started.01_hello_window.content")
    cur_file     = getattr(cur_file, 'Content')(window, viewport_size, cam, file_dir)


    # render loop
    while not glfw.window_should_close(window):
        glfw.poll_events()
        process_input(window)
        impl.process_inputs()
        
        glViewport(args.window_size[0] - 300, 0, 300, args.window_size[1])
        glScissor(args.window_size[0] - 300, 0, 300, args.window_size[1])
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

        # inspector initialize
        inspector_win_size = [300, args.window_size[1] - 20]
        imgui.set_next_window_size(inspector_win_size[0], inspector_win_size[1])
        imgui.set_next_window_position(args.window_size[0] - inspector_win_size[0], 20)
        imgui.begin("Inspector", True)

        # main setting
        imgui.begin_group()
        imgui_ext.title_bar("Main Setting")
        imgui.dummy(0, 5)
        
        # camera setting
        imgui.text("Cam setting")
        changed_cam_mode, cam_mode = imgui.combo(
            " mode", cam_mode, ["GUI", "Keyboard"]
        )
        if changed_cam_mode:
            if cam_mode == 0:
                cam_pos = cam.position
                cam_rot[1] = cam.yaw
                cam_rot[2] = cam.pitch

        if cam_mode == 0:
            imgui.text("Cam position")
            imgui.same_line()
            reset_pos   = imgui.small_button("reset pos")
            if reset_pos:
                cam_pos = [0, 0, 0]
            imgui.push_item_width(140)
            _, cam_pos[0] = imgui.input_float('X', cam_pos[0], 0.1, 0.1, format='%.1f')
            _, cam_pos[1] = imgui.input_float('Y', cam_pos[1], 0.1, 0.1, format='%.1f')
            _, cam_pos[2] = imgui.input_float('Z', cam_pos[2], 0.1, 0.1, format='%.1f')
            imgui.pop_item_width()

            imgui.text("Cam rotation")
            imgui.same_line()            
            reset_rot   = imgui.small_button("reset rot")
            if reset_rot:
                cam_rot = [0, 0, 0]            
            imgui.push_item_width(120)
            _, cam_rot[0] = imgui.slider_float('Roll',  cam_rot[0], -360.0, 360.0, '%.2f', 1.0)
            _, cam_rot[1] = imgui.slider_float('Yaw',   cam_rot[1], -360.0, 360.0, '%.2f', 1.0)
            _, cam_rot[2] = imgui.slider_float('Pitch', cam_rot[2], -360.0, 360.0, '%.2f', 1.0)
            imgui.pop_item_width()

            cam.set_position(cam_pos)
            cam.set_rotation(cam_rot)

        elif cam_mode == 1:
            imgui.text("Keyboard")
            imgui.text("- W: Forward  \n" +
                       "- S: Backward \n" + 
                       "- A: Left     \n" +
                       "- D: Right    \n")

            imgui.text("Mouse")
            imgui.text("- L Button: rotation \n" +
                       "- Middle Button: zoom")

        # visualize setting
        imgui.dummy(0, 5)
        imgui.text("Visual setting")
        _, wire_mode = imgui.checkbox("Wire mode", wire_mode)

        imgui.end_group()
        
        imgui.dummy(0, 15)
        imgui.separator()


        # tutorial select
        imgui.begin_group()
        imgui_ext.title_bar("Select Tutorial")
        imgui.dummy(0, 5)

        changed_cur_chap, chapter = imgui.combo(
            " Chapter", chapter, file_chap_list
        )
        if (changed_cur_chap):
            # os.system("python {}".format('..02_lighting.04_lighting_maps.04_lighting_maps.py'))            
            chapter_name = file_chap_list[chapter].split('/')
            file_dir     = file_dir_list[chapter]

            file_module = '{}.{}.{}'.format(chapter_name[0], chapter_name[1], "content")
            cur_file     = importlib.import_module(file_module)
            cur_file     = getattr(cur_file, 'Content')(window, viewport_size, cam, file_dir)
        imgui.end_group()

        imgui.dummy(0, 15)
        imgui.separator()

        # tutorial setting
        imgui.begin_group()
        imgui_ext.title_bar(file_chap_list[chapter])
        imgui.dummy(0, 5)
        imgui.text("Tutorial setting")
        cur_file.inspector()
        imgui.end_group()

        imgui.end()

        glViewport(0, 0, viewport_size[0], viewport_size[1])
        glScissor(0, 0, viewport_size[0], viewport_size[1])
        # opengl render
        gl.glEnable(GL_DEPTH_TEST)
        
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wire_mode else GL_FILL)
        cur_file.render()

        # render and swap buffers
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    cur_file.destroy()

    impl.shutdown()
    glfw.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--window_size",  dest="window_size", default=[1280, 720])

    args = parser.parse_args()

    main(args)