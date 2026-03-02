# Initialization and imports (Lines 2-5) - Initializes Pygame, and NumPy for math operations
import pygame
import numpy as np
pygame.init()

# Screen and dimension setup (Lines 7-10) - Sets screen dimensions and creates a double-buffered window for smooth rendering
HEIGHT = 720
WIDTH = 1280
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)

# Font and text surface setup (Lines 12-24) - Sets up fonts and text surfaces for the title and nest placement instructions with positioning
main_font = pygame.font.Font('graphics/font/NueGothicRound-Bwan.ttf', 100)
ui_font = pygame.font.Font('graphics/font/NueGothicRound-Bwan.ttf', 20)
text_surface = main_font.render("ant colony", True, 'black')
text_rect = text_surface.get_rect(center=(WIDTH/2, (HEIGHT/2)-50))
option_text_surface = main_font.render("Colony Setup", True, 'black')
option_text_rect = option_text_surface.get_rect(center=(WIDTH/2, 80))
Nest_text_surface = main_font.render("Click to place nest", True, 'white')
Nest_text_surface = pygame.transform.rotozoom(Nest_text_surface, 0, 0.7)
Nest_text_rect = option_text_surface.get_rect(center=((WIDTH/2)-10, 80))

# Additional text surfaces for instructions and status - Creates text for reset, generation status, and start prompt with scaling
esc_text_surface = main_font.render("(Click Esc to reset)", True, 'white')
esc_text_surface = pygame.transform.rotozoom(esc_text_surface, 0, 0.3)
esc_text_rect = esc_text_surface.get_rect(center=((WIDTH/2)-10, 130))

generating_text_surface = main_font.render("Generating..", True, 'white')
generating_text_surface = pygame.transform.rotozoom(generating_text_surface, 0, 0.25)
generating_text_rect = esc_text_surface.get_rect(center=((WIDTH/2)+60, (HEIGHT/2)+120))

generated_text_surface = main_font.render("Generated!", True, 'white')
generated_text_surface = pygame.transform.rotozoom(generated_text_surface, 0, 0.25)
generated_text_rect = esc_text_surface.get_rect(center=((WIDTH/2)+60, (HEIGHT/2)+120))

begin_text = main_font.render("Click any button to begin", True, 'black')
begin_text = pygame.transform.rotozoom(begin_text, 0, 0.5)
begin_text_rect = begin_text.get_rect(center=(WIDTH/2, HEIGHT-50))

# Spider mode and checkbox setup (Lines 47-55) - Initializes spider mode toggle and sets up a checkbox with text
spider_mode = False
checkbox_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 20, 20)
spider_mode_text = ui_font.render("Spider Mode", True, (255, 255, 255))
spider_mode_text_rect = spider_mode_text.get_rect(midleft=(checkbox_rect.right + 10, checkbox_rect.centery))

# Spider nest text setup (Lines 57-63) - Creates and scales text for spider nest placement instructions
spider_nest_text_surface = main_font.render("Click to place spider nest", True, 'white')
spider_nest_text_surface = pygame.transform.rotozoom(spider_nest_text_surface, 0, 0.7)
spider_nest_text_rect = spider_nest_text_surface.get_rect(center=((WIDTH / 2) - 10, 80))

# Seed font and map generation flags (Lines 65-69) - Defines font for seed display and flags for map generation status
seed_font = pygame.font.Font(None, 40)
map_generated = False
Generated = False

# Color and button setup (Lines 71-82) - Sets brown color constant and defines start button dimensions and position
brown = (151, 125, 94)
button_width = 200
button_height = 50
button_x = WIDTH // 2 - button_width // 2  
button_y = HEIGHT - 40 - button_height 
button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

# Slider setup (Lines 84-98) - Configures rectangles for ant and food sliders, positioning them above the button
slider_width = 200
slider_height = 10
ant_slider_rect = pygame.Rect(WIDTH // 2 - slider_width // 2, button_y - 100, slider_width, slider_height)
food_slider_rect = pygame.Rect(WIDTH // 2 - slider_width // 2, button_y - 60, slider_width, slider_height)

# Ant knob setup (Lines 100-107) - Loads and scales ant image for slider knob, rotates and positions it on the ant slider
ant_knob_image = pygame.image.load('graphics/ant/ant_2.png').convert_alpha()
ant_knob_image = pygame.transform.scale(ant_knob_image, (20, 20))
ant_knob_image = pygame.transform.rotate(ant_knob_image, -90) 
ant_knob = ant_knob_image.get_rect(center=(ant_slider_rect.right, ant_slider_rect.centery))

# Food knob setup (Lines 109-118) - Loads and scales food image for slider knob, centers it on food slider, initializes dragging flags
food_knob_image = pygame.image.load('graphics/food/food.png').convert_alpha()  
food_knob_image = pygame.transform.scale(food_knob_image, (20, 20))  
food_knob = food_knob_image.get_rect(center=(food_slider_rect.left + (slider_width // 2), food_slider_rect.centery))  
ant_dragging = False
food_dragging = False

# Input box and generate button setup (Lines 120-128) - Sets up input box and generate button, initializes seed text and activity flag
font = pygame.font.Font(None, 36)
input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 40)
generate_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 40)
seed_text = ''
active = False

# Terrain and color definitions (Lines 130-142) - Defines terrain dimensions and a dictionary of colors for terrain types
width_terrain, height_terrain = 1280, 720
tile_size = 1
colors = {
    'water_deep': (28, 163, 236),
    'water_shore': (116, 204, 244),
    'sand': (151, 125, 94),
    'rock': (63, 63, 63),
}

# Clock and surface setup (Lines 144-147) - Initializes game clock and creates a brown-filled surface as the background
clock = pygame.time.Clock()
main_surface = pygame.Surface((WIDTH, HEIGHT))
main_surface.fill(brown)