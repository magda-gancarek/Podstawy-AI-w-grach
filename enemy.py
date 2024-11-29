import pygame
import random
from entity import MovingEntity
import math
from settings import *
import sys
from utils import check_collision, distance_between_points, check_collision_plus_bounding, check_collision_hiding_spots
import time

draw_debuge_walls = False
draw_debuge_obsticles = True
draw_debuge_arrive = True
draw_debuge_wander = False
draw_debuge_hide = False


SEEK = False
FLEE = False
ARRIVE = False
INTERPOSE = False
WANDER = True
PURSUIT = False
EVADE = False
OBSTACLEAVOIDANCE = True
WALLAVOIDANCE = True
HIDE = False
COHESION = False
SEPARATION = False
ALIGNMENT = False
ATTACK = False

# weightseek = 0.1
# weightflee  = 0.1
# weightinterpose = 0.1
# weightpursuit = 0.01
# weightevade = 0.01
weightobstacleavoidance = 1000
weightwallavoidance = 1000

weighthide = 0.1
weightarrive = 0.0001
weightwander = 0.0015
weighattack = 1.0

# weightalignment = 1.0
# weightseparation = 0.1
# weightcohesion = 0.1


# Function to blend colors from green to red based on a value (0 to 200)
def blend_color(value, max_value=200):
    # Clamp value between 0 and max_value
    value = max(0, min(value, max_value))
    # Calculate the ratio for blending (1 means green, 0 means red)
    ratio = value / max_value
    red = int(255 * (1 - ratio))
    green = int(255 * ratio)
    return (red, green, 0)  # Blue remains 0 to keep it in the green-red spectrum

def spawn_enemy(obstacles):
    enemies = []
    # Spawn an enemy at a random position, avoiding obstacles
    while len(enemies) < ENEMY_COUNT:
        x = random.randint(ENEMY_RADIUS, SCREEN_WIDTH - ENEMY_RADIUS)
        y = random.randint(ENEMY_RADIUS, SCREEN_HEIGHT - ENEMY_RADIUS)
        enemy_pos = pygame.Vector2(x, y)
        enemy = Enemy(enemy_pos)
        # Check if this position collides with any obstacle
        if not check_collision_plus_bounding(enemy, obstacles, BOUNDING):
            enemies.append(enemy)
    return enemies

class Enemy(MovingEntity):
    def __init__(self, pos):
        self.pos = pos
        self.angle = 0
        self.radius = ENEMY_RADIUS
        self.mass = 1.0
        self.max_speed = ENEMY_SPEED
        self.max_force = 0.3
        self.velocity = pygame.Vector2(1,0) # default direction
        self.direction = self.velocity.normalize()
        self.side = self.velocity.rotate(90).normalize() # Vector perpendicular to direction
        self.acceleration = pygame.Vector2(0, 0)

        self.wander_target = pygame.Vector2(0, 0)  # Initialize wander target

        self.color = (random.randint(1,255), random.randint(1,255), random.randint(1,255))
        self.tag = False
        self.feelers = []
        self._steering_force = pygame.Vector2(0, 0)
        self.target = None
        self.attacking = False

        self.hide_timer = random.uniform(0, 1)
        self.wander_timer = 0
        self.hiding = False

    def draw_enemy(self, screen):
        # triangle
        front_x = self.pos.x + self.radius * math.cos(math.radians(self.angle))
        front_y = self.pos.y - self.radius * math.sin(math.radians(self.angle))

        left_x = self.pos.x + self.radius * math.cos(math.radians(self.angle + 120))
        left_y = self.pos.y - self.radius * math.sin(math.radians(self.angle + 120))

        right_x = self.pos.x + self.radius * math.cos(math.radians(self.angle + 240))
        right_y = self.pos.y - self.radius * math.sin(math.radians(self.angle + 240))

        points = [(front_x, front_y), (left_x, left_y), (right_x, right_y)]
        pygame.draw.line(screen, "blue", self.pos, self.pos + self.direction * 100, 4) # line indicating movement direction
        pygame.draw.circle(screen, self.color, (self.pos.x, self.pos.y), self.radius)
        pygame.draw.polygon(screen, "coral3", points)


    def seek(self, screen, target):
        # Desired velocity is the vector pointing from the agent to the target
        desired_velocity = (target - self.pos).normalize() * self.max_speed

        # Steering force is the difference between the desired velocity and current velocity
        steering_force = desired_velocity - self.velocity

        return steering_force

    def flee(self, screen, target):
        # Desired velocity is the vector pointing from the target to the agent
        desired_velocity = (self.pos - target).normalize() * self.max_speed

        # Steering force is the difference between the desired velocity and current velocity
        steering_force = desired_velocity - self.velocity

        return steering_force

    def arrive(self, screen, target_pos):
        # Calculate the desired velocity
        to_target = target_pos - self.pos
        distance = to_target.length()

        if draw_debuge_arrive:
            pygame.draw.circle(screen, "red", target_pos, 2, 2)
            pygame.draw.circle(screen, "green", target_pos, ARRIVE_SLOWING_RADIUS, 1)

        # If we're close enough to the target, stop
        if distance < 1:
            return pygame.Vector2(0, 0)
        else:
            # Scale the speed according to distance within the slowing radius
            if distance < ARRIVE_SLOWING_RADIUS:
                desired_speed = self.max_speed * (distance / ARRIVE_SLOWING_RADIUS)
                if draw_debuge_arrive:
                    pygame.draw.circle(screen, blend_color(distance), target_pos, distance, 1)
            else:
                desired_speed = self.max_speed

            # Set the desired velocity towards the target with the calculated speed
            desired_velocity = to_target.normalize() * desired_speed

            # Calculate the steering force
            steering_force = desired_velocity - self.velocity
            return steering_force

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

        if draw_debuge_wander:
            pygame.draw.circle(screen, "grey", (int(wander_center.x), int(wander_center.y)), WANDER_RADIUS, 1)
            pygame.draw.circle(screen, "red", (int(wander_point.x), int(wander_point.y)), 5)

        steering_force = wander_point - self.pos

        return steering_force

    def wall_avoidance(self, screen, walls):
        # Draw feelers
        feeler_angles = [0, 30, -30]  # Feelers: straight, right, left
        self.feelers = []
        feeler_lenght = 50
        for angle in feeler_angles:
            direction = self.velocity.rotate(angle).normalize()
            feeler_end = self.pos + direction * feeler_lenght
            self.feelers.append((self.pos, feeler_end))
        if draw_debuge_walls:
            for start, end in self.feelers:
                pygame.draw.line(screen, "coral", start, end, 1)

        dist_to_closest_wall = sys.maxsize
        closest_wall = None
        closest_point = pygame.Vector2(0.0, 0.0)
        steering_force = pygame.Vector2(0.0, 0.0)

        for x,y in self.feelers:
            for wall in walls:
                intersection, distance_to_wall, point_of_intersection = self.are_lines_intersecting(x,y, wall.start, wall.end)
                if intersection:
                    if draw_debuge_walls:
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
                '''
                if steering_force.length() > self.max_force:
                    steering_force = steering_force.normalize() * self.
                '''
        return steering_force

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

    def get_obstacles_within_view_range(self, obstacles, view_range, screen):
        found = []
        for obstacle in obstacles:
            radii = view_range + obstacle.radius
            if (self.pos - obstacle.pos).length_squared() < radii * radii:
                found.append(obstacle)
                if draw_debuge_obsticles:
                    pygame.draw.circle(screen, (255, 0, 0), (obstacle.pos.x, obstacle.pos.y), obstacle.radius, 2)

        return found

    def obstacle_avoidance(self, screen, obstacles):
        length = (self.velocity.length() / self.max_speed) * MIN_COLISION_DETECTION_BOX_LEN + MIN_COLISION_DETECTION_BOX_LEN
        bounding = PLAYER_SIZE

        if draw_debuge_obsticles:
            p1 = (self.pos + length * self.direction + bounding * self.side)
            p2 = (self.pos + length * self.direction - bounding * self.side)
            p3 = (self.pos - bounding * self.side)
            p4 = (self.pos + bounding * self.side)
            pygame.draw.lines(screen, "grey", True, [p1, p2, p3, p4])
            pygame.draw.line(screen, "grey", self.pos, self.pos + self.direction * length, 2)

        # calculte steering force away from obstacle
        steering_force = pygame.Vector2(0.0, 0.0)
        _obstacles = self.get_obstacles_within_view_range(obstacles, length, screen)
        closest_intersecting_obstacle = None
        dist_to_closest_IP = sys.maxsize
        local_pos_of_closest_obstacle = pygame.Vector2(0.0, 0.0)
        bounding_radius = OBSTACLE_AVOIDANCE_BOUNDING_RADIUS
        for o in _obstacles:
            circle_x, circle_y = self.point_to_local_2d(o.pos,self.pos, self.angle)
            # obstacles behind the vehicle are ignored
            if circle_x >= 0:

                expanded_radius = o.radius + bounding_radius
                if draw_debuge_obsticles:
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
                        if draw_debuge_arrive:
                            pygame.draw.line(screen, "red", self.pos, self.pos + self.direction * length, 2)


        if closest_intersecting_obstacle:
            bounding_radius = closest_intersecting_obstacle.radius
            # the closer, the stronger the steering force should be
            multiplier = 10.0 + (length - local_pos_of_closest_obstacle.x) / length
            # lateral force
            steering_force.y = (bounding_radius - local_pos_of_closest_obstacle.y) * multiplier
            self.break_weight = 0.5
            # apply a breaking force proportional to the distance to obstacle
            steering_force.x = (bounding_radius - local_pos_of_closest_obstacle.x) * self.break_weight

            # convert the steering vector to global space
            steering_force = self.vector_to_world_2d(steering_force, self.pos, self.angle)
            # print("steering force: ", steering_force)

        return steering_force

    def point_to_local_2d(self, global_point,object_position, object_rotation):
        point = global_point - object_position
        point = point.rotate(object_rotation)
        return point

    def vector_to_world_2d(self, local_point, object_position, object_rotation):
        point = local_point.rotate(object_rotation)
        point = point + object_position
        return point
    
    def push_out_of_obstacles(self, obstacles):
        for obstacle in obstacles:
            diff = self.pos - obstacle.pos
            distance = diff.length()
            min_distance = self.radius + obstacle.radius
            
            if distance < min_distance:
                overlap = min_distance - distance
                diff = diff.normalize() if distance > 0 else pygame.Vector2(1, 0)  
                self.pos += diff * overlap


    def hide(self, screen, player, obstacles):
        best_hiding_spot = pygame.Vector2(0.0, 0.0)
        dist_to_closest_o = sys.maxsize

        for obstacle in obstacles:

            direction_to_obstacle = (obstacle.pos - player.pos).normalize()
            if draw_debuge_hide:
                pygame.draw.line(screen, "grey", player.pos, obstacle.pos, 1)
            # Place the hiding spot slightly behind the obstacle from the player's perspective
            hiding_spot = obstacle.pos + direction_to_obstacle * (obstacle.radius + BOUND_FOR_HIDING_SPOT)
            hiding_spot_radius = 5
            if check_collision_hiding_spots(hiding_spot, obstacles, hiding_spot_radius):
                size = 6
                if draw_debuge_hide:
                    pygame.draw.line(screen, "red", (hiding_spot.x - size // 2, hiding_spot.y - size // 2), (hiding_spot.x + size // 2, hiding_spot.y + size // 2), 2)
                    pygame.draw.line(screen, "red", (hiding_spot.x - size // 2, hiding_spot.y + size // 2), (hiding_spot.x + size // 2, hiding_spot.y - size // 2), 2)
                continue

            if draw_debuge_hide:
                pygame.draw.circle(screen, "grey", hiding_spot, hiding_spot_radius, 5)

            # Measure distance from the agent to this hiding spot
            distance_to_hiding_spot = (hiding_spot - self.pos).length()

            # Choose the closest hiding spot to the agent
            if distance_to_hiding_spot < dist_to_closest_o:
                dist_to_closest_o = distance_to_hiding_spot
                best_hiding_spot = hiding_spot

        if draw_debuge_hide:
            pygame.draw.circle(screen, "green", best_hiding_spot, 5, 5)
        if dist_to_closest_o == sys.maxsize:
            return self.evade(player)
        return self.arrive(screen, best_hiding_spot)

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
                    direction = self.evade(enemy) # Move away from the other enemy
                    self.pos += direction * overlap  # Push the enemy out of the collision
                    # todo: modify the direction here to change the movement angle


    def should_hide(self):
        current_time = time.time()

        # If hiding, check if hiding time has elapsed
        if self.hiding:
            if current_time >= self.hide_timer:
                self.hiding = False
                self.wander_timer = current_time + random.uniform(0, 3)  # Wander for 3-6 seconds
            return True

        # If wandering, check if wandering time has elapsed
        else:
            if current_time >= self.wander_timer:
                self.hiding = True
                self.hide_timer = current_time + random.uniform(0, 3)  # Hide for 2-5 seconds
            return False


    def evade(self, target):
        to_pursuer = target.pos - self.pos
        look_ahead_time = to_pursuer.length() / (self.max_speed + target.velocity.length())
        future_position = target.pos + target.velocity * look_ahead_time
        return (self.pos - future_position).normalize()

    def group_enemies(self, screen, enemies):
        MAX_GROUP_DISTANCE = 100
        GROUP_ATTACK_COUNT = 6
        count = 0

        # Assign nearby agents to the same group
        for e in enemies:
            # Reset all groups
            e.tag = False
            #e.color = "white"
            if e is not self and distance_between_points(e, self) < MAX_GROUP_DISTANCE:
                e.tag = True
                count += 1
 
        if count >= GROUP_ATTACK_COUNT:
            for e in enemies:
                if e.tag == True:
                    e.color = self.color
                    e.attacking = True
            

    def alignment(self, screen, enemies):
        # uses previously tagged vehicles
        average_heading = pygame.Vector2(0.0, 0.0)
        count = 0
        for e in enemies:
            # if vehicle is not self._vehicle and vehicle.tag is True:
            if e.tag is True and e is not self:
                average_heading += e.direction
                count += 1

        if count > 0:
            average_heading /= float(count)
            # substract vehicles heading to get steering force
            return average_heading - self.direction
        return pygame.Vector2(0.0, 0.0)

    def cohesion(self, screen, enemies):
        # uses previously tagged vehicles
        center_of_mass = pygame.Vector2(0.0, 0.0)
        count = 0
        for e in enemies:
            # if vehicle is not self._vehicle and vehicle.tag is True:
            if e.tag is True and e is not self:
                center_of_mass += e.pos
                count += 1
        # print(count)
        if count > 0:
            center_of_mass /= float(count)
            return self.seek(screen, center_of_mass)
        return center_of_mass


    def separation(self, screen, enemies):
        # uses previously tagged enemies
        steering_force = pygame.Vector2(0.0, 0.0)
        for e in enemies:
            # if vehicle is not self._vehicle and vehicle.tag is True:
            if e.tag is True and e is not self:
                to_agent = self.pos - e.pos
                # scale force inversily proportional to the agents distance
                # steering_force += to_agent.normalized / to_agent.length
                length = float(to_agent.length())
                if length > 0:
                    force = (to_agent / length) / length
                    # print length, force.length
                    steering_force += force
        return steering_force
    
    def attack(self, screen, enemies, player):
        if self.attacking == True:
            return self.arrive(screen, player.pos)
        else:
            return pygame.Vector2(0.0, 0.0)



    # ========================================================================================

    def calculate(self, player, enemies, obstacles, walls, screen):
        # the order of the if statements is the prioritation
        self._steering_force = pygame.Vector2(0,0) # reset
        _steering_force = pygame.Vector2(0,0)

        if WALLAVOIDANCE:
            _steering_force += self.wall_avoidance(screen, walls) * weightwallavoidance
            if self.exceed_accumulate_force(_steering_force):
                return self._steering_force
        if OBSTACLEAVOIDANCE:
            _steering_force += self.obstacle_avoidance(screen, obstacles) * weightobstacleavoidance
            if self.exceed_accumulate_force(_steering_force):
                return self._steering_force
        if ATTACK:
            _steering_force += self.attack(screen, enemies, player) * weighattack
            if self.exceed_accumulate_force(_steering_force):
                return self._steering_force
        if HIDE:
            _steering_force += self.hide(screen, player, obstacles) * weighthide
            if self.exceed_accumulate_force(_steering_force):
                return self._steering_force
        if WANDER:
            _steering_force += self.wander(screen) * weightwander
            if self.exceed_accumulate_force(_steering_force):
                return self._steering_force

        # if EVADE:
        #     _steering_force += self.evade(screen, player) * weightevade
        #     if self.exceed_accumulate_force(_steering_force):
        #         return self._steering_force
        # if FLEE:
        #     _steering_force += self.flee(screen, self.target) * weightflee
        #     if self.exceed_accumulate_force(_steering_force):
        # #         return self._steering_force
        # if SEPARATION:
        #     # uses previously tagged vehicles
        #     _steering_force += self.separation(screen, enemies) * weightseparation
        #     if self.exceed_accumulate_force(_steering_force):
        #         return self._steering_force
        # if ALIGNMENT:
        #     # uses previously tagged vehicles
        #     _steering_force += self.alignment(screen, enemies) * weightalignment
        #     if self.exceed_accumulate_force(_steering_force):
        #         return self._steering_force
        # if COHESION:
        #     # print("COHES")
        #     # uses previously tagged vehicles
        #     _steering_force += self.cohesion(screen, enemies) * weightcohesion
        #     if self.exceed_accumulate_force(_steering_force):
        #         return self._steering_force
        # # if SEEK:
        #     _steering_force += self.seek(screen, self.target) * weightseek
        #     if self.exceed_accumulate_force(_steering_force):
        #         return self._steering_force
        # if ARRIVE:
        #     _steering_force += self.arrive(screen, self.target) * weightarrive
        #     if self.exceed_accumulate_force(_steering_force):
        #         return self._steering_force
        # if INTERPOSE:
        #     _steering_force += self.interpose(self.target_agent1, self.target_agent2) * weightinterpose
        #     if self.exceed_accumulate_force(_steering_force):
        #         return self._steering_force
        # if PURSUIT:
        #     _steering_force += self.pursuit(self.target_agent1) * weightpursuit
        #     if self.exceed_accumulate_force(_steering_force):
        #         return self._steering_force
        
        return _steering_force

    def exceed_accumulate_force(self, force: pygame.Vector2):
        # //calculate how much steering force the vehicle has used so far
        magnitude_so_far = self._steering_force.length()
        #print(magnitude_so_far, "vs max", self.max_force)
        # //calculate how much steering force remains to be used by this vehicle
        magnitude_remaining = self.max_force - magnitude_so_far
        # //return true if there is no more force left to use
        if magnitude_remaining <= 0.0:
            return True
        # //calculate the magnitude of the force we want to add
        magnitude_to_add = force.length()
        # //if the magnitude of the sum of ForceToAdd and the running total
        # //does not exceed the maximum force available to this vehicle, just
        # //add together. Otherwise add as much of the ForceToAdd vector is
        # //possible without going over the max.
        if magnitude_to_add < magnitude_remaining:
            self._steering_force += force
        else:
            # //add it to the steering force
            self._steering_force += force.normalize() * magnitude_remaining
        # return false;
        return False

    '''
    def enforce_non_penetration(self, entities):
        for entity in entities:
            if entity is not self:
                to_entity = self.position - entity.position
                dist_from_each_other = to_entity.length
                amount_of_overlap = entity.bounding_radius + self.bounding_radius - dist_from_each_other
                if amount_of_overlap > 0:
                    entity.position -= (to_entity / dist_from_each_other) * amount_of_overlap
    '''

    def update_sum_force(self, player, enemies, obstacles, walls, screen):
        global HIDE, WANDER, COHESION, SEPARATION, ALIGNMENT, ARRIVE, ATTACK

        self.group_enemies(screen, enemies)
        #for e in enemies:
        if self.attacking is True:
            print("ATTACK")
            self.radius = ENEMY_RADIUS + 3
            WANDER = False
            HIDE = False
            ATTACK = True

        if self.should_hide():
            print("HIDE!")
            WANDER = False
            HIDE = True
        else:
            print("Not hide!")
            WANDER = True
            HIDE = False

        # COHESION = True
        # SEPARATION = False
        # ALIGNMENT = True

        steering_force = self.calculate(player, enemies, obstacles, walls, screen)
        acceleration = steering_force / self.mass
        self.velocity += acceleration
        # make sure it does not exeed max speed
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed

        if self.velocity.length() > 0:  # If there's a valid direction
            self.angle = self.velocity.angle_to(pygame.Vector2(1, 0))

        self.pos += self.velocity
        # update direction if it has a velocity
        EPSILON = 1e-9
        if pygame.Vector2.length_squared(self.velocity) > EPSILON:
            self.direction = pygame.Vector2.normalize(self.velocity)
            self.side = self.direction.rotate(90)

        self.resolve_enemy_collisions(enemies)
