class NPC():
    def __init__(self, name, health, damage, size):
        self.name = name
        self.health = health
        self.damage = damage
        self.size = size

    ...

class Boar(NPC):
    def __init__(self, name, health, damage, size):
        NPC.__init__(self, name, health, damage, size)

    
    ...