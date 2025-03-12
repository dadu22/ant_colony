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
pygame.mixer.init()

Sim_active = False
Options_menu = False
pygame.mouse.set_visible(False)

boundary = pygame.Rect(0, 0, WIDTH, HEIGHT)

if octaves < 30:
    quadtree = Quadtree(boundary, capacity=3, max_depth=5)
    pheremone_quadtree = Quadtree(boundary, capacity=2, max_depth=5)
    mobs_quadtree = Quadtree(boundary, capacity=3, max_depth=4)
elif 30 < octaves < 60:
    pheremone_quadtree = Quadtree(boundary, capacity=2, max_depth=5)
    mobs_quadtree = Quadtree(boundary, capacity=3, max_depth=4)
else:
    pheremone_quadtree = Quadtree(boundary, capacity=3, max_depth=6)
    mobs_quadtree = Quadtree(boundary, capacity=4, max_depth=5)

ant_limit = 100
food_spawn_amount = 20

ant_count = 0
ant_timer = pygame.USEREVENT + 1
pygame.time.set_timer(ant_timer, 10)
ant_group = pygame.sprite.Group()

spider_group = pygame.sprite.Group()
spider_count = 0
spider_limit = 1
spider_timer = pygame.USEREVENT + 3
pygame.time.set_timer(spider_timer, 7000)

pheremones = pygame.sprite.Group()

pheremone_time = pygame.USEREVENT + 1
pygame.time.set_timer(pheremone_time, 400)

red_pheremone_time = pygame.USEREVENT + 2
pygame.time.set_timer(red_pheremone_time, 400)

nest_placed = False
spider_nest_placed = False
nest_position = (0, 0)
spider_nest_position = (0, 0)
nest = Nest()
spider_nest = SpiderNest()

red_pheremones = 0

generate = 1
start_simulation = False
map_generating = False
terrain_future = None
nest_click = 1

food_group = pygame.sprite.Group()



def check_no_food(ant_group, food_group):
    no_free_food = len(food_group) == 0
    no_ants_holding_food = all(ant.holding_food is None for ant in ant_group)
    if no_free_food and no_ants_holding_food:
        for pheromone in pheremones:
            if pheromone.color == (240, 87, 77):
                pheromone.kill()
    return no_free_food and no_ants_holding_food

FPS = 30
clock = pygame.time.Clock()

def reset_simulation():
    global ant_count, spider_count, nest_placed, spider_nest_placed, red_pheremones
    global nest_position, spider_nest_position, nest_click, food_group
    global ant_group, spider_group, pheremones, mobs_quadtree, pheremone_quadtree
    
    ant_count = 0
    spider_count = 0
    red_pheremones = 0
    
    nest_placed = False
    spider_nest_placed = False
    nest_position = (0, 0)
    spider_nest_position = (0, 0)
    nest_click = 1
    
    ant_group.empty()
    spider_group.empty()
    pheremones.empty()
    food_group.empty()
    
    mobs_quadtree.clear()
    pheremone_quadtree.clear()
    
    if octaves < 30:
        mobs_quadtree = Quadtree(boundary, capacity=3, max_depth=4)
        pheremone_quadtree = Quadtree(boundary, capacity=2, max_depth=5)
    elif 30 < octaves < 60:
        mobs_quadtree = Quadtree(boundary, capacity=3, max_depth=4)
        pheremone_quadtree = Quadtree(boundary, capacity=2, max_depth=5)
    else:
        mobs_quadtree = Quadtree(boundary, capacity=4, max_depth=5)
        pheremone_quadtree = Quadtree(boundary, capacity=3, max_depth=6)
    


while True:
    print(int(clock.get_fps()))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if not Options_menu:
            if event.type == pygame.KEYDOWN:
                Options_menu = True

        if Options_menu:
            pygame.mouse.set_visible(True)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    Sim_active = True
                    Options_menu = False
                    pygame.mouse.set_visible(False)
                if input_box.collidepoint(event.pos):
                    active = not active
                elif generate_button.collidepoint(event.pos):
                    if seed_text:
                        seed_str = str(seed_text)
                        if len(seed_str) >= 9:
                            map_generated = False
                            map_generating = True
                            start_simulation = False
                            print("generating")
                            noise_scale_x = int(seed_str[0:3])
                            noise_scale_y = int(seed_str[3:6])
                            octaves = int(seed_str[6:8])
                            base = int(seed_str[8:])
                            terrain_future = executor.submit(
                                generate_terrain_surface, width_terrain, height_terrain , seed_text
                            )
                    else:
                        map_generated = False
                        map_generating = True
                        start_simulation = False
                        screen.blit(generating_text_surface,generating_text_rect)
                        print("generating")
                        terrain_future = executor.submit(
                            generate_terrain_surface, width_terrain, height_terrain, seed_text
                        )
                elif ant_slider_rect.collidepoint(event.pos):
                    ant_dragging = True
                elif food_slider_rect.collidepoint(event.pos):
                    food_dragging = True
                elif checkbox_rect.collidepoint(event.pos):
                    spider_mode = not spider_mode
                    if spider_mode and ant_limit > 40:
                        ant_limit = 40 
                        ant_knob.centerx = ant_slider_rect.right
                    else:
                        ant_limit = 100
                        ant_knob.centerx = ant_slider_rect.right


            if event.type == pygame.MOUSEBUTTONUP:
                ant_dragging = False
                food_dragging = False

            if event.type == pygame.MOUSEMOTION:
                if ant_dragging:
                    ant_knob.centerx = max(ant_slider_rect.left, min(ant_slider_rect.right, event.pos[0]))
                    if spider_mode:
                        
                        ant_limit = int(10 + ((ant_knob.centerx - ant_slider_rect.left) / slider_width) * (40 - 10))
                    else:
                        ant_limit = int(40 + ((ant_knob.centerx - ant_slider_rect.left) / slider_width) * (100 - 40))
                if food_dragging:
                    food_knob.centerx = max(food_slider_rect.left, min(food_slider_rect.right, event.pos[0]))
                    food_spawn_amount = int(10 + ((food_knob.centerx - food_slider_rect.left) / slider_width) * (50 - 10))
                    
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    seed_text = seed_text[:-1]
                elif event.unicode.isdigit():
                    seed_text += event.unicode

        if Sim_active:

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    reset_simulation()
                    Options_menu = True
                    Sim_active = False
                    pygame.mouse.set_visible(True)




            if Sim_active:
             
             if not nest_placed:
                nest_position = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check terrain_surface, not screen, for the true terrain color
                    if nest_click == 2 :
                        terrain_color = terrain_surface.get_at(nest_position)[:3]  # RGB only

                    if nest_click == 2:
                        if terrain_color == brown:
                            if nest_click == 2:
                                nest_placed = True
                                print(f"Nest placed at {nest_position} on brown terrain")
                    
                    if nest_click < 2:
                     nest_click += 1

             elif spider_mode and not spider_nest_placed and nest_placed:
                spider_nest_position = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check terrain_surface, not screen, for the true terrain color
                    terrain_color = terrain_surface.get_at(spider_nest_position)[:3]  # RGB only
                    if terrain_color == brown:
                        spider_nest_placed = True
                        pygame.mouse.set_visible(True)

            if ant_limit != ant_count and nest_placed and (not spider_mode or spider_nest_placed):
                if event.type == ant_timer:
                    ant_group.add(Ant(nest_position, mobs_quadtree, pheremone_quadtree, food_group))
                    ant_count += 1

            if spider_mode and spider_count < spider_limit and spider_nest_placed:
                if event.type == spider_timer:
                    spider_group.add(Spider(spider_nest_position, mobs_quadtree, pheremone_quadtree, ant_group))
                    spider_count += 1

            if event.type == pheremone_time:
                for i in ant_group:
                    if i.holding_food is None and i.check_pheremones() == []:
                        if len(pheremones) < 300:
                            distance = np.sqrt((nest_position[0] - i.rect.centerx) ** 2 + (nest_position[1] - i.rect.centery) ** 2)
                            intesity = 1 / (0.00002 * distance + 1 / 1600)
                            pheromone = Pheromones(i.rect.centerx, i.rect.centery, 1000, intesity)
                            pheromone.color = (84, 149, 232)
                            pheremones.add(pheromone)

            if event.type == red_pheremone_time:
                for i in ant_group:
                    if i.holding_food is not None and i.check_pheremones() == []:
                        if red_pheremones < 50:
                            distance = np.sqrt((nest_position[0] - i.rect.centerx) ** 2 + (nest_position[1] - i.rect.centery) ** 2)
                            intesity = 1 / (0.00002 * distance + 1 / 1600)
                            pheromone = Pheromones(i.rect.centerx, i.rect.centery, 500, (-intesity + 2400))
                            pheromone.color = (240, 87, 77)
                            pheremones.add(pheromone)
                            red_pheremones += 1

    if Sim_active:

        mobs_quadtree.clear()
        pheremone_quadtree.clear()

        for pheremone in pheremones:
            pheremone_quadtree.insert(pheremone)

        for ant in ant_group:
            mobs_quadtree.insert(ant)

        if spider_mode:
            for spider in spider_group:
                mobs_quadtree.insert(spider)

        for food in food_group:
            mobs_quadtree.insert(food)

        for ant in ant_group:
            range_rect = pygame.Rect(ant.rect.centerx - 8, ant.rect.centery - 8, 16, 16)
            nearby_ants = mobs_quadtree.query(range_rect)
            for other_ant in nearby_ants:
                if other_ant != ant and isinstance(other_ant, Ant):
                    ant.ant_collision(other_ant)

        for ant in ant_group:
            range_rect = pygame.Rect(ant.rect.centerx - 8, ant.rect.centery - 8, 16, 16)
            nearby_objects = mobs_quadtree.query(range_rect)
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
                        food_group.remove(carried_food)
                        carried_food.carried_by = None
                        ant.holding_food = None

        if spider_mode:
            spiders_to_remove = []
            for spider in spider_group:
                range_rect = pygame.Rect(spider.rect.centerx - 32, spider.rect.centery - 32, 64, 64)
                nearby_ants = mobs_quadtree.query(range_rect)
                spider.update_nearby_ants(nearby_ants)
                if not spider.is_alive:
                    spiders_to_remove.append(spider)
                    spider_count -= 1

            for spider in spiders_to_remove:
                spider_group.remove(spider)

        if check_no_food(ant_group, food_group):
            red_pheremones = 0
            spawn_food_cluster(terrain_surface, cluster_radius=30, food_group=food_group, amount=food_spawn_amount)
            for ant in ant_group:
                ant.pheremone_list = []

        screen.blit(main_surface, (0, 0))
        screen.blit(terrain_surface, (2.5, 2.5))

        for pheremone in pheremones:
            pheremone.draw(screen)

        ant_group.draw(screen)
        if spider_mode:
            spider_group.draw(screen)
        food_group.draw(screen)

        pheremones.update()
        food_group.update()
        ant_group.update()
        if spider_mode:
            spider_group.update()

        for food in food_group:
            if food.carried_by is not None and not food.carried_by.is_alive:
                food.carried_by = None

        if not nest_placed:
            nest_position = pygame.mouse.get_pos()
            screen.blit(Nest_text_surface, Nest_text_rect)
            screen.blit(esc_text_surface, esc_text_rect)
            nest.draw(screen, nest_position)
        elif spider_mode and not spider_nest_placed:
            spider_nest_position = pygame.mouse.get_pos()
            screen.blit(esc_text_surface, esc_text_rect)
            screen.blit(spider_nest_text_surface, spider_nest_text_rect)
            spider_nest.draw(screen, spider_nest_position)

        if nest_placed:
            nest.draw(screen, nest_position)
        if spider_mode and spider_nest_placed:
            spider_nest.draw(screen, spider_nest_position)

        seed_display = seed_font.render(f"seed: {seed_text}", True, (255, 255, 255))
        seed_rect = seed_display.get_rect(topleft=(10, 10))  
        screen.blit(seed_display, seed_rect)

    elif Options_menu:
        if map_generating and terrain_future is not None and terrain_future.done():
            terrain_surface, generated_seed = terrain_future.result()
            seed_text = generated_seed
            map_generating = False
            start_simulation = True
            terrain_future = None
            screen.blit(generated_text_surface, generated_text_rect)
            print("generated")
            spawn_food_cluster(terrain_surface, cluster_radius=30, food_group=food_group, amount=food_spawn_amount)
            map_generated = True

        screen.blit(main_surface, (0, 0))
        screen.blit(option_text_surface, option_text_rect)

        if map_generating and terrain_future is not None and not terrain_future.done():
            screen.blit(generating_text_surface, generating_text_rect)

        if map_generated == True:
            screen.blit(generated_text_surface, generated_text_rect)

        mouse_pos = pygame.mouse.get_pos()

        generate_button_base = pygame.Rect(generate_button.x, generate_button.y, generate_button.w, generate_button.h)
        if generate_button_base.collidepoint(mouse_pos):
            generate_button_hover = generate_button_base.inflate(10, 10)
            pygame.draw.rect(screen, (colors['rock']), generate_button_hover, border_radius=15)
            generate_text = ui_font.render("Generate Map", True, (255, 255, 255))
            generate_text_rect = generate_text.get_rect(center=generate_button_hover.center)
        else:
            pygame.draw.rect(screen, (colors['rock']), generate_button_base, border_radius=15)
            generate_text = ui_font.render("Generate Map", True, (255, 255, 255))
            generate_text_rect = generate_text.get_rect(center=generate_button_base.center)
        screen.blit(generate_text, generate_text_rect)

        if start_simulation and not map_generating:
            button_rect_base = pygame.Rect(button_rect.x, button_rect.y, button_rect.w, button_rect.h)
            if button_rect_base.collidepoint(mouse_pos):
                button_rect_hover = button_rect_base.inflate(10, 10) 
                pygame.draw.rect(screen, (colors['rock']), button_rect_hover, border_radius=15)
                start_text = ui_font.render("Start Simulation", True, (255, 255, 255))
                start_text_rect = start_text.get_rect(center=button_rect_hover.center)
            else:
                pygame.draw.rect(screen, (colors['rock']), button_rect_base, border_radius=15)
                start_text = ui_font.render("Start Simulation", True, (255, 255, 255))
                start_text_rect = start_text.get_rect(center=button_rect_base.center)
            screen.blit(start_text, start_text_rect)

        font_small = pygame.font.Font(None, 28)
        instruction_text = ui_font.render("Enter 9-12 digit seed or Generate for random", True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(input_box.centerx, input_box.y - 40))
        screen.blit(instruction_text, instruction_rect)

        pygame.draw.rect(screen, (255, 255, 255) if active else (200, 200, 200), input_box)
        text_surface = ui_font.render(seed_text, True, (0, 0, 0))
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
        input_box.w = max(200, text_surface.get_width() + 10)

        pygame.draw.rect(screen, (150, 150, 150), ant_slider_rect)
        screen.blit(ant_knob_image, ant_knob)
        ant_label = ui_font.render(f"Ants: {ant_limit}", True, (255, 255, 255))
        screen.blit(ant_label, (ant_slider_rect.right + 10, ant_slider_rect.y - 5))

        pygame.draw.rect(screen, (150, 150, 150), food_slider_rect)
        screen.blit(food_knob_image, food_knob)
        food_label = ui_font.render(f"Food: {food_spawn_amount}", True, (255, 255, 255))
        screen.blit(food_label, (food_slider_rect.right + 10, food_slider_rect.y - 5))

        pygame.draw.rect(screen, (255, 255, 255), checkbox_rect, 2)
        if spider_mode:
            pygame.draw.line(screen, (255, 255, 255), (checkbox_rect.left + 2, checkbox_rect.centery), 
                            (checkbox_rect.centerx, checkbox_rect.bottom - 2), 2)
            pygame.draw.line(screen, (255, 255, 255), (checkbox_rect.centerx, checkbox_rect.bottom - 2), 
                            (checkbox_rect.right - 2, checkbox_rect.top + 2), 2)
        screen.blit(spider_mode_text, spider_mode_text_rect)

        if 'decor_ants' not in globals():
            decor_ants = pygame.sprite.Group()
            for _ in range(100):
                ant = Ant((WIDTH // 2, HEIGHT // 2), None, None, None)
                ant.speed = 1
                ant.rect.center = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
                ant.mobs_quadtree = None
                ant.pheremone_quadtree = None
                ant.food_group = None
                ant.holding_food = None
                ant.original_image = pygame.image.load('graphics/ant/ant_2.png').convert_alpha()
                ant.original_image = pygame.transform.rotozoom(ant.original_image, 0, 0.02)
                ant.rect = ant.original_image.get_rect(center=ant.rect.center)
                decor_ants.add(ant)

        for ant in decor_ants:
            ant.angle += random.uniform(-0.1, 0.1)
            ant.speedx = ant.speed * np.cos(ant.angle)
            ant.speedy = -ant.speed * np.sin(ant.angle)
            ant.rect.x += ant.speedx
            ant.rect.y += ant.speedy
            if ant.rect.left < 0:
                ant.angle = random.uniform(0, np.pi)
            elif ant.rect.right > WIDTH:
                ant.angle = random.uniform(np.pi, 2 * np.pi)
            if ant.rect.top < 0:
                ant.angle = random.uniform(np.pi / 2, 3 * np.pi / 2)
            elif ant.rect.bottom > HEIGHT:
                ant.angle = random.uniform(-np.pi / 2, np.pi / 2)
            ant.rotate_image(np.degrees(ant.angle))
            screen.blit(ant.image, ant.rect)

    else:
        screen.blit(main_surface, (0, 0))
        screen.blit(text_surface, text_rect)
        screen.blit(begin_text, begin_text_rect)

        if 'decor_ants' not in globals():
            decor_ants = pygame.sprite.Group()
            for _ in range(100):
                ant = Ant((WIDTH // 2, HEIGHT // 2), None, None, None)
                ant.speed = 1
                ant.rect.center = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
                ant.mobs_quadtree = None
                ant.pheremone_quadtree = None
                ant.food_group = None
                ant.holding_food = None
                ant.original_image = pygame.image.load('graphics/ant/ant_2.png').convert_alpha()
                ant.original_image = pygame.transform.rotozoom(ant.original_image, 0, 0.02)
                ant.rect = ant.original_image.get_rect(center=ant.rect.center)
                decor_ants.add(ant)

        for ant in decor_ants:
            ant.angle += random.uniform(-0.1, 0.1)
            ant.speedx = ant.speed * np.cos(ant.angle)
            ant.speedy = -ant.speed * np.sin(ant.angle)
            ant.rect.x += ant.speedx
            ant.rect.y += ant.speedy
            if ant.rect.left < 0:
                ant.angle = random.uniform(0, np.pi)
            elif ant.rect.right > WIDTH:
                ant.angle = random.uniform(np.pi, 2 * np.pi)
            if ant.rect.top < 0:
                ant.angle = random.uniform(np.pi / 2, 3 * np.pi / 2)
            elif ant.rect.bottom > HEIGHT:
                ant.angle = random.uniform(-np.pi / 2, np.pi / 2)
            ant.rotate_image(np.degrees(ant.angle))
            screen.blit(ant.image, ant.rect)

    pygame.display.update()
    clock.tick(FPS)