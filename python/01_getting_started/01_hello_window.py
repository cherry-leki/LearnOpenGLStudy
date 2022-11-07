import sys
import glfw
from OpenGL.GL import *
 
# whenever the window size changed (by OS or user) this callback function executes
def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)

# process all input
# : query GLFW whether relevant keys are pressed/released this frame and react accordingly
def process_input(window):
    if(glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS):
        glfw.set_window_should_close(window, True)
 
def main():
    # initialize GLFW
    glfw.init()

    # OpenGL version (Major).(Minor). We use OpenGL version 3.3
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    # Using the core-profile
    # : getting access to a smaller subset of OpenGL features without backward-compatible features
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    if (sys.platform == "darwin"):  # for Mac OS. forward compatibility
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
 
    window = glfw.create_window(800, 600, "LearnOpenGL", None, None)
    if window is None:
        print("Failed to create GLFW window")
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    # render loop
    while (not glfw.window_should_close(window)):
        process_input(window)

        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # check and call events and swap the buffers
        glfw.swap_buffers(window)
        glfw.poll_events()

    # clear all previously allocated GLFW resources
    glfw.terminate()


if __name__ == "__main__":
    main()