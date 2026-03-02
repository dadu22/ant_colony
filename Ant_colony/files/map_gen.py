# Imported modules (Lines 2-4) - Imports Pygame, random, and noise libraries for terrain generation
import pygame
import random
import noise
from files.pygame_background import colors

# Global Random Parameters for Map Generation (Lines 6-9) - Defines random parameters for noise-based terrain generation
noise_scale_x = random.randint(100, 300)
noise_scale_y = random.randint(100, 300)
octaves = random.choice(range(10, 99))
base = random.randint(0, 1000)

# Generate seed text from these random parameters (Lines 11-12) - Creates a default seed text from global parameters
default_seed_text = f"{noise_scale_x:03d}{noise_scale_y:03d}{octaves:02d}{base:03d}"

# Function to generate terrain surface (Lines 14-53) - Generates a procedural terrain surface using Perlin noise
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

    # If no seed text is provided, use global random parameters (Lines 20-23) - Sets default parameters if no seed is given
    if not seed_text or len(seed_text) < 9:
        seed_text = default_seed_text
        # Parameters are already set globally
    else:
        # Use provided seed text (Lines 26-29) - Parses seed text into parameters
        noise_scale_x = int(seed_text[0:3])
        noise_scale_y = int(seed_text[3:6])
        octaves = int(seed_text[6:8])
        base = int(seed_text[8:])


    surface = pygame.Surface((width, height))
    amplitude = 0.4
    frequency = 2.0
    
    for y in range(height):
        for x in range(width):
            # Noise value calculation (Lines 43-46) - Computes Perlin noise value for each pixel
            nx = (x + base) / noise_scale_x
            ny = (y + base) / noise_scale_y
            noise_val = noise.pnoise2(
                nx, ny,
                octaves=octaves,
                persistence=amplitude,
                lacunarity=frequency
            )

            # Terrain type determination (Lines 48-52) - Assigns color based on noise value thresholds
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