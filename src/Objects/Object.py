import pyray as rl
from Misc.CONSTANTS import PLAYER_HEIGHT

class Object:
    def __init__(self, name, x, y, texture):

        self.texture = texture

        self.base = (x + texture.width // 2, y + texture.height // 2)

        self.updates = {
                    'x' : x,
                    'y' : y,
                    'coord' : None,
                    'nme' : name,
                    'swim' : False,
                    'ismoving' : False,
                    'isattacking' : False, 
                    'canmove' : True,

                    'action' : {
                            'type' : None,
                            'target' :None,
                            'x' : None,
                            'y' : None,
                        }
                }
    
    def draw(self):
        rl.draw_texture_pro(self.texture, rl.Rectangle(0,0,self.texture.width * self.updates['direction'], self.texture.height), 
                            rl.Rectangle(self.updates['x'],self.updates['y'] - (self.texture.height * 2 * self.updates['size']) + PLAYER_HEIGHT,self.texture.width * 2 * self.updates['size'], self.texture.height * 2 * self.updates['size']), 
                            rl.Vector2(0,0),
                            0.0, 
                            rl.WHITE)

    def get_y(self):
        return self.updates['y']



class Palm:

    def __init__(self, x, y, direction, size):
        self.updates = {
            'x' : x,
            'y' : y,
            'direction' : direction,
            'size' : size,
            # 'palm_texture' : palm_texture
        }

    def draw(self, palm_textures):
        rl.draw_texture_pro(palm_textures, rl.Rectangle(0,0,palm_textures.width * self.updates['direction'], palm_textures.height), 
                            rl.Rectangle(self.updates['x'],self.updates['y'] - (palm_textures.height * 2 * self.updates['size']) + PLAYER_HEIGHT,palm_textures.width * 2 * self.updates['size'], palm_textures.height * 2 * self.updates['size']), 
                            rl.Vector2(0,0),
                            0.0, 
                            rl.WHITE)

class Shrub(Object):
    ...