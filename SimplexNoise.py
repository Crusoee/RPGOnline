import noise
import numpy as np
import matplotlib.pyplot as plt
from CONSTANTS import CHUNK_SIZE
import random

# Parameters for the Perlin noise
width = 100   # Width of the tilemap
height = 100  # Height of the tilemap
scale = 100.0  # Scale of the noise
octaves = 6    # Number of layers of noise (more octaves = more detail)
persistence = 0.5  # Persistence of noise (controls roughness)
lacunarity = 2.0   # Lacunarity of noise (controls frequency)

def generate_landscape():

    # Generate a 2D array of Perlin noise values
    terrain_map = np.zeros((height, width))

    for y in range(height):
        for x in range(width):
            terrain_map[y][x] = noise.pnoise2(
                x / scale, 
                y / scale, 
                octaves=octaves, 
                persistence=persistence, 
                lacunarity=lacunarity, 
                repeatx=1024, 
                repeaty=1024, 
                base=42
            )

    # Normalize the terrain values to be between 0 and 1
    terrain_map = (terrain_map - np.min(terrain_map)) / (np.max(terrain_map) - np.min(terrain_map))

    return terrain_map

# Function to generate Perlin noise at given coordinates
# x, y, scale=75.0, octaves=4, persistence=.3, lacunarity=2.0, seed=2

"""
        noise.snoise2(x / 1000,
        y / 1000,
        octaves=4,
        persistence=.3,
        lacunarity=2.0,
        base=2),

        noise.snoise2(x / 800,
        y / 800,
        octaves=5,
        persistence=.3,
        lacunarity=5,
        base=2),
"""

def simplex_noise(x, y):

    list_noise = [
        noise.snoise2(x / 5000,
        y / 5000,
        octaves=4,
        persistence=.3,
        lacunarity=2.0,
        base=2),

        noise.snoise2(x / 1000,
        y / 1000,
        octaves=5,
        persistence=.3,
        lacunarity=5,
        base=2),
        
        noise.snoise2(x / 800,
        y / 800,
        octaves=6,
        persistence=.3,
        lacunarity=5,
        base=2)

        -1.2 * noise.snoise2(x / 800,
        y / 800,
        octaves=6,
        persistence=.3,
        lacunarity=5,
        base=3)        

    ]

    return sum(list_noise)

def generate_terrain_chunk(chunk_x, chunk_y):
    """Generates Perlin noise for a given chunk using world coordinates."""
    chunk_data = np.zeros((CHUNK_SIZE, CHUNK_SIZE))

    for y in range(CHUNK_SIZE):
        for x in range(CHUNK_SIZE):
            # Convert chunk coordinates to world coordinates
            chunk_data[y][x] = simplex_noise(chunk_x * CHUNK_SIZE + x, chunk_y * CHUNK_SIZE + y)

    return chunk_data

def show_landscape(terrain_map):

    # Visualize the terrain
    plt.imshow(terrain_map, cmap='terrain')
    plt.colorbar()
    plt.title("2D Perlin Noise Terrain Map")
    plt.show()

def generate_palms(chunk_x, chunk_y):
    random.seed(10)
    palm_locations = [(random.randint(-CHUNK_SIZE * 64, CHUNK_SIZE * 64), random.randint(-CHUNK_SIZE * 64, CHUNK_SIZE * 64)) for x in range(3)]