#include <glm/glm.hpp>
#include "physics.hpp"


bool rayIntersectsTriangle(
    const glm::vec3& orig, const glm::vec3& dir,
    const glm::vec3& v0, const glm::vec3& v1, const glm::vec3& v2,
    float& t)
{
    const float EPSILON = 1e-6;
    glm::vec3 edge1 = v1 - v0;
    glm::vec3 edge2 = v2 - v0;
    glm::vec3 h = glm::cross(dir, edge2);
    float a = glm::dot(edge1, h);
    if (a > -EPSILON && a < EPSILON)
        return false; // parallel

    float f = 1.0f / a;
    glm::vec3 s = orig - v0;
    float u = f * glm::dot(s, h);
    if (u < 0.0 || u > 1.0)
        return false;

    glm::vec3 q = glm::cross(s, edge1);
    float v = f * glm::dot(dir, q);
    if (v < 0.0 || u + v > 1.0)
        return false;

    t = f * glm::dot(edge2, q);
    return t > EPSILON;
}

MovementVector ApplyGravity(MovementVector MVector, float AccelerationDueToGravity) {
    if (!MVector.GravityOn) {
        MVector.GravityOn = true;
        MVector.Acceleration.y -= AccelerationDueToGravity;
    }
    return MVector;
}

MovementVector ApplyAcceleration(MovementVector MVector, float Friction) {
    MVector.Velocity += MVector.Acceleration;
    MVector.Acceleration *= (1.0f - std::fmin(Friction, 1.0f));

    MVector.Position += MVector.Velocity;

    return MVector;
}

