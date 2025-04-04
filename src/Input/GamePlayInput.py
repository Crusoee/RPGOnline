import raylib
import pyray as rl
import math

from Generation.Generation import simplex_noise
from Misc.CONSTANTS import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, CHUNK_SIZE, PLAYER_HEIGHT, PLAYER_WIDTH
import Generation.Generation as Generation
from Misc.Helper import select_player, distance

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
            self.player.updates['x'] = self.player.respawn.x
            self.player.updates['y'] = self.player.respawn.y

        # If there's a player target, follow it
        if self.player.updates['action']['target'] in shared_memory['playersupdate'][0].keys():
            player = shared_memory['playersupdate'][0][self.player.updates['action']['target']]
            self.player.updates['action']['type'] = None
            self.attacking = True
            target_distance = distance(self.player.updates['x'],self.player.updates['y'], player['x'],player['y'])
            if target_distance < self.player.stats['attackingdist']:
                self.player.updates['action']['type'] = 'attack'
                # self.player.updates['coord'] = None
            elif target_distance > self.player.stats['trackingdist']:
                self.player.updates['action'] = EMPTY
                self.attacking = False
            else:
                self.player.updates['action']['type'] = None
                self.player.updates['coord'] = (player['x'] - self.player.base.x, 
                                            player['y'] - self.player.base.y)
        # If there's an NPC target, follow it
        elif self.player.updates['action']['target'] in shared_memory['npcs'][0].keys():
            self.player.updates['action']['type'] = None
            self.attacking = True
            target_distance = distance(self.player.updates['x'],self.player.updates['y'], self.player.updates['action']['x'],self.player.updates['action']['y'])
            if target_distance < self.player.stats['attackingdist']:
                self.player.updates['action']['type'] = 'attacknpc'
                # self.player.updates['coord'] = None
            elif target_distance > self.player.stats['trackingdist']:
                self.player.updates['action'] = EMPTY
                self.attacking = False
            else:
                self.player.updates['action']['type'] = None
                self.player.updates['coord'] = (self.player.updates['action']['x'] + shared_memory['npcs'][0][self.player.updates['action']['target']].size // 2,self.player.updates['action']['y'] + shared_memory['npcs'][0][self.player.updates['action']['target']].size // 2)            
        else:
            self.player.updates['action'] = EMPTY


        # If you press the right mouse button, set updates['coord'] to that location to move
        if raylib.IsMouseButtonDown(raylib.MOUSE_BUTTON_RIGHT) and not self.player.updates['action']['target']:
            # if self.player.updates['coord']:
            #     self.player.updates['angle'] = math.degrees(math.atan2(-(self.player.updates['coord'][1] - self.player.updates['y'] + self.player.base.y), (self.player.updates['coord'][0] - self.player.updates['x'] + self.player.base.x)))
            mouse_position_window = rl.get_mouse_position()
            self.player.updates['coord'] = (
                (mouse_position_window.x - self.camera.offset.x) / self.camera.zoom + self.camera.target.x,
                (mouse_position_window.y - self.camera.offset.y) / self.camera.zoom + self.camera.target.y
            )

        if raylib.IsKeyPressed(raylib.KEY_V):
            self.player.respawn.x = self.player.updates['x']
            self.player.respawn.y = self.player.updates['y']

        # self.collision(chunk_data[int((self.player.updates['x'] - self.player.base.x) // (TILE_SIZE * CHUNK_SIZE)), int((self.player.updates['y'] - self.player.base.y) // (TILE_SIZE * CHUNK_SIZE))][1])

    def select(self, shared_memory):

        if raylib.IsMouseButtonPressed(raylib.MOUSE_BUTTON_RIGHT):
            # if self.player.updates['coord']:
            #     self.player.updates['angle'] = math.degrees(math.atan2(-(self.player.updates['coord'][1] - self.player.updates['y'] + self.player.base.y), (self.player.updates['coord'][0] - self.player.updates['x'] + self.player.base.x)))
            mouse_position_window = rl.get_mouse_position()
            select_coordinate = (
                (mouse_position_window.x - self.camera.offset.x) / self.camera.zoom + self.camera.target.x,
                (mouse_position_window.y - self.camera.offset.y) / self.camera.zoom + self.camera.target.y
            )

            for key, value in shared_memory['playersupdate'][0].items():
                if key == shared_memory['user']:
                    continue

                player = shared_memory['playersupdate'][0][key]

                if raylib.CheckCollisionPointRec(rl.Vector2(select_coordinate[0], select_coordinate[1]), select_player(player)):
                    self.player.updates['action']['target'] = key
                    return
                
            for key, value in shared_memory['npcs'][0].items():
                npc = shared_memory['npcs'][0][key]
                if raylib.CheckCollisionPointRec(rl.Vector2(select_coordinate[0], select_coordinate[1]), rl.Rectangle(npc.updates['x'],npc.updates['y'],npc.size,npc.size)):
                    self.player.updates['action']['target'] = npc.get_id()
                    self.player.updates['action']['type'] = 'attacknpc'
                    self.player.updates['action']['x'] = npc.updates['x']
                    self.player.updates['action']['y'] = npc.updates['y']
                    return
            
            self.attacking = False
            self.player.updates['action']['type'] = None
            self.player.updates['action']['target'] = None
            self.player.updates['action']['x'] = None
            self.player.updates['action']['y'] = None

        if raylib.IsMouseButtonPressed(raylib.MOUSE_BUTTON_LEFT):
            mouse_position_window = rl.get_mouse_position()
            select_coordinate = (
                (mouse_position_window.x - self.camera.offset.x) / self.camera.zoom + self.camera.target.x,
                (mouse_position_window.y - self.camera.offset.y) / self.camera.zoom + self.camera.target.y
            )

            for key, value in shared_memory['playersinfo'][0].items():
                if key == shared_memory['user']:
                    continue

                player = shared_memory['playersinfo'][0][key]

                if raylib.CheckCollisionPointRec(rl.Vector2(select_coordinate[0], select_coordinate[1]), select_player(shared_memory['playersupdate'][0][key])):
                    print(player)

    def GamePlayInput_call(self, chunk_data, shared_memory):

        self.select(shared_memory)

        self.move(chunk_data, shared_memory)

        # self.collision(chunk_data[int((self.player.updates['x'] - self.player.base.x) // (TILE_SIZE * CHUNK_SIZE)), int((self.player.updates['y'] - self.player.base.y) // (TILE_SIZE * CHUNK_SIZE))][1])