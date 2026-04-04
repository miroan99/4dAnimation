#version 330 core

in vec3 FragPos;
in vec3 Normal;
in vec3 VertColor;

out vec4 FragColor;

struct Light {
    vec3 direction;
    vec3 color;
    float ambient;
    float diffuse;
};

uniform Light light;

void main() {
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(-light.direction);

    float diff = max(dot(norm, lightDir), 0.0);
    vec3 ambient = light.ambient * light.color;
    vec3 diffuse = light.diffuse * diff * light.color;

    vec3 color = (ambient + diffuse) * VertColor;
    FragColor = vec4(color, 1.0);
}