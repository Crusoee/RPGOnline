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
                            'dmg' : 1,
                            'mgc' : 0,
                            'arm' : 0,
                            'hlth' : 10,
                            'hit' : '',
                            'speed' : 300,
                            'swmspeed' : 150
                        }
        
        self.distance = 50
        self.tracking_distance = 1000
        
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
            rl.Vector2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2),  # Offset from the center of the screen
            rl.Vector2(self.locsize.x, self.locsize.y),      # The target position in the world
            0.0,                   # Camera rotation in degrees
            1.0                    # Camera zoom (1.0 is default)
        )

    def draw(self):

        # raylib.DrawRectangleRec(self.prev_locsize, rl.BROWN)
        if self.in_water:
            raylib.DrawRectangleRec(rl.Rectangle(self.locsize.x,self.locsize.y + PLAYER_HEIGHT / 2,PLAYER_WIDTH,PLAYER_HEIGHT / 2), self.color)
        else:
            raylib.DrawRectangleRec(self.locsize, self.color)

        if self.coordinate != None and self.attacking == False:
            raylib.DrawCircle(int(self.coordinate.x), int(self.coordinate.y), 5.0, rl.YELLOW)

        rl.draw_text(self.name, int(self.locsize.x - (len(self.name) // 2)), int(self.locsize.y - 20), 20, rl.GREEN)

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

        self.prev_locsize = rl.Vector2(self.locsize.x - self.base.x, self.locsize.y - self.base.y)
        
        # If your health is 0, respawn: NEEDS TO BE EXPOUNDED
        if self.stats['hlth'] <= 0:
            self.locsize.x = self.respawn.x
            self.locsize.y = self.respawn.y

        # The current noise level your character is standing on
        value = simplex_noise((self.locsize.x - self.base.x) // TILE_SIZE, 
                        (self.locsize.y - self.base.y) // TILE_SIZE)

        # Changing the speed of your player
        if value < Render.water:
            self.speed = self.stats['swmspeed']
            self.in_water = True
        else:
            self.speed = self.stats['speed']
            self.in_water = False

        # If there's a target, follow it
        if self.action['target'] and self.action['target'] in shared_memory['playersupdate'][0].keys():
            player = shared_memory['playersupdate'][0][self.action['target']]
            self.action['type'] = None
            self.attacking = True
            target_distance = distance(self.locsize.x,self.locsize.y, player['x'],player['y'])
            if target_distance < self.distance:
                self.action['type'] = 'attack'
                self.coordinate = None
            elif target_distance > self.tracking_distance:
                self.action = EMPTY
                self.attacking = False
            else:
                self.action['type'] = None
                self.coordinate = rl.Vector2(player['x'] - self.base.x, 
                                            player['y'] - self.base.y)
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

            for key, value in shared_memory['playersupdate'][0].items():
                if key == shared_memory['user']:
                    continue

                player = shared_memory['playersupdate'][0][key]

                if raylib.CheckCollisionPointRec(select_coordinate, select_player(player)):
                    print(f'{player['hlth']}, {player['dmg']}, {player['mgc']}, {player['arm']}')

    def attack_reset(self):
        self.attacking = False
        self.hit = ''

    def update(self, shared_memory):
        # If my user name that the server recognizes my client as, has my stats in its player database, give me those stats
        if shared_memory['user'] in shared_memory['playersinfo'][0].keys():
            stats = shared_memory['playersinfo'][0][shared_memory['user']]

            self.stats['hlth'] = stats['hlth']
            self.stats['dmg'] = stats['dmg']
            self.stats['mgc'] = stats['mgc']
            self.stats['arm'] = stats['arm']
            self.stats['speed'] = stats['speed']
            self.stats['swmspeed'] = stats['swmspeed']