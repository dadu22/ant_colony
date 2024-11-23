import pygame
import random
import noise
import numpy as np

width_terrain, height_terrain = 1275, 715
tile_size = 1
print(tile_size)
noise_scale_x = random.randint(100,300)
noise_scale_y = random.randint(100,300)
print(noise_scale_x,noise_scale_y)
octaves_list = [3,4,5]
octaves = random.choice(octaves_list)
print(octaves)

colors = {
    'water_deep': (28,163,236),
    'water_shore': (116,204,244),
    'rock': ((63, 63, 63)),
}

pygame.init()



def generate_terrain_surface(width, height, tile_size):
    terrain_surface = pygame.Surface((width, height))

    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            noise_val = noise.pnoise2(x / noise_scale_x, y / noise_scale_y, octaves)
            if noise_val < -0.27:
                color = colors['water_deep']
            elif noise_val < -0.19:
                color = colors['water_shore']
            elif noise_val > 0.2:
                color = colors['rock']
            else:
                color = (151, 125, 94)
            
            pygame.draw.rect(terrain_surface, color,(x,y,tile_size,tile_size))

    return terrain_surface 