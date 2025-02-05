from Objects.Object import Object

class NPC(Object):
    def __init__(self, name, x, y, texture, width, height):
        super().__init__(name, x, y, texture, width, height)

    def get_key(self):
        return f'{self.x}{self.y}'