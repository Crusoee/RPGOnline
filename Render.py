import pyray as rl
import raylib as raylib
from CONSTANTS import NUM_CHUNKS, CHUNK_SIZE, TILE_SIZE
from SimplexNoise import generate_terrain_chunk

water = -.1
shallow = 0
sand = 0.1
grass = 0.3
forest = 0.45
rocks = None

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


def draw_tiles(player, chunk_data, tiles):
    # Calculate player's chunk position
    player_chunk_x = player.locsize.x // (CHUNK_SIZE * TILE_SIZE)
    player_chunk_y = player.locsize.y // (CHUNK_SIZE * TILE_SIZE)

    # Determine visible chunk range
    chunk_x_start = player_chunk_x - NUM_CHUNKS // 2
    chunk_y_start = player_chunk_y - NUM_CHUNKS // 2
    chunk_x_end = chunk_x_start + NUM_CHUNKS
    chunk_y_end = chunk_y_start + NUM_CHUNKS

    # Loop through visible chunks
    for chunk_y in range(int(chunk_y_start), int(chunk_y_end)):
        for chunk_x in range(int(chunk_x_start), int(chunk_x_end)):
            # Generate chunk if not already cached
            if (chunk_x, chunk_y) not in chunk_data:
                chunk_data[chunk_x, chunk_y] = generate_terrain_chunk(chunk_x, chunk_y)
                # print(chunk_x, chunk_y)

            # Draw tiles in the chunk
            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    tile_type = chunk_data[chunk_x, chunk_y][y][x]
                    tile_texture = get_tile_texture(tile_type, tiles)
                    tile_draw_x = (chunk_x * CHUNK_SIZE + x) * TILE_SIZE
                    tile_draw_y = (chunk_y * CHUNK_SIZE + y) * TILE_SIZE
                    rl.draw_texture(tile_texture, tile_draw_x, tile_draw_y, rl.WHITE)

def draw_players(shared_memory):
    for key, value in shared_memory['players'][0].items():
        if key == shared_memory['user']:
            continue
        raylib.DrawRectangle(shared_memory['players'][0][key][0], shared_memory['players'][0][key][1], 40, 80, rl.RED)