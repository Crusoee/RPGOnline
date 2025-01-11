import pyray as rl
import raylib as raylib
from CONSTANTS import NUM_CHUNKS, CHUNK_SIZE, TILE_SIZE, PLAYER_HEIGHT, PLAYER_WIDTH, SCREEN_WIDTH
from SimplexNoise import generate_terrain_chunk
from Helper import distance
import math

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

def draw_players(shared_memory,player_textures):
    for key, value in shared_memory['playersupdate'][0].items():
        if key == shared_memory['user']:
            continue

        try:
            player = shared_memory['playersupdate'][0][key]
            text_size = rl.measure_text_ex(player_textures["name_font"], player['nme'], 30, 0.0)
            rl.draw_text_ex(player_textures["name_font"], player['nme'], rl.Vector2(int(player['x'] - (text_size.x / 2)  + PLAYER_WIDTH / 2), int(player['y'] - 80)), 40, 0.0, rl.BLACK)
            
            # Ensure health ratio is clamped between 0 and 1
            health_ratio = max(0, min(1, shared_memory['playersinfo'][0][key]['hlth'] / shared_memory['playersinfo'][0][key]['mhlth']))
            # Calculate base position for the health bar
            base_x = int(player['x'] - 40 + PLAYER_WIDTH // 2)
            base_y = int(player['y'] - 40)
            # # Draw the health bar
            # rl.draw_rectangle(base_x, base_y, 80, 20, rl.RED)  # Background
            # rl.draw_rectangle(base_x, base_y, int(80 * health_ratio), 20, rl.GREEN)  # Health bar

            rl.draw_texture_pro(player_textures["healthframe"], rl.Rectangle(0,0,player_textures["healthframe"].width, player_textures["healthframe"].height), 
                        rl.Rectangle(base_x, base_y, 80, 20), 
                        rl.Vector2(0,0),
                        0.0, 
                        rl.WHITE)
            rl.draw_texture_pro(player_textures["healthbar"], rl.Rectangle(0,0,player_textures["healthbar"].width * health_ratio, player_textures["healthbar"].height), 
                        rl.Rectangle(base_x, base_y, 80 * health_ratio, 20), 
                        rl.Vector2(0,0),
                        0.0, 
                        rl.WHITE)

            if player['swim'] == True:
                if player['ismoving']:
                    if -135 < player['angle'] <= -45:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),0,256, 150), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,player_textures['player'].width/10, player_textures['player'].height/10 - 47), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)
                    if -45 < player['angle'] <= 45:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),(256 * 3),256, 150), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,player_textures['player'].width/10, player_textures['player'].height/10 - 47), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)
                    if 45 < player['angle'] <= 135:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),(256 * 1),256, 150), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,player_textures['player'].width/10, player_textures['player'].height/10 - 47), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)
                    if player['angle'] <= -135 or player['angle'] > 135:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),(256 * 2),256, 150), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,player_textures['player'].width/10, player_textures['player'].height/10 - 47), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)
                else:
                    if -135 < player['angle'] <= -45:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle((0),0,256, 150), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,player_textures['player'].width/10, player_textures['player'].height/10 - 47), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)
                    if -45 < player['angle'] <= 45:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle((0),(256 * 3),256, 150), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,player_textures['player'].width/10, player_textures['player'].height/10 - 47), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)
                    if 45 < player['angle'] <= 135:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle((0),(256 * 1),256, 150), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,player_textures['player'].width/10, player_textures['player'].height/10 - 47), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)
                    if player['angle'] <= -135 or player['angle'] > 135:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle((0),(256 * 2),256, 150), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,player_textures['player'].width/10, player_textures['player'].height/10 - 47), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)
            else:
                if player['ismoving']:
                    if -135 < player['angle'] <= -45:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),0,256, 256), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10,player_textures['player'].width/10, player_textures['player'].height/10), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)
                    if -45 < player['angle'] <= 45:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),(256 * 3),256, 256), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10,player_textures['player'].width/10, player_textures['player'].height/10), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)
                    if 45 < player['angle'] <= 135:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),(256 * 1),256, 256), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10,player_textures['player'].width/10, player_textures['player'].height/10), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)
                    if player['angle'] <= -135 or player['angle'] > 135:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),(256 * 2),256, 256), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10,player_textures['player'].width/10, player_textures['player'].height/10), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)
                else:
                    if -135 < player['angle'] <= -45:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle(0,0,256, 256), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10,player_textures['player'].width/10, player_textures['player'].height/10), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)
                    if -45 < player['angle'] <= 45:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle(0,(256 * 3),256, 256), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10,player_textures['player'].width/10, player_textures['player'].height/10), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)
                    if 45 < player['angle'] <= 135:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle(0,(256 * 1),256, 256), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10,player_textures['player'].width/10, player_textures['player'].height/10), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)
                    if player['angle'] <= -135 or player['angle'] > 135:
                        rl.draw_texture_pro(player_textures['player'], rl.Rectangle(0,(256 * 2),256, 256), 
                                            rl.Rectangle(player['x'] - 31,player['y'] - 10,player_textures['player'].width/10, player_textures['player'].height/10), 
                                            rl.Vector2(0,0),
                                            0.0, 
                                            rl.WHITE)

        except KeyError as e:
            print("Error Occurred in draw_players: ", e)

def draw_npcs(shared_memory, npc):
    for key, value in shared_memory['npcs'][0].items():
        try:
            rl.draw_texture_pro(npc,rl.Rectangle(0,0,npc.width, npc.height), rl.Rectangle(value.x,value.y,npc.width + 20, npc.height + 20), rl.Vector2(0,0), 0.0, rl.WHITE)
            
        except (KeyError) as e:
            print("Error: ", e)

def draw_info(player):
    # rl.draw_text(f"fps: {1 / (raylib.GetFrameTime() + .00000000001)}", 50, 100, 40, rl.BLACK)
    # rl.draw_text(f"X: {player.locsize.x // TILE_SIZE}, Y: {player.locsize.y // TILE_SIZE}", 50, 50, 40, rl.BLACK)
    # rl.draw_text(f"X: {player.locsize.x}, Y: {player.locsize.y}", 50, 50, 40, rl.BLACK)
    # rl.draw_text(f"C X: {player.locsize.x // (TILE_SIZE * CHUNK_SIZE)}, C Y: {player.locsize.y // (TILE_SIZE * CHUNK_SIZE)}", 50, 150, 40, rl.BLACK)
    
    # rl.draw_text(f"health: {player.stats['hlth']}", 20, 20, 20, rl.RED)
    # rl.draw_text(f"damage: {player.stats['dmg']}", 20, 40, 20, rl.BLACK)
    # rl.draw_text(f"armor: {player.stats['arm']}", 20, 60, 20, rl.GRAY)
    # rl.draw_text(f"regen: {player.stats['regens'] / 60} sec", 20, 80, 20, rl.GREEN)
    # rl.draw_text(f"magic: {player.stats['arm']}", 20, 100, 20, rl.BLUE)
    ...

