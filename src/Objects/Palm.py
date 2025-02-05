from Objects.NPC import NPC

class Palm(NPC):

    def __init__(self, x, y, direction, size):
        super().__init__('palm', x, y)

    # def draw(self, palm_textures):
    #     rl.draw_texture_pro(palm_textures, rl.Rectangle(0,0,palm_textures.width * self.updates['direction'], palm_textures.height), 
    #                         rl.Rectangle(self.updates['x'],self.updates['y'] - (palm_textures.height * 2 * self.updates['size']) + PLAYER_HEIGHT,palm_textures.width * 2 * self.updates['size'], palm_textures.height * 2 * self.updates['size']), 
    #                         rl.Vector2(0,0),
    #                         0.0, 
    #                         rl.WHITE)