import pygame
import numpy as np
pygame.init()
pygame.mixer.init()

HEIGHT = 720
WIDTH = 1280

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)

main_font = pygame.font.Font('graphics/font/NueGothicRound-Bwan.ttf',100)
ui_font = pygame.font.Font('graphics/font/NueGothicRound-Bwan.ttf', 20)

text_surface = main_font.render("ant colony",True,'black')
text_rect = text_surface.get_rect(center = (WIDTH/2,(HEIGHT/2)-50))

option_text_surface = main_font.render("Colony Setup",True,'black')
option_text_rect = option_text_surface.get_rect(center=(WIDTH/2, 80))

Nest_text_surface = main_font.render("Click to place nest",True,'white')
Nest_text_surface = pygame.transform.rotozoom(Nest_text_surface,0,0.7)
Nest_text_rect = option_text_surface.get_rect(center=(((WIDTH/2)-10), 80))

esc_text_surface = main_font.render("(Click Esc to reset)",True,'white')
esc_text_surface = pygame.transform.rotozoom(esc_text_surface,0,0.3)
esc_text_rect = esc_text_surface.get_rect(center=(((WIDTH/2)-10), 110))

generating_text_surface = main_font.render("Generating..",True,'white')
generating_text_surface = pygame.transform.rotozoom(generating_text_surface,0,0.25)
generating_text_rect = esc_text_surface.get_rect(center=(((WIDTH/2)+60), (HEIGHT/2)+120))

generated_text_surface = main_font.render("Generated!",True,'white')
generated_text_surface = pygame.transform.rotozoom(generated_text_surface,0,0.25)
generated_text_rect = esc_text_surface.get_rect(center=(((WIDTH/2)+60), (HEIGHT/2)+135))

begin_text = main_font.render("Click any button to begin",True,'black')
begin_text = pygame.transform.rotozoom(begin_text,0,0.5)
begin_text_rect = begin_text.get_rect(center = (WIDTH/2,HEIGHT-50))

spider_mode = False
checkbox_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 20, 20)
spider_mode_text = ui_font.render("Spider Mode", True, (255, 255, 255))
spider_mode_text_rect = spider_mode_text.get_rect(midleft=(checkbox_rect.right + 10, checkbox_rect.centery))

spider_nest_text_surface = main_font.render("Click to place spider nest", True, 'white')
spider_nest_text_surface = pygame.transform.rotozoom(spider_nest_text_surface, 0, 0.7)
spider_nest_text_rect = spider_nest_text_surface.get_rect(center=((WIDTH / 2) - 10, 80))


seed_font = pygame.font.Font(None, 40)

map_generated = False



brown = (151, 125, 94)

Generated = False


button_width = 200
button_height = 50
button_x = WIDTH // 2 - button_width // 2  
button_y = HEIGHT - 40 - button_height 
button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

slider_width = 200
slider_height = 10
ant_slider_rect = pygame.Rect(WIDTH // 2 - slider_width // 2, button_y - 100, slider_width, slider_height)
food_slider_rect = pygame.Rect(WIDTH // 2 - slider_width // 2, button_y - 60, slider_width, slider_height)

ant_knob_image = pygame.image.load('graphics/ant/ant_2.png').convert_alpha()
ant_knob_image = pygame.transform.scale(ant_knob_image, (20, 20))
ant_knob_image = pygame.transform.rotate(ant_knob_image, -90) 
ant_knob = ant_knob_image.get_rect(center=(ant_slider_rect.right, ant_slider_rect.centery))


food_knob_image = pygame.image.load('graphics/food/food.png').convert_alpha()  
food_knob_image = pygame.transform.scale(food_knob_image, (20, 20))  
food_knob = food_knob_image.get_rect(center=(food_slider_rect.left + (slider_width // 2), food_slider_rect.centery))  
ant_dragging = False
food_dragging = False


font = pygame.font.Font(None, 36)
input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 40)
generate_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 40)
seed_text = ''
active = False

width_terrain, height_terrain = 1280, 720
tile_size = 1

colors = {
    'water_deep': (28, 163, 236),
    'water_shore': (116, 204, 244),
    'sand': (151, 125, 94),
    'rock': (63, 63, 63),
}




clock = pygame.time.Clock()
main_surface = pygame.Surface((WIDTH,HEIGHT))
main_surface.fill(brown)
