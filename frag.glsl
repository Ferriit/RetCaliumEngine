#version 460 core

// Input from vertex shader (interpolated)
in vec3 vertexColor;
out vec4 FragColor;

in vec3 fragNormal;
in float fragSpecFactor;
in float fragAlphaExponent;
in vec3 fragPos;

uniform vec3 cameraPos;

in vec2 fragUV;
uniform sampler2D tex0;

// TestLight
uniform vec3 lightPos;
uniform vec3 lightColor;
uniform float lightIntensity;

// Vignette Settings
uniform vec3 VignetteColor;
uniform float VignetteStrength;

// Screen Size
uniform vec2 screenResolution;

// 4x4 Bayer matrix for dithering (values scaled from 0 to 1)
float BayerDither(vec2 fragCoord) {
    int x = int(mod(fragCoord.x, 4.0));
    int y = int(mod(fragCoord.y, 4.0));

    int index = y * 4 + x;
    float bayer[16] = float[](
        0.0,  8.0,  2.0, 10.0,
       12.0,  4.0, 14.0,  6.0,
        3.0, 11.0,  1.0,  9.0,
       15.0,  7.0, 13.0,  5.0
    );

    return bayer[index] / 16.0;
}


vec3 ApplyVignette(vec3 imageColor) {
    vec3 Col = VignetteColor;
    float Strength = VignetteStrength;
    
    float dist = clamp(pow(length((gl_FragCoord.xy - 0.5 * screenResolution.xy) / screenResolution.xy) * Strength, 2.f), 0., 1.);
    
    return vec3(Col * dist + imageColor * (1. - dist));
}


void main() {
    int SimulatedBitSize = 15;
    float PaletteSize = pow(2., float(SimulatedBitSize) / 3.);

    // === Chromatic Aberration Offsets ===
    float aberrationStrength = 0.001;
    float depthFactor = 1.5f;
    float vignetteStrength = 1.0f;
    float depth = length(fragPos - cameraPos) * depthFactor; // world-space depth

    vec2 offsetDir = normalize(fragUV - 0.5);
    vec2 offset = offsetDir * depth * aberrationStrength;

    // === Chromatic Aberration Vignette ===
    float vignette = length(offsetDir) * vignetteStrength; // stronger near edges
    offset *= vignette;

    vec2 uv_r = clamp(fragUV + offset, 0.0, 1.0);
    vec2 uv_g = fragUV;
    vec2 uv_b = clamp(fragUV - offset, 0.0, 1.0);

    vec3 texColor;
    texColor.r = texture(tex0, uv_r).r;
    texColor.g = texture(tex0, uv_g).g;
    texColor.b = texture(tex0, uv_b).b;

    // === Lighting ===
    vec3 LambertianColor = texColor * lightColor * lightIntensity * max(0, dot(fragNormal, normalize(lightPos)));
    vec3 H = normalize(normalize(lightPos) + normalize(cameraPos - fragPos));
    vec3 Blinn_PhongColor = texColor * lightColor * lightIntensity * pow(max(0, dot(fragNormal, H)), fragAlphaExponent);

    vec3 Color = ApplyVignette(round(Blinn_PhongColor * fragSpecFactor + LambertianColor * (1.0 - fragSpecFactor) * PaletteSize) / PaletteSize);

    // === Bayer Dithering ===
    float threshold = BayerDither(gl_FragCoord.xy) - 0.5;
    float ditherStrength = 1.0 / SimulatedBitSize;

    float red = Color.r + threshold * ditherStrength;
    float green = Color.g + threshold * ditherStrength;
    float blue = Color.b + threshold * ditherStrength;

    FragColor = vec4(red, green, blue, 1.0);

}
