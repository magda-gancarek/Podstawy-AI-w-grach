import pygame
import random
from entity import MovingEntity
import math
from settings import *
from utils import check_collision, distance_between_points
#from steering_behaviors import hide, wander, evade


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
        self.max_speed = ENEMY_SPEED
        self.velocity = pygame.Vector2(1,0) # default direction #TODO: arrive behaviour
        self.wander_target = pygame.Vector2(0, 0)  # Initialize wander target
        self.max_force = 0.1
        self.acceleration = pygame.Vector2(0, 0)
        self.feelers = []

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

        # # Draw direction line indicating movement direction
        # line_length = 60
        # line_end_x = front_x + line_length * math.cos(math.radians(self.angle))
        # line_end_y = front_y - line_length * math.sin(math.radians(self.angle))
        # pygame.draw.line(screen, RED, (front_x, front_y), (line_end_x, line_end_y), 2)

        # Draw feelers for wall avoidance
        feeler_angles = [0, 30, -30]  # Feelers: straight, right, left
        self.feelers = []
        feeler_lenght = 60
        for angle in feeler_angles:
            direction = self.velocity.rotate(angle).normalize()
            feeler_end = self.pos + direction * feeler_lenght
            self.feelers.append((self.pos, feeler_end))
        for start, end in self.feelers:
            pygame.draw.line(screen, "red", start, end, 1)

        # draw rectangle for obsticles avoidance
        line_length_rect = 200
        line_left_end_x = left_x + line_length_rect * math.cos(math.radians(self.angle))
        line_left_end_y = left_y - line_length_rect * math.sin(math.radians(self.angle))
        pygame.draw.line(screen, "grey", (left_x, left_y), (line_left_end_x, line_left_end_y), 1)

        line_right_end_x = right_x + line_length_rect * math.cos(math.radians(self.angle))
        line_right_end_y = right_y - line_length_rect * math.sin(math.radians(self.angle))
        pygame.draw.line(screen, "grey", (right_x, right_y), (line_right_end_x, line_right_end_y), 1)


    def seek(self, target):
        # Desired velocity is the vector pointing from the agent to the target
        desired_velocity = (target - self.pos).normalize() * self.max_speed
        
        # Steering force is the difference between the desired velocity and current velocity
        steering_force = desired_velocity - self.velocity

        # Limit the steering force to max_force
        if steering_force.length() > self.max_force:
            steering_force = steering_force.normalize() * self.max_force

        # Apply the steering force to the agent's acceleration
        self.apply_steering(steering_force)

        # Debug visuals: return vectors for drawing
        return desired_velocity, steering_force
    
    def wander(self, screen):
        # Random jitter for the wander target
        jitter = pygame.Vector2(
            random.uniform(-1, 1) * WANDER_JITTER,
            random.uniform(-1, 1) * WANDER_JITTER
        )
        self.wander_target += jitter

        # Limit the wander target to remain on the wander circle
        self.wander_target = self.wander_target.normalize() * WANDER_RADIUS

        # Calculate the world-space position of the wander target
        wander_center = self.pos + self.velocity.normalize() * WANDER_DISTANCE
        wander_point = wander_center + self.wander_target

        # Steering force towards the wander point
        steering_force = (wander_point - self.pos).normalize() * self.max_force
        self.apply_steering(steering_force)

        pygame.draw.circle(screen, (100, 100, 100), (int(wander_center.x), int(wander_center.y)), WANDER_RADIUS, 1)
        pygame.draw.circle(screen, (255, 0, 0), (int(wander_point.x), int(wander_point.y)), 5)

    def apply_steering(self, steering):
        # Apply the steering to acceleration and limit to max_force
        self.acceleration += steering
        if self.acceleration.length() > self.max_force:
            self.acceleration = self.acceleration.normalize() * self.max_force


    def update(self, player, enemies, obstacles, screen):
        # Update velocity, position, and reset acceleration
        self.velocity += self.acceleration
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed
        
        # Update the angle based on the direction
        if self.velocity.length() > 0:  # If there's a valid direction
            self.angle = self.velocity.angle_to(pygame.Vector2(1, 0))
        self.acceleration = pygame.Vector2(0, 0)

        # Calculate the potential new position
        potential_pos = self.pos + (self.velocity * self.max_speed)

        # Check if the potential position is within screen bounds
        if 0 <= potential_pos.x <= SCREEN_WIDTH and 0 <= potential_pos.y <= SCREEN_HEIGHT:
            # Create a temporary object to check collisions
            temp_enemy = MovingEntity(potential_pos, self.radius, self.max_speed)

            # Check collision with other enemies and obstacles
            if not self.check_enemy_collision(temp_enemy, enemies) and not check_collision(temp_enemy, obstacles):
                # Move the enemy based on the chosen velocity if no collision
                self.move(self.velocity)
            else:
                # Resolve collision with other enemies
                self.resolve_enemy_collisions(enemies)


    def wall_avoidance(self, walls):
        for x,y in self.feelers:
            print(x,y)
            for wall in walls:
                intersection = self.are_lines_intersecting(x,y, wall.start, wall.end)
                if intersection:
                    self.velocity = wall.normal
    
    def are_lines_intersecting(self, p1, p2, p3, p4):
        """Returns intersection point of lines if they intersect."""
        denom = (p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0])
        if denom == 0:
            return None  # Lines are parallel

        intersect_x = ((p1[0] * p2[1] - p1[1] * p2[0]) * (p3[0] - p4[0]) - (p1[0] - p2[0]) * (p3[0] * p4[1] - p3[1] * p4[0])) / denom
        intersect_y = ((p1[0] * p2[1] - p1[1] * p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] * p4[1] - p3[1] * p4[0])) / denom

        if min(p1[0], p2[0]) <= intersect_x <= max(p1[0], p2[0]) and min(p1[1], p2[1]) <= intersect_y <= max(p1[1], p2[1]) \
                and min(p3[0], p4[0]) <= intersect_x <= max(p3[0], p4[0]) and min(p3[1], p4[1]) <= intersect_y <= max(p3[1], p4[1]):
            return (intersect_x, intersect_y)
        return None

    '''
    def update(self, player, enemies, obstacles, screen):
        # Decide whether to hide or wander
        if self.should_hide(player):
            self.velocity = hide(self, player, obstacles)
        else:
            self.velocity = wander(self, screen)

        # Update the angle based on the direction
        if self.velocity.length() > 0:  # If there's a valid direction
            self.angle = self.velocity.angle_to(pygame.Vector2(1, 0))  # Calculate the angle based on the direction

        # Calculate the potential new position
        potential_pos = self.pos + (self.velocity * self.speed)

        # Check if the potential position is within screen bounds
        if 0 <= potential_pos.x <= SCREEN_WIDTH and 0 <= potential_pos.y <= SCREEN_HEIGHT:
            # Create a temporary object to check collisions
            temp_enemy = MovingEntity(potential_pos, self.radius, self.speed)

            # Check collision with other enemies and obstacles
            if not self.check_enemy_collision(temp_enemy, enemies) and not check_collision(temp_enemy, obstacles):
                # Move the enemy based on the chosen velocity if no collision
                self.move(self.velocity)
            else:
                # Resolve collision with other enemies
                self.resolve_enemy_collisions(enemies)
    '''
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
                    direction = self.evade(self, enemy) # Move away from the other enemy
                    self.pos += direction * overlap  # Push the enemy out of the collision
                    # todo: modify the direction here to change the movement angle
    
    def should_hide(self, player):
        return (self.pos - player.pos).length() < 300
    
    def evade(enemy, target):
        # Move in the opposite direction of the target
        return (enemy.pos - target.pos).normalize()

