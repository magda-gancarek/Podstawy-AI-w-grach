import pygame
import math
class Wall:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        v = self.end - self.start
        self.normal = pygame.Vector2(v.y, -v.x).normalize()


    def draw_wall(self, screen):
        pygame.draw.line(screen, "white", self.start, self.end, 2)
        # middle of the wall
        middle = (self.start + self.end) * 0.5
        line_length = 50
        direction_vector = self.normal * line_length

        # Calculate the end point
        end_point = middle + direction_vector
        pygame.draw.line(screen, "pink", middle, end_point, 1)