import math
from entity import MovingEntity
from utils import distance_between_points
import pygame
from settings import *

class Player(MovingEntity):
    def __init__(self, pos):
        self.angle = 0
        self.speed = 5
        self.size = PLAYER_SIZE
        self.radius = PLAYER_SIZE
        self.pos = pos
        self.health = 100
        self.color = "chartreuse4"

    def player_move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.pos.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.pos.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.pos.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.pos.y += self.speed
        
        # Keep player on the screen
        self.pos.x = max(0, min(self.pos.x, SCREEN_WIDTH - 20))
        self.pos.y = max(0, min(self.pos.y, SCREEN_HEIGHT - 20))

    def player_rotate(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Calculate the angle between the player and the mouse position
        dx = mouse_x - self.pos.x
        dy = self.pos.y - mouse_y  # Invert dy because y-coordinates in Pygame increase downwards
        self.angle = math.degrees(math.atan2(dy, dx))
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        self.draw_triangle(screen)
        

    def draw_triangle(self, screen):
        # Calculate the points of the triangle
        front_x = self.pos.x + self.size * math.cos(math.radians(self.angle))
        front_y = self.pos.y - self.size * math.sin(math.radians(self.angle))

        left_x = self.pos.x + self.size * math.cos(math.radians(self.angle + 120))
        left_y = self.pos.y - self.size * math.sin(math.radians(self.angle + 120))

        right_x = self.pos.x + self.size * math.cos(math.radians(self.angle + 240))
        right_y = self.pos.y - self.size * math.sin(math.radians(self.angle + 240))

        points = [(front_x, front_y), (left_x, left_y), (right_x, right_y)]
        pygame.draw.polygon(screen, "darkgreen", points)

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
                
                # Check bounds before accessing the pixel
                if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                    if screen.get_at((int(x), int(y))) == WHITE:
                        break # Stop if the beam hits a wall
                else:
                    break # Break if out of bounds

            points.append((x, y))
            
        # Draw transparent shape
        beam_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        #pygame.draw.polygon(beam_surface, TRANSPARENT_YELLOW, points)
        screen.blit(beam_surface, (0, 0))

    def check_player_collision(self, obstacles):

        for obstacle in obstacles:
            # Calculate the distance between player and obstacle centers
            dist = distance_between_points(self, obstacle)

            # Check if the distance is less than the sum of the radii (collision condition)
            if dist < self.radius + obstacle.radius:
                # Calculate the overlap distance
                overlap = self.radius + obstacle.radius - dist

                # Move the player back by the overlap distance to prevent crossing
                # Calculate the direction to move the player away from the obstacle
                direction = (self.pos - obstacle.pos).normalize()
                self.pos += direction * overlap