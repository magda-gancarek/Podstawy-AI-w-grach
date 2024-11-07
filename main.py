import pygame
from player import Player
from enemy import spawn_enemy
from obstacle import Obstacle
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, OBSTICLE_COUNT
import sys
import random
from wall import Wall

pygame.init()

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH + 40, SCREEN_HEIGHT+40))

# Initialize player, obstacles, and enemies
player = Player(pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
obstacles = [
        Obstacle(
            pygame.Vector2(random.randint(50, SCREEN_WIDTH - 50),random.randint(50, SCREEN_HEIGHT - 50)), 
            random.randint(20, 70) 
        )
        for _ in range(OBSTICLE_COUNT)
    ]
walls = [
            Wall(pygame.Vector2(SCREEN_WIDTH , 0+20), pygame.Vector2(0+20, 0+20)), # -
            Wall(pygame.Vector2(0+20, SCREEN_HEIGHT), pygame.Vector2(SCREEN_WIDTH , SCREEN_HEIGHT)), # _
            Wall(pygame.Vector2(0+20, 0+20), pygame.Vector2(0+20 , SCREEN_HEIGHT)), # | <-
            Wall(pygame.Vector2(SCREEN_WIDTH , SCREEN_HEIGHT), pygame.Vector2(SCREEN_WIDTH, 0+20)), # -> |
         ]

enemies = spawn_enemy(obstacles)

# Main game loop
clock = pygame.time.Clock()
running = True

target_position = pygame.Vector2(0, 0)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Update target position to mouse click location
            # for seek 
            target_position = pygame.Vector2(pygame.mouse.get_pos())

    keys = pygame.key.get_pressed()
    player.check_player_collision(obstacles)
    player.player_move(keys)
    player.player_rotate()

    # Clear screen
    screen.fill("black")


    # Draw obstacles
    for o in obstacles:
        o.draw_obstacle(screen)

    for w in walls:
        w.draw_wall(screen)      

    # Draw enemies
    for e in enemies:
        #e.seek(target_position)
        #e.flee(target_position)
        e.wander(screen)
        # bez włączenego wander zmienia rysowanie boxa w obsticle avoidance XD
        e.wall_avoidance(walls)
        e.obstacle_avoidance(screen, obstacles)

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
