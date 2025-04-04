from Objects.ObjectInfo import ObjectInfo
from Misc.CONSTANTS import TILE_SIZE, CHUNK_SIZE
import random
 
class SSNPC(ObjectInfo):
    def __init__(self, name, x, y, size, chunk_x, chunk_y, npc_number):
        """
        An NPC needs a name (it seems that I will be using names as a means of distinguishing all NPC types), an x and y coordinate,
        a size, the chunk coordinates of where it originates, and the order in which the NPC was created.
        """
        super().__init__(name, x, y)
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
        self.npc_number = npc_number

        self.movement_cntr = 0
        self.retrack_speed = random.randint(70, 500)
        self.id = f'{chunk_x}{chunk_y}{npc_number}'
        self.size = size

    def move(self):

        starting_x = int((self.chunk_x * CHUNK_SIZE) * TILE_SIZE)
        starting_y = int((self.chunk_y * CHUNK_SIZE) * TILE_SIZE)
        ending_x = int((self.chunk_x * CHUNK_SIZE + CHUNK_SIZE - 1) * TILE_SIZE)
        ending_y = int((self.chunk_y * CHUNK_SIZE + CHUNK_SIZE - 1) * TILE_SIZE)

        self.updates['coord'] = (random.randint(starting_x,ending_x), random.randint(starting_y,ending_y))
        # print(self.updates['coord'])

    def get_current_chunk(self):
        return (int((self.updates['x']) // (TILE_SIZE * CHUNK_SIZE)), int((self.updates['y']) // (TILE_SIZE * CHUNK_SIZE)))

    def get_id(self):
        """
        {chunkx chunky}.{npc number}
        """
        return self.id