import pyray as rl
import raylib
from Misc.CONSTANTS import PLAYER_HEIGHT
from Objects.ObjectInfo import ObjectInfo
from Misc.Helper import distance
import math

from Generation.Generation import simplex_noise
import Generation.Generation as Generation

from Misc.CONSTANTS import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE

class Object(ObjectInfo):
    def __init__(self, name, x, y, texture, width, height):

        super().__init__(name, x, y)

        self.texture = texture

        self.width = width
        self.height = height

        self.base = (x + width // 2, y + height)
    
    def draw(self):
        rl.draw_texture_pro(self.texture, rl.Rectangle(0,0,self.texture.width * self.updates['direction'], self.texture.height), 
                            rl.Rectangle(self.updates['x'],self.updates['y'] - (self.texture.height * 2 * self.updates['size']) + PLAYER_HEIGHT,self.texture.width * 2 * self.updates['size'], self.texture.height * 2 * self.updates['size']), 
                            rl.Vector2(0,0),
                            0.0, 
                            rl.WHITE)

    def get_y(self):
        return self.updates['y']
    
    def move(self):

        # The current noise level your character is standing on
        value = simplex_noise((self.updates['x'] - self.base.x) // TILE_SIZE, 
                        (self.updates['y'] - self.base.y) // TILE_SIZE)

        if value < Generation.water:
            self.updates['swim'] = True
        else:
            self.updates['swim'] = False

        # moving depending on if there is a updates['coord'] to follow
        if self.updates['action']['type'] != None:
            self.is_moving = distance(self.updates['x'] - self.base.x,self.updates['y'] - self.base.y, self.updates['coord'][0], self.updates['coord'][1]) > self.stats['attackingdist']
        else:
            self.is_moving = distance(self.updates['x'] - self.base.x,self.updates['y'] - self.base.y, self.updates['coord'][0], self.updates['coord'][1]) > 1.0
        
        if self.is_moving:
            self.animcntr -= rl.get_frame_time() * (self.stats['speed'] / 25 * self.stats['hinderedspeedmult'])
            # self.is_moving = True
            displaced = rl.Vector2(self.updates['coord'][0] - self.updates['x'] + self.base.x, self.updates['coord'][1] - self.updates['y'] + self.base.y)
            self.angle = math.degrees(math.atan2(-displaced.y, displaced.x))
            length = math.sqrt(displaced.x**2 + displaced.y**2)
            if length != 0:
                dir_vec = rl.Vector2(displaced.x / length, displaced.y / length)
                if value < Generation.water:
                    self.updates['x'] += dir_vec.x * self.stats['swmspeed'] * self.stats['hinderedspeedmult'] * raylib.GetFrameTime()
                    self.updates['y'] += dir_vec.y * self.stats['swmspeed'] * self.stats['hinderedspeedmult'] * raylib.GetFrameTime()
                else:
                    self.updates['x'] += dir_vec.x * self.stats['speed'] * self.stats['hinderedspeedmult'] * raylib.GetFrameTime()
                    self.updates['y'] += dir_vec.y * self.stats['speed'] * self.stats['hinderedspeedmult'] * raylib.GetFrameTime()

                # if length < 150.0 * raylib.GetFrameTime():
                #     self.updates['coord'] = None
        else:
            self.animcntr = 0
            # self.is_moving = False