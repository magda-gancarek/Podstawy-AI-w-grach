import pygame
screen = pygame.display.set_mode()
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

LIGHT_RADIUS = 200
LIGHT_ANGLE = 60  # in degrees

RED = (255, 0, 0)
GREEN = (0, 255, 0)
TRANSPARENT_YELLOW = (255, 255, 0, 128)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

FPS = 24

PLAYER_SIZE  = 15

ENEMY_COUNT = 30
ENEMY_RADIUS = 15
ENEMY_SPEED = 3

OBSTACLE_COUNT = 20

# Wander parameters
WANDER_RADIUS = 40   # Radius of the wander circle
WANDER_DISTANCE = 100  # Distance the wander circle is projected in front of the agent
WANDER_JITTER = 20.0   # Maximum displacement added to the wander target each second

BOUNDING = 150

BOUND_FOR_HIDING_SPOT = 70
MIN_COLISION_DETECTION_BOX_LEN = 45
ARRIVE_SLOWING_RADIUS = 100
OBSTACLE_AVOIDANCE_BOUNDING_RADIUS = 10
