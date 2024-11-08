import pygame
import random
from entity import MovingEntity
import math
from settings import *
import sys
from utils import check_collision, distance_between_points
#from steering_behaviors import hide, wander, evade

def spawn_enemy(obstacles):
    enemies = []
    # Spawn an enemy at a random position, avoiding obstacles
    for _ in range(ENEMY_COUNT):
        x = random.randint(ENEMY_RADIUS, SCREEN_WIDTH - ENEMY_RADIUS)
        y = random.randint(ENEMY_RADIUS, SCREEN_HEIGHT - ENEMY_RADIUS)
        enemy_pos = pygame.Vector2(x, y)
        enemy = Enemy(enemy_pos)
        # Check if this position collides with any obstacle
        if not check_collision(enemy, obstacles):
            enemies.append(enemy)
    return enemies


# Function to blend colors from green to red based on a value (0 to 200)
def blend_color(value, max_value=200):
    # Clamp value between 0 and max_value
    value = max(0, min(value, max_value))
    # Calculate the ratio for blending (1 means green, 0 means red)
    ratio = value / max_value
    red = int(255 * (1 - ratio))
    green = int(255 * ratio)
    return (red, green, 0)  # Blue remains 0 to keep it in the green-red spectrum

class Enemy(MovingEntity):
    def __init__(self, pos):
        self.pos = pos
        self.angle = 0
        self.radius = ENEMY_RADIUS
        self.max_speed = ENEMY_SPEED
        self.velocity = pygame.Vector2(1,0) # default direction 
        # Vector perpendicular to direction 
        self.side = self.velocity.rotate(90).normalize()

        self.wander_target = pygame.Vector2(0, 0)  # Initialize wander target
        self.max_force = 0.1
        self.acceleration = pygame.Vector2(0, 0)
        self.feelers = []

    def draw_enemy(self, screen): 
        # triangle       
        front_x = self.pos.x + self.radius * math.cos(math.radians(self.angle))
        front_y = self.pos.y - self.radius * math.sin(math.radians(self.angle))

        left_x = self.pos.x + self.radius * math.cos(math.radians(self.angle + 120))
        left_y = self.pos.y - self.radius * math.sin(math.radians(self.angle + 120))

        right_x = self.pos.x + self.radius * math.cos(math.radians(self.angle + 240))
        right_y = self.pos.y - self.radius * math.sin(math.radians(self.angle + 240))

        points = [(front_x, front_y), (left_x, left_y), (right_x, right_y)]

        pygame.draw.circle(screen, "darksalmon", (self.pos.x, self.pos.y), self.radius)
        pygame.draw.polygon(screen, "coral3", points)
        pygame.draw.circle(screen, "white", (front_x, front_y), 3)

        # # Draw direction line indicating movement direction
        # line_length = 60
        # line_end_x = front_x + line_length * math.cos(math.radians(self.angle))
        # line_end_y = front_y - line_length * math.sin(math.radians(self.angle))
        # pygame.draw.line(screen, RED, (front_x, front_y), (line_end_x, line_end_y), 2)


    def seek(self, target):
        # Desired velocity is the vector pointing from the agent to the target
        desired_velocity = (target - self.pos).normalize() * self.max_speed
        
        # Steering force is the difference between the desired velocity and current velocity
        steering_force = desired_velocity - self.velocity

        # Limit the steering force to max_force
        if steering_force.length() > self.max_force:
            steering_force = steering_force.normalize() * self.max_force

        # Apply the steering force to the agent's acceleration
        self.apply_steering(steering_force)
    
    def flee(self, target):
        # Desired velocity is the vector pointing from the target to the agent
        desired_velocity = (self.pos - target).normalize() * self.max_speed
        
        # Steering force is the difference between the desired velocity and current velocity
        steering_force = desired_velocity - self.velocity

        # Limit the steering force to max_force
        if steering_force.length() > self.max_force:
            steering_force = steering_force.normalize() * self.max_force

        # Apply the steering force to the agent's acceleration
        self.apply_steering(steering_force)

    def arrive(self, screen, target_pos):
        # Calculate the desired velocity
        to_target = target_pos - self.pos
        distance = to_target.length()
        slowing_radius = 200

        pygame.draw.circle(screen, "red", target_pos, 2, 2)
        pygame.draw.circle(screen, "green", target_pos, slowing_radius, 1)

        # If we're close enough to the target, stop
        if distance < 2:
            self.velocity =  pygame.Vector2(0, 0)
        else:
            # Scale the speed according to distance within the slowing radius
            if distance < slowing_radius:
                desired_speed = self.max_speed * (distance / slowing_radius)
                pygame.draw.circle(screen, blend_color(distance), target_pos, distance, 1)
            else:
                desired_speed = self.max_speed

            # Set the desired velocity towards the target with the calculated speed
            desired_velocity = to_target.normalize() * desired_speed
            
            # Calculate the steering force
            steering_force = desired_velocity - self.velocity
            # Limit the steering force to max_force
            if steering_force.length() > self.max_force:
                steering_force = steering_force.normalize() * self.max_force

            # Apply the steering force to the agent's acceleration
            print(steering_force)
            self.apply_steering(steering_force)


    def wander(self, screen):
        # Random jitter for the wander target
        jitter = pygame.Vector2(
            random.uniform(-1, 1) * WANDER_JITTER,
            random.uniform(-1, 1) * WANDER_JITTER
        )
        self.wander_target += jitter

        # Limit the wander target to remain on the wander circle
        self.wander_target = self.wander_target.normalize() * WANDER_RADIUS

        # Calculate the world-space position of the wander target
        wander_center = self.pos + self.velocity.normalize() * WANDER_DISTANCE
        wander_point = wander_center + self.wander_target

        # Steering force towards the wander point
        steering_force = (wander_point - self.pos).normalize() * self.max_force
        self.apply_steering(steering_force)

        pygame.draw.circle(screen, "grey", (int(wander_center.x), int(wander_center.y)), WANDER_RADIUS, 1)
        pygame.draw.circle(screen, "red", (int(wander_point.x), int(wander_point.y)), 5)

    def apply_steering(self, steering):
        # Apply the steering to acceleration and limit to max_force
        self.acceleration += steering
        if self.acceleration.length() > self.max_force:
            self.acceleration = self.acceleration.normalize() * self.max_force

    '''
    def calculate(self, player, enemies, walls, obstacles, screen):
        self.steering_force.zero() # reset
        self.steering_force +=         
        #e.seek(target_position)
        #e.flee(target_position)
        self.wander(screen)
        # bez włączenego wander zmienia rysowanie boxa w obsticle avoidance XD
        self.wall_avoidance(walls)
        self.obstacle_avoidance(screen, obstacles)

    def update(self, player, enemies, obstacles, walls, screen, elapsed):
        steering_force = self.calculate(player, enemies, obstacles, screen)
        acceleration = steering_force / self.mass
        self.velocity += acceleration * elapsed
        # # make sure it does not exeed max speed
        # self.velocity.truncate(self.max_speed)
        # self.position += self.velocity * elapsed
        # # update heading if it has a velocity
        # if self.velocity.length_sq > EPSILON:
        #     self.heading = self.velocity.normalized
        #     self.side = self.heading.perp
            
        # if self.is_non_penetration_on:
        #     self.enforce_non_penetration(self.world.vehicles)
            
        # # treat the screen as a toroid
        # self.position.wrap_around(self.world.size)

    '''
    def update(self, player, enemies, obstacles, screen):
        # Update velocity, position, and reset acceleration
        self.velocity += self.acceleration
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed
        
        # Update the angle based on the direction
        if self.velocity.length() > 0:  # If there's a valid direction
            self.angle = self.velocity.angle_to(pygame.Vector2(1, 0))

        self.acceleration = pygame.Vector2(0, 0)

        # Calculate the potential new position
        potential_pos = self.pos + (self.velocity * self.max_speed)

        # Check if the potential position is within screen bounds
        if 0 <= potential_pos.x <= SCREEN_WIDTH and 0 <= potential_pos.y <= SCREEN_HEIGHT:
            # Create a temporary object to check collisions
            temp_enemy = MovingEntity(potential_pos, self.radius, self.max_speed)

            # Check collision with other enemies and obstacles
            if not self.check_enemy_collision(temp_enemy, enemies) and not check_collision(temp_enemy, obstacles):
                # Move the enemy based on the chosen velocity if no collision
                self.move(self.velocity)
            else:
                # Resolve collision with other enemies
                self.resolve_enemy_collisions(enemies)

    def wall_avoidance(self, screen, walls):
        # Draw feelers 
        feeler_angles = [0, 30, -30]  # Feelers: straight, right, left
        self.feelers = []
        feeler_lenght = 100
        for angle in feeler_angles:
            direction = self.velocity.rotate(angle).normalize()
            feeler_end = self.pos + direction * feeler_lenght
            self.feelers.append((self.pos, feeler_end))
        for start, end in self.feelers:
            pygame.draw.line(screen, "coral", start, end, 1)

        dist_to_closest_wall = sys.maxsize
        closest_wall = None
        closest_point = pygame.Vector2(0.0, 0.0)

        for x,y in self.feelers:
            for wall in walls:
                intersection, distance_to_wall, point_of_intersection = self.are_lines_intersecting(x,y, wall.start, wall.end)
                if intersection:
                    pygame.draw.line(screen, "red", wall.start, wall.end, 2)
                    if distance_to_wall < dist_to_closest_wall:
                        dist_to_closest_wall = distance_to_wall
                        closest_wall = wall
                        closest_point = point_of_intersection

            if closest_wall:
                feeler = pygame.Vector2(x,y)
                overshoot = feeler - closest_point
                # create force away from wall
                steering_force = closest_wall.normal * overshoot.length()
                self.apply_steering(steering_force)
    
    def are_lines_intersecting(self, A, B, C, D):
        rTop = (A.y - C.y) * (D.x - C.x) - (A.x - C.x) * (D.y - C.y)
        rBot = (B.x - A.x) * (D.y - C.y) - (B.y - A.y) * (D.x - C.x)

        sTop = (A.y - C.y) * (B.x - A.x) - (A.x - C.x) * (B.y - A.y)
        sBot = (B.x - A.x) * (D.y - C.y) - (B.y - A.y) * (D.x - C.x)

        if (rBot == 0) or (sBot == 0):
            # lines are parallel
            return False, None, None

        r = rTop / rBot
        s = sTop / sBot

        if (r > 0) and (r < 1) and (s > 0) and (s < 1):
            dist = pygame.math.Vector2.distance_to(A, B) * r
            point = A + r * (B - A)
            return True, dist, point
        else:
            return False, 0, None

    def get_obstacles_within_view_range(self, obstacles, view_range):
        found = []
        for obstacle in obstacles:
            radii = view_range + obstacle.radius
            if pygame.math.Vector2.distance_squared_to(self.pos, obstacle.pos) < radii * radii:
                found.append(obstacle)
        return found

    def obstacle_avoidance(self, screen, obsticles):
        lenght = 200
        bounding = 20
        side = self.velocity.rotate(90).normalize()
        p1 = (self.pos + lenght * self.velocity + bounding * side)
        p2 = (self.pos + lenght * self.velocity - bounding * side)
        p3 = (self.pos - bounding * side)
        p4 = (self.pos + bounding * side)
        pygame.draw.lines(screen, "grey", True, [p1, p2, p3, p4])
        pygame.draw.line(screen, "grey", self.pos, self.pos + self.velocity * lenght, 2)

        _obstacles = self.get_obstacles_within_view_range(obsticles, lenght)
        closest_intersecting_obstacle = None
        dist_to_closest_IP = 10000
        local_pos_of_closest_obstacle = pygame.Vector2(0.0, 0.0)
        bounding_radius = 20
        for o in _obstacles:
            circle_x, circle_y = self.point_to_local_2d(o.pos,self.pos, self.angle)
            # obstacles behind the vehicle are ignored
            if circle_x >= 0:
                
                expanded_radius = o.radius + bounding_radius
                pygame.draw.circle(screen, "grey", (o.pos.x, o.pos.y), expanded_radius, 1)
                # Checks to see if any obstacles overlap the detection box 
                # Compare local y value with the sum of half of the box’s width and the radius of obstacles
                if abs(circle_y) < expanded_radius:

                    # Finds the intersection point closest to the vehicle by a simple line/circle intersection test

                    sqrt_part = math.sqrt(expanded_radius * expanded_radius + circle_y * circle_y)

                    ip = circle_x - sqrt_part

                    if ip <= 0:
                        ip = circle_x + sqrt_part

                    # see if this is the closes so far
                    if ip < dist_to_closest_IP:
                        dist_to_closest_IP = ip
                        closest_intersecting_obstacle = o
                        local_pos_of_closest_obstacle = pygame.Vector2(circle_x, circle_y)
                        pygame.draw.line(screen, "red", self.pos, self.pos + self.velocity * lenght, 2)
            
            # calculte steering force away from obstacle
            steering_force = pygame.Vector2(0.0, 0.0)
            if closest_intersecting_obstacle:
                # the closer, the stronger the steering force should be
                multiplier = 1.0 + (lenght - local_pos_of_closest_obstacle.x) / lenght
                # lateral force
                steering_force.y = (bounding_radius - local_pos_of_closest_obstacle.y) * multiplier
                self.break_weight = 0.2
                # apply a breaking force proportional to the distance to obstacle
                steering_force.x = (bounding_radius - local_pos_of_closest_obstacle.x) * self.break_weight

                # convert the steering vector to global space
                s = self.vector_to_world_2d(steering_force, self.pos, self.angle)
                steering_force = s
                self.apply_steering(steering_force)

    def point_to_local_2d(self, global_point,object_position, object_rotation):
        point = global_point - object_position
        point = point.rotate(object_rotation)
        return point
    
    def vector_to_world_2d(self, local_point, object_position, object_rotation):
        point = local_point.rotate(object_rotation)
        point = point + object_position
        return point


    '''
    def update(self, player, enemies, obstacles, screen):
        # Decide whether to hide or wander
        if self.should_hide(player):
            self.velocity = hide(self, player, obstacles)
        else:
            self.velocity = wander(self, screen)

        # Update the angle based on the direction
        if self.velocity.length() > 0:  # If there's a valid direction
            self.angle = self.velocity.angle_to(pygame.Vector2(1, 0))  # Calculate the angle based on the direction

        # Calculate the potential new position
        potential_pos = self.pos + (self.velocity * self.speed)

        # Check if the potential position is within screen bounds
        if 0 <= potential_pos.x <= SCREEN_WIDTH and 0 <= potential_pos.y <= SCREEN_HEIGHT:
            # Create a temporary object to check collisions
            temp_enemy = MovingEntity(potential_pos, self.radius, self.speed)

            # Check collision with other enemies and obstacles
            if not self.check_enemy_collision(temp_enemy, enemies) and not check_collision(temp_enemy, obstacles):
                # Move the enemy based on the chosen velocity if no collision
                self.move(self.velocity)
            else:
                # Resolve collision with other enemies
                self.resolve_enemy_collisions(enemies)
    '''
    def check_enemy_collision(self, temp_enemy, enemies):
        for enemy in enemies:
            if enemy != self:  # Avoid checking collision with itself
                dist = distance_between_points(temp_enemy, enemy)
                # If the distance is less than the sum of radii, there's a collision
                if dist < temp_enemy.radius + enemy.radius:
                    return True
        return False
    
    def resolve_enemy_collisions(self, enemies):
        for enemy in enemies:
            if enemy != self:  # Avoid checking collision with itself
                dist = distance_between_points(self, enemy)
                if dist < self.radius + enemy.radius:  # Collision detected
                    # Calculate the overlap
                    overlap = self.radius + enemy.radius - dist

                    # Calculate the direction to move away from the other enemy
                    direction = self.evade(self, enemy) # Move away from the other enemy
                    self.pos += direction * overlap  # Push the enemy out of the collision
                    # todo: modify the direction here to change the movement angle
    
    def should_hide(self, player):
        return (self.pos - player.pos).length() < 300
    
    def evade(enemy, target):
        # Move in the opposite direction of the target
        return (enemy.pos - target.pos).normalize()

