import pygame
from files.pygame_background import *
from files.mobs import *
from files.Nest import *
from files.map_gen import *
from files.quadtree import *
from files.pheremones import *
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

pygame.init()

Sim_active = False
pygame.mouse.set_visible(False)

boundary = pygame.Rect(0, 0, WIDTH, HEIGHT)

if octaves == 3:
    quadtree = Quadtree(boundary, capacity=2, max_depth=5)

elif octaves == 4 :
    quadtree = Quadtree(boundary, capacity=2, max_depth=7)

elif octaves == 5 :
    quadtree = Quadtree(boundary, capacity=2, max_depth=8)

ant_limit = 20
ant_count = 0
ant_timer = pygame.USEREVENT + 1
pygame.time.set_timer(ant_timer, 1000)
ant_group = pygame.sprite.Group()

pheremones = pygame.sprite.Group()
pheremone_time = pygame.USEREVENT + 1
pygame.time.set_timer(pheremone_time,300)

nest_placed = False
nest_position = pygame.mouse.get_pos()
nest = Nest()


food_group = pygame.sprite.Group()

def check_no_food(ant_group, food_group):
        """
        Check if no food is left on the screen and no ant is holding food.
        :param ant_group: Group of ants in the simulation.
        :param food_group: Group of food objects in the simulation.
        :return: True if no food is left and no ants are holding food, otherwise False.
        """
        # Check if there is no food in the food group
        no_free_food = len(food_group) == 0

        # Check if no ants are holding food
        no_ants_holding_food = all(ant.holding_food is None for ant in ant_group)

        return no_free_food and no_ants_holding_food

terrain_surface = generate_terrain_surface(width_terrain, height_terrain, tile_size)
spawn_food_cluster(terrain_surface, cluster_radius=30, food_group=food_group)

FPS = 30

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if not Sim_active:
            if event.type == pygame.KEYDOWN:
                Sim_active = True
        

        if ant_limit != ant_count and nest_placed:
            if event.type == ant_timer:
                ant_group.add(Ant(nest_position, quadtree,food_group))
                ant_count += 1

        if event.type == pheremone_time:
            for i in ant_group:
                if i.holding_food is not None:
                    pheremone = Pheromones(i.rect.centerx,i.rect.centery,100,500)
                    pheremone.color = ((240, 87, 77))
                else:
                    pheremone = Pheromones(i.rect.centerx,i.rect.centery,100,1000)
                    pheremone.color = (84, 149, 232, 255)
                    

                pheremones.add(pheremone)

        if not nest_placed:
            nest_position = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                nest_placed = True
                pygame.mouse.set_visible(True)

    if Sim_active:

        '''def update_ant(ant):
            ant.update()  # Handles movement, pheromone following, etc.

        if pygame.time.get_ticks() % 2 == 0:
            ant_futures = [executor.submit(update_ant, ant) for ant in ant_group]
            [future.result() for future in ant_futures]  # Wait for all threads to finish

        # Parallel updates for pheromones
        def update_pheromone(pheromone):
            pheromone.update()  # Reduce lifespan, etc.

        
        if pygame.time.get_ticks() % 5 == 0:
            pheromone_futures = [executor.submit(update_pheromone, pheromone) for pheromone in pheremones]
            [future.result() for future in pheromone_futures]'''
            

        quadtree.clear()

        for pheremone in pheremones:
            quadtree.insert(pheremone)

        for ant in ant_group:
            quadtree.insert(ant)

        for food in food_group:
         quadtree.insert(food)

        for ant in ant_group:
            range_rect = pygame.Rect(ant.rect.centerx - 8, ant.rect.centery - 8, 16, 16)
            nearby_ants = quadtree.query(range_rect)
            for other_ant in nearby_ants:
                if other_ant != ant:
                    ant.ant_collision(other_ant)


        for ant in ant_group:
            range_rect = pygame.Rect(ant.rect.centerx - 8, ant.rect.centery - 8, 16, 16)
            nearby_objects = quadtree.query(range_rect)
            for obj in nearby_objects:
                if isinstance(obj, Food):  
                    if ant.rect.colliderect(obj.rect) and obj.carried_by is None and ant.holding_food is None:
                        obj.carried_by = ant 
                        ant.holding_food = obj
                        break



        for ant in ant_group:
            if ant.holding_food is not None and nest.rect is not None:
                if ant.rect.colliderect(nest.rect.inflate(20, 20)):
                    carried_food = ant.holding_food
                    if carried_food in food_group:
                        food_group.remove(carried_food)  #
                        carried_food.carried_by = None  
                        ant.holding_food = None  

        
        
        if check_no_food(ant_group, food_group):

            pheremones = pygame.sprite.Group(
            pheremone for pheremone in pheremones if pheremone.color != (240, 87, 77)
            )
            spawn_food_cluster(terrain_surface, cluster_radius=30, food_group=food_group)


        screen.blit(main_surface, (0, 0))
        screen.blit(terrain_surface, (2.5, 2.5))

        for pheremone in pheremones:
            if pheremone.lifespan !=0 :
                pheremone.draw(screen)


        ant_group.draw(screen)
        food_group.draw(screen)

        if pygame.time.get_ticks() % 8 == 0:
            pheremones.update()

        food_group.update()
        ant_group.update()

        if nest_placed:
            mouse_position = pygame.mouse.get_pos()
            nest.draw(screen, nest_position)
        else:
            nest.draw(screen, nest_position)
    else:
        screen.blit(main_surface, (0, 0))
        screen.blit(text_surface, (text_rect))
        screen.blit(begin_text, (begin_text_rect))

    pygame.display.update()
    clock.tick(FPS)
