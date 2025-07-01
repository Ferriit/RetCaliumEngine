# RetCalium V-C++

## Description:
*This is a Work-in-Progress game engine that uses Modern OpenGL to render .obj files and textures in real-time with future support of Entity Component Systems and mod support*

![ScreenShot](images/screenshot.png)


## Planned Features:
- Map loading based on the original DOOM and Build engines that instead uses a syntax more similar to .OBJ files **(CURRENTLY IMPLEMENTING)**
- Shader effects that are fully controlable on the CPU **(FULLY IMPLEMENTED)**:
    1. Color Depth limiting (Same as PS1)
    2. Vignette with customizeable color
    3. Lambertian diffuse and Blinn-Phong shading
    4. Chromatic Aberration
- Forward+ rendering that supports multiple lights **(NOT IMPLEMENTED)**
- Built-in Entity Component System **(NOT IMPLEMENTED)**
- Built-in mod support with the previously mentioned ECS **(NOT IMPLEMENTED)**


## Building:
- To install dependencies just run `make install`
- To build the engine just run `make`
