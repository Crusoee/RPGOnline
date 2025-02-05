import pyray as rl
from Misc.CONSTANTS import PLAYER_HEIGHT
from Objects.ObjectInfo import ObjectInfo

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
        ...

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