import pygame
from player import Player
from enemy import spawn_enemy
from obstacle import Obstacle
from settings import FPS, OBSTACLE_COUNT, SCREEN_HEIGHT, SCREEN_WIDTH, screen
import sys
import random
from wall import Wall
from utils import check_collision, distance_between_points, check_collision_plus_bounding
import math
from settings import *

pygame.init()

# TO DO
# Atak w stronę przeciwnika - Wszytskie się ruszają a nie tylko wybrana grupa 


# Initialize player, obstacles, and enemies
player = Player(pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

obstacles = []
for _ in range(OBSTACLE_COUNT):
    radius = random.randint(50, 70)
    margin = BOUND_FOR_HIDING_SPOT + 50 + radius
    pos = pygame.Vector2(random.randint(margin, SCREEN_WIDTH - margin),random.randint(margin, SCREEN_HEIGHT - margin))
    o = Obstacle(pos, radius)
    if not check_collision_plus_bounding(o, obstacles, PLAYER_SIZE + 10):
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
        self.color = "yellow"
        self.x = x
        self.y = y
        self.pos = pygame.Vector2(x,y)

        # Calculate direction vector
        angle = math.atan2(target_y - y, target_x - x)
        self.vel_x = math.cos(angle) * 20
        self.vel_y = math.sin(angle) * 20

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.pos = pygame.Vector2(self.x,self.y)

    def draw(self, surface):
        # Draw the bullet as a circle
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

bullets = []
damage_timer = 0
damage_flash_duration = 300  # milliseconds
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)
game_over = False

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

    # Clear screen
    screen.fill("black")

    if not game_over:
        keys = pygame.key.get_pressed()
        player.check_player_collision(obstacles)
        player.player_move(keys)
        player.player_rotate()

        for b in bullets:
            b.draw(screen)

        for bullet in bullets[:]:  # Copy the list to avoid modifying it while iterating
            bullet.move()

            if check_collision(bullet, obstacles):
                bullets.remove(bullet)  # Remove the bullet
            elif bullet.x < 20 or bullet.x > SCREEN_WIDTH-20 or bullet.y < 20 or bullet.y > SCREEN_HEIGHT-20:
                bullets.remove(bullet)  # Remove bullet if it goes off-screen
            else:
                for e in enemies[:]:  # Copy the list to avoid modifying it while iterating
                    # Distance-based collision detection
                    distance = math.sqrt((bullet.x - (e.pos.x + e.radius // 2)) ** 2 + 
                                        (bullet.y - (e.pos.y + e.radius // 2)) ** 2)
                    if distance < bullet.radius + e.radius // 2:
                        enemies.remove(e)  # Remove the enemy
                        bullets.remove(bullet)  # Remove the bullet
                        break
                

        # Draw obstacles
        for o in obstacles:
            o.draw_obstacle(screen)

        for w in walls:
            w.draw_wall(screen)      

        # Draw enemies
        for e in enemies:
            e.update_sum_force(player, enemies, obstacles, walls, screen)
            e.push_out_of_obstacles(obstacles)
            e.draw_enemy(screen)

        # Draw player
        player.draw(screen)
        player.draw_light_beam(screen)

        # Check atack from enemies
        for e in enemies:
            if distance_between_points(player, e) < 20:
                if damage_timer == 0:  # Apply damage only if not in cooldown
                    player.health -= e.damage  # Decrease HP
                    damage_timer = pygame.time.get_ticks()  # Start damage timer

        # Draw player with damage effect
        if damage_timer > 0:
            if pygame.time.get_ticks() - damage_timer < damage_flash_duration:
                player.color = "red"  # Flash red
            else:
                damage_timer = 0  # Reset timer
                player.color = "chartreuse4"  # Normal color

        # Display HP
        hp_text = font.render(f"HP: {player.health}", True, "white")
        screen.blit(hp_text, (40, 30))
        pygame.draw.rect(screen, "red", (40, 60, 200, 20))  # Background (red)
        pygame.draw.rect(screen, "green", (40, 60, max(0, player.health * 2), 20))  # Foreground (green)

        # Check game over
        if player.health <= 0:
            game_over = True
            print("Game Over")
    else:
        game_over_text = game_over_font.render("GAME OVER", True, "red")
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, game_over_rect)


    # Update the display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
