#version 330 core
out vec4 FragColor;

struct Material {
    sampler2D diffuse;
    sampler2D specular;
    float shininess;
};

struct Light {
    vec3 position;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

uniform vec3 viewPos;
uniform Material material;
uniform Light light;

void main()
{
    vec3 finalDiffuse  = texture(material.diffuse, TexCoord).rgb;
    vec3 finalSpecular = texture(material.specular, TexCoord).rgb;

    // ambient
    vec3 ambient = light.ambient * finalDiffuse;

    // diffuse
    vec3 norm     = normalize(Normal);
    vec3 lightDir = normalize(light.position - FragPos);
    float diff    = max(dot(norm, lightDir), 0.0);
    vec3 diffuse  = light.diffuse * diff * finalDiffuse;

    // specular
    vec3 viewDir    = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);

    float spec    = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    vec3 specular = light.specular * spec * finalSpecular;

    vec3 result = (ambient + diffuse + specular);
    FragColor   = vec4(result, 1.0);
}