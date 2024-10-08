import pygame
import sys
import math
import random

pygame.init()

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

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 5
        self.size = 30

    def player_rotate(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Calculate the angle between the player and the mouse position
        dx = mouse_x - self.x
        dy = self.y - mouse_y  # Invert dy because y-coordinates in Pygame increase downwards
        self.angle = math.degrees(math.atan2(dy, dx))

    def draw(self, screen):
        # Calculate the points of the triangle
        front_x = self.x + self.size * math.cos(math.radians(self.angle))
        front_y = self.y - self.size * math.sin(math.radians(self.angle))

        left_x = self.x + self.size * math.cos(math.radians(self.angle + 120))
        left_y = self.y - self.size * math.sin(math.radians(self.angle + 120))

        right_x = self.x + self.size * math.cos(math.radians(self.angle + 240))
        right_y = self.y - self.size * math.sin(math.radians(self.angle + 240))

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
        front_x = self.x + self.size * math.cos(math.radians(self.angle))
        front_y = self.y - self.size * math.sin(math.radians(self.angle))
        angle = math.degrees(math.atan2(mouse_y - front_y, mouse_x - front_x))
        start_angle = math.radians(angle - LIGHT_ANGLE / 2)
        end_angle = math.radians(angle + LIGHT_ANGLE / 2)
        points = [(front_x, front_y)]

        for i in range(30):
            ang = start_angle + i * (end_angle - start_angle) / 29
            for r in range(LIGHT_RADIUS):
                x = front_x + r * math.cos(ang)
                y = front_y + r * math.sin(ang)
                if screen.get_at((int(x), int(y))) == RED or not (0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT):
                    break
            points.append((x, y))
        # Draw transparent shape
        beam_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(beam_surface, TRANSPARENT_YELLOW, points)
        screen.blit(beam_surface, (0, 0))

    def player_move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed
        
        # Keep player on the screen
        self.x = max(0, min(self.x, SCREEN_WIDTH - 20))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - 20))

class Obstacle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (self.x, self.y), self.radius)

# Create obstacles
obstacles = [
        Obstacle(
            random.randint(50, SCREEN_WIDTH - 50), 
            random.randint(50, SCREEN_HEIGHT - 50), 
            random.randint(20, 70) 
        )
        for _ in range(5)
    ]

# Main game loop
clock = pygame.time.Clock()
running = True
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.player_move(keys)
    player.player_rotate()

    # Clear screen
    screen.fill("black")

    # Draw obstacles
    for obstacle in obstacles:
        obstacle.draw(screen)

    # Draw player
    player.draw(screen)
    player.draw_light_beam(screen)

    # Update the display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
