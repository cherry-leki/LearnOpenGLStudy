#version 330 core
out vec4 FragColor;

in vec3 ourColor;
in vec2 TexCoord;

// texture sampler
uniform int textureNum;
uniform sampler2D texture1;
uniform sampler2D texture2;

void main()
{
    if (textureNum == 1) {
        FragColor = texture(texture1, TexCoord);
    }
    else {
        FragColor = mix(texture(texture1, TexCoord), texture(texture2, TexCoord), 0.2);
    }
}