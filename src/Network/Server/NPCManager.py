from Misc.CONSTANTS import TILE_SIZE, CHUNK_SIZE, PLAYER_WIDTH, PLAYER_HEIGHT
from Objects.ServerSideNPC import SSNPC

class NPCManager:

    npc_chunk = {}

    def __init__(self):
        ...

    def move_npcs(self, players):
        for name, player in players.items():
            chunk_x = (player['x'] + PLAYER_WIDTH // 2) // (TILE_SIZE * CHUNK_SIZE)
            chunk_y = (player['y'] + PLAYER_HEIGHT) // (TILE_SIZE * CHUNK_SIZE)
            if (chunk_x, chunk_y) not in self.npc_chunk:
                self.npc_chunk[chunk_x, chunk_y] = self.get_nearby_npcs(chunk_x, chunk_y)
            else:
                for id, npc in self.npc_chunk[chunk_x, chunk_y].items():
                    if npc.movement_cntr >= npc.retrack_speed:
                        npc.move()
                        npc.movement_cntr = 0
                    else:
                        npc.movement_cntr += 1

    def get_nearby_npcs(self, chunk_x, chunk_y) -> list:
        npcs = {}
        npc_number = 0
        for _ in range(1):
            npc = SSNPC('@hog', 4416, -768, 100, chunk_x, chunk_y, npc_number)
            npcs[npc.get_id()] = npc
            npc_number += 1
        return npcs

    def get_player_chunk(self, x, y):
        chunk_x = (x + PLAYER_WIDTH // 2) // (TILE_SIZE * CHUNK_SIZE)
        chunk_y = (y + PLAYER_HEIGHT) // (TILE_SIZE * CHUNK_SIZE)
        return (chunk_x,chunk_y)

    def display_npcs_id(self):
        for chunk, npcs in self.npc_chunk.items():
            for npc in npcs:
                print(npc.get_id())

    def display_npcs_stats(self):
        for chunk, npcs in self.npc_chunk.items():
            for npc in npcs:
                print(npc.stats)
