import raylib
import pyray as rl
import math
from Helper import select_player, distance

from SimplexNoise import simplex_noise
import Render
from CONSTANTS import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, CHUNK_SIZE, PLAYER_HEIGHT, PLAYER_WIDTH

EMPTY = {
            'type' : None,
            'target' :None,
            'x' : None,
            'y' : None,
        }

class Player():
    def __init__(self, color, locsize, speed, name):

        self.name = name

        self.respawn = rl.Vector2(locsize.x,locsize.y)

        self.action = {
                'type' : None,
                'target' :None,
                'x' : None,
                'y' : None,
            }
        
        self.stats =    {  
                'dmg' : 10,
                'lifesteal' : 0,
                'poison' : 0,

                'crit' : 1.1,
                'chance' : 50,

                'mgcdamage' : 0,
                'maxmgc' : 500,
                'mgc' : 500,
                'mgcregen' : 120,
                'mgcregenbonus' : 1,
                'mgcctnr' : 0,
                'mgcheal' : 5,
                'mgcburn' : 0.1,

                'arm' : 0,
                'thorns' : 0,

                'hlth' : 100,
                'mhlth' : 100,
                'regens' : 120,
                'regencntr' : 0,
                'regenbonus' : 1,

                # 'hit' : '',

                'atc' : 60,
                'ats' : 60,

                'ress' : 600,
                'rescntr' : 0,

                'speed' : 200,
                'swmspeed' : 100,

                'killcount' : 0,

                'attackingdist' : 50,
                'trackingdist' : 1000,

                'maxenergy' : 600,
                'energy' : 600,
                'energyregen' : 120,
                'energyregenbonus' : 1,
                'energycntr' : 0,
            }
        
        # self.distance = 50
        # self.tracking_distance = 1000
        
        self.attacking = False
        self.can_move = True
        self.in_water = False

        self.speed = speed
        self.color = color

        self.locsize = locsize

        self.base = rl.Vector2(-int(locsize.width / 2), -locsize.height)
        self.coordinate = None

        self.prev_locsize = rl.Vector2(locsize.x - self.base.x,locsize.y - self.base.y)

        self.camera = rl.Camera2D(
            rl.Vector2(SCREEN_WIDTH/2 - self.locsize.width/2, SCREEN_HEIGHT/2),  # Offset from the center of the screen
            rl.Vector2(self.locsize.x, self.locsize.y),      # The target position in the world
            0.0,                   # Camera rotation in degrees
            1.0                    # Camera zoom (1.0 is default)
        )

    def draw(self, textures, player_shaders):


        if self.coordinate != None and self.attacking == False:
            # raylib.DrawCircle(int(self.coordinate.x), int(self.coordinate.y), 5.0, rl.YELLOW)
            # rl.draw_texture(textures["click"],int(self.coordinate.x), int(self.coordinate.y),rl.YELLOW)
            shrink_factor = 0.2  # For example, shrink to 50% of original size

            # Calculate new width and height after shrinking
            new_width = textures["click"].width * shrink_factor
            new_height = textures["click"].height * shrink_factor

            # Center the destination rectangle
            rl.draw_texture_pro(
                textures["click"], 
                rl.Rectangle(0, 0, textures["click"].width, textures["click"].height),  # Full source rectangle
                rl.Rectangle(
                    int(self.coordinate.x) - new_width / 2, 
                    int(self.coordinate.y) - new_height / 2, 
                    new_width, 
                    new_height
                ), 
                rl.Vector2(0, 0),  # Origin for rotation
                0.0, 
                rl.Color(255,255,255,255)
            )

        # raylib.DrawRectangleRec(self.prev_locsize, rl.BROWN)
        if self.in_water:
            raylib.DrawRectangleRec(rl.Rectangle(self.locsize.x,self.locsize.y + PLAYER_HEIGHT / 2,PLAYER_WIDTH,PLAYER_HEIGHT / 2), self.color)
        else:
            raylib.DrawRectangleRec(self.locsize, self.color)


        # rl.begin_shader_mode(player_shaders['invert_text'])

        text_size = rl.measure_text_ex(textures["name_font"], self.name, 30, 0.0)
        rl.draw_text_ex(textures["name_font"], self.name, rl.Vector2(int(self.locsize.x - (text_size.x / 2) + PLAYER_WIDTH / 2), int(self.locsize.y - 80)), 40, 0.0, rl.BLACK)

        # Ensure health ratio is clamped between 0 and 1
        health_ratio = max(0, min(1, self.stats['hlth'] / self.stats['mhlth']))
        energy_ratio = max(0, min(1, self.stats['energy'] / self.stats['maxenergy']))
        magic_ratio = max(0, min(1, self.stats['mgc'] / self.stats['maxmgc']))
        # Calculate base position for the health bar
        base_x = int(self.locsize.x  - 40 + PLAYER_WIDTH // 2)
        base_y = int(self.locsize.y  - 40)
        # Draw the health bar
        # rl.draw_rectangle(base_x, base_y, 80, 20, rl.RED)  # Background
        # rl.draw_rectangle(base_x, base_y, int(80 * health_ratio), 20, rl.GREEN)  # Health bar

        rl.draw_texture_pro(textures["healthframe"], rl.Rectangle(0,0,textures["healthframe"].width, textures["healthframe"].height), 
                    rl.Rectangle(base_x, base_y, 80, 20), 
                    rl.Vector2(0,0),
                    0.0, 
                    rl.WHITE)
        rl.draw_texture_pro(textures["healthbar"], rl.Rectangle(0,0,textures["healthbar"].width * health_ratio, textures["healthbar"].height), 
                    rl.Rectangle(base_x, base_y, 80 * health_ratio, 20), 
                    rl.Vector2(0,0),
                    0.0, 
                    rl.WHITE)
        rl.draw_texture_pro(textures["Energybar"], rl.Rectangle(0,0,textures["Energybar"].width * energy_ratio, textures["Energybar"].height), 
                    rl.Rectangle(base_x, base_y + 15, 80 * energy_ratio, 10), 
                    rl.Vector2(0,0),
                    0.0, 
                    rl.WHITE)
        rl.draw_texture_pro(textures["Magicbar"], rl.Rectangle(0,0,textures["Magicbar"].width * magic_ratio, textures["Magicbar"].height), 
                    rl.Rectangle(base_x, base_y + 20, 80 * magic_ratio, 10), 
                    rl.Vector2(0,0),
                    0.0, 
                    rl.WHITE)

        # rl.end_shader_mode()

        # if self.attacking == True:
        #     rl.draw_circle(int(self.locsize.x - self.base.x),int(self.locsize.y - self.base.y / 2),self.distance,rl.Color(255,255,0,100))


    def collision(self, collidable_objects):
        for object in collidable_objects:
            if raylib.CheckCollisionPointRec(rl.Vector2(self.locsize.x - self.base.x,self.locsize.y - self.base.y), object):

                # Left
                if self.prev_locsize.x <= object.x:
                    self.locsize.x = object.x + self.base.x
                # Right
                if self.prev_locsize.x >= object.x + object.width:
                    self.locsize.x = object.x + object.width + self.base.x
                # Top
                if self.prev_locsize.y <= object.y:
                    self.locsize.y = object.y + self.base.y
                # Bottom
                if self.prev_locsize.y >= object.y + object.height:
                    self.locsize.y = object.y + object.height + self.base.y

    def move(self, chunk_data, shared_memory):

        # Getting players previous location
        self.prev_locsize = rl.Vector2(self.locsize.x - self.base.x, self.locsize.y - self.base.y)
        
        # If your health is 0, respawn: NEEDS TO BE EXPOUNDED
        if self.stats['hlth'] <= 0:
            self.locsize.x = self.respawn.x
            self.locsize.y = self.respawn.y

        # The current noise level your character is standing on
        value = simplex_noise((self.locsize.x - self.base.x) // TILE_SIZE, 
                        (self.locsize.y - self.base.y) // TILE_SIZE)

        # Changing the speed of your player depending on what terrain their standing on
        if value < Render.water:
            self.speed = self.stats['swmspeed']
            self.in_water = True
        else:
            self.speed = self.stats['speed']
            self.in_water = False

        # If there's a player target, follow it
        if self.action['target'] in shared_memory['playersupdate'][0].keys():
            player = shared_memory['playersupdate'][0][self.action['target']]
            self.action['type'] = None
            self.attacking = True
            target_distance = distance(self.locsize.x,self.locsize.y, player['x'],player['y'])
            if target_distance < self.stats['attackingdist']:
                self.action['type'] = 'attack'
                self.coordinate = None
            elif target_distance > self.stats['trackingdist']:
                self.action = EMPTY
                self.attacking = False
            else:
                self.action['type'] = None
                self.coordinate = rl.Vector2(player['x'] - self.base.x, 
                                            player['y'] - self.base.y)
        # If there's an NPC target, follow it
        elif self.action['target'] in shared_memory['npcs'][0].keys():
            self.action['type'] = None
            self.attacking = True
            target_distance = distance(self.locsize.x,self.locsize.y, self.action['x'],self.action['y'])
            if target_distance < self.stats['attackingdist']:
                self.action['type'] = 'attacknpc'
                self.coordinate = None
            elif target_distance > self.stats['trackingdist']:
                self.action = EMPTY
                self.attacking = False
            else:
                self.action['type'] = None
                self.coordinate = rl.Vector2(self.action['x'] + shared_memory['npcs'][0][self.action['target']].size // 2,self.action['y'] + shared_memory['npcs'][0][self.action['target']].size // 2)            
        else:
            self.action = EMPTY


        # If you press the right mouse button, set coordinate to that location to move
        if raylib.IsMouseButtonDown(raylib.MOUSE_BUTTON_RIGHT) and not self.action['target']:
            mouse_position_window = rl.get_mouse_position()
            self.coordinate = rl.Vector2(
                (mouse_position_window.x - self.camera.offset.x) / self.camera.zoom + self.camera.target.x,
                (mouse_position_window.y - self.camera.offset.y) / self.camera.zoom + self.camera.target.y
            )
        
        # moving depending on if there is a coordinate to follow
        if self.coordinate != None and self.can_move:
            displaced = rl.Vector2(self.coordinate.x - self.locsize.x + self.base.x, self.coordinate.y - self.locsize.y + self.base.y)
            length = math.sqrt(displaced.x**2 + displaced.y**2)
            if length != 0:
                dir_vec = rl.Vector2(displaced.x / length, displaced.y / length)
                self.locsize.x += dir_vec.x * self.speed * raylib.GetFrameTime()
                self.locsize.y += dir_vec.y * self.speed * raylib.GetFrameTime()
                if length < 150.0 * raylib.GetFrameTime():
                    self.coordinate = None


        if raylib.IsKeyPressed(raylib.KEY_V):
            self.respawn.x = self.locsize.x
            self.respawn.y = self.locsize.y

        self.camera.target.x = self.locsize.x
        self.camera.target.y = self.locsize.y

        self.collision(chunk_data[int((self.locsize.x - self.base.x) // (TILE_SIZE * CHUNK_SIZE)), int((self.locsize.y - self.base.y) // (TILE_SIZE * CHUNK_SIZE))][1])

    def select(self, shared_memory):

        if raylib.IsMouseButtonPressed(raylib.MOUSE_BUTTON_RIGHT):
            
            mouse_position_window = rl.get_mouse_position()
            select_coordinate = rl.Vector2(
                (mouse_position_window.x - self.camera.offset.x) / self.camera.zoom + self.camera.target.x,
                (mouse_position_window.y - self.camera.offset.y) / self.camera.zoom + self.camera.target.y
            )

            for key, value in shared_memory['playersupdate'][0].items():
                if key == shared_memory['user']:
                    continue

                player = shared_memory['playersupdate'][0][key]

                if raylib.CheckCollisionPointRec(select_coordinate, select_player(player)):
                    self.action['target'] = key
                    return
                
            for key, value in shared_memory['npcs'][0].items():
                npc = shared_memory['npcs'][0][key]
                if raylib.CheckCollisionPointRec(select_coordinate, rl.Rectangle(npc.x,npc.y,npc.size,npc.size)):
                    self.action['target'] = f"{npc.x}{npc.y}"
                    self.action['x'] = npc.x
                    self.action['y'] = npc.y
                    return
            
            self.attacking = False
            self.action['type'] = None
            self.action['target'] = None
            self.action['x'] = None
            self.action['y'] = None

        if raylib.IsMouseButtonPressed(raylib.MOUSE_BUTTON_LEFT):
            mouse_position_window = rl.get_mouse_position()
            select_coordinate = rl.Vector2(
                (mouse_position_window.x - self.camera.offset.x) / self.camera.zoom + self.camera.target.x,
                (mouse_position_window.y - self.camera.offset.y) / self.camera.zoom + self.camera.target.y
            )

            for key, value in shared_memory['playersinfo'][0].items():
                if key == shared_memory['user']:
                    continue

                player = shared_memory['playersinfo'][0][key]

                if raylib.CheckCollisionPointRec(select_coordinate, select_player(shared_memory['playersupdate'][0][key])):
                    print(player)

    def attack_reset(self):
        self.attacking = False
        self.hit = ''

    def update(self, shared_memory):
        # If my user name that the server recognizes my client as, has my stats in its player database, give me those stats
        if shared_memory['user'] in shared_memory['playersinfo'][0].keys():
            stats = shared_memory['playersinfo'][0][shared_memory['user']]

            self.stats = stats

            # self.stats['hlth'] = stats['hlth']
            # self.stats['dmg'] = stats['dmg']
            # self.stats['mgc'] = stats['mgc']
            # self.stats['arm'] = stats['arm']
            # self.stats['speed'] = stats['speed']
            # self.stats['swmspeed'] = stats['swmspeed']