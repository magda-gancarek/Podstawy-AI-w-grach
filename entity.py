import pygame
from settings import WHITE


class MovingEntity:
    def __init__(self, pos, radius, speed):
        self.pos = pos
        self.radius = radius
        self.speed = speed

    def move(self, direction):
        self.pos += direction * self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.pos.x), int(self.pos.y)), self.radius)



