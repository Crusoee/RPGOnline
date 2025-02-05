import traceback
import random
import time
import asyncio

from Misc.CONSTANTS import TICK_RATE
from Objects.NPC import NPC
from Network.Server.Communication import send_message

async def game_loop(client_data, action_queue, client_stats, client_con):
    """
    NPCs
    TESTING PHASE:
    This is the NPC dictionary to keep track of all npcs that are in the world currently.
    I use npc location as a means of giving them Keys so that the server and the client can better
    communicate what the player is attacking.
    """
    npcs = {}
    # for i in range(10):
    #     npc = NPC("orb", 60, 0, random.randint(-1000,1000), random.randint(-1000,1000), 64)
    #     # the key can be whatever its coordinates are
    #     npcs[npc.get_key()] = npc

    while True: 
        try:
            """
            start_time keeps tabs on the amount of time it took for a single iteration of this while loop.
            This is to keep the server running at a constant speed.
            """
            start_time = time.time()

            """
            This is the while loop to handle all actions created by the players.
            This while loop continues until all player actions have been handled. while not action_queue.empty()...
            """
            # Process actions
            while not action_queue.empty():
                # Get the next action on the queue
                action = action_queue.get()
                # Keep tabs on who initiated the action

                """
                If a player attacks another player
                """

                if action['type'] == 'attack' and client_stats[action['initiator']]['atc'] >= client_stats[action['initiator']]['ats'] and action['target'] in client_stats.keys():

                    if client_stats[action['initiator']]['energy'] - client_stats[action['initiator']]['energyconsumption'] < 0:
                        continue

                    client_stats[action['initiator']]['energy'] -= client_stats[action['initiator']]['energyconsumption']

                    # Damage Calculation and Crit
                    # How much true damage initiator did to target
                    true_damage = round(client_stats[action['initiator']]['dmg'] * (client_stats[action['initiator']]['crit'] if random.randint(1, client_stats[action['initiator']]['chance']) == 1 else 1), 2)
                    # How much damage initiator did to target after armor calculation
                    damage = round(true_damage - true_damage * client_stats[action['target']]['arm'] / true_damage, 2)
                    # How much reversal damage target did to initiator
                    thorns = round(damage * client_stats[action['target']]['thorns'], 2)
                    # How much life steal initiator gets from damage
                    lifesteal = round(damage * client_stats[action['initiator']]['lifesteal'], 2)
                    # How much life steal target gets from reversal damage
                    target_lifesteal = round(thorns * client_stats[action['target']]['lifesteal'], 2)

                    client_stats[action['target']]['hlth'] -= damage
                    client_stats[action['target']]['hlth'] += target_lifesteal
                    client_stats[action['initiator']]['hlth'] -= thorns
                    client_stats[action['initiator']]['hlth'] += lifesteal

                    if client_stats[action['target']]['hlth'] > client_stats[action['target']]['mhlth']:
                        client_stats[action['target']]['hlth'] = client_stats[action['target']]['mhlth']

                    if client_stats[action['initiator']]['hlth'] > client_stats[action['initiator']]['mhlth']:
                        client_stats[action['initiator']]['hlth'] = client_stats[action['initiator']]['mhlth']

                    # Reset attack Counter
                    client_stats[action['initiator']]['atc'] = 0

                    # Add 1 to a players kill count
                    if client_stats[action['target']]['hlth'] <= 0:
                        client_stats[action['initiator']]['killcount'] += 1

                """
                If a player attacks an NPC
                """
                if action['type'] == 'attacknpc' and client_stats[action['initiator']]['atc'] >= client_stats[action['initiator']]['ats'] and action['target'] in npcs.keys():
                    npcs[action['target']].health -= client_stats[action['initiator']]['dmg']
                    # Reset attack Counter
                    client_stats[action['initiator']]['atc'] = 0

                    # If an npcs health is less than 0
                    if npcs[action['target']].health < 0:
                        client_stats[action['initiator']]['dmg'] += 0.01
                        if client_stats[action['initiator']]['hlth'] + 5.0 < client_stats[action['initiator']]['mhlth']:
                            client_stats[action['initiator']]['hlth'] += 5.0
                        else:
                            client_stats[action['initiator']]['hlth'] = client_stats[action['initiator']]['mhlth']

                        npcs.pop(action['target'], None)

                if action['type'] == 'loot':
                    ...

            """
            TICK UPDATES
            """
            for addr, stats in client_stats.items():

                # Melee Attacking
                if client_stats[addr]['atc'] * client_stats[addr]['hinderedspeedmult'] < client_stats[addr]['ats']:
                    client_stats[addr]['atc'] += 1

                # Respawning
                if client_stats[addr]['hlth'] <= 0:
                    client_stats[addr]['rescntr'] += 1
                    if client_stats[addr]['rescntr'] >= client_stats[addr]['ress']:
                        client_stats[addr]['hlth'] = client_stats[addr]['mhlth']
                        client_stats[addr]['rescntr'] = 0

                # Health Regeneration
                if client_stats[addr]['hlth'] < client_stats[addr]['mhlth']:
                    if client_stats[addr]['regencntr'] < client_stats[addr]['regens']:
                        client_stats[addr]['regencntr'] += 1
                    else:
                        client_stats[addr]['regencntr'] = 0
                        client_stats[addr]['hlth'] += client_stats[addr]['regenbonus']
                    
                    if client_stats[addr]['hlth'] > client_stats[addr]['mhlth']:
                        client_stats[addr]['hlth'] = client_stats[addr]['mhlth']

                # Energy Regeneration
                if client_data[addr]['swim'] == True:
                    if client_stats[addr]['energyconsumptionratecntr'] >= client_stats[addr]['energyconsumptionrate']:
                        if client_stats[addr]['energy'] <= 0:
                            client_stats[addr]['hlth'] -= client_stats[addr]['mhlth'] // 8
                            client_stats[addr]['energy'] = 0
                        client_stats[addr]['energy'] -= client_stats[addr]['energyconsumption']
                        client_stats[addr]['energyconsumptionratecntr'] = 0

                    else:
                        client_stats[addr]['energyconsumptionratecntr'] += 1
                else:
                    if client_stats[addr]['energycntr'] >= client_stats[addr]['energyregen']:
                        if client_stats[addr]['energy'] + client_stats[addr]['energyregenbonus'] < client_stats[addr]['maxenergy']:
                            client_stats[addr]['energy'] += client_stats[addr]['energyregenbonus']
                            client_stats[addr]['energycntr'] = 0
                        else:
                            client_stats[addr]['energy'] = client_stats[addr]['maxenergy']
                            client_stats[addr]['energycntr'] = 0
                    else:
                        client_stats[addr]['energycntr'] += 1

                if client_stats[addr]['energy'] <= int(client_stats[addr]['maxenergy'] / 6):
                    client_stats[addr]['hinderedspeedmult'] = client_stats[addr]['lowenergyspeed']
                else:
                    client_stats[addr]['hinderedspeedmult'] = 1

                # client_stats[addr] = client

            # Update all clients
            for addr, con in client_con.items():
                # sending 3 messages to all clients with both updates and info on other clients
                await send_message(client_con[addr], [client_data], False)
                await send_message(client_con[addr], [client_stats], False)
                await send_message(client_con[addr], [npcs], False)

            # Wait until the next tick
            elapsed = time.time() - start_time
            if elapsed < TICK_RATE:
                await asyncio.sleep(TICK_RATE - elapsed)
            elif elapsed > TICK_RATE:
                print("tickrate longer", elapsed)
        except (TimeoutError, EOFError, KeyError) as e:
            print(f"Error processing data!", traceback.format_exc())
            # print(len(client_stats), client_stats.keys())
        except (ConnectionAbortedError, ConnectionResetError) as e:
            del client_data[addr]
            del client_stats[addr]
            del client_con[addr]
        except Exception as e:
            print(traceback.format_exc())
            print(client_data)