import pygame
from utils import random_clamped
from settings import *

def seek(entity, target_pos):
    desired_velocity = (target_pos - entity.pos).normalize() * entity.speed
    return desired_velocity - entity.velocity

def flee(entity, target_pos):
    desired_velocity = (entity.pos - target_pos).normalize() * entity.speed
    return desired_velocity - entity.velocity



def wander(agent):
    # First, add a small random vector to the target’s position
    agent.wander_target += pygame.Vector2(random_clamped() * WANDER_JITTER,
                                          random_clamped() * WANDER_JITTER)

    # Normalize the vector and scale it by the wander radius
    agent.wander_target = agent.wander_target.normalize() * WANDER_RADIUS

    # Move the target into a position WANDER_DISTANCE in front of the agent
    target_local = agent.wander_target + pygame.Vector2(WANDER_DISTANCE, 0)

    # Project the target into world space (this is a simplified version)
    target_world = (target_local.rotate(agent.angle) + agent.pos)

    # Return the steering vector (the direction to the target)
    return (target_world - agent.pos).normalize()



def get_hiding_position(pos_ob, radius_ob, pos_target, distance_from_boundary=30.0):
    """
    Calculate the hiding position behind an obstacle relative to the target (player).
    
    :param pos_ob: Position of the obstacle (Vector2)
    :param radius_ob: Radius of the obstacle
    :param pos_target: Position of the target (player)
    :param distance_from_boundary: Additional distance to keep from the obstacle boundary
    :return: The best hiding position as a Vector2
    """
    # calculate how far away the agent is to be from the chosen obstacle’s bounding radius
    dist_away = radius_ob + distance_from_boundary

    # calculate the heading toward the object from the target 
    to_ob = (pos_ob - pos_target).normalize()

    # scale it to size and add to the obstacle's position to get the hiding spot
    hiding_spot = to_ob * dist_away + pos_ob
    return hiding_spot

def hide(enemy, target, obstacles):
    """
    Calculates the best hiding position behind obstacles relative to the target (player).
    
    :param enemy: The enemy trying to hide
    :param target: The player (target)
    :param obstacles: A list of obstacles to hide behind
    :return: Direction vector towards the best hiding spot or an evade direction
    """
    best_hiding_spot = None
    dist_to_closest = float('inf')

    for obstacle in obstacles:
        # Get the position of the hiding spot behind the obstacle
        hiding_spot = get_hiding_position(obstacle.pos, obstacle.radius, target.pos)

        # Calculate the squared distance between the enemy and the hiding spot
        dist = (hiding_spot - enemy.pos).length_squared()

        # Keep track of the closest hiding spot
        if dist < dist_to_closest:
            dist_to_closest = dist
            best_hiding_spot = hiding_spot

    # If no suitable obstacle was found, evade the target
    if best_hiding_spot is None:
        return evade(enemy, target) 

    # Otherwise, move toward the hiding spot (you can refine with an "arrive" behavior)
    return (best_hiding_spot - enemy.pos).normalize()

def evade(enemy, target):
    """
    Makes the enemy evade the player by moving away from them.
    
    :param enemy: The enemy trying to evade
    :param target: The player (target)
    :return: A normalized vector pointing away from the player
    """
    # Move in the opposite direction of the target
    return (enemy.pos - target.pos).normalize()