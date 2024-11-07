import pygame
import math
class Wall:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        v = self.end - self.start
        self.normal = pygame.Vector2(v.y, -v.x).normalize()
        self.middle = (self.start + self.end) * 0.5
        line_length = 50
        direction_vector = self.normal * line_length
        self.end_point = self.middle + direction_vector


    def draw_wall(self, screen):
        pygame.draw.line(screen, "white", self.start, self.end, 2)
        pygame.draw.line(screen, "pink", self.middle, self.end_point, 1)