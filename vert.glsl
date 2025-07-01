#version 460 core

// Input: vertex position (location = 0)
layout(location = 0) in vec3 aPos;

// Input: vertex color (location = 1)
layout(location = 1) in vec3 aColor;

// Input: vertex normal (location = 2)
layout(location = 2) in vec3 aNormal;

// Input: UV Coods (location = 3)
layout (location = 3) in vec2 inUV;
out vec2 fragUV;

// Input: vertex specular factor (location = 4)
layout(location = 4) in float aSpecFactor;

// Input: vertex shininess exponent (location = 5)
layout(location = 5) in float aShininessExponent;

out vec3 fragNormal;  // Pass to fragment shader
out vec3 fragPos;
out float fragSpecFactor;
out float fragAlphaExponent;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform vec3 cameraPos;

// Screen Size
uniform vec2 screenResolution;

// Output to fragment shader
out vec3 vertexColor;

void main() {
    // Grid snapping settings
    float gridSize = 0.05; // Size of the grid units
    //float gridSize = 0.000000001;

    // Snap the world-space position to the grid
    vec3 snappedPos = floor((model * vec4(aPos, 1.0)).xyz / gridSize) * gridSize;

    // Use snappedPos for rendering
    vec4 worldPosition = vec4(snappedPos, 1.0);


    // Pass world-space position to fragment shader
    fragPos = worldPosition.xyz;

    // Transform normal (model matrix without translation & scale ideally)
    fragNormal = normalize(mat3(transpose(inverse(model))) * aNormal);

    // Pass vertex color and spec factor
    vertexColor = aColor;
    fragSpecFactor = aSpecFactor;
    fragAlphaExponent = aShininessExponent;
    fragUV = inUV;
    // Calculate clip space position
    gl_Position = projection * view * worldPosition;
}
