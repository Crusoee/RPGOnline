import socket
import multiprocessing
import pickle
import zlib
import time
import datetime
import random
import asyncio
import traceback
import json

from NPC import NPC
from SimplexNoise import simplex_noise

# Constants
HOST = "0.0.0.0"
PORT = 65432
TICK_RATE = 1 / 20 # 60 Hz
MAX_PLAYERS = 80

def send_message(conn, data, use_compression=True):
    # Serialize data
    serialized_data = pickle.dumps(data)
    
    # Optionally compress data
    if use_compression:
        serialized_data = zlib.compress(serialized_data)
    
    # Send total size of the data first
    total_size = len(serialized_data)
    conn.sendall(total_size.to_bytes(4, 'big'))
    
    # Send data in chunks
    chunk_size = 1024
    for i in range(0, total_size, chunk_size):
        chunk = serialized_data[i:i + chunk_size]
        conn.sendall(chunk)

def get_message(conn, use_compression=True):
    # Receive total size of the data
    total_size = int.from_bytes(conn.recv(4), 'big')
    
    # Receive data in chunks
    received_data = b''
    while len(received_data) < total_size:
        chunk = conn.recv(min(1024, total_size - len(received_data)))
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

def game_loop(client_updates, action_queue, client_info):
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

            client_info_mutable = dict(client_info)
            

            """
            This is the while loop to handle all actions created by the players.
            This while loop continues until all player actions have been handled. while not action_queue.empty()...
            """
            # Process actions
            while not action_queue.empty():
                # Get the next action on the queue
                action = action_queue.get()
                # Keep tabs on who initiated the action
                # initiator = client_info_mutable[action['initiator']]

                """
                If a player attacks another player
                """

                if action['type'] == 'attack' and client_info_mutable[action['initiator']]['atc'] >= client_info_mutable[action['initiator']]['ats'] and action['target'] in client_info.keys():
                    # with client_data_lock:
                    # target = client_info[action['target']]

                    if client_info_mutable[action['initiator']]['energy'] - client_info_mutable[action['initiator']]['energyconsumption'] < 0:
                        continue

                    client_info_mutable[action['initiator']]['energy'] -= client_info_mutable[action['initiator']]['energyconsumption']

                    # Damage Calculation and Crit
                    # How much true damage initiator did to target
                    true_damage = round(client_info_mutable[action['initiator']]['dmg'] * (client_info_mutable[action['initiator']]['crit'] if random.randint(1, client_info_mutable[action['initiator']]['chance']) == 1 else 1), 2)
                    # How much damage initiator did to target after armor calculation
                    damage = round(true_damage - true_damage * client_info_mutable[action['target']]['arm'] / true_damage, 2)
                    # How much reversal damage target did to initiator
                    thorns = round(damage * client_info_mutable[action['target']]['thorns'], 2)
                    # How much life steal initiator gets from damage
                    lifesteal = round(damage * client_info_mutable[action['initiator']]['lifesteal'], 2)
                    # How much life steal target gets from reversal damage
                    target_lifesteal = round(thorns * client_info_mutable[action['target']]['lifesteal'], 2)

                    client_info_mutable[action['target']]['hlth'] -= damage
                    client_info_mutable[action['target']]['hlth'] += target_lifesteal
                    client_info_mutable[action['initiator']]['hlth'] -= thorns
                    client_info_mutable[action['initiator']]['hlth'] += lifesteal

                    if client_info_mutable[action['target']]['hlth'] > client_info_mutable[action['target']]['mhlth']:
                        client_info_mutable[action['target']]['hlth'] = client_info_mutable[action['target']]['mhlth']

                    if client_info_mutable[action['initiator']]['hlth'] > client_info_mutable[action['initiator']]['mhlth']:
                        client_info_mutable[action['initiator']]['hlth'] = client_info_mutable[action['initiator']]['mhlth']

                    # Reset attack Counter
                    client_info_mutable[action['initiator']]['atc'] = 0

                    # Add 1 to a players kill count
                    if client_info_mutable[action['target']]['hlth'] <= 0:
                        client_info_mutable[action['initiator']]['killcount'] += 1

                    # Reset the target
                    # with client_data_lock:
                    # client_info[action['target']] = target

                """
                If a player attacks an NPC
                """
                if action['type'] == 'attacknpc' and client_info_mutable[action['initiator']]['atc'] >= client_info_mutable[action['initiator']]['ats'] and action['target'] in npcs.keys():
                    npcs[action['target']].health -= client_info_mutable[action['initiator']]['dmg']
                    # Reset attack Counter
                    client_info_mutable[action['initiator']]['atc'] = 0

                    # If an npcs health is less than 0
                    if npcs[action['target']].health < 0:
                        client_info_mutable[action['initiator']]['dmg'] += 0.01
                        if client_info_mutable[action['initiator']]['hlth'] + 5.0 < client_info_mutable[action['initiator']]['mhlth']:
                            client_info_mutable[action['initiator']]['hlth'] += 5.0
                        else:
                            client_info_mutable[action['initiator']]['hlth'] = client_info_mutable[action['initiator']]['mhlth']

                        npcs.pop(action['target'], None)

                if action['type'] == 'loot':
                    ...

                # with client_data_lock:
                # client_info[action['initiator']] = initiator

            """
            TICK UPDATES
            """
            for addr, stats in client_info.items():

                # client = client_info[addr]

                # Melee Attacking
                if client_info_mutable[addr]['atc'] * client_info_mutable[addr]['hinderedspeedmult'] < client_info_mutable[addr]['ats']:
                    client_info_mutable[addr]['atc'] += 1

                # Respawning
                if client_info_mutable[addr]['hlth'] <= 0:
                    client_info_mutable[addr]['rescntr'] += 1
                    if client_info_mutable[addr]['rescntr'] >= client_info_mutable[addr]['ress']:
                        client_info_mutable[addr]['hlth'] = client_info_mutable[addr]['mhlth']
                        client_info_mutable[addr]['rescntr'] = 0

                # Health Regeneration
                if client_info_mutable[addr]['hlth'] < client_info_mutable[addr]['mhlth']:
                    if client_info_mutable[addr]['regencntr'] < client_info_mutable[addr]['regens']:
                        client_info_mutable[addr]['regencntr'] += 1
                    else:
                        client_info_mutable[addr]['regencntr'] = 0
                        client_info_mutable[addr]['hlth'] += client_info_mutable[addr]['regenbonus']
                    
                    if client_info_mutable[addr]['hlth'] > client_info_mutable[addr]['mhlth']:
                        client_info_mutable[addr]['hlth'] = client_info_mutable[addr]['mhlth']

                # Energy Regeneration NEEDS A LOCK
                # with client_data_lock:
                if client_updates[addr]['swim'] == True:
                    if client_info_mutable[addr]['energyconsumptionratecntr'] >= client_info_mutable[addr]['energyconsumptionrate']:
                        if client_info_mutable[addr]['energy'] <= 0:
                            client_info_mutable[addr]['hlth'] -= client_info_mutable[addr]['mhlth'] // 8
                            client_info_mutable[addr]['energy'] = 0
                        client_info_mutable[addr]['energy'] -= client_info_mutable[addr]['energyconsumption']
                        client_info_mutable[addr]['energyconsumptionratecntr'] = 0

                    else:
                        client_info_mutable[addr]['energyconsumptionratecntr'] += 1
                else:
                    if client_info_mutable[addr]['energycntr'] >= client_info_mutable[addr]['energyregen']:
                        if client_info_mutable[addr]['energy'] + client_info_mutable[addr]['energyregenbonus'] < client_info_mutable[addr]['maxenergy']:
                            client_info_mutable[addr]['energy'] += client_info_mutable[addr]['energyregenbonus']
                            client_info_mutable[addr]['energycntr'] = 0
                        else:
                            client_info_mutable[addr]['energy'] = client_info_mutable[addr]['maxenergy']
                            client_info_mutable[addr]['energycntr'] = 0
                    else:
                        client_info_mutable[addr]['energycntr'] += 1

                if client_info_mutable[addr]['energy'] <= int(client_info_mutable[addr]['maxenergy'] / 6):
                    client_info_mutable[addr]['hinderedspeedmult'] = client_info_mutable[addr]['lowenergyspeed']
                else:
                    client_info_mutable[addr]['hinderedspeedmult'] = 1

                # client_info[addr] = client

            # Update all clients
            # with client_data_lock:
                # making a sendable copy of client data that doesn't have the socket connection
            # client_info_sendable = dict(client_info_mutable)
            # client_info = manager.dict(client_info_mutable)
            client_info.update(client_info_mutable)
            for addr, value in client_info_mutable.items():
                client_info_mutable[addr].pop('conn', None)
            for addr, stats in client_info.items():
                # sending 2 messages to all clients with both updates and info on other clients
                send_message(client_info[addr]['conn'], [dict(client_updates)], False)
                send_message(client_info[addr]['conn'], [client_info_mutable], False)
                send_message(client_info[addr]['conn'], [npcs], False)

            # Wait until the next tick
            elapsed = time.time() - start_time
            if elapsed < TICK_RATE:
                time.sleep(TICK_RATE - elapsed)
            elif elapsed > TICK_RATE:
                print("tickrate longer", elapsed)
        except (TimeoutError, EOFError, KeyError, ConnectionResetError) as e:
            print(f"Error processing data!", traceback.format_exc())
            print(len(client_info), client_info.keys())
        except (ConnectionAbortedError) as e:
            del client_updates[addr]
            del client_info[addr]

def handle_client(conn, addr, client_updates, client_data_lock, action_queue, client_info):
    print(f"Connection with {addr[0]} on port {addr[1]} started...")

    """
    handle_client essentially is exactly what the name entails. It connects the client to the server. It keeps the server updated with client received 
    information. We take the client address and port and make it into an identifiable key for each client individually (WHICH MAY BE BAD PRACTICE?). In this 
    function we create 2 dictionaries, updates is for information coming from the client and info is information of the client from the server going to the 
    client. The client sends login info so that the server can load in his/her player stats into the info dictionary. client_info and client_updates are both shared
    dictionaries between the handle_client and game_loop processes. We send both entire dicts to all clients so that they can see each others names and stats.
    Because the data inside a shared dictionary is immutable, we create a copy of a the dict of the player inside the shared dict, we update it, then we set it
    again (this seems to be the only way to edit specific values).

    """

    conn.settimeout(5.0)

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
                'mgcregen' : 120,
                'mgcregenbonus' : 1,
                'mgcctnr' : 0,
                'mgcheal' : 5,
                'mgcburn' : 0.1,

                'arm' : 0,
                'thorns' : 0,

                'hlth' : 100,
                'mhlth' : 100,
                'regens' : 120,
                'regencntr' : 0,
                'regenbonus' : 1,

                # 'hit' : '',

                'atc' : 60,
                'ats' : 60,

                'ress' : 600,
                'rescntr' : 0,

                'hinderedspeedmult' : 1,

                'speed' : 130,
                'swmspeed' : 65,

                'killcount' : 0,

                'attackingdist' : 50,
                'trackingdist' : 800,

                'maxenergy' : 300,
                'energy' : 300,
                'energyregen' : 120,
                'energycntr' : 0,
                'energyregenbonus' : 10,

                'energyconsumption' : 20,
                'energyconsumptionrate' : 60,
                'energyconsumptionratecntr' : 0,
                'lowenergyspeed' : 0.5,

                # 'inventory' : [],

                'conn' : conn
            }
    
    """
    LOGIN...
    """
    
    # Incoming Player Request
    login = get_message(conn, False)

    # Opening all player accounts and storing them in a dictionary
    with open("players.json", "r") as json_file:
        player_data_loaded_from_storage = json.load(json_file)

    # Logging in to an Existing Player Account
    if login[2] == '0':
        login_accepted = False

        # Looping through all player accounts for matching username and password (also that they're not logged in already).
        for player in player_data_loaded_from_storage:
            if player["username"] == login[0] and player["password"] == login[1] and login[0] not in client_info.keys():
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
            send_message(conn, True, False)
        # Sending login failure message back for client
        else:
            print("login failed", login[0])
            send_message(conn, False, False)
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
            send_message(conn, True, False)
            # Creating username variable
            username = login[0]
            # Creating a spot for username to be saved within info evn though it already is saved in the json?
            info['username'] = login[0]
        # Sending login failure message back for client
        else:
            print("login failed", login[0])
            send_message(conn, False, False)
            return
        
        # Creating a savable copy of the new player info
        save_info = info.copy()
        # Deleting the connection key and value because it is unpicklable
        del save_info['conn']

        # Organizing a dict
        new_player = {"username" : login[0], "password" : login[1],"info" : save_info}
        # Appending it to the current list of players
        player_data_loaded_from_storage.append(new_player)
        # Saving it back to the file
        with open("players.json", "w") as f:
            json.dump(player_data_loaded_from_storage, f,indent=4)
    else:
        print("login failed", login[0])
        send_message(conn, False, False)
        return

    # setting up client
    with client_data_lock:
        client_updates[login[0]] = updates
        client_info[login[0]] = info

    """
    CLIENT LOOP
    """

    while True:
        try:
            # creating a mutable copy of client data
            info = client_updates[username]

            # get the message from the client
            updates = get_message(conn, False)
            
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
            if updates[0]['action']['type'] != None and client_info[username]['hlth'] > 0:
                updates[0]['action']['initiator'] = username
                action_queue.put(updates[0]['action'])

            # Finally, update the client_updates dict
            client_updates[username] = info

        except (TimeoutError, KeyError, ConnectionResetError) as e:
            print(f"Error processing data from {username}: {traceback.format_exc()}")
            break
        except (EOFError) as e:
            print("End of input...", e)
            break

    """
    SAVE DATA AFTER CLIENT EXITING
    """

    with open("players.json", "r") as json_file:
        player_data_loaded_from_storage = json.load(json_file)

        save_info = client_info[username].copy()
        del save_info["conn"]

        for i in range(len(player_data_loaded_from_storage)):
            if player_data_loaded_from_storage[i]["username"] == username:
                player_data_loaded_from_storage[i]["info"] = save_info

    with open("players.json", "w") as f:
        json.dump(player_data_loaded_from_storage, f,indent=4)

    # Removing client from active dictionaries
    with client_data_lock:
        del client_updates[username]
        del client_info[username]

    print(f"Connection with {addr[0]} on port {addr[1]} finished...")

def start_server():
    client_stats_lock = multiprocessing.Lock()
    manager = multiprocessing.Manager()

    client_data = manager.dict()
    client_stats = manager.dict()
    action_queue = manager.Queue()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        # multiprocessing.Process(target=get_status, args=(client_data,client_stats_backup)).start()
        multiprocessing.Process(target=game_loop, args=(client_data, action_queue, client_stats)).start()

        while True:
            try:
                conn, addr = s.accept()
                multiprocessing.Process(
                    target=handle_client, 
                    args=(conn, addr, client_data, client_stats_lock, action_queue, client_stats)
                    ).start()
                
                if len(client_data) > MAX_PLAYERS:
                    login = get_message(conn, False)
                    # Sending login failure message back for client
                    print("PLAYER LIMIT: Rejected", login[0])
                    send_message(conn, False, False)

            except KeyboardInterrupt:
                print("Server shutting down...")
                break
            except Exception as e:
                print(f"Server error: {e}")

if __name__ == "__main__":
    print('Server Starting...')
    start_server()
