import pygame
import random
import numpy as np
from files.pygame_background import *
from files.Nest import *
from files.map_gen import *
from files.quadtree import *
from files.pheremones import *
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

pygame.init()


class Ant(pygame.sprite.Sprite):
    def __init__(self, nest_position, mobs_quadtree, pheremone_quadtree, food_group):
        super().__init__()
        self.original_image = pygame.image.load('graphics/ant/ant_2.png').convert_alpha()

        if octaves == 3:
            self.original_image = pygame.transform.rotozoom(self.original_image, 0, 0.01)
        elif octaves == 4:
            self.original_image = pygame.transform.rotozoom(self.original_image, 0, 0.013)
        else:
            self.original_image = pygame.transform.rotozoom(self.original_image, 0, 0.01)
        
        image = pygame.image.load('graphics/ant/ant_2.png').convert_alpha()
        self.image = pygame.transform.rotozoom(image, 0, 0.009)
        self.rect = self.image.get_rect(midbottom=(nest_position))
        self.speed = 4  # Base speed
        self.original_speed = [self.speed]
        self.collisiond = self.speed * 2
        self.angle = random.uniform(0, 2 * np.pi)
        self.speedx_time = 0
        self.speedy_time = 0
        self.is_alive = True
        self.collided = False
        self.holding_food = None
        self.food_group = food_group
        self.nest_position = nest_position
        self.time_tick = 0
        self.time_tick_nest = 0
        self.mobs_quadtree = mobs_quadtree
        self.pheremone_quadtree = pheremone_quadtree
        self.pheremone_list = []

    def rotate_image(self, ant_direction):
        rotated_image = pygame.transform.rotate(self.original_image, ant_direction - 90)
        self.image = rotated_image
        self.rect = self.image.get_rect(center=self.rect.center)

    def check_pheremones(self):
        vision_pheremone = 35
        vision_rect_pheremone = pygame.Rect(
            self.rect.centerx - vision_pheremone,
            self.rect.centery - vision_pheremone,
            vision_pheremone * 2,
            vision_pheremone * 2,
        )
        nearby_pheromones = self.pheremone_quadtree.query(vision_rect_pheremone)
        
        if self.holding_food is not None:
            target_pheromones = [pher for pher in nearby_pheromones if pher.color[:3] == (240, 87, 77)]
        else:
            target_pheromones = [pher for pher in nearby_pheromones if pher.color[:3] == (84, 149, 232)]
        return target_pheromones

    def follow_pheromones(self):
        fractions = [0.001,0.01,0.015,0.03, 0.10, 0.33, 0.5, 0.66, 0.9, 0.96]
        if len(self.food_group) == 0 or not any(food.carried_by is None for food in self.food_group):
            if self.holding_food is not None:
                pass
            else:
                return

        vision_pheremone = 80  # Original value that worked
        vision_rect_pheremone = pygame.Rect(
            self.rect.centerx - vision_pheremone,
            self.rect.centery - vision_pheremone,
            vision_pheremone * 2,
            vision_pheremone * 2,
        )
        vision_radius = 70 # Original value that worked
        vision_rect = pygame.Rect(
            self.rect.centerx - vision_radius,
            self.rect.centery - vision_radius,
            vision_radius * 2,
            vision_radius * 2,
        )
        
        visible_food = [food for food in self.food_group if vision_rect.colliderect(food.rect) and food.carried_by is None]
        if visible_food and self.holding_food is None:
            closest_food = min(
                visible_food,
                key=lambda food: np.sqrt(
                    (food.rect.centerx - self.rect.centerx) ** 2 +
                    (food.rect.centery - self.rect.centery) ** 2
                )
            )
            for fraction in fractions:
                color = self.get_color_along_line(self.rect.center, (closest_food.rect.centerx, closest_food.rect.centery), fraction)
                if color is None or color != brown:
                    return
            dx = closest_food.rect.centerx - self.rect.centerx
            dy = closest_food.rect.centery - self.rect.centery
            self.angle = np.arctan2(-dy, dx)
            return
        
        if self.holding_food is not None:
            dx = self.nest_position[0] - self.rect.centerx
            dy = self.nest_position[1] - self.rect.centery
            distance_to_nest = np.sqrt(dx ** 2 + dy ** 2)
            if distance_to_nest <= vision_radius:
                self.angle = np.arctan2(-dy, dx)
                return

        nearby_pheromones = self.pheremone_quadtree.query(vision_rect_pheremone)
        if not nearby_pheromones:
            return

        if self.holding_food is not None:
            target_pheromones = [pher for pher in nearby_pheromones if pher.color[:3] == (84, 149, 232)]
        else:
            target_pheromones = [pher for pher in nearby_pheromones if pher.color[:3] == (240, 87, 77)]

        if not target_pheromones:
            return
        
        if self.holding_food is None:
            target_pheromones.sort(
                key=lambda p: (-p.intensity, 
                            np.sqrt((p.x - self.rect.centerx) ** 2 + (p.y - self.rect.centery) ** 2))
            )
        else:
            target_pheromones.sort(
                key=lambda p: (-p.intensity, 
                            np.sqrt((p.x - self.rect.centerx) ** 2 + (p.y - self.rect.centery) ** 2))
            )

        if target_pheromones[0].id in self.pheremone_list:
            if self.holding_food is not None and self.time_tick_nest == 2:
                dx = self.nest_position[0] - self.rect.centerx
                dy = self.nest_position[1] - self.rect.centery
                target_angle = np.arctan2(-dy, dx)
                self.angle += self.angle_direction_pheremone(target_angle) * 0.1
                self.time_tick_nest = 0
            elif self.time_tick_nest != 2:
                self.time_tick_nest += 1
            return
        else:
            target_pheromone = target_pheromones[0]

        for fraction in fractions:
            color = self.get_color_along_line(self.rect.center, (target_pheromone.x, target_pheromone.y), fraction)
            if color is None or color != brown:
                return

        self.pheremone_list.append(target_pheromone.id)
        dx = target_pheromone.x - self.rect.centerx
        dy = target_pheromone.y - self.rect.centery
        proposed_angle = np.arctan2(-dy, dx)
        self.angle = proposed_angle

    def angle_direction_pheremone(self, target_angle):
        angle_diff = (target_angle - self.angle + np.pi) % (2 * np.pi) - np.pi
        return angle_diff

    def get_color_along_line(self, start, end, fraction):
        x = int(start[0] + fraction * (end[0] - start[0]))
        y = int(start[1] + fraction * (end[1] - start[1]))
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            return screen.get_at((x, y))[:3]
        return None

    def flee_from_spider(self, nearby_objects):
        vision_radius = 50
        vision_rect = pygame.Rect(
            self.rect.centerx - vision_radius,
            self.rect.centery - vision_radius,
            vision_radius * 2,
            vision_radius * 2,
        )
        nearby_spiders = [obj for obj in nearby_objects if isinstance(obj, Spider) and not obj.eating]
        if nearby_spiders:
            closest_spider = min(
                nearby_spiders,
                key=lambda s: np.sqrt(
                    (s.rect.centerx - self.rect.centerx) ** 2 +
                    (s.rect.centery - self.rect.centery) ** 2
                )
            )
            dx = self.rect.centerx - closest_spider.rect.centerx
            dy = self.rect.centery - closest_spider.rect.centery
            return np.arctan2(-dy, dx)  # Return angle instead of setting it
        return None

    def move_towards_spider(self, spider_pos):
        dx = spider_pos[0] - self.rect.centerx
        dy = spider_pos[1] - self.rect.centery
        return np.arctan2(-dy, dx)  # Return angle instead of setting it

    def movement(self):
        self.terrain_collision()

        range_rect = pygame.Rect(self.rect.centerx - 50, self.rect.centery - 50, 100, 100)
        nearby_objects = self.mobs_quadtree.query(range_rect)
        nearby_spiders = [obj for obj in nearby_objects if isinstance(obj, Spider)]

        # Random angle adjustment
        if random.randint(1, 20) == 1:
            if random.randint(1, 2) == 1:
                self.angle += random.uniform(0.03, 0.1)
            else:
                self.angle -= random.uniform(0.03, 0.1)

        # Apply movement based on current angle
        self.angle += 0.005 * np.sin(pygame.time.get_ticks() * 0.001)
        self.speedx = self.speed * np.cos(self.angle)
        self.speedy = -self.speed * np.sin(self.angle)
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        self.terrain_collision()
        self.collision()
        self.time_tick += 1


        # Default behavior: follow pheromones

        # Spider overrides: apply only if conditions met
        if nearby_spiders:
            closest_spider = min(
                nearby_spiders,
                key=lambda s: np.sqrt(
                    (s.rect.centerx - self.rect.centerx) ** 2 +
                    (s.rect.centery - self.rect.centery) ** 2
                )
            )
            if closest_spider.eating:
                swarm_radius = 120
                swarm_rect = pygame.Rect(
                    closest_spider.rect.centerx - swarm_radius,
                    closest_spider.rect.centery - swarm_radius,
                    swarm_radius * 2,
                    swarm_radius * 2,
                )
                if swarm_rect.colliderect(self.rect):
                    swarm_angle = self.move_towards_spider(closest_spider.rect.center)
                    self.angle = swarm_angle
                    self.speed = self.original_speed[0]
            else:
                flee_angle = self.flee_from_spider(nearby_objects)
                if flee_angle is not None:
                    self.angle = flee_angle
                    self.speed = self.original_speed[0] * 1.04

        if not nearby_spiders:
            self.follow_pheromones()




    def collision(self):
        if self.rect.x < 5:
            Target_direction = self.angle_direction(-0.25, 0.25)
            self.angle += Target_direction * 0.1
        elif self.rect.x >= WIDTH - 30:
            Target_direction = self.angle_direction(0.75, 1.25)
            self.angle += Target_direction * 0.1
        elif self.rect.y < 40:
            Target_direction = self.angle_direction(1.25, 1.75)
            self.angle += Target_direction * 0.1
        elif self.rect.y >= HEIGHT - 30:
            Target_direction = self.angle_direction(0.25, 0.75)
            self.angle += Target_direction * 0.1
        rotation_angle = np.degrees(self.angle)
        self.rotate_image(rotation_angle)

    def angle_direction(self, start, end):
        angle_dir = random.uniform(start * np.pi, end * np.pi)
        angle_direct = self.angle_different(angle_dir)
        self.rotate_image(angle_direct)
        return angle_direct

    def angle_different(self, direction):
        angle_diff = (direction - self.angle + np.pi) % (2 * np.pi) - np.pi
        return angle_diff

    def detect_collision(self, ant2):
        if self.rect.colliderect(ant2.rect):
            top_overlap = ant2.rect.bottom - self.rect.top
            bottom_overlap = self.rect.bottom - ant2.rect.top
            left_overlap = ant2.rect.right - self.rect.left
            right_overlap = self.rect.right - ant2.rect.left
            min_overlap = min(top_overlap, bottom_overlap, left_overlap, right_overlap)
            if min_overlap == top_overlap:
                return "top"
            elif min_overlap == bottom_overlap:
                return "bottom"
            elif min_overlap == left_overlap:
                return "left"
            elif min_overlap == right_overlap:
                return "right"
        return None

    def ant_collision(self, ant2):
        self.pseudo_rect = self.rect.inflate(5, 5)
        if self.detect_collision(ant2) == "top":
            self.angle += self.angle_direction(1.25, 1.75) * 0.1
            self.rotate_image(np.degrees(self.angle))
            self.collided = True
        elif self.detect_collision(ant2) == "bottom":
            self.angle += self.angle_direction(-1.25, -1.75) * 0.1
            self.rotate_image(np.degrees(self.angle))
            self.collided = True
        elif self.detect_collision(ant2) == "left":
            self.angle += self.angle_direction(-0.25, 0.25) * 0.1
            self.rotate_image(np.degrees(self.angle))
            self.collided = True
        elif self.detect_collision(ant2) == "right":
            self.angle += self.angle_direction(1.2, 0.8) * 0.1
            self.rotate_image(np.degrees(self.angle))
            self.collided = True

    def terrain_collision(self):
        if not self.is_alive:
            return
        self.pseudo_rect = self.rect.inflate(8, 8)

        def is_within_bounds(x, y):
            return 0 <= x < WIDTH and 0 <= y < HEIGHT

        if is_within_bounds(*self.rect.center):
            center_color = screen.get_at(self.rect.center)[:3]
            if center_color == (116, 204, 244):
                self.speed = 0.95
            else:
                self.speed = self.original_speed[0] if self.speed <= self.original_speed[0] else self.original_speed[0] * 1.04

        collision_detected = False
        pushback_factor = self.collisiond * 0.75
        angle_adjustment = 0.6
        terrain_colors = [(28, 163, 236), (63, 63, 63)]

        if (is_within_bounds(*self.pseudo_rect.midtop) and 
            screen.get_at(self.pseudo_rect.midtop)[:3] in terrain_colors):
            self.angle += self.angle_different(random.uniform(1.25, 1.75) * np.pi) * angle_adjustment
            collision_detected = True
        elif (is_within_bounds(*self.pseudo_rect.midbottom) and 
              screen.get_at(self.pseudo_rect.midbottom)[:3] in terrain_colors):
            self.angle += self.angle_different(random.uniform(-1.25, -1.75) * np.pi) * angle_adjustment
            self.rect.centery -= pushback_factor
            collision_detected = True
        elif (is_within_bounds(*self.pseudo_rect.midright) and 
              screen.get_at(self.pseudo_rect.midright)[:3] in terrain_colors):
            self.angle += self.angle_different(random.uniform(1.2, 0.8) * np.pi) * angle_adjustment
            self.rect.centerx -= pushback_factor
            collision_detected = True
        elif (is_within_bounds(*self.pseudo_rect.midleft) and 
              screen.get_at(self.pseudo_rect.midleft)[:3] in terrain_colors):
            self.angle += self.angle_different(random.uniform(-0.25, 0.25) * np.pi) * angle_adjustment
            self.rect.centerx += pushback_factor
            collision_detected = True

        if (is_within_bounds(*self.rect.midbottom) and 
            is_within_bounds(*self.pseudo_rect.midtop) and 
            screen.get_at(self.rect.midbottom)[:3] in terrain_colors and 
            screen.get_at(self.pseudo_rect.midtop)[:3] in terrain_colors):
            self.angle += self.angle_different(random.uniform(1.2, 0.8) * np.pi) * angle_adjustment
            self.rect.centerx -= pushback_factor
            collision_detected = True

        if collision_detected:
            self.rotate_image(np.degrees(self.angle))
            self.collided = True
            self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def update_food_position(self):
        if self.holding_food is not None:
            self.holding_food["rect"].center = self.rect.center

    def position(self):
        return self.rect.center

    def update(self):
        self.movement()

class Spider(pygame.sprite.Sprite):
    def __init__(self, spider_nest_position, mobs_quadtree, pheremone_quadtree, ant_group):
        super().__init__()
        self.original_image = pygame.image.load('graphics/Spider/Spider.png').convert_alpha()
        self.original_image = pygame.transform.rotozoom(self.original_image, 0, 0.15)
        self.image = self.original_image
        self.rect = self.image.get_rect(midbottom=spider_nest_position)
        self.base_speed = 1.5  # Reduced base speed
        self.chase_speed = 5 # Reduced chase speed
        self.speed = self.base_speed
        self.original_speed = [self.base_speed]
        self.collisiond = self.speed * 2
        self.angle = random.uniform(0, 2 * np.pi)
        self.speedx_time = 0
        self.is_alive = True
        self.collided = False
        self.spider_nest_position = spider_nest_position
        self.mobs_quadtree = mobs_quadtree
        self.pheremone_quadtree = pheremone_quadtree
        self.ant_group = ant_group
        self.eating = False
        self.eating_timer = 0
        self.target_ant = None

    def rotate_image(self, ant_direction):
        rotated_image = pygame.transform.rotate(self.original_image, ant_direction - 90)
        self.image = rotated_image
        self.rect = self.image.get_rect(center=self.rect.center)

    def chase_ants(self):
        vision_radius = 60
        vision_rect = pygame.Rect(
            self.rect.centerx - vision_radius,
            self.rect.centery - vision_radius,
            vision_radius * 2,
            vision_radius * 2,
        )
        nearby_ants = [ant for ant in self.ant_group if vision_rect.colliderect(ant.rect) and ant.is_alive]
        if nearby_ants:
            closest_ant = min(
                nearby_ants,
                key=lambda ant: np.sqrt(
                    (ant.rect.centerx - self.rect.centerx) ** 2 +
                    (ant.rect.centery - self.rect.centery) ** 2
                )
            )
            dx = closest_ant.rect.centerx - self.rect.centerx
            dy = closest_ant.rect.centery - self.rect.centery
            target_angle = np.arctan2(-dy, dx)
            angle_diff = (target_angle - self.angle + np.pi) % (2 * np.pi) - np.pi
            self.angle += min(max(angle_diff, -0.2), 0.2)
            self.speed = self.chase_speed  # Speed up when chasing
            return True
        self.speed = self.base_speed  # Reset to base speed when no ants nearby
        return False

    def movement(self):
        if self.eating:
            self.eating_timer -= 1
            if self.eating_timer <= 0:
                self.eating = False
                self.target_ant = None
            return

        self.terrain_collision()
        self.speedx_time += 1
        if self.speedx_time >= 5:
            self.speedx_time = 0

        if not self.chase_ants():
            if random.randint(1, 10) == 1:
                if random.randint(1, 2) == 1:
                    self.angle += random.uniform(0.03, 0.1)
                else:
                    self.angle -= random.uniform(0.03, 0.1)

        self.angle += 0.005 * np.sin(pygame.time.get_ticks() * 0.001)
        self.speedx = self.speed * np.cos(self.angle)
        self.speedy = -self.speed * np.sin(self.angle)
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        self.terrain_collision()
        self.collision()

    def collision(self):
        if self.rect.x < 5:
            self.angle += self.angle_direction(-0.25, 0.25) * 0.1
        elif self.rect.x >= WIDTH - 30:
            self.angle += self.angle_direction(0.75, 1.25) * 0.1
        elif self.rect.y < 40:
            self.angle += self.angle_direction(1.25, 1.75) * 0.1
        elif self.rect.y >= HEIGHT - 30:
            self.angle += self.angle_direction(0.25, 0.75) * 0.1
        rotation_angle = np.degrees(self.angle)
        self.rotate_image(rotation_angle)

    def angle_direction(self, start, end):
        angle_dir = random.uniform(start * np.pi, end * np.pi)
        angle_direct = self.angle_different(angle_dir)
        self.rotate_image(angle_direct)
        return angle_direct

    def angle_different(self, direction):
        angle_diff = (direction - self.angle + np.pi) % (2 * np.pi) - np.pi
        return angle_diff

    def terrain_collision(self):
        if not self.is_alive:
            return
        self.pseudo_rect = self.rect.inflate(8, 8)

        def is_within_bounds(x, y):
            return 0 <= x < WIDTH and 0 <= y < HEIGHT

        if is_within_bounds(*self.rect.center):
            center_color = screen.get_at(self.rect.center)[:3]
            if center_color == (116, 204, 244):
                self.speed = 0.95
            else:
                self.speed = self.original_speed[0] if self.speed <= self.original_speed[0] else self.chase_speed

        collision_detected = False
        pushback_factor = self.collisiond * 0.75
        angle_adjustment = 0.6
        terrain_colors = [(28, 163, 236), (63, 63, 63)]

        if (is_within_bounds(*self.pseudo_rect.midtop) and
            screen.get_at(self.pseudo_rect.midtop)[:3] in terrain_colors):
            self.angle += self.angle_different(random.uniform(1.25, 1.75) * np.pi) * angle_adjustment
            collision_detected = True
        elif (is_within_bounds(*self.pseudo_rect.midbottom) and
              screen.get_at(self.pseudo_rect.midbottom)[:3] in terrain_colors):
            self.angle += self.angle_different(random.uniform(-1.25, -1.75) * np.pi) * angle_adjustment
            self.rect.centery -= pushback_factor
            collision_detected = True
        elif (is_within_bounds(*self.pseudo_rect.midright) and
              screen.get_at(self.pseudo_rect.midright)[:3] in terrain_colors):
            self.angle += self.angle_different(random.uniform(1.2, 0.8) * np.pi) * angle_adjustment
            self.rect.centerx -= pushback_factor
            collision_detected = True
        elif (is_within_bounds(*self.pseudo_rect.midleft) and
              screen.get_at(self.pseudo_rect.midleft)[:3] in terrain_colors):
            self.angle += self.angle_different(random.uniform(-0.25, 0.25) * np.pi) * angle_adjustment
            self.rect.centerx += pushback_factor
            collision_detected = True

        if collision_detected:
            self.rotate_image(np.degrees(self.angle))
            self.collided = True
            self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def update_nearby_ants(self, nearby_ants):
        if self.eating:
            # Check ants within a 10-pixel radius for death condition
            death_radius = 5
            death_rect = pygame.Rect(
                self.rect.centerx - death_radius,
                self.rect.centery - death_radius,
                death_radius * 2,
                death_radius * 2,
            )
            ants_on_spider = sum(1 for ant in self.ant_group if death_rect.colliderect(ant.rect) and ant.is_alive)
            if ants_on_spider >= 3:
                self.is_alive = False
                self.kill()
            return

        for ant in nearby_ants:
            if isinstance(ant, Ant) and ant.is_alive and self.rect.colliderect(ant.rect):
                if ant.holding_food is not None:
                    ant.holding_food.carried_by = None  # Reset carried_by when ant dies
                ant.kill()
                self.eating = True
                self.eating_timer = 90  # 3 seconds at 30 FPS
                self.target_ant = ant
                break

    def update(self):
        self.movement()

class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('graphics/food/food.png').convert_alpha()
        if octaves == 3:
            self.image = pygame.transform.scale(self.image, (6, 6))
        elif octaves == 4:
            self.image = pygame.transform.scale(self.image, (5, 5))
        else:
            self.image = pygame.transform.scale(self.image, (4, 4))
        self.rect = self.image.get_rect(center=(x, y))
        self.carried_by = None

    def update(self):
        if self.carried_by is not None and self.carried_by.is_alive:
            self.rect.center = self.carried_by.rect.center

    def draw(self, screen):
        screen.blit(self.image, self.rect)

def spawn_food_cluster(surface, cluster_radius, food_group, amount=20):
    def is_safe_spawn(x, y):
        buffer = 20  # Full pseudo rect inflation (8 pixels each side)
        offsets = [(-15, 0), (15, 0), (0, -15), (0, 15), (-15, -15), (-15, 15), (15, -15), (15, 15)]
        # Check if position is too close to borders
        if (x < buffer or x >= surface.get_width() - buffer or
            y < buffer or y >= surface.get_height() - buffer):
            return False
        for dx, dy in offsets:
            nx, ny = x + dx, y + dy
            if 0 <= nx < surface.get_width() and 0 <= ny < surface.get_height():
                if surface.get_at((nx, ny))[:3] != brown:
                    return False
        return True

    buffer = 20  # Match pseudo rect inflation
    while True:
        x = random.randint(buffer, surface.get_width() - buffer)
        y = random.randint(buffer, surface.get_height() - buffer)
        color = surface.get_at((x, y))[:3]
        if color == brown and is_safe_spawn(x, y):
            break

    for _ in range(amount):
        while True:
            angle = random.uniform(0, 2 * np.pi)
            distance = random.uniform(0, cluster_radius)
            food_x = int(x + distance * np.cos(angle))
            food_y = int(y + distance * np.sin(angle))
            if (buffer <= food_x < surface.get_width() - buffer and
                buffer <= food_y < surface.get_height() - buffer):
                food_color = surface.get_at((food_x, food_y))[:3]
                if food_color == brown and is_safe_spawn(food_x, food_y):
                    food = Food(food_x, food_y)
                    food_group.add(food)
                    break