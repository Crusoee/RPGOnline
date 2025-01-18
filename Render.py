import pyray as rl
import raylib as raylib
from CONSTANTS import NUM_CHUNKS, CHUNK_SIZE, TILE_SIZE, PLAYER_HEIGHT, PLAYER_WIDTH, SCREEN_WIDTH
from Generation import generate_terrain_chunk, generate_palms, generate_collision_chunk, get_tile_texture, sand
import math

class Render:

    def __init__(self, player, tile_textures, palm_textures, player_textures, npc_textures, cursor_texture, menu, window_size):
        self.menu = menu
        self.cursor_texture = cursor_texture
        self.window_size = window_size
        self.player = player
        self.tile_textures = tile_textures
        self.palm_textures = palm_textures
        self.player_textures = player_textures
        self.npc_textures = npc_textures
        self.chunk_data = {}

        self.zoom = 1.3
        self.camera = rl.Camera2D(
            rl.Vector2(window_size[0]/2 - PLAYER_WIDTH/2, window_size[1]/2),  # Offset from the center of the screen
            rl.Vector2(self.player.updates['x'], self.player.updates['y']),      # The target position in the world
            0.0,                   # Camera rotation in degrees
            self.zoom                    # Camera zoom (1.0 is default)
        )

        self.all_players = [player]

    def draw_tiles(self):
        # Calculate player's chunk position
        player_chunk_x = self.player.updates['x'] // (CHUNK_SIZE * TILE_SIZE)
        player_chunk_y = self.player.updates['y'] // (CHUNK_SIZE * TILE_SIZE)

        # Determine visible chunk range
        chunk_x_start = player_chunk_x - NUM_CHUNKS // 2
        chunk_y_start = player_chunk_y - NUM_CHUNKS // 2
        chunk_x_end = chunk_x_start + NUM_CHUNKS
        chunk_y_end = chunk_y_start + NUM_CHUNKS

        # Loop through visible chunks
        for chunk_y in range(int(chunk_y_start), int(chunk_y_end)):
            for chunk_x in range(int(chunk_x_start), int(chunk_x_end)):
                # Generate chunk if not already cached
                if (chunk_x, chunk_y) not in self.chunk_data:
                    terrain_data = generate_terrain_chunk(chunk_x, chunk_y)
                    collision_data = generate_collision_chunk(terrain_data, chunk_x, chunk_y)
                    palm_data = generate_palms(chunk_x, chunk_y)
                    # print(collision_data, chunk_x, chunk_y)
                    self.chunk_data[chunk_x, chunk_y] = [terrain_data,collision_data, palm_data]

                # Draw tiles in the chunk
                for y in range(CHUNK_SIZE):
                    for x in range(CHUNK_SIZE):
                        tile_type = self.chunk_data[chunk_x, chunk_y][0][y][x]
                        tile_texture = get_tile_texture(tile_type, self.tile_textures)
                        tile_draw_x = (chunk_x * CHUNK_SIZE + x) * TILE_SIZE
                        tile_draw_y = (chunk_y * CHUNK_SIZE + y) * TILE_SIZE
                        rl.draw_texture(tile_texture, tile_draw_x, tile_draw_y, rl.WHITE)

        for chunk_y in range(int(chunk_y_start), int(chunk_y_end)):
            for chunk_x in range(int(chunk_x_start), int(chunk_x_end)):

                for palm in self.chunk_data[chunk_x, chunk_y][2]:
                    rl.draw_texture_pro(self.palm_textures, rl.Rectangle(0,0,self.palm_textures.width * palm[2], self.palm_textures.height), 
                                        rl.Rectangle(palm[0],palm[1],self.palm_textures.width * 2 * palm[3], self.palm_textures.height * 2 * palm[3]), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)

    def draw_players(self, shared_memory):
        for key, value in shared_memory['playersupdate'][0].items():
            if key == shared_memory['user']:
                continue

            try:
                player = shared_memory['playersupdate'][0][key]
                text_size = rl.measure_text_ex(self.player_textures["name_font"], player['nme'], 30, 0.0)
                rl.draw_text_ex(self.player_textures["name_font"], player['nme'], rl.Vector2(int(player['x'] - (text_size.x / 2)  + PLAYER_WIDTH / 2), int(player['y'] - 80)), 40, 0.0, rl.BLACK)
                
                # Ensure health ratio is clamped between 0 and 1
                health_ratio = max(0, min(1, shared_memory['playersinfo'][0][key]['hlth'] / shared_memory['playersinfo'][0][key]['mhlth']))
                # Calculate base position for the health bar
                base_x = int(player['x'] - 40 + PLAYER_WIDTH // 2)
                base_y = int(player['y'] - 40)
                # # Draw the health bar
                # rl.draw_rectangle(base_x, base_y, 80, 20, rl.RED)  # Background
                # rl.draw_rectangle(base_x, base_y, int(80 * health_ratio), 20, rl.GREEN)  # Health bar

                rl.draw_texture_pro(self.player_textures["healthframe"], rl.Rectangle(0,0,self.player_textures["healthframe"].width, self.player_textures["healthframe"].height), 
                            rl.Rectangle(base_x, base_y, 80, 20), 
                            rl.Vector2(0,0),
                            0.0, 
                            rl.WHITE)
                rl.draw_texture_pro(self.player_textures["healthbar"], rl.Rectangle(0,0,self.player_textures["healthbar"].width * health_ratio, self.player_textures["healthbar"].height), 
                            rl.Rectangle(base_x, base_y, 80 * health_ratio, 20), 
                            rl.Vector2(0,0),
                            0.0, 
                            rl.WHITE)

                if player['swim'] == True:
                    if player['ismoving']:
                        if -135 < player['angle'] <= -45:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),0,256, 150), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,self.player_textures['player'].width/10, self.player_textures['player'].height/10 - 47), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)
                        if -45 < player['angle'] <= 45:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),(256 * 3),256, 150), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,self.player_textures['player'].width/10, self.player_textures['player'].height/10 - 47), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)
                        if 45 < player['angle'] <= 135:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),(256 * 1),256, 150), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,self.player_textures['player'].width/10, self.player_textures['player'].height/10 - 47), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)
                        if player['angle'] <= -135 or player['angle'] > 135:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),(256 * 2),256, 150), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,self.player_textures['player'].width/10, self.player_textures['player'].height/10 - 47), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)
                    else:
                        if -135 < player['angle'] <= -45:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle((0),0,256, 150), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,self.player_textures['player'].width/10, self.player_textures['player'].height/10 - 47), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)
                        if -45 < player['angle'] <= 45:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle((0),(256 * 3),256, 150), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,self.player_textures['player'].width/10, self.player_textures['player'].height/10 - 47), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)
                        if 45 < player['angle'] <= 135:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle((0),(256 * 1),256, 150), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,self.player_textures['player'].width/10, self.player_textures['player'].height/10 - 47), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)
                        if player['angle'] <= -135 or player['angle'] > 135:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle((0),(256 * 2),256, 150), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10 + 34,self.player_textures['player'].width/10, self.player_textures['player'].height/10 - 47), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)
                else:
                    if player['ismoving']:
                        if -135 < player['angle'] <= -45:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),0,256, 256), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10,self.player_textures['player'].width/10, self.player_textures['player'].height/10), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)
                        if -45 < player['angle'] <= 45:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),(256 * 3),256, 256), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10,self.player_textures['player'].width/10, self.player_textures['player'].height/10), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)
                        if 45 < player['angle'] <= 135:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),(256 * 1),256, 256), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10,self.player_textures['player'].width/10, self.player_textures['player'].height/10), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)
                        if player['angle'] <= -135 or player['angle'] > 135:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle((256 * math.floor(player['animcntr'])),(256 * 2),256, 256), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10,self.player_textures['player'].width/10, self.player_textures['player'].height/10), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)
                    else:
                        if -135 < player['angle'] <= -45:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle(0,0,256, 256), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10,self.player_textures['player'].width/10, self.player_textures['player'].height/10), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)
                        if -45 < player['angle'] <= 45:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle(0,(256 * 3),256, 256), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10,self.player_textures['player'].width/10, self.player_textures['player'].height/10), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)
                        if 45 < player['angle'] <= 135:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle(0,(256 * 1),256, 256), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10,self.player_textures['player'].width/10, self.player_textures['player'].height/10), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)
                        if player['angle'] <= -135 or player['angle'] > 135:
                            rl.draw_texture_pro(self.player_textures['player'], rl.Rectangle(0,(256 * 2),256, 256), 
                                                rl.Rectangle(player['x'] - 31,player['y'] - 10,self.player_textures['player'].width/10, self.player_textures['player'].height/10), 
                                                rl.Vector2(0,0),
                                                0.0, 
                                                rl.WHITE)

            except KeyError as e:
                print("Error Occurred in draw_players: ", e)

    def draw_npcs(self, shared_memory):
        for key, value in shared_memory['npcs'][0].items():
            try:
                rl.draw_texture_pro(self.npc_textures,rl.Rectangle(0,0,self.npc_textures.width, self.npc_textures.height), rl.Rectangle(value.x,value.y,self.npc_textures.width + 20, self.npc_textures.height + 20), rl.Vector2(0,0), 0.0, rl.WHITE)
                
            except (KeyError) as e:
                print("Error: ", e)

    def draw_call(self, shared_memory, player_manager):

        raylib.BeginDrawing()
        raylib.ClearBackground(rl.RAYWHITE)
        raylib.BeginMode2D(self.camera)

        self.draw_tiles()

        self.draw_npcs(shared_memory)

        for name, player in player_manager.items():
            player.draw(self.player_textures)

        # self.draw_players(shared_memory)

        # self.player.draw(self.player_textures)

        raylib.EndMode2D()

        # 105 fps
        rl.draw_text(f"fps: {1 / (raylib.GetFrameTime() + .00000000001)}", self.window_size[0] - 180, 50, 40, rl.BLACK)
        rl.draw_text(f"X: {self.player.updates['x'] // TILE_SIZE}, Y: {self.player.updates['x'] // TILE_SIZE}", self.window_size[0] - 200, 100, 30, rl.BLACK)

        self.menu.render(self.player)

        rl.draw_texture_pro(self.cursor_texture, rl.Rectangle(0,0,self.cursor_texture.width, self.cursor_texture.height), 
                            rl.Rectangle(rl.get_mouse_position().x,rl.get_mouse_position().y,self.cursor_texture.width + 20, self.cursor_texture.height + 20), 
                            rl.Vector2(0,0),
                            0.0, 
                            rl.WHITE)
        
        
        raylib.EndDrawing()

