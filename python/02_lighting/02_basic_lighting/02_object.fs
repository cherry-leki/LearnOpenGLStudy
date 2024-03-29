#version 330 core
out vec4 FragColor;

in vec3 Normal;
in vec3 FragPos;

in vec2 TexCoord;

uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;
uniform vec3 objectColor;
uniform int shininess;

uniform int textureNum;
uniform sampler2D texture1;
uniform sampler2D texture2;

void main()
{
    // ambient
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * lightColor;

    // diffuse
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;

    // specular
    float specularStrength = 0.5;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);

    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    vec3 specular = specularStrength * spec * lightColor;

    vec3 result = (ambient + diffuse + specular) * objectColor;

    if (textureNum == 1) {
        result = (ambient + diffuse + specular) * vec3(texture(texture1, TexCoord));
    }
    else if (textureNum == 2) {
        result = (ambient + diffuse + specular) * vec3(mix(texture(texture1, TexCoord), texture(texture2, TexCoord), 0.2));
    }
    
    FragColor = vec4(result, 1.0);
}