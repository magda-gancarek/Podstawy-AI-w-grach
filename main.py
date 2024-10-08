import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 20
OBSTACLE_SIZE = 40
LIGHT_RADIUS = 200
LIGHT_ANGLE = 60  # in degrees
OBSTACLE_COLOR = (255, 0, 0)
TRANSPARENT_YELLOW = (255, 255, 0, 128)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create player
player = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE)


class Obstacle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, screen):
        pygame.draw.circle(screen, OBSTACLE_COLOR, (self.x, self.y), self.radius)

# Create obstacles
obstacles = [Obstacle(random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50), 30) for _ in range(5)]

def draw_light_beam(surface, player_rect, angle, radius):
    # Calculate the end points of the light beam
    start_angle = math.radians(angle - LIGHT_ANGLE / 2)
    end_angle = math.radians(angle + LIGHT_ANGLE / 2)
    points = [player_rect.center]

    for i in range(30):
        ang = start_angle + i * (end_angle - start_angle) / 29
        for r in range(radius):
            x = player_rect.centerx + r * math.cos(ang)
            y = player_rect.centery + r * math.sin(ang)
            if surface.get_at((int(x), int(y))) == OBSTACLE_COLOR or not (0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT):
                break
        points.append((x, y))
    #draw transparent shape
    beam_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(beam_surface, TRANSPARENT_YELLOW, points)
    screen.blit(beam_surface, (0, 0))

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= 5
    if keys[pygame.K_RIGHT]:
        player.x += 5
    if keys[pygame.K_UP]:
        player.y -= 5
    if keys[pygame.K_DOWN]:
        player.y += 5

    # Keep player on the screen
    player.x = max(0, min(player.x, SCREEN_WIDTH - PLAYER_SIZE))
    player.y = max(0, min(player.y, SCREEN_HEIGHT - PLAYER_SIZE))

    # Clear screen
    screen.fill("black")

    # Draw obstacles
    for obstacle in obstacles:
        obstacle.draw(screen)

    # Draw light beam
    mouse_x, mouse_y = pygame.mouse.get_pos()
    angle = math.degrees(math.atan2(mouse_y - player.centery, mouse_x - player.centerx))
    draw_light_beam(screen, player, angle, LIGHT_RADIUS)

    # Draw player
    pygame.draw.rect(screen, "green", player)

    # Update the display
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
