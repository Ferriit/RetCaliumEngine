#pragma once

#include <glm/glm.hpp>

struct MovementVector {
    glm::vec3 Acceleration;
    glm::vec3 Velocity;
    bool GravityOn;
    glm::vec3 Position;
};

