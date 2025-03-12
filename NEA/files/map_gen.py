import pygame
import random
import noise

# Global Random Parameters for Map Generation
noise_scale_x = random.randint(100, 300)
noise_scale_y = random.randint(100, 300)
octaves = random.choice(range(10, 99))
base = random.randint(0, 1000)

# Generate seed text from these random parameters
default_seed_text = f"{noise_scale_x:03d}{noise_scale_y:03d}{octaves:02d}{base:03d}"

def generate_terrain_surface(width, height, seed_text=None):
    """
    Generate a procedural terrain surface using Perlin noise.
    
    Args:
        width (int): Width of the terrain surface
        height (int): Height of the terrain surface
        seed_text (str, optional): Seed text from user input. Defaults to None.
    
    Returns:
        tuple: A surface and the seed used for generation
    """
    global noise_scale_x, noise_scale_y, octaves, base

    # If no seed text is provided, use global random parameters
    if not seed_text or len(seed_text) < 9:
        seed_text = default_seed_text
        # Parameters are already set globally
    else:
        # Use provided seed text
        noise_scale_x = int(seed_text[0:3])
        noise_scale_y = int(seed_text[3:6])
        octaves = int(seed_text[6:8])
        base = int(seed_text[8:])

    # Color Definitions
    colors = {
        'water_deep': (28, 163, 236),
        'water_shore': (116, 204, 244),
        'sand': (151, 125, 94),
        'rock': (63, 63, 63),
    }

    surface = pygame.Surface((width, height))
    amplitude = 0.4
    frequency = 2.0
    
    for y in range(height):
        for x in range(width):
            "noise value"
            nx = (x + base) / noise_scale_x
            ny = (y + base) / noise_scale_y
            noise_val = noise.pnoise2(
                nx, ny,
                octaves=octaves,
                persistence=amplitude,
                lacunarity=frequency
            )

            "terrain type"
            if noise_val < -0.27:
                color = colors['water_deep']
            elif noise_val < -0.19:
                color = colors['water_shore']
            elif noise_val > 0.178:
                color = colors['rock']
            else:  # Default to sand
                color = colors['sand']
            
            surface.set_at((x, y), color)
    
    return surface, seed_text