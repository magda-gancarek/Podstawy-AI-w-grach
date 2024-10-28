import pygame
import random
from entity import MovingEntity
import math
from settings import *
from utils import check_collision, distance_between_points
from steering_behaviors import hide, wander, evade


def spawn_enemy(obstacles):
    enemies = []
    # Spawn an enemy at a random position, avoiding obstacles
    for _ in range(ENEMY_COUNT):
        x = random.randint(ENEMY_RADIUS, SCREEN_WIDTH - ENEMY_RADIUS)
        y = random.randint(ENEMY_RADIUS, SCREEN_HEIGHT - ENEMY_RADIUS)
        enemy_pos = pygame.Vector2(x, y)
        enemy = Enemy(enemy_pos)
        # Check if this position collides with any obstacle
        if not check_collision(enemy, obstacles):
            enemies.append(enemy)
    return enemies


class Enemy(MovingEntity):
    def __init__(self, pos):
        self.pos = pos
        self.angle = 0
        self.radius = ENEMY_RADIUS
        self.speed = ENEMY_SPEED
        self.direction = pygame.Vector2(1,0) # default direction #TODO: arrive behaviour
        self.wander_target = pygame.Vector2(0, 0)  # Initialize wander target

    def draw_enemy(self, screen):        
        front_x = self.pos.x + self.radius * math.cos(math.radians(self.angle))
        front_y = self.pos.y - self.radius * math.sin(math.radians(self.angle))

        left_x = self.pos.x + self.radius * math.cos(math.radians(self.angle + 120))
        left_y = self.pos.y - self.radius * math.sin(math.radians(self.angle + 120))

        right_x = self.pos.x + self.radius * math.cos(math.radians(self.angle + 240))
        right_y = self.pos.y - self.radius * math.sin(math.radians(self.angle + 240))

        points = [(front_x, front_y), (left_x, left_y), (right_x, right_y)]

        pygame.draw.circle(screen, RED, (self.pos.x, self.pos.y), self.radius)
        pygame.draw.polygon(screen, GREEN, points)
        pygame.draw.circle(screen, "white", (front_x, front_y), 3)

    def update(self, player, enemies, obstacles, screen):
        # Decide whether to hide or wander
        if self.should_hide(player):
            self.direction = hide(self, player, obstacles)
        else:
            self.direction = wander(self, screen)

        # Update the angle based on the direction
        if self.direction.length() > 0:  # If there's a valid direction
            self.angle = self.direction.angle_to(pygame.Vector2(1, 0))  # Calculate the angle based on the direction

        # Calculate the potential new position
        potential_pos = self.pos + (self.direction * self.speed)

        # Check if the potential position is within screen bounds
        if 0 <= potential_pos.x <= SCREEN_WIDTH and 0 <= potential_pos.y <= SCREEN_HEIGHT:
            # Create a temporary object to check collisions
            temp_enemy = MovingEntity(potential_pos, self.radius, self.speed)

            # Check collision with other enemies and obstacles
            if not self.check_enemy_collision(temp_enemy, enemies) and not check_collision(temp_enemy, obstacles):
                # Move the enemy based on the chosen direction if no collision
                self.move(self.direction)
            else:
                # Resolve collision with other enemies
                self.resolve_enemy_collisions(enemies)

    def check_enemy_collision(self, temp_enemy, enemies):
        for enemy in enemies:
            if enemy != self:  # Avoid checking collision with itself
                dist = distance_between_points(temp_enemy, enemy)
                # If the distance is less than the sum of radii, there's a collision
                if dist < temp_enemy.radius + enemy.radius:
                    return True
        return False
    
    def resolve_enemy_collisions(self, enemies):
        for enemy in enemies:
            if enemy != self:  # Avoid checking collision with itself
                dist = distance_between_points(self, enemy)
                if dist < self.radius + enemy.radius:  # Collision detected
                    # Calculate the overlap
                    overlap = self.radius + enemy.radius - dist

                    # Calculate the direction to move away from the other enemy
                    direction = evade(self, enemy) # Move away from the other enemy
                    self.pos += direction * overlap  # Push the enemy out of the collision
                    # todo: modify the direction here to change the movement angle
    
    def should_hide(self, player):
        return (self.pos - player.pos).length() < 300



