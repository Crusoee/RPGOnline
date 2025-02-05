import pyray as rl
import raylib as raylib
from Misc.CONSTANTS import NUM_CHUNKS, CHUNK_SIZE, TILE_SIZE, PLAYER_HEIGHT, PLAYER_WIDTH, SCREEN_WIDTH
from Generation.Generation import generate_terrain_chunk, generate_palms, generate_collision_chunk, get_tile_texture, sand
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

        self.zoom = 1.7
        self.camera = rl.Camera2D(
            rl.Vector2(window_size[0]/2 - PLAYER_WIDTH/2, window_size[1]/2),  # Offset from the center of the screen
            rl.Vector2(self.player.updates['x'] - self.player.base.x, self.player.updates['y'] + PLAYER_HEIGHT // 2),      # The target position in the world
            0.0,                   # Camera rotation in degrees
            self.zoom                    # Camera zoom (1.0 is default)
        )

        self.all_players = [player]

    def center_camera(self):
        self.camera.target = rl.Vector2(self.player.updates['x'] - self.player.base.x, self.player.updates['y'] + PLAYER_HEIGHT // 2)

    def draw_tiles(self, all_players):
        # Calculate player's chunk position
        player_chunk_x = int((self.player.updates['x'] - self.player.base.x) // (TILE_SIZE * CHUNK_SIZE))
        player_chunk_y = int((self.player.updates['y'] - self.player.base.y) // (TILE_SIZE * CHUNK_SIZE))

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

        self.chunk_data = dict(sorted(self.chunk_data.items(), key=lambda item: item[0][1]))

        skip_chunk_left = int((self.player.updates['x'] - self.player.base.x) // (TILE_SIZE * CHUNK_SIZE)) -1
        skip_chunk_right = int((self.player.updates['x'] - self.player.base.x) // (TILE_SIZE * CHUNK_SIZE)) +1

        for chunk_y in range(int(chunk_y_start), int(chunk_y_end)):
            for chunk_x in range(int(chunk_x_start), int(chunk_x_end)):
                if (chunk_x == skip_chunk_left or chunk_x == skip_chunk_right) and chunk_y == player_chunk_y:
                    continue
                elif chunk_x == player_chunk_x and chunk_y == player_chunk_y:
                    chunk_objects = list(all_players.values()) + self.chunk_data[chunk_x, chunk_y][2] + self.chunk_data[skip_chunk_left, chunk_y][2] + self.chunk_data[skip_chunk_right, chunk_y][2]
                else:
                    chunk_objects = self.chunk_data[chunk_x, chunk_y][2]

                chunk_objects.sort(key=lambda item: item.updates['y'])

                for object in chunk_objects:
                    if 'direction' in object.updates.keys():
                        object.draw(self.palm_textures)
                    else:
                        object.draw()

    def draw_npcs(self, shared_memory):
        for key, value in shared_memory['npcs'][0].items():
            try:
                rl.draw_texture_pro(self.npc_textures,rl.Rectangle(0,0,self.npc_textures.width, self.npc_textures.height), rl.Rectangle(value.x,value.y,self.npc_textures.width + 20, self.npc_textures.height + 20), rl.Vector2(0,0), 0.0, rl.WHITE)
                
            except (KeyError) as e:
                print("Error: ", e)

    def draw_highlight(self):
        if self.player.updates['coord'] != None:
            # raylib.DrawCircle(int(self.coordinate.x), int(self.coordinate.y), 5.0, rl.YELLOW)
            # rl.draw_texture(textures["click"],int(self.coordinate.x), int(self.coordinate.y),rl.YELLOW)
            shrink_factor = 0.2  # For example, shrink to 50% of original size

            # Calculate new width and height after shrinking
            new_width = self.player_textures["click"].width * shrink_factor
            new_height = self.player_textures["click"].height * shrink_factor

            # Center the destination rectangle
            rl.draw_texture_pro(
                self.player_textures["click"], 
                rl.Rectangle(0, 0, self.player_textures["click"].width, self.player_textures["click"].height),  # Full source rectangle
                rl.Rectangle(
                    int(self.player.updates['coord'][0]) - new_width / 2, 
                    int(self.player.updates['coord'][1]) - new_height / 2, 
                    new_width, 
                    new_height
                ), 
                rl.Vector2(0, 0),  # Origin for rotation
                0.0, 
                rl.Color(255,255,255,255)
            )

    def draw_call(self, shared_memory, all_players):

        raylib.BeginDrawing()
        raylib.ClearBackground(rl.RAYWHITE)
        raylib.BeginMode2D(self.camera)

        self.draw_npcs(shared_memory)

        self.draw_tiles(all_players)

        self.draw_highlight()

        # for name, player in all_players.items():
        #     player.draw(self.player_textures)

        raylib.EndMode2D()

        # 105 fps
        rl.draw_text(f"fps: {1 / (raylib.GetFrameTime() + .00000000001)}", self.window_size[0] - 180, 50, 40, rl.BLACK)
        rl.draw_text(f"X: {self.player.updates['x'] // TILE_SIZE}, Y: {self.player.updates['y'] // TILE_SIZE}", self.window_size[0] - 300, 100, 30, rl.BLACK)

        self.menu.render(self.player)

        rl.draw_texture_pro(self.cursor_texture, rl.Rectangle(0,0,self.cursor_texture.width, self.cursor_texture.height), 
                            rl.Rectangle(rl.get_mouse_position().x,rl.get_mouse_position().y,self.cursor_texture.width + 20, self.cursor_texture.height + 20), 
                            rl.Vector2(0,0),
                            0.0, 
                            rl.WHITE)
        
        
        raylib.EndDrawing()

