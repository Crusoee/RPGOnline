import pyray as rl
import raylib as raylib
from CONSTANTS import NUM_CHUNKS, CHUNK_SIZE, TILE_SIZE, PLAYER_HEIGHT, PLAYER_WIDTH, SCREEN_WIDTH
from SimplexNoise import generate_terrain_chunk
from Helper import distance

water = -.1
shallow = 0
sand = 0.1
grass = 0.3
forest = 0.48
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
    
def generate_collision_chunk(values, chunk_x, chunk_y):
    chunkers = []

    for y in range(values.shape[1]):
        for x in range(values.shape[0]):
            # Convert chunk coordinates to world coordinates
            if values[y, x] > forest:
                # print((chunk_x * CHUNK_SIZE + x) * TILE_SIZE, (chunk_y * CHUNK_SIZE + y) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                chunkers.append(rl.Rectangle((chunk_x * CHUNK_SIZE + x) * TILE_SIZE, (chunk_y * CHUNK_SIZE + y) * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    
    return chunkers


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
                terrain_data = generate_terrain_chunk(chunk_x, chunk_y)
                collision_data = generate_collision_chunk(terrain_data, chunk_x, chunk_y)
                # print(collision_data, chunk_x, chunk_y)
                chunk_data[chunk_x, chunk_y] = [terrain_data,collision_data]

            # Draw tiles in the chunk
            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    tile_type = chunk_data[chunk_x, chunk_y][0][y][x]
                    tile_texture = get_tile_texture(tile_type, tiles)
                    tile_draw_x = (chunk_x * CHUNK_SIZE + x) * TILE_SIZE
                    tile_draw_y = (chunk_y * CHUNK_SIZE + y) * TILE_SIZE
                    rl.draw_texture(tile_texture, tile_draw_x, tile_draw_y, rl.WHITE)

def draw_players(shared_memory):
    for key, value in shared_memory['playersupdate'][0].items():
        if key == shared_memory['user']:
            continue

        try:
            player = shared_memory['playersupdate'][0][key]
            if player['swim'] == True:
                if key == shared_memory['player']['action']['target']:
                    raylib.DrawRectangle(int(player['x']), int(player['y']) + PLAYER_HEIGHT // 2, PLAYER_WIDTH, PLAYER_HEIGHT // 2, rl.YELLOW)
                    rl.draw_text(player['nme'],int(player['x']) - len(player['nme']) // 2, int(player['y']) - 40,20,rl.BLACK)
                else:
                    raylib.DrawRectangle(int(player['x']), int(player['y']) + PLAYER_HEIGHT // 2, PLAYER_WIDTH, PLAYER_HEIGHT // 2, rl.SKYBLUE)
                    rl.draw_text(player['nme'],int(player['x']) - len(player['nme']) // 2, int(player['y']) - 40,20,rl.BLACK)
            else:
                # print(shared_memory['player']['action']['target'], key)
                if key == shared_memory['player']['action']['target']:
                    raylib.DrawRectangle(int(player['x']), int(player['y']), PLAYER_WIDTH, PLAYER_HEIGHT, rl.YELLOW)
                    rl.draw_text(player['nme'],int(player['x']) - len(player['nme']) // 2, int(player['y']) - 40,20,rl.BLACK)
                else:
                    raylib.DrawRectangle(int(player['x']), int(player['y']), PLAYER_WIDTH, PLAYER_HEIGHT, rl.SKYBLUE)
                    rl.draw_text(player['nme'],int(player['x']) - len(player['nme']) // 2, int(player['y']) - 40,20,rl.BLACK)
        except KeyError as e:
            print("Error Occurred in draw_players: ", e)

def draw_npcs(shared_memory, npc):
    for key, value in shared_memory['npcs'][0].items():
        try:
            rl.draw_texture(npc,value.x,value.y,rl.WHITE)
        except (KeyError) as e:
            print("Error: ", e)

def draw_info(player):
    # rl.draw_text(f"fps: {1 / (raylib.GetFrameTime() + .00000000001)}", 50, 100, 40, rl.BLACK)
    # rl.draw_text(f"X: {player.locsize.x // TILE_SIZE}, Y: {player.locsize.y // TILE_SIZE}", 50, 50, 40, rl.BLACK)
    # rl.draw_text(f"X: {player.locsize.x}, Y: {player.locsize.y}", 50, 50, 40, rl.BLACK)
    # rl.draw_text(f"C X: {player.locsize.x // (TILE_SIZE * CHUNK_SIZE)}, C Y: {player.locsize.y // (TILE_SIZE * CHUNK_SIZE)}", 50, 150, 40, rl.BLACK)
    
    rl.draw_text(f"health: {player.stats['hlth']}", 20, 20, 20, rl.RED)
    rl.draw_text(f"damage: {player.stats['dmg']}", 20, 40, 20, rl.BLACK)
    # rl.draw_text(f"health: {player.stats['hlth']}", 20, 20, 10, rl.RED)
    # rl.draw_text(f"health: {player.stats['hlth']}", 20, 20, 10, rl.RED)
    # rl.draw_text(f"health: {player.stats['hlth']}", 20, 20, 10, rl.RED)