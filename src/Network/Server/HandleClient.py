import asyncio
import aiofiles
import json
import traceback

from Objects.ObjectInfo import ObjectInfo
from Network.Server.Communication import send_message, get_message

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

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, client_data, action_queue, client_stats, client_con):
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
    # Place holder
    object_info = ObjectInfo('',0,0)

    # Client updates to server
    updates = object_info.updates

    # Player info sent to clients
    info = object_info.stats
    
    """
    LOGIN...
    """
    
    # Incoming Player Request
    # login = get_message(conn, False)
    login = await get_message(reader, False)

    # Opening all player accounts and storing them in a dictionary
    async with aiofiles.open(f"src\\Network\\Server\\players.json", mode='r') as json_file:
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
        await append(f"src\\Network\\Server\\players.json",new_player)

    else:
        print("login failed", login[0])
        await send_message(writer, False, False)
        return

    # setting up client
    # with client_data_lock:
    updates = await get_message(reader, False)
    client_data[login[0]] = updates[0]
    client_stats[login[0]] = info
    client_con[login[0]] = writer

    """
    CLIENT LOOP
    """

    while True:
        try:
            # creating a mutable copy of client data
            # info = client_data[username]

            # get the message from the client
            updates = await get_message(reader, False)
            
            if updates in [0, None]:
                break

            # If an action is created by the client, add it to the queue
            if updates[0]['action']['type'] != None and client_stats[username]['hlth'] > 0:
                updates[0]['action']['initiator'] = username
                action_queue.put(updates[0]['action'])

            # Finally, update the client_data dict
            client_data[username] = updates[0]

        except (TimeoutError, KeyError, ConnectionResetError) as e:
            print(f"Error processing data from {username}: {traceback.format_exc()}")
            break
        except (EOFError) as e:
            print("End of input...", e)
            break

    """
    SAVE DATA AFTER CLIENT EXITING
    """

    async with aiofiles.open(f"src\\Network\\Server\\players.json", mode='r') as json_file:
        player_data = await json_file.read()
        player_data_loaded_from_storage = json.loads(player_data)

        for i in range(len(player_data_loaded_from_storage)):
            if player_data_loaded_from_storage[i]["username"] == username:
                player_data_loaded_from_storage[i]["info"] = client_stats[username]


    async with aiofiles.open(f"src\\Network\\Server\\players.json", mode='w') as json_file:
        # Serialize the data and write to the file
        await json_file.write(json.dumps(player_data_loaded_from_storage, indent=4))

    # Removing client from active dictionaries
    # with client_data_lock:
    del client_data[username]
    del client_stats[username]
    del client_con[username]