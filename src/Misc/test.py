from Network.Server.NPCManager import NPCManager
from Objects.ObjectInfo import ObjectInfo

import time

def NPC_Behavior_test():
    npc_obj = NPCManager()

    player = ObjectInfo('',100,100)
    
    while True:
        # npc_obj.get_nearby_npcs(0,0)
        time.sleep(1/30)

        npc_obj.move_npcs([player])

        print(npc_obj.npc_chunk, player.updates['x'])

        player.updates['x'] += 50
        player.updates['y'] += 50