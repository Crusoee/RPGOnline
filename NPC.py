class NPC():
    def __init__(self, name, health, damage, x, y, size):
        self.name = name
        self.health = health
        self.damage = damage
        self.size = size
        self.x = x
        self.y = y
        self.respawnt = 3600
        self.respawnc = 0

    def get_key(self):
        return f'{self.x}{self.y}'

class NPC_Handler():
    def __init__(self):
        
        ...
    ...