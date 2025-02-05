import asyncio
from queue import Queue

from Objects.Player import Player as Player
from Network.Server.ActionLoop import game_loop
from Network.Server.HandleClient import handle_client

# Constants
HOST = "0.0.0.0"
PORT = 65432
MAX_PLAYERS = 80

async def start_server():

    client_data = dict()
    client_stats = dict()
    client_con = dict()
    action_queue = Queue()

    gameloop = asyncio.create_task(game_loop(client_data,action_queue,client_stats,client_con))

    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, client_data, action_queue, client_stats, client_con),
        HOST,
        PORT
    )

    print(f"Server listening on {HOST}:{PORT}")

    async with server:
        await server.serve_forever()
