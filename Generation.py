import noise
import numpy as np
import matplotlib.pyplot as plt
from CONSTANTS import CHUNK_SIZE, TILE_SIZE
import random
import pyray as rl
import raylib as raylib

from Object import Palm

# # Parameters for the Perlin noise
# width = 100   # Width of the tilemap
# height = 100  # Height of the tilemap
# scale = 100.0  # Scale of the noise
# octaves = 6    # Number of layers of noise (more octaves = more detail)
# persistence = 0.5  # Persistence of noise (controls roughness)
# lacunarity = 2.0   # Lacunarity of noise (controls frequency)

# def generate_landscape():

#     # Generate a 2D array of Perlin noise values
#     terrain_map = np.zeros((height, width))

#     for y in range(height):
#         for x in range(width):
#             terrain_map[y][x] = noise.pnoise2(
#                 x / scale, 
#                 y / scale, 
#                 octaves=octaves, 
#                 persistence=persistence, 
#                 lacunarity=lacunarity, 
#                 repeatx=1024, 
#                 repeaty=1024, 
#                 base=42
#             )

#     # Normalize the terrain values to be between 0 and 1
#     terrain_map = (terrain_map - np.min(terrain_map)) / (np.max(terrain_map) - np.min(terrain_map))

#     return terrain_map

# def show_landscape(terrain_map):

#     # Visualize the terrain
#     plt.imshow(terrain_map, cmap='terrain')
#     plt.colorbar()
#     plt.title("2D Perlin Noise Terrain Map")
#     plt.show()

water = -.1
shallow = 0
sand = 0.1
grass = 0.3
forest = 0.48
rocks = None



# Function to generate Perlin noise at given coordinates
# x, y, scale=75.0, octaves=4, persistence=.3, lacunarity=2.0, seed=2


def get_tile_texture(value, tiles):
    if value < water:
        return tiles['water_tile']
    elif value < shallow:
        return tiles['shallow_tile']
    elif value < sand:
        return tiles['sand_tile']
    elif value < grass:
        return tiles['grass_tile']
    elif value < forest:
        return tiles['forest_tile']
    else:
        return tiles['rock_tile']
    
def map_to_non_negative(n):
    return 2 * abs(n) if n >= 0 else 2 * abs(n) + 1

def cantor_pairing(a, b):
    a_mapped = map_to_non_negative(a)
    b_mapped = map_to_non_negative(b)
    return (a_mapped + b_mapped) * (a_mapped + b_mapped + 1) // 2 + b_mapped
    
def generate_collision_chunk(values, chunk_x, chunk_y):
    chunkers = []

    for y in range(values.shape[1]):
        for x in range(values.shape[0]):
            # Convert chunk coordinates to world coordinates
            if values[y, x] > forest:
                # print((chunk_x * CHUNK_SIZE + x) * TILE_SIZE, (chunk_y * CHUNK_SIZE + y) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                chunkers.append(rl.Rectangle((chunk_x * CHUNK_SIZE + x) * TILE_SIZE, (chunk_y * CHUNK_SIZE + y) * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    
    return chunkers

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
    palm_data = []

    for y in range(CHUNK_SIZE):
        for x in range(CHUNK_SIZE):
            # Convert chunk coordinates to world coordinates
            chunk_data[y][x] = simplex_noise(chunk_x * CHUNK_SIZE + x, chunk_y * CHUNK_SIZE + y)

    return chunk_data

def generate_palms(chunk_x, chunk_y):
    random.seed(cantor_pairing(chunk_x, chunk_y))
    amount = random.randint(5,15)
    palm_data = []
    for i in range(amount):
        direction = random.choice([-1,1])
        size = random.choice([.75,.8,1,1,1,1,1.2,1.2,1.5,1.7])
        data = (random.randint(chunk_x * CHUNK_SIZE * 64, (chunk_x + 1) * CHUNK_SIZE * 64), random.randint(chunk_y * CHUNK_SIZE * 64, (chunk_y + 1) * CHUNK_SIZE * 64), direction, size)
        if simplex_noise(data[0] // 64, data[1] // 64) > shallow:
            # palm_data.append(data)
            palm_data.append(Palm(data[0],data[1],direction,size))

    palm_data.sort(key=lambda item: item.updates['y'])
    return palm_data

