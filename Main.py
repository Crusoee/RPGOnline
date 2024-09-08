import pyray as rl
import raylib as raylib
import multiprocessing

from Player import Player
from CONSTANTS import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, CHUNK_SIZE, NUM_CHUNKS
from Client import client_communication_loop
import Render

# --- main ---
def game_loop(player, shared_memory):
    raylib.InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, b"Hide And Seek")
    raylib.SetTargetFPS(0)

    tiles = {'water_tile' : rl.load_texture("topdown_tiles\\tiles\\deep0\\straight\\0\\0.png"),
        'shallow_tile' : rl.load_texture("topdown_tiles\\tiles\\shallow0\\straight\\0\\0.png"),
        'sand_tile' : rl.load_texture("topdown_tiles\\tiles\\beach0\\straight\\0\\0.png"),
        'grass_tile' : rl.load_texture("topdown_tiles\\tiles\\grass0\\straight\\0\\0.png"),
        'forest_tile' : rl.load_texture("topdown_tiles\\Forest.png"),
        'rock_tile' : rl.load_texture("topdown_tiles\\Mountain.png")}
    
    chunk_data = {}

    while not raylib.WindowShouldClose():
        # Draw
        raylib.BeginDrawing()
        raylib.ClearBackground(rl.RAYWHITE)
        raylib.BeginMode2D(player.camera)

        Render.draw_tiles(player, chunk_data, tiles)

        Render.draw_players(shared_memory)

        player.draw()

        # for jim in chunk_data[int(player.locsize.x // (TILE_SIZE * CHUNK_SIZE)), int(player.locsize.y // (TILE_SIZE * CHUNK_SIZE))][1]:
        #     raylib.DrawRectangleRec(jim, rl.GREEN)

        raylib.EndMode2D()

        rl.draw_text(f"{1 / (raylib.GetFrameTime() + .00000000001)}", 50, 100, 40, rl.BLACK)
        # rl.draw_text(f"X: {player.locsize.x // TILE_SIZE}, Y: {player.locsize.y // TILE_SIZE}", 50, 50, 40, rl.DARKBLUE)
        rl.draw_text(f"X: {player.locsize.x}, Y: {player.locsize.y}", 50, 50, 40, rl.BLACK)
        rl.draw_text(f"X: {player.locsize.x // (TILE_SIZE * CHUNK_SIZE)}, Y: {player.locsize.y // (TILE_SIZE * CHUNK_SIZE)}", 50, 150, 40, rl.DARKBLUE)

        raylib.EndDrawing()
        
        # Handle Player
        player.move(chunk_data)

        player.select(shared_memory)

        # updating my current coordinates for other players
        shared_memory['player'] = [player.locsize.x, player.locsize.y, player.damage, player.magic, player.armor, player.health]

    shared_memory['running'] = False
    raylib.CloseWindow()

def main() -> int:
    player = Player(rl.SKYBLUE, rl.Rectangle(0, 0, 40, 80), 500)
    
    manager = multiprocessing.Manager()
    shared_memory = manager.dict()
    shared_memory["player"] = [player.locsize.x, player.locsize.y, player.damage, player.magic, player.armor, player.health]
    shared_memory["players"] = manager.list([{}])  # Use a managed list for nested data
    shared_memory["user"] = ""
    shared_memory["running"] = True

    communicationloop = multiprocessing.Process(target=client_communication_loop, args=(shared_memory,))
    communicationloop.start()

    game_loop(player, shared_memory)

    communicationloop.join()

    return 0

if __name__ == "__main__":
    exit(main())