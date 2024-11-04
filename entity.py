import pygame
from settings import WHITE


class MovingEntity:
    def __init__(self, pos, radius, max_speed):
        self.pos = pos
        self.radius = radius
        self.max_speed = max_speed

    def move(self, direction):
        self.pos += direction * self.max_speed

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.pos.x), int(self.pos.y)), self.radius)



