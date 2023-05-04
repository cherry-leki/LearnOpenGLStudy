#version 330 core
out vec4 FragColor;

uniform vec3 color;

void main()
{
    vec3 result = color;
    FragColor = vec4(result, 1.0); // set all 4 vector values to 1.0
}