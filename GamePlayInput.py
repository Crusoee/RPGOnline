import raylib
import pyray as rl
import math

from Generation import simplex_noise
from CONSTANTS import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, CHUNK_SIZE, PLAYER_HEIGHT, PLAYER_WIDTH
import Generation
from Helper import select_player, distance

EMPTY = {
            'type' : None,
            'target' :None,
            'x' : None,
            'y' : None,
        }

class GamePlayInput():
    def __init__(self, player, camera):
        self.player = player
        self.camera = camera

        self.attacking = False
        self.speed = player.stats['speed'] * player.stats['hinderedspeedmult']

    def collision(self, collidable_objects):
        for object in collidable_objects:
            if raylib.CheckCollisionPointRec(rl.Vector2(self.player.updates['x'] - self.player.base.x,self.player.updates['y'] - self.player.base.y), object):
                # Left
                if self.player.prev_locsize.x <= object.x:
                    self.player.updates['x'] = object.x + self.player.base.x
                # Right
                if self.player.prev_locsize.x >= object.x + object.width:
                    self.player.updates['x'] = object.x + object.width + self.player.base.x
                # Top
                if self.player.prev_locsize.y <= object.y:
                    self.player.updates['y'] = object.y + self.player.base.y
                # Bottom
                if self.player.prev_locsize.y >= object.y + object.height:
                    self.player.updates['y'] = object.y + object.height + self.player.base.y

    def move(self, chunk_data, shared_memory):

        # Getting players previous location
        self.player.prev_locsize = rl.Vector2(self.player.updates['x'] - self.player.base.x, self.player.updates['y'] - self.player.base.y)
        
        # If your health is 0, respawn: NEEDS TO BE EXPOUNDED
        if self.player.stats['hlth'] <= 0:
            self.player.updates['x'] = self.respawn.x
            self.player.updates['y'] = self.respawn.y

        # The current noise level your character is standing on
        value = simplex_noise((self.player.updates['x'] - self.player.base.x) // TILE_SIZE, 
                        (self.player.updates['y'] - self.player.base.y) // TILE_SIZE)

        # Changing the speed of your player depending on what terrain their standing on
        if value < Generation.water:
            self.speed = self.player.stats['swmspeed'] * self.player.stats['hinderedspeedmult']
            self.player.updates['swim'] = True
        else:
            self.speed = self.player.stats['speed'] * self.player.stats['hinderedspeedmult']
            self.player.updates['swim'] = False

        # If there's a player target, follow it
        if self.player.updates['action']['target'] in shared_memory['playersupdate'][0].keys():
            player = shared_memory['playersupdate'][0][self.player.updates['action']['target']]
            self.player.updates['action']['type'] = None
            self.attacking = True
            target_distance = distance(self.player.updates['x'],self.player.updates['y'], player['x'],player['y'])
            if target_distance < self.player.stats['attackingdist']:
                self.player.updates['action']['type'] = 'attack'
                self.player.coordinate = None
            elif target_distance > self.player.stats['trackingdist']:
                self.player.updates['action'] = EMPTY
                self.attacking = False
            else:
                self.player.updates['action']['type'] = None
                self.player.coordinate = rl.Vector2(player['x'] - self.player.base.x, 
                                            player['y'] - self.player.base.y)
        # If there's an NPC target, follow it
        elif self.player.updates['action']['target'] in shared_memory['npcs'][0].keys():
            self.player.updates['action']['type'] = None
            self.attacking = True
            target_distance = distance(self.player.updates['x'],self.player.updates['y'], self.player.updates['action']['x'],self.player.updates['action']['y'])
            if target_distance < self.player.stats['attackingdist']:
                self.player.updates['action']['type'] = 'attacknpc'
                self.player.coordinate = None
            elif target_distance > self.player.stats['trackingdist']:
                self.player.updates['action'] = EMPTY
                self.attacking = False
            else:
                self.player.updates['action']['type'] = None
                self.player.coordinate = rl.Vector2(self.player.updates['action']['x'] + shared_memory['npcs'][0][self.player.updates['action']['target']].size // 2,self.player.updates['action']['y'] + shared_memory['npcs'][0][self.player.updates['action']['target']].size // 2)            
        else:
            self.player.updates['action'] = EMPTY


        # If you press the right mouse button, set coordinate to that location to move
        if raylib.IsMouseButtonDown(raylib.MOUSE_BUTTON_RIGHT) and not self.player.updates['action']['target']:
            mouse_position_window = rl.get_mouse_position()
            self.player.coordinate = rl.Vector2(
                (mouse_position_window.x - self.camera.offset.x) / self.camera.zoom + self.camera.target.x,
                (mouse_position_window.y - self.camera.offset.y) / self.camera.zoom + self.camera.target.y
            )
        
        # moving depending on if there is a coordinate to follow
        if self.player.coordinate != None and self.player.updates['canmove']:
            self.player.is_moving = True
            displaced = rl.Vector2(self.player.coordinate.x - self.player.updates['x'] + self.player.base.x, self.player.coordinate.y - self.player.updates['y'] + self.player.base.y)
            length = math.sqrt(displaced.x**2 + displaced.y**2)
            if length != 0:
                dir_vec = rl.Vector2(displaced.x / length, displaced.y / length)
                self.player.updates['x'] += dir_vec.x * self.speed * raylib.GetFrameTime()
                self.player.updates['y'] += dir_vec.y * self.speed * raylib.GetFrameTime()
                if length < 150.0 * raylib.GetFrameTime():
                    self.player.coordinate = None
        else:
            self.player.is_moving = False


        if raylib.IsKeyPressed(raylib.KEY_V):
            self.player.respawn.x = self.player.updates['x']
            self.player.respawn.y = self.player.updates['y']

        self.camera.target.x = self.player.updates['x']
        self.camera.target.y = self.player.updates['y']

        # self.player.collision(chunk_data[int((self.player.updates['x'] - self.player.base.x) // (TILE_SIZE * CHUNK_SIZE)), int((self.player.updates['y'] - self.player.base.y) // (TILE_SIZE * CHUNK_SIZE))][1])

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
                    self.player.updates['action']['target'] = key
                    return
                
            for key, value in shared_memory['npcs'][0].items():
                npc = shared_memory['npcs'][0][key]
                if raylib.CheckCollisionPointRec(select_coordinate, rl.Rectangle(npc.x,npc.y,npc.size,npc.size)):
                    self.player.updates['action']['target'] = f"{npc.x}{npc.y}"
                    self.player.updates['action']['x'] = npc.x
                    self.player.updates['action']['y'] = npc.y
                    return
            
            self.attacking = False
            self.player.updates['action']['type'] = None
            self.player.updates['action']['target'] = None
            self.player.updates['action']['x'] = None
            self.player.updates['action']['y'] = None

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

    def GamePlayInput_call(self):
        ...