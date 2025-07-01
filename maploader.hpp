#pragma once

#include <glm/glm.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <GL/glew.h>
#include <string>


GLuint LoadTexture(const char* path);

struct Transform {
    glm::vec3 position = glm::vec3(0.0f);
    glm::vec3 rotation = glm::vec3(0.0f);  // Euler angles in radians: pitch (X), yaw (Y), roll (Z)
    glm::vec3 scale = glm::vec3(1.0f);
};

struct Mesh {
    GLuint VAO;
    int VertexCount;
    Transform transform; 
    GLuint texture;
};

struct Light {
    glm::vec3 position;
    glm::vec3 color;
    float intensity;
};

struct Map {
    Mesh mesh;
    Light light;
    char* name;
};

struct Vertex {
    glm::vec3 position;
    glm::vec3 normal;
    glm::vec3 color;
};


int split(char* input, char delimiter, char** tokens, int maxTokens);

int CountOccurrences(const char* str, const char* sub);

Mesh CreateMesh(float* vertices, size_t size, GLuint texture);

std::string ReadFile(std::string name);

Map ReadMap(std::string filename);
