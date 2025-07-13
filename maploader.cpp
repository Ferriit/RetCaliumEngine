#include <glm/glm.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <GL/glew.h>
#include <fstream>
#include <ostream>
#include <sstream>
#include <iostream>
#include "maploader.hpp"

#define VAO_ATTRIBS 5
#define VAO_ATTRIB_SIZE 13

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"


int CountOccurrences(const char* str, const char* sub) {
    int count = 0;
    size_t subLen = strlen(sub);
    if (subLen == 0) return 0; // avoid infinite loop

    for (const char* p = str; *p != '\0'; ++p) {
        if (strncmp(p, sub, subLen) == 0) {
            count++;
            p += subLen - 1;  // advance pointer to avoid overlapping counts
        }
    }
    return count;
}


int split(char* input, char delimiter, char** tokens, int maxTokens) {
    int count = 0;
    char* start = input;


    while (*input && count < maxTokens) {
        if (*input == delimiter) {
            *input = '\0';             // Null-terminate the current token
            tokens[count++] = start;   // Save pointer to token
            start = input + 1;         // Move to the next character
        }
        ++input;
    }

    if (*start != '\0' && count < maxTokens) {
        tokens[count++] = start;       // Last token
    }


    return count;  // Number of tokens written
}


GLuint LoadTexture(const char* path) {
    int w, h, channels;
    unsigned char* data = stbi_load(path, &w, &h, &channels, 0);

    if (!data) {
        std::cerr << "Failed to load texture: " << path << "\n";
        return 0;
    }

    GLuint texture;
    glGenTextures(1, &texture);
    glBindTexture(GL_TEXTURE_2D, texture);

    GLenum format = (channels == 4) ? GL_RGBA : GL_RGB;
    glTexImage2D(GL_TEXTURE_2D, 0, format, w, h, 0, format, GL_UNSIGNED_BYTE, data);
    glGenerateMipmap(GL_TEXTURE_2D);

    stbi_image_free(data);
    return texture;
}


Mesh CreateMesh(float* vertices, size_t size, GLuint texture) {
    GLuint VAO, VBO;

    // Generate and bind VAO
    glGenVertexArrays(1, &VAO);
    glBindVertexArray(VAO);

    // Generate and bind VBO, upload data
    glGenBuffers(1, &VBO);
    glBindBuffer(GL_ARRAY_BUFFER, VBO);
    glBufferData(GL_ARRAY_BUFFER, size, vertices, GL_STATIC_DRAW);

    // Uploading Data
    // Position (location = 0):
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, VAO_ATTRIB_SIZE * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);

    // Color (location = 1):
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, VAO_ATTRIB_SIZE * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);

    // Normals (location = 2):
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, VAO_ATTRIB_SIZE * sizeof(float), (void*)(6 * sizeof(float)));
    glEnableVertexAttribArray(2);

    // UV (location = 3):
    glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, VAO_ATTRIB_SIZE * sizeof(float), (void*)(9 * sizeof(float)));
    glEnableVertexAttribArray(3);

    // Specular (location = 4):
    glVertexAttribPointer(4, 1, GL_FLOAT, GL_FALSE, VAO_ATTRIB_SIZE * sizeof(float), (void*)(11 * sizeof(float)));
    glEnableVertexAttribArray(4);

    // Shininess (location = 5):
    glVertexAttribPointer(5, 1, GL_FLOAT, GL_FALSE, VAO_ATTRIB_SIZE * sizeof(float), (void*)(12 * sizeof(float)));
    glEnableVertexAttribArray(5);

    // Unbind VAO
    glBindVertexArray(0);

    int vertexCount = size / (VAO_ATTRIB_SIZE * sizeof(float));

    return (Mesh){VAO, vertexCount, Transform(), texture};
}


std::string ReadFile(std::string name) {
    std::ifstream File(name);

    std::stringstream buf;
    buf << File.rdbuf();
    File.close();
    return buf.str();
}


Map ReadMap(std::string filename) {
    std::string fileStr = ReadFile(filename);

    if (fileStr.empty()) {
    std::cerr << "Failed to read OBJ file: " << filename << "\n";
    return Map();
    }

    const char* rawdata = fileStr.c_str();
    char* file = new char[strlen(rawdata) + 1];
    strcpy(file, rawdata);

    //std::cout << file << std::endl;

    int BufSize = CountOccurrences(file, "\n");

    char* Buf[BufSize];

    int LineAmount = split(file, '\n', Buf, BufSize);

    std::cout << "LineAmount: " << LineAmount << " BufSize: " << BufSize << std::endl;

    for (int i = 0; i < LineAmount; i++) {
        std::cout << "Buf#" << i << ": " << Buf[i] << std::endl;
                
    }
    
    delete[] file;

    return Map();
}
