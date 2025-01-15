import multiprocessing
import pickle
import zlib
import time
import datetime
import random
import traceback
import json

import asyncio
import aiofiles
# import copy

from NPC import NPC
from SimplexNoise import simplex_noise

# Constants
HOST = "0.0.0.0"
PORT = 65432
TICK_RATE = 1 / 30 # 60 Hz
MAX_PLAYERS = 80

async def send_message(writer: asyncio.StreamWriter, data, use_compression=True):
    # Serialize data
    serialized_data = pickle.dumps(data)
    
    # Optionally compress data
    if use_compression:
        serialized_data = zlib.compress(serialized_data)
    
    # Send total size of the data first
    total_size = len(serialized_data)
    writer.write(total_size.to_bytes(4, 'big'))
    await writer.drain()  # Ensure the size is sent
    
    # Send data in chunks
    chunk_size = 1024
    for i in range(0, total_size, chunk_size):
        chunk = serialized_data[i:i + chunk_size]
        writer.write(chunk)
        await writer.drain()  # Ensure the chunk is sent

async def get_message(reader: asyncio.StreamReader, use_compression=True):
    # Receive total size of the data (first 4 bytes)
    size_data = await reader.readexactly(4)  # Read exactly 4 bytes for size
    total_size = int.from_bytes(size_data, 'big')
    
    # Receive data in chunks
    received_data = b''
    while len(received_data) < total_size:
        chunk = await reader.read(min(1024, total_size - len(received_data)))
        if not chunk:
            raise ConnectionError("Connection closed while receiving data")
        received_data += chunk
    
    # Optionally decompress data
    if use_compression:
        received_data = zlib.decompress(received_data)
    
    # Deserialize data
    return pickle.loads(received_data)

def get_status(client_data,client_stats_backup):
    while True:
        time.sleep(20)
        print(datetime.datetime.now(), "Amount of Players: ", len(client_data))

def match_dict(dictionary1, dictionary2_set):
    dict_copy = dictionary2_set.copy()
    for key1, item1 in dictionary1.items():
        for key2, item2 in  dictionary2_set.items():
            if key1 == key2:
                dict_copy[key1] = item1
    return dict_copy

async def append(file_name, new_data):
        # Appending it to the current list of players
        try:
            # Read the existing data
            async with aiofiles.open(file_name, mode='r') as json_file:
                try:
                    data = json.loads(await json_file.read())
                except json.JSONDecodeError:
                    # File might be empty or invalid JSON, start with empty data
                    data = []

            # Append the new data
            if isinstance(data, list):  # Ensure we're working with a list
                data.append(new_data)
            else:
                raise ValueError("JSON data is not a list, appending is not possible.")

            # Write the updated data back to the file
            async with aiofiles.open(file_name, mode='w') as json_file:
                await json_file.write(json.dumps(data, indent=4))
        except FileNotFoundError:
            # If the file does not exist, create it with the new data as the first entry
            async with aiofiles.open(file_name, mode='w') as json_file:
                await json_file.write(json.dumps([new_data], indent=4))

async def game_loop(client_data, action_queue, client_stats, client_con):
    """
    NPCs
    TESTING PHASE:
    This is the NPC dictionary to keep track of all npcs that are in the world currently.
    I use npc location as a means of giving them Keys so that the server and the client can better
    communicate what the player is attacking.
    """
    npcs = {}
    for i in range(10):
        npc = NPC("orb", 60, 0, random.randint(-1000,1000), random.randint(-1000,1000), 64)
        # the key can be whatever its coordinates are
        npcs[npc.get_key()] = npc

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

                # Energy Regeneration NEEDS A LOCK
                # with client_data_lock:
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
            print(e)
            # print(len(client_stats), client_stats.keys())
        except (ConnectionAbortedError, ConnectionResetError) as e:
            del client_data[addr]
            del client_stats[addr]
            del client_con[addr]
        except Exception as e:
            print(traceback.format_exc())

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, client_data, client_stats_lock, action_queue, client_stats, client_con):
    # print(f"Connection with {addr[0]} on port {addr[1]} started...")

    """
    handle_client essentially is exactly what the name entails. It connects the client to the server. It keeps the server updated with client received 
    information. We take the client address and port and make it into an identifiable key for each client individually (WHICH MAY BE BAD PRACTICE?). In this 
    function we create 2 dictionaries, updates is for information coming from the client and info is information of the client from the server going to the 
    client. The client sends login info so that the server can load in his/her player stats into the info dictionary. client_stats and client_data are both shared
    dictionaries between the handle_client and game_loop processes. We send both entire dicts to all clients so that they can see each others names and stats.
    Because the data inside a shared dictionary is immutable, we create a copy of a the dict of the player inside the shared dict, we update it, then we set it
    again (this seems to be the only way to edit specific values).

    """

    loop = asyncio.get_event_loop()

    # Client updates to server
    updates =  {
                'x' : 0,
                'y' : 0,
                'nme' : '',
                'swim' : False,
                'angle' : -90,
                'ismoving' : 0
            }

    # Player info sent to clients
    info = {
                'dmg' : 10,
                'lifesteal' : 0,
                'poison' : 0,

                'crit' : 1.1,
                'chance' : 50,

                'mgcdamage' : 18,
                'maxmgc' : 500,
                'mgc' : 500,
                'mgcregen' : 90,
                'mgcregenbonus' : 1,
                'mgcctnr' : 0,
                'mgcheal' : 5,
                'mgcburn' : 0.1,

                'arm' : 0,
                'thorns' : 0,

                'hlth' : 100,
                'mhlth' : 100,
                'regens' : 60,
                'regencntr' : 0,
                'regenbonus' : 1,

                'atc' : 30,
                'ats' : 30,

                'ress' : 300,
                'rescntr' : 0,

                'hinderedspeedmult' : 1,

                'speed' : 130,
                'swmspeed' : 65,

                'killcount' : 0,

                'attackingdist' : 50,
                'trackingdist' : 800,

                'maxenergy' : 100,
                'energy' : 100,
                'energyregen' : 120,
                'energycntr' : 0,
                'energyregenbonus' : 10,

                'energyconsumption' : 20,
                'energyconsumptionrate' : 30,
                'energyconsumptionratecntr' : 0,
                'lowenergyspeed' : 0.5,
            }
    
    """
    LOGIN...
    """
    
    # Incoming Player Request
    # login = get_message(conn, False)
    login = await get_message(reader, False)

    # Opening all player accounts and storing them in a dictionary
    async with aiofiles.open("players.json", mode='r') as json_file:
        player_data = await json_file.read()
        player_data_loaded_from_storage = json.loads(player_data)

    # Logging in to an Existing Player Account
    if login[2] == '0':
        login_accepted = False

        # Looping through all player accounts for matching username and password (also that they're not logged in already).
        for player in player_data_loaded_from_storage:
            if player["username"] == login[0] and player["password"] == login[1] and login[0] not in client_stats.keys():
                # Creating a variable "username"
                username = player["username"]
                # Overriding the default info dict with the the saved info dict of the player
                info = match_dict(player['info'], info)
                # Creating a spot for username to be saved within info evn though it already is saved in the json?
                info['username'] = username
                # Log in was accepted
                login_accepted = True
        # Sending login successful message back for client
        if login_accepted:
            print("login successful: ", login[0])
            await send_message(writer, True, False)
        # Sending login failure message back for client
        else:
            print("login failed", login[0])
            await send_message(writer, False, False)
            return
    # Creating a New Player Account
    elif login[2] == '1':
        login_accepted = True

        # Looping through all player accounts for matching username to make sure new account request doesn't overwrite a currently created account
        for player in player_data_loaded_from_storage:
            if player["username"] == login[0]:
                login_accepted = False
        # Sending login successful message back for client and set up
        if login_accepted:
            print("login successful: ", login[0])
            await send_message(writer, True, False)
            # Creating username variable
            username = login[0]
            # Creating a spot for username to be saved within info evn though it already is saved in the json?
            info['username'] = login[0]
        # Sending login failure message back for client
        else:
            print("login failed", login[0])
            await send_message(writer, False, False)
            return

        # Organizing a dict
        new_player = {"username" : login[0], "password" : login[1],"info" : info}

        # Appending it to the current list of players
        await append("players.json",new_player)

    else:
        print("login failed", login[0])
        await send_message(writer, False, False)
        return

    # setting up client
    # with client_data_lock:
    client_data[login[0]] = updates
    client_stats[login[0]] = info
    client_con[login[0]] = writer

    """
    CLIENT LOOP
    """

    while True:
        try:
            # creating a mutable copy of client data
            info = client_data[username]

            # get the message from the client
            updates = await get_message(reader, False)
            
            if updates in [0, None]:
                break

            # Stats that the server trusts from the client
            info['x'] = updates[0]['x']
            info['y'] = updates[0]['y']
            info['nme'] = updates[0]['nme']
            info['swim'] = updates[0]['swim']
            info['angle'] = updates[0]['angle']
            info['ismoving'] = updates[0]['ismoving']
            info['animcntr'] = updates[0]['animcntr']

            # If an action is created by the client, add it to the queue
            if updates[0]['action']['type'] != None and client_stats[username]['hlth'] > 0:
                updates[0]['action']['initiator'] = username
                action_queue.put(updates[0]['action'])

            # Finally, update the client_data dict
            client_data[username] = info

        except (TimeoutError, KeyError, ConnectionResetError) as e:
            print(f"Error processing data from {username}: {traceback.format_exc()}")
            break
        except (EOFError) as e:
            print("End of input...", e)
            break

    """
    SAVE DATA AFTER CLIENT EXITING
    """

    async with aiofiles.open("players.json", mode='r') as json_file:
        player_data = await json_file.read()
        player_data_loaded_from_storage = json.loads(player_data)

        for i in range(len(player_data_loaded_from_storage)):
            if player_data_loaded_from_storage[i]["username"] == username:
                player_data_loaded_from_storage[i]["info"] = client_stats[username]


    async with aiofiles.open("players.json", mode='w') as json_file:
        # Serialize the data and write to the file
        await json_file.write(json.dumps(player_data_loaded_from_storage, indent=4))

    # Removing client from active dictionaries
    # with client_data_lock:
    del client_data[username]
    del client_stats[username]
    del client_con[username]

    # print(f"Connection with {addr[0]} on port {addr[1]} finished...")

async def start_server():
    from queue import Queue
    client_stats_lock = multiprocessing.Lock()

    client_data = dict()
    client_stats = dict()
    client_con = dict()
    action_queue = Queue()

    gameloop = asyncio.create_task(game_loop(client_data,action_queue,client_stats,client_con))

    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, client_data, client_stats_lock, action_queue, client_stats, client_con),
        HOST,
        PORT
    )

    print(f"Server listening on {HOST}:{PORT}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    print('Server Starting...')
    asyncio.run(start_server())
