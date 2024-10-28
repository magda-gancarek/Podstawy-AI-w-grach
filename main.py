import pygame
from player import Player
from enemy import spawn_enemy
from obstacle import Obstacle
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, OBSTICLE_COUNT
import sys
import random

pygame.init()

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Initialize player, obstacles, and enemies
player = Player(pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
obstacles = [
        Obstacle(
            pygame.Vector2(random.randint(50, SCREEN_WIDTH - 50),random.randint(50, SCREEN_HEIGHT - 50)), 
            random.randint(20, 70) 
        )
        for _ in range(OBSTICLE_COUNT)
    ]
enemies = spawn_enemy(obstacles)

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.check_player_collision(obstacles)
    player.player_move(keys)
    player.player_rotate()

    # Clear screen
    screen.fill("black")

    # Draw obstacles
    for o in obstacles:
        o.draw_obstacle(screen)

    # Draw enemies
    for e in enemies:
        e.draw_enemy(screen)
        e.update(player, enemies, obstacles, screen)

    # Draw player
    player.draw(screen)
    player.draw_triangle(screen)
    player.draw_light_beam(screen)

    # Update the display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
