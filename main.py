import pygame
from player import Player
from enemy import spawn_enemy
from obstacle import Obstacle
from settings import FPS, OBSTACLE_COUNT, SCREEN_HEIGHT, SCREEN_WIDTH, screen
import sys
import random
from wall import Wall
from utils import check_collision
import math

pygame.init()

# TO DO

# obstacles avoidance: poprawić kolizje, czasem wchodzą na przeszkody. dlaczego?
# Atak w stronę przeciwnika - Wszytskie się ruszają a nie tylko wybrana grupa 


# Initialize player, obstacles, and enemies
player = Player(pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

obstacles = []
for _ in range(OBSTACLE_COUNT):
    o = Obstacle(
        pygame.Vector2(random.randint(50, SCREEN_WIDTH - 50),random.randint(50, SCREEN_HEIGHT - 50)), 
        random.randint(20, 70) 
    )
    if not check_collision(o, obstacles):
        obstacles.append(o)

walls = [
            Wall(pygame.Vector2(SCREEN_WIDTH-20 , 0+20), pygame.Vector2(0+20, 0+20)), # -
            Wall(pygame.Vector2(0+20, SCREEN_HEIGHT-40), pygame.Vector2(SCREEN_WIDTH-20 , SCREEN_HEIGHT-40)), # _
            Wall(pygame.Vector2(0+20, 0+20), pygame.Vector2(0+20 , SCREEN_HEIGHT-40)), # | <-
            Wall(pygame.Vector2(SCREEN_WIDTH-20 , SCREEN_HEIGHT-40), pygame.Vector2(SCREEN_WIDTH-20, 0+20)), # -> |
         ]

enemies = spawn_enemy(obstacles)

# Main game loop
clock = pygame.time.Clock()
running = True

#target_position = pygame.Vector2(0, 0)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        self.radius = 5  # Radius of the bullet
        self.color = "white"
        self.x = x
        self.y = y

        # Calculate direction vector
        angle = math.atan2(target_y - y, target_x - x)
        self.vel_x = math.cos(angle) * 20
        self.vel_y = math.sin(angle) * 20

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def draw(self, surface):
        # Draw the bullet as a circle
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

bullets = []

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #elif event.type == pygame.MOUSEBUTTONDOWN:
            # Update target position to mouse click location
            # for seek 
            #target_position = pygame.Vector2(pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Fire a bullet toward mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            bullets.append(Bullet(player.pos.x + player.size // 2, player.pos.y + player.size // 2, mouse_x, mouse_y))

    keys = pygame.key.get_pressed()
    player.check_player_collision(obstacles)
    player.player_move(keys)
    player.player_rotate()

    # Clear screen
    screen.fill("black")

    for b in bullets:
        b.draw(screen)

    for bullet in bullets[:]:  # Copy the list to avoid modifying it while iterating
        bullet.move()
        if bullet.x < 0 or bullet.x > SCREEN_WIDTH or bullet.y < 0 or bullet.y > SCREEN_HEIGHT:
            bullets.remove(bullet)  # Remove bullet if it goes off-screen
        else:
            for enemy in enemies[:]:  # Copy the list to avoid modifying it while iterating
                # Distance-based collision detection
                distance = math.sqrt((bullet.x - (enemy.pos.x + enemy.radius // 2)) ** 2 + 
                                     (bullet.y - (enemy.pos.y + enemy.radius // 2)) ** 2)
                if distance < bullet.radius + enemy.radius // 2:
                    enemies.remove(enemy)  # Remove the enemy
                    bullets.remove(bullet)  # Remove the bullet
                    break

    # Draw obstacles
    for o in obstacles:
        o.draw_obstacle(screen)

    for w in walls:
        w.draw_wall(screen)      

    # Draw enemies
    for e in enemies:
        #e.arrive(screen, target_position)
        #e.seek(screen, target_position)
        #e.flee(screen, target_position)
        # e.wander(screen) # bez włączenego wander zmienia rysowanie boxa w obstacle avoidance XD
        # e.wall_avoidance(screen, walls)
        # e.obstacle_avoidance(screen, obstacles)

        # # Check if the agent should hide
        # distance_to_enemy = (e.pos - player.pos).length()
        # danger_zone = 300
        # pygame.draw.circle(screen, "red", player.pos, danger_zone, 1)
        # if distance_to_enemy < danger_zone:
        #     hiding_spot, distance = e.find_hiding_spot(screen, player, obstacles)
        #     # Move agent to hiding spot
        #     if distance == sys.maxsize:
        #         e.evade_move(screen, hiding_spot)
        #     else:
        #         steering = e.arrive(screen, hiding_spot)
        # e.draw_enemy(screen)
        # e.update(player, enemies, obstacles, walls, screen)

        e.update_sum_force(player, enemies, obstacles, walls, screen)
        e.draw_enemy(screen)


    # Draw player
    player.draw(screen)
    player.draw_light_beam(screen)

    # Update the display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
