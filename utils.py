import math
import random
from settings import BOUNDING
import pygame

def distance_between_points(p1, p2):
    # Calculate distance between two points
    return math.sqrt((p1.pos.x - p2.pos.x) ** 2 + (p1.pos.y - p2.pos.y) ** 2)

def check_collision(object, obstacles):
    for obstacle in obstacles:
        dist = distance_between_points(object, obstacle)
        # If the distance is less than the sum of radii, there's a collision
        if dist < object.radius + obstacle.radius:
            return True
    return False

def check_collision_plus_bounding(object, obstacles, bounding):
    for obstacle in obstacles:
        dist = distance_between_points(object, obstacle)
        # If the distance is less than the sum of radii, there's a collision
        if dist < object.radius + bounding + obstacle.radius:
            return True
    return False

def check_collision_hiding_spots(object, obstacles, radius = 5):
    for obstacle in obstacles:
        dist = pygame.math.Vector2.distance_to(object, obstacle.pos)
        # If the distance is less than the sum of radii, there's a collision
        if dist < radius + obstacle.radius:
            return True
    return False

# Utility function to get a random float between -1 and 1
def random_clamped():
    return random.uniform(-1, 1)