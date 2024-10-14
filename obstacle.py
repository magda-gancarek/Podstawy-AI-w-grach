import pygame
from settings import WHITE


class Obstacle:
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius

    def draw_obstacle(self, screen):
        pygame.draw.circle(screen, WHITE, (self.pos.x, self.pos.y), self.radius)

