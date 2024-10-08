import pygame
import sys
import math
import random

pygame.init()

# TO DO:
# Steering behaviours for enemies
# WANDER
# HIDE
# WALL AVOIDING
# OBSTICLE AVOIDING
# GROUP -> ATTACK


SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
LIGHT_RADIUS = 200
LIGHT_ANGLE = 60  # in degrees
RED = (255, 0, 0)
GREEN = (0, 255, 0)
TRANSPARENT_YELLOW = (255, 255, 0, 128)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
FPS = 60
ENEMY_COUNT = 100
ENEMY_RADIUS = 10

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class Player:
    def __init__(self, pos):
        self.angle = 0
        self.speed = 5
        self.size = 30
        self.radius = 30
        self.pos = pos
        self.health = 100

    def player_rotate(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Calculate the angle between the player and the mouse position
        dx = mouse_x - self.pos.x
        dy = self.pos.y - mouse_y  # Invert dy because y-coordinates in Pygame increase downwards
        self.angle = math.degrees(math.atan2(dy, dx))

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.pos.x), int(self.pos.y)), self.radius)
    
    def draw_triangle(self, screen):
        # Calculate the points of the triangle
        front_x = self.pos.x + self.size * math.cos(math.radians(self.angle))
        front_y = self.pos.y - self.size * math.sin(math.radians(self.angle))

        left_x = self.pos.x + self.size * math.cos(math.radians(self.angle + 120))
        left_y = self.pos.y - self.size * math.sin(math.radians(self.angle + 120))

        right_x = self.pos.x + self.size * math.cos(math.radians(self.angle + 240))
        right_y = self.pos.y - self.size * math.sin(math.radians(self.angle + 240))

        points = [(front_x, front_y), (left_x, left_y), (right_x, right_y)]
        pygame.draw.polygon(screen, GREEN, points)

        # Draw the direction line from the front of the triangle
        line_length = 200
        line_end_x = front_x + line_length * math.cos(math.radians(self.angle))
        line_end_y = front_y - line_length * math.sin(math.radians(self.angle))
        pygame.draw.line(screen, YELLOW, (front_x, front_y), (line_end_x, line_end_y), 2)
    
    def draw_light_beam(self, screen):
        # Calculate the end points of the light beam
        mouse_x, mouse_y = pygame.mouse.get_pos()
        front_x = self.pos.x + self.size * math.cos(math.radians(self.angle))
        front_y = self.pos.y - self.size * math.sin(math.radians(self.angle))
        angle = math.degrees(math.atan2(mouse_y - front_y, mouse_x - front_x))
        start_angle = math.radians(angle - LIGHT_ANGLE / 2)
        end_angle = math.radians(angle + LIGHT_ANGLE / 2)
        points = [(front_x, front_y)]

        for i in range(30):
            ang = start_angle + i * (end_angle - start_angle) / 29
            for r in range(LIGHT_RADIUS):
                x = front_x + r * math.cos(ang)
                y = front_y + r * math.sin(ang)
                if screen.get_at((int(x), int(y))) == WHITE or not (0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT):
                    break
            points.append((x, y))
        # Draw transparent shape
        beam_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(beam_surface, TRANSPARENT_YELLOW, points)
        screen.blit(beam_surface, (0, 0))

    def player_move(self, keys):
        if keys[pygame.K_LEFT]:
            self.pos.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.pos.x += self.speed
        if keys[pygame.K_UP]:
            self.pos.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.pos.y += self.speed
        
        # Keep player on the screen
        self.pos.x = max(0, min(self.pos.x, SCREEN_WIDTH - 20))
        self.pos.y = max(0, min(self.pos.y, SCREEN_HEIGHT - 20))

class Obstacle:
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius

    def draw_obsticle(self, screen):
        pygame.draw.circle(screen, WHITE, (self.pos.x, self.pos.y), self.radius)


class Enemy:
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius

    def draw_enemy(self, screen, obsticle):
        pygame.draw.circle(screen, RED, (self.pos.x, self.pos.y), self.radius)

# Create obstacles
obstacles = [
        Obstacle(
            pygame.Vector2(random.randint(50, SCREEN_WIDTH - 50),random.randint(50, SCREEN_HEIGHT - 50)), 
            random.randint(20, 70) 
        )
        for _ in range(5)
    ]

def distance_between_points(p1, p2):
    # Calculate distance between two points
    return math.sqrt((p1.pos.x - p2.pos.x) ** 2 + (p1.pos.y - p2.pos.y) ** 2)

def check_player_collision(player, obstacles):

    for obstacle in obstacles:
        # Calculate the distance between player and obstacle centers
        dist = distance_between_points(player, obstacle)

        # Check if the distance is less than the sum of the radii (collision condition)
        if dist < player.radius + obstacle.radius:
            # Calculate the overlap distance
            overlap = player.radius + obstacle.radius - dist

            # Move the player back by the overlap distance to prevent crossing
            # Calculate the direction to move the player away from the obstacle
            direction = (player.pos - obstacle.pos).normalize()
            player.pos += direction * overlap


def check_collision(object, obstacles):
    for obstacle in obstacles:
        dist = distance_between_points(object, obstacle)
        # If the distance is less than the sum of radii, there's a collision
        if dist < object.radius + obstacle.radius:
            return True
    return False

enemies = []

def spawn_enemy(enemies, obstacles):
    # Spawn an enemy at a random position, avoiding obstacles
    for i in range(ENEMY_COUNT):
        x = random.randint(ENEMY_RADIUS, SCREEN_WIDTH - ENEMY_RADIUS)
        y = random.randint(ENEMY_RADIUS, SCREEN_HEIGHT - ENEMY_RADIUS)
        enemy_pos = pygame.Vector2(x, y)
        enemy = Enemy(enemy_pos, ENEMY_RADIUS)
        # Check if this position collides with any obstacle
        if not check_collision(enemy, obstacles):
            print("I an not colliding")
            enemies.append(enemy)

spawn_enemy(enemies, obstacles)


# Main game loop
clock = pygame.time.Clock()
running = True
player = Player(pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    check_player_collision(player, obstacles)
    player.player_move(keys)
    player.player_rotate()

    # Clear screen
    screen.fill("black")

    # Draw obstacles
    for o in obstacles:
        o.draw_obsticle(screen)
    # Draw enemies
    for e in enemies:
        e.draw_enemy(screen, obstacles)

    # Draw player
    player.draw(screen)
    player.draw_triangle(screen)
    player.draw_light_beam(screen)

    # Update the display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
