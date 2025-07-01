#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <iostream>
#include <glm/glm.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <cstdlib>
#include "maploader.hpp"

#define VAO_ATTRIBS 5
#define VAO_ATTRIB_SIZE 13

#define WIDTH 800.0f
#define HEIGHT 600.0f

#define MODEL_AMOUNT 3

float fov = 90.0f; // in degrees

/*
 * Compile Command: g++ renderer.cpp maploader.cpp -o renderer -lglfw -lGLEW -lGL
*/

float aspectRatio;

float angle = 0.0f;

float lastX = 0.0f;
float lastY = 0.0f;
bool firstMouse = true;

float mouseX = 0.0f;
float mouseY = 0.0f;

// View matrix — camera position and orientation
glm::vec3 cameraPos = glm::vec3(0.0f, 0.0f, 3.0f);
glm::vec3 cameraFront = glm::vec3(0.0f, 0.0f, -1.0f);
glm::vec3 cameraTarget= glm::vec3(0.0f, 0.0f, 0.0f);
glm::vec3 cameraUp    = glm::vec3(0.0f, 1.0f, 0.0f);

float yaw = -90.0f;  // horizontal angle (left/right), initialized facing -Z
float pitch = 0.0f;  // vertical angle (up/down)

glm::mat4 view = glm::lookAt(cameraPos, cameraTarget, cameraUp);

// Model matrix — object's transform in world space
glm::mat4 model = glm::mat4(1.0f);  // Identity matrix (no transform yet)

GLuint MissingTex;


float vertices[] = {
    // positions         // colors           // normals           // Diffuse/Specular Factor + Shininess Exponent
    -0.5f, -0.5f, 0.0f,   1.0f, 0.0f, 0.0f,   0.0f, 0.0f, 1.0f,    0.5f,   10.0f, // bottom left
     0.5f, -0.5f, 0.0f,   0.0f, 1.0f, 0.0f,   0.0f, 0.0f, 1.0f,    0.5f,   10.0f, // bottom right
     0.0f,  0.5f, 0.0f,   0.0f, 0.0f, 1.0f,   0.0f, 0.0f, 1.0f,    0.5f,   10.0f  // top
};


// Test light:
Light light = {
    glm::vec3(0.0f, 3.0f, 2.0f),
    glm::vec3(1.0f, 1.0f, 1.0f),
    2.0f
};


glm::vec3 GetDirectionFromYawPitch(float yaw, float pitch) {
    glm::vec3 direction;
    direction.x = cos(glm::radians(pitch)) * cos(glm::radians(yaw));
    direction.y = sin(glm::radians(pitch));
    direction.z = cos(glm::radians(pitch)) * sin(glm::radians(yaw));
    return glm::normalize(direction);
}


void MoveCamera(GLFWwindow* window) {
    glm::vec3 direction = GetDirectionFromYawPitch(yaw, pitch);
    glm::vec3 worldUp = glm::vec3(0.0f, 1.0f, 0.0f);
    glm::vec3 right = glm::normalize(glm::cross(direction, worldUp));  // right vector

    float speed = 0.1f;

    if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS) {
        cameraPos += direction * speed;
    }
    if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS) {
        cameraPos -= direction * speed;
    }
    if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS) {
        cameraPos += right * speed;
    }
    if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS) {
        cameraPos -= right * speed;
    }
    if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS) {
        cameraPos += worldUp * speed;
    }
    if (glfwGetKey(window, GLFW_KEY_LEFT_CONTROL) == GLFW_PRESS) {
        cameraPos -= worldUp * speed;
    }
}


void MouseCallback(GLFWwindow* window, double xpos, double ypos) {
    if (firstMouse) {
        lastX = xpos;
        lastY = ypos;
        firstMouse = false;
    }

    float xoffset = xpos - lastX;
    float yoffset = lastY - ypos; // reversed

    lastX = xpos;
    lastY = ypos;

    float sensitivity = 0.1f;
    xoffset *= sensitivity;
    yoffset *= sensitivity;

    yaw += xoffset;
    pitch += yoffset;

    // Clamp pitch to avoid gimbal lock
    if (pitch > 89.0f) pitch = 89.0f;
    if (pitch < -89.0f) pitch = -89.0f;

    glm::vec3 front;
    front.x = cos(glm::radians(pitch)) * cos(glm::radians(yaw));
    front.y = sin(glm::radians(pitch));
    front.z = cos(glm::radians(pitch)) * sin(glm::radians(yaw));
    cameraFront = glm::normalize(front);
}


void Replace(char* String, char Element, char EndElement, char* buf, GLuint texture) {
    for (int i = 0; String[i] != '\0'; i++) {
        if (String[i] == Element) {
            buf[i] = EndElement;
        } else {
            buf[i] = String[i];
        }
    }
}


Mesh LoadOBJ(const char* filename,
    glm::vec3 Color,
    GLuint texture,
    float specFactor = 0.5f,
    float shininessExp = 32.0f) {

    std::string fileStr = ReadFile(filename);

    if (fileStr.empty()) {
    std::cerr << "Failed to read OBJ file: " << filename << "\n";
    return Mesh();
    }

    const char* rawdata = fileStr.c_str();
    char* file = new char[strlen(rawdata) + 1];
    strcpy(file, rawdata);

    int NormalVectorAmount = CountOccurrences(file, "vn");
    int TextureCoordsAmount = CountOccurrences(file, "vt");
    int VertexAmount = CountOccurrences(file, "v") - TextureCoordsAmount - NormalVectorAmount;
    int FaceAmount = CountOccurrences(file, "f");

    if (VertexAmount <= 0 || FaceAmount <= 0 || NormalVectorAmount <= 0) {
    std::cerr << "Invalid OBJ file. Vertices: " << VertexAmount
             << ", Faces: " << FaceAmount
             << ", Normals: " << NormalVectorAmount << "\n";
    delete[] file;
    return Mesh();
    }

    float (*Vertices)[3] = new float[VertexAmount][3];
    float (*NormalVectors)[3] = new float[NormalVectorAmount][3];
    int (*Faces)[3][3] = new int[FaceAmount][3][3];

    int BufSize = CountOccurrences(file, "\n") + 1;
    char** buf = new char*[BufSize];

    int SplitSize = split(file, '\n', buf, BufSize);
    int VertexCount = 0, FaceCount = 0, NormalCount = 0;

    float (*TextureCoords)[2] = new float[TextureCoordsAmount][2];
    int TextureCount = 0;


    for (int i = 0; i < SplitSize; i++) {
        int CurrBufSize = CountOccurrences(buf[i], " ") + 1;

        // Skip malformed or empty lines
        if (CurrBufSize < 1) continue;

        char** CurrentBuf = new char*[CurrBufSize];
        split(buf[i], ' ', CurrentBuf, CurrBufSize);

        //std::cout << CurrBufSize << '\n';

        if (strcmp(CurrentBuf[0], "v") == 0) {
            if (CurrBufSize > 2) {
                Vertices[VertexCount][0] = strtof(CurrentBuf[1], nullptr);
                Vertices[VertexCount][1] = strtof(CurrentBuf[2], nullptr);
                Vertices[VertexCount][2] = strtof(CurrentBuf[3], nullptr);
                VertexCount++;
           }
        }
        else if (strcmp(CurrentBuf[0], "vn") == 0) {
           if (CurrBufSize > 2) {
                NormalVectors[NormalCount][0] = strtof(CurrentBuf[1], nullptr);
                NormalVectors[NormalCount][1] = strtof(CurrentBuf[2], nullptr);
                NormalVectors[NormalCount][2] = strtof(CurrentBuf[3], nullptr);
                NormalCount++;
           }
        }
        else if (strcmp(CurrentBuf[0], "f") == 0) {
            //std::cout << "f\n";
            if (CurrBufSize > 2) { // 3 vertices expected for triangle
                for (int j = 1; j <= 3; ++j) {
                    char* vtn[3] = { nullptr, nullptr, nullptr };
                    int vtnCount = split(CurrentBuf[j], '/', vtn, 3);

                    Faces[FaceCount][j - 1][0] = (vtnCount >= 1 && vtn[0]) ? atoi(vtn[0]) - 1 : -1;
                    Faces[FaceCount][j - 1][1] = (vtnCount >= 2 && vtn[1]) ? atoi(vtn[1]) - 1 : -1;
                    Faces[FaceCount][j - 1][2] = (vtnCount == 3 && vtn[2]) ? atoi(vtn[2]) - 1 : -1;
                }
                FaceCount++;
           }
        }
        else if (strcmp(CurrentBuf[0], "vt") == 0) {
            if (CurrBufSize > 2) {
                TextureCoords[TextureCount][0] = strtof(CurrentBuf[1], nullptr);
                TextureCoords[TextureCount][1] = strtof(CurrentBuf[2], nullptr);
                TextureCount++;
            }
        }
        

        delete[] CurrentBuf;
    }

    int TotalVertices = FaceCount * 3;
    int totalFloats = TotalVertices * VAO_ATTRIB_SIZE;
    float* OrderedFaces = new float[totalFloats];

    int outIndex = 0;
    for (int i = 0; i < FaceCount; i++) {
        for (int j = 0; j < 3; j++) {
           int vIdx = Faces[i][j][0];
           int nIdx = Faces[i][j][2];

           if (vIdx < 0 || vIdx >= VertexAmount || nIdx < 0 || nIdx >= NormalVectorAmount) {
               std::cerr << "Warning: invalid index in face " << i << "\n";
               continue;
           }

           int tIdx = Faces[i][j][1]; // texture index

           // Position
           OrderedFaces[outIndex++] = Vertices[vIdx][0];
           OrderedFaces[outIndex++] = Vertices[vIdx][1];
           OrderedFaces[outIndex++] = Vertices[vIdx][2];
           
           // Color
           OrderedFaces[outIndex++] = Color.r;
           OrderedFaces[outIndex++] = Color.g;
           OrderedFaces[outIndex++] = Color.b;
           
           // Normal
           OrderedFaces[outIndex++] = NormalVectors[nIdx][0];
           OrderedFaces[outIndex++] = NormalVectors[nIdx][1];
           OrderedFaces[outIndex++] = NormalVectors[nIdx][2];
           
           // UV
           if (tIdx >= 0 && tIdx < TextureCoordsAmount) {
               OrderedFaces[outIndex++] = TextureCoords[tIdx][0];
               OrderedFaces[outIndex++] = TextureCoords[tIdx][1];
           } else {
               OrderedFaces[outIndex++] = 0.0f;
               OrderedFaces[outIndex++] = 0.0f;
           }
           
           // Specular
           OrderedFaces[outIndex++] = specFactor;
           
           // Shininess
           OrderedFaces[outIndex++] = shininessExp;
        }
    }

    std::cout << "Uploading " << TotalVertices << " vertices (" << totalFloats * VAO_ATTRIB_SIZE << " floats) to GPU\n";

    Mesh mesh = CreateMesh(OrderedFaces, sizeof(float) * totalFloats, texture);

    delete[] Vertices;
    delete[] NormalVectors;
    delete[] Faces;
    delete[] buf;
    delete[] OrderedFaces;
    delete[] file;

    return mesh;
}


GLuint CompileShaders(const std::string& vertexShaderSource, const std::string& fragmentShaderSource) {
    // === Compile vertex shader ===
    GLuint vertexShader = glCreateShader(GL_VERTEX_SHADER);
    const char* vShaderCode = vertexShaderSource.c_str();
    glShaderSource(vertexShader, 1, &vShaderCode, nullptr);
    glCompileShader(vertexShader);

    // Check vertex shader compilation status
    GLint success;
    glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);
    if (!success) {
        char infoLog[512];
        glGetShaderInfoLog(vertexShader, 512, nullptr, infoLog);
        fprintf(stderr, "Vertex shader compilation failed:\n%s\n", infoLog);

        std::cout << vertexShaderSource;
        // You can choose to return 0 here or throw an exception
    }

    // === Compile fragment shader ===
    GLuint fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
    const char* fShaderCode = fragmentShaderSource.c_str();
    glShaderSource(fragmentShader, 1, &fShaderCode, nullptr);
    glCompileShader(fragmentShader);

    // Check fragment shader compilation status
    glGetShaderiv(fragmentShader, GL_COMPILE_STATUS, &success);
    if (!success) {
        char infoLog[512];
        glGetShaderInfoLog(fragmentShader, 512, nullptr, infoLog);
        fprintf(stderr, "Fragment shader compilation failed:\n%s\n", infoLog);
        // Handle error
    }

    // === Link shaders into a shader program ===
    GLuint shaderProgram = glCreateProgram();
    glAttachShader(shaderProgram, vertexShader);
    glAttachShader(shaderProgram, fragmentShader);
    glLinkProgram(shaderProgram);

    // Check linking status
    glGetProgramiv(shaderProgram, GL_LINK_STATUS, &success);
    if (!success) {
        char infoLog[512];
        glGetProgramInfoLog(shaderProgram, 512, nullptr, infoLog);
        fprintf(stderr, "Shader program linking failed:\n%s\n", infoLog);
        // Handle error
    }

    // Delete shaders after linking
    glDeleteShader(vertexShader);
    glDeleteShader(fragmentShader);

    return shaderProgram;
}


// Move mesh in world space
void SetPosition(Mesh &m, float x, float y, float z) {
    m.transform.position = glm::vec3(x, y, z);
}

// Rotate mesh (pitch, yaw, roll) in radians
void SetRotation(Mesh &m, float pitch, float yaw, float roll) {
    m.transform.rotation = glm::vec3(pitch, yaw, roll);
}

// Scale mesh non-uniformly
void SetScale(Mesh &m, float sx, float sy, float sz) {
    m.transform.scale = glm::vec3(sx, sy, sz);
}


void RenderMesh(const Mesh& m, GLint modelLoc) {
    // Build model matrix from transform
    if (m.texture != 0) {
        glBindTexture(GL_TEXTURE_2D, m.texture);
    }
    else {
        glBindTexture(GL_TEXTURE_2D, MissingTex);
    }

    glm::mat4 model = glm::mat4(1.0f);
    model = glm::translate(model, m.transform.position);
    model = glm::rotate(model, m.transform.rotation.x, glm::vec3(1,0,0));
    model = glm::rotate(model, m.transform.rotation.y, glm::vec3(0,1,0));
    model = glm::rotate(model, m.transform.rotation.z, glm::vec3(0,0,1));
    model = glm::scale(model, m.transform.scale);

    // Upload model matrix
    glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));

    // Draw
    glBindVertexArray(m.VAO);
    glDrawArrays(GL_TRIANGLES, 0, m.VertexCount);
    glBindVertexArray(0);
}


void Render(Mesh* meshes, int meshCount, GLint modelLoc) {
    SetRotation(meshes[0], 0.0f, angle, 0.0f);
    SetRotation(meshes[1], 0.0f, angle, 0.0f);
    SetRotation(meshes[2], 0.0f, angle, 0.0f);

    SetPosition(meshes[0], -2.5f, 0.0f, 0.0f);
    SetPosition(meshes[1], 0.0f, 0.0f, 0.0f);
    SetPosition(meshes[2], 2.5f, 0.0f, 0.0f);

    SetScale(meshes[0], 0.75f, 0.75f, 0.75f);
    SetScale(meshes[1], 0.75f, 0.75f, 0.75f);
    SetScale(meshes[2], 0.75f, 0.75f, 0.75f);

    angle += 0.01f;
    for (int i = 0; i < meshCount; ++i) {
        Mesh& m = meshes[i];

        glm::mat4 model = glm::mat4(1.0f);
        model = glm::translate(model, m.transform.position);
        model = glm::rotate(model, m.transform.rotation.y, glm::vec3(0,1,0));
        model = glm::rotate(model, m.transform.rotation.x, glm::vec3(1,0,0));
        model = glm::rotate(model, m.transform.rotation.z, glm::vec3(0,0,1));             
        model = glm::scale(model, m.transform.scale);

        // Upload the model matrix for this mesh
        glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));

        // Now draw it
        RenderMesh(meshes[i], modelLoc); 
    }
}


int main() {
    if (!glfwInit()) {
        std::cerr << "Failed to initialize GLFW\n";
        return -1;
    }

    const GLFWvidmode* mode = glfwGetVideoMode(glfwGetPrimaryMonitor());
    int screenWidth = mode->width;
    int screenHeight = mode->height;

    aspectRatio = screenWidth / screenHeight;
    // Projection matrix — perspective projection
    glm::mat4 projection = glm::perspective(glm::radians(fov), aspectRatio, 0.1f, 100.0f);


    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 6);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    GLFWwindow* window = glfwCreateWindow(screenWidth, screenHeight, "OpenGL Window", glfwGetPrimaryMonitor(), nullptr);

    if (!window) {
        std::cerr << "Failed to create GLFW window\n";
        glfwTerminate();
        return -1;
    }

    glfwMakeContextCurrent(window);

    glewExperimental = GL_TRUE;
    if (glewInit() != GLEW_OK) {
        std::cerr << "Failed to initialize GLEW\n";
        return -1;
    }

    std::cout << "OpenGL Version: " << glGetString(GL_VERSION) << "\n" << mode->width << "x" << mode->height << "\n";


    GLuint ShaderProgram = CompileShaders(ReadFile("vert.glsl"), ReadFile("frag.glsl"));
    glUseProgram(ShaderProgram);

    const int TextureAmount = 2;

    GLuint tex[TextureAmount] = {LoadTexture("cobblesmall.png"), LoadTexture("cobblesmallcube.png")};
    MissingTex = LoadTexture("MissingTexture.png");
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, MissingTex);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);

    for (int i = 0; i < TextureAmount; i++) {
        glBindTexture(GL_TEXTURE_2D, tex[i]);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    }

    //Mesh Triangle = CreateMesh(vertices, sizeof(vertices));
    Mesh Suzanne = LoadOBJ("suzanne.obj", glm::vec3(0.5f), tex[0], 0.0f);
    Mesh Donut = LoadOBJ("donut.obj", glm::vec3(0.0f, 0.5f, 1.0f), tex[0], 0.0f);
    Mesh Cube = LoadOBJ("cube.obj", glm::vec3(0.5f), tex[1], 0.0f);
    Mesh Meshes[] = {Suzanne, Donut, Cube};

    // Resolution
    // after creating window and making context current:
    int fbW, fbH;
    glfwGetFramebufferSize(window, &fbW, &fbH);
    // make sure your viewport matches:
    glViewport(0, 0, fbW, fbH);
    // upload these exact values:
    // after glViewport(...)
    GLint loc = glGetUniformLocation(ShaderProgram, "screenResolution");
    glUniform2f(loc, float(fbW), float(fbH));
    std::cout << "Framebuffer size: " << fbW << " x " << fbH << std::endl;


    // Get uniform locations once
    GLint modelLoc = glGetUniformLocation(ShaderProgram, "model");
    GLint viewLoc = glGetUniformLocation(ShaderProgram, "view");
    GLint projLoc = glGetUniformLocation(ShaderProgram, "projection");
    GLint cameraPosLoc = glGetUniformLocation(ShaderProgram, "cameraPos");

    // Projection is static unless window resizes
    glUniformMatrix4fv(projLoc, 1, GL_FALSE, glm::value_ptr(projection));

    //ReadMap("actualtest.cmap");

    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
    glfwSetCursorPosCallback(window, MouseCallback);

    glDisable(GL_BLEND);
    glDisable(GL_MULTISAMPLE);
    glEnable(GL_CULL_FACE);
    glCullFace(GL_BACK);       // Cull back faces
    glFrontFace(GL_CCW);       // Treat counter-clockwise as front-facing
    glEnable(GL_DEPTH_TEST);


    float VignetteStrength = 2.0f;
    glm::vec3 VignetteColor = {0.0f, 0.0f, 0.0f};


    Map test = ReadMap("actualtest.cmap");

    // Main loop
    while (!glfwWindowShouldClose(window) && glfwGetKey(window, GLFW_KEY_ESCAPE) != GLFW_PRESS) {
        // Per-frame camera/view setup
        view = glm::lookAt(cameraPos, cameraPos + cameraFront, cameraUp);

        // Clear screen
        //glClearColor(0.1f, 0.2f, 0.3f, 1.0f);
        glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // Upload view and cameraPos each frame
        glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));
        glUniform3fv(cameraPosLoc, 1, glm::value_ptr(cameraPos));

        MoveCamera(window);

        // Updating lights
        GLint locLightPos = glGetUniformLocation(ShaderProgram, "lightPos");
        GLint locLightColor = glGetUniformLocation(ShaderProgram, "lightColor");
        GLint locLightIntensity = glGetUniformLocation(ShaderProgram, "lightIntensity");
        glUniform3fv(locLightPos, 1, glm::value_ptr(light.position));
        glUniform3fv(locLightColor, 1, glm::value_ptr(light.color));
        glUniform1f(locLightIntensity, light.intensity);

        // Updating Vignette
        GLint VgStrength = glGetUniformLocation(ShaderProgram, "VignetteStrength");
        GLint VgCol = glGetUniformLocation(ShaderProgram, "VignetteColor");
        glUniform1f(VgStrength, VignetteStrength);
        glUniform3fv(VgCol, 1, glm::value_ptr(VignetteColor));

        // Render scene
        glUniform1i(glGetUniformLocation(ShaderProgram, "tex0"), 0);
        Render(Meshes, MODEL_AMOUNT, modelLoc);

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}
