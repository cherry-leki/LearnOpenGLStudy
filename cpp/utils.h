//
//  utils.hpp
//  LearnedOpenGL
//
//  Created by Leki on 2021/07/20.
//

#ifndef utils_h
#define utils_h

#define GL_SILENCE_DEPRECATION

#include <iostream>
#include <glad/glad.h>
#include <GLFW/glfw3.h>

const unsigned int SCR_WIDTH  = 800;
const unsigned int SCR_HEIGHT = 600;

void framebuffer_size_callback(GLFWwindow* window, int width, int height);

void processInput(GLFWwindow *window);

#endif /* utils_hpp */
