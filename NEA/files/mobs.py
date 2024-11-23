import pygame
import random
import numpy as np
from files.pygame_background import *
from files.Nest import *
from files.map_gen import *
from files.quadtree import *
from files.pheremones import *

pygame.init()


class Ant(pygame.sprite.Sprite):
    def __init__(self,nest_position,quadtree,food_group):
        super().__init__()
        self.original_image = pygame.image.load('graphics/ant/ant_2.png').convert_alpha()

        if octaves == 3:
            self.original_image = pygame.transform.rotozoom(self.original_image, 0, 0.01)

        elif octaves == 4 :
            self.original_image = pygame.transform.rotozoom(self.original_image, 0, 0.020)

        elif octaves == 5 :
            self.original_image = pygame.transform.rotozoom(self.original_image, 0, 0.01)
        
        image = pygame.image.load('graphics/ant/ant_2.png').convert_alpha()
        self.image = pygame.transform.rotozoom(image, 0, 0.009)
        self.rect = self.image.get_rect(midbottom=(nest_position))
        self.speed = 3
        self.angle = random.uniform(0, 2 * np.pi) 
        self.speedx_time = 0
        self.speedy_time = 0
        self.is_alive = True
        self.collided = False
        self.holding_food = None
        self.food_group = food_group
        self.nest_position = nest_position
        self.time_tick =0

        self.quadtree = quadtree

    def rotate_image(self,ant_direction):
        rotated_image = pygame.transform.rotate(self.original_image, ant_direction-90)
        self.image = rotated_image
        self.rect = self.image.get_rect(center=self.rect.center)



    def follow_pheromones(self):

        if len(self.food_group) == 0 or not any(food.carried_by is None for food in self.food_group):
            if self.holding_food is not None:
                pass
            else:
                return 
            

        vision_pheremone = 160
        vision_rect_pheremone = pygame.Rect(
            self.rect.centerx - vision_pheremone,
            self.rect.centery - vision_pheremone,
            vision_pheremone * 2,
            vision_pheremone * 2,
        )


        vision_radius = 80
        vision_rect = pygame.Rect(
            self.rect.centerx - vision_radius,
            self.rect.centery - vision_radius,
            vision_radius * 2,
            vision_radius * 2,
        )

        
        
        visible_food = [
        food for food in self.food_group
        if vision_rect.colliderect(food.rect) and food.carried_by is None
    ]

        if visible_food and self.holding_food== None :
            # Move directly toward the closest visible food
            closest_food = min(
                visible_food,
                key=lambda food: np.sqrt(
                    (food.rect.centerx - self.rect.centerx) ** 2 +
                    (food.rect.centery - self.rect.centery) ** 2
                )
            )
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

        nearby_objects = self.quadtree.query(vision_rect_pheremone)

        nearby_pheromones = [obj for obj in nearby_objects if isinstance(obj, Pheromones)]

        if not nearby_pheromones:
            return

        if self.holding_food is not None:
            target_pheromones = [
                pher for pher in nearby_pheromones if pher.color[:3] == (84, 149, 232)
            ]
        else:
            target_pheromones = [
                pher for pher in nearby_pheromones if pher.color[:3] == (240, 87, 77)
            ]

        if not target_pheromones:
            return

        target_pheromones.sort(key=lambda p: p.intensity)

        target_pheromone = target_pheromones[0]


        dx = target_pheromone.x - self.rect.centerx
        dy = target_pheromone.y - self.rect.centery
        proposed_angle = np.arctan2(-dy, dx)
        
        # Simulate a small step to check terrain
        step_x = self.rect.centerx + self.speed * np.cos(proposed_angle)
        step_y = self.rect.centery - self.speed * np.sin(proposed_angle)
        pseudo_rect = pygame.Rect(step_x - 15, step_y - 15, 30, 30)  # Inflate for checking
        self.angle = proposed_angle





    def movement(self):

       
        self.speedx_time += 1

        if self.speedx_time >= 5: 
            self.speedx_time = 0

        if random.randint(1, 2) == 1:
                self.angle += random.uniform(0.03, 0.1) 
        else:
                self.angle -= random.uniform(0.03, 0.1)  

        self.angle += 0.005 * np.sin(pygame.time.get_ticks() * 0.001)
        
        self.speedx = self.speed * np.cos(self.angle)
        self.speedy = -self.speed * np.sin(self.angle)
        self.speed_change = random.uniform(0.1,1)
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        self.collision()
        self.terrain_collision()
        self.time_tick += 1
        if self.time_tick == 5:
            self.follow_pheromones()
            self.time_tick=0


    def collision(self):
        if self.rect.x < 5:
            Target_direction = self.angle_direction(-0.25, 0.25)
            self.angle += Target_direction * 0.1
        elif self.rect.x >= WIDTH-30:
            Target_direction = self.angle_direction(0.75, 1.25)
            self.angle += Target_direction * 0.1
        elif self.rect.y < 40:
            Target_direction = self.angle_direction(1.25, 1.75)
            self.angle += Target_direction * 0.1
        elif self.rect.y >= HEIGHT-30:
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
        angle_diff = (direction - self.angle +
                      np.pi) % (2 * np.pi) - np.pi
        return angle_diff
    



    def detect_collision(self,ant2):


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


    def ant_collision(self,ant2):
        self.pseudo_rect = self.rect.inflate(5,5)

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
 
        self.pseudo_rect = self.rect.inflate(30, 30)
        if not self.is_alive:
            return

        if 0 < self.rect.centerx < 1280 and 0 < self.rect.centery < 720:
            try:

                if screen.get_at(self.pseudo_rect.center)[:3] == (116, 204, 244):
                    self.speed = 1
                else:
                    self.speed = 3
                
                if screen.get_at(self.pseudo_rect.midtop)[:3] in [(28, 163, 236), (63, 63, 63)]:
                    self.angle += self.angle_direction(1.25, 1.75) * 0.3
                    self.rect.centery += 1
                    self.rotate_image(np.degrees(self.angle))
                    self.collided = True
                    

                elif screen.get_at(self.pseudo_rect.midbottom)[:3] in [(28, 163, 236), (63, 63, 63)] :
                    self.angle += self.angle_direction(-1.25, -1.75) * 0.3
                    self.rect.centery += 1
                    self.rotate_image(np.degrees(self.angle))
                    self.collided = True
                
                elif screen.get_at(self.pseudo_rect.midbottom)[:3] in [(28, 163, 236), (63, 63, 63)] and screen.get_at(self.pseudo_rect.midtop)[:3] in [(28, 163, 236), (63, 63, 63)] :
                    self.angle += self.angle_direction(1.2, 0.8) * 0.4
                    self.rect.centerx -= 1
                    self.rotate_image(np.degrees(self.angle))
                    self.collided = True

                elif screen.get_at(self.pseudo_rect.midright)[:3] in [(28, 163, 236), (63, 63, 63)]:
                    self.angle += self.angle_direction(1.2, 0.8) * 0.4
                    self.rect.centerx -= 1
                    self.rotate_image(np.degrees(self.angle))
                    self.collided = True

                elif screen.get_at(self.pseudo_rect.midleft)[:3] in [(28, 163, 236), (63, 63, 63)]:
                    self.angle += self.angle_direction(-0.25, 0.25) * 0.4
                    self.rect.centerx += 1
                    self.rotate_image(np.degrees(self.angle))
                    self.collided = True


            except Exception as e:
                pass


    def update_food_position(self):
        if self.holding_food is not None:
            self.holding_food["rect"].center = self.rect.center


    def position(self):
        return self.rect.center



    def update(self):
        self.movement()


class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('graphics/food/food.png').convert_alpha()
        if octaves == 3:
            self.image = pygame.transform.scale(self.image, (6,6))

        elif octaves == 4 :
            self.image = pygame.transform.scale(self.image, (5,5))

        elif octaves == 5 :
            self.image = pygame.transform.scale(self.image, (4,4))
        self.rect = self.image.get_rect(center=(x, y))
        self.carried_by = None  # Track which ant is carrying the food (if any)


    def update(self):
        # If carried, follow the ant's position
        if self.carried_by is not None:
            self.rect.center = self.carried_by.rect.center

    def draw(self, screen):
        screen.blit(self.image, self.rect)


def spawn_food_cluster(surface, cluster_radius, food_group):


    while True:
        # Generate random position for the cluster center
        x = random.randint(0, surface.get_width())
        y = random.randint(0, surface.get_height())

        # Check if the center position is valid (on ground)
        color = surface.get_at((x, y))[:3]
        if color == (151, 125, 94):  # Replace with your ground color
            break

    # Generate exactly 40 food pieces around the cluster center
    for _ in range(20):
        angle = random.uniform(0, 2 * np.pi)
        distance = random.uniform(0, cluster_radius)
        food_x = int(x + distance * np.cos(angle))
        food_y = int(y + distance * np.sin(angle))

        # Ensure the food is within bounds and on valid ground
        if 0 <= food_x < surface.get_width() and 0 <= food_y < surface.get_height():
            food_color = surface.get_at((food_x, food_y))[:3]
            if food_color == (151, 125, 94):  # Replace with your ground color
                food = Food(food_x, food_y)
                food_group.add(food)
