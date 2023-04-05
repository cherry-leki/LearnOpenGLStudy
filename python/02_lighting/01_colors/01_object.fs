#version 330 core
out vec4 FragColor;

uniform vec3 objectColor;
uniform vec3 lightColor;

in vec2 TexCoord;

// texture sampler
uniform int textureNum;
uniform sampler2D texture1;
uniform sampler2D texture2;

void main()
{
    if (textureNum == 1) {
        FragColor = vec4(lightColor * vec3(texture(texture1, TexCoord)), 1.0);
    }
    else if (textureNum == 2) {
        vec3 mix_tex = vec3(mix(texture(texture1, TexCoord), texture(texture2, TexCoord), 0.2));
        FragColor = vec4(lightColor * mix_tex, 1.0);
    }
    else {
        FragColor = vec4(lightColor * objectColor, 1.0);
    }
}