import pyray as rl
import raylib as raylib
import multiprocessing

from Objects.Player import Player
from Objects.ObjectInfo import ObjectInfo
from Misc.CONSTANTS import PLAYER_WIDTH
from Network.Client.Client import client_communication_loop

import Render.Render as Render
import Menu.Menu as Menu
import Input.GamePlayInput as GamePlayInput
import Network.Client.PlayerManager as PlayerManager 

# --- main ---
def game_loop(default, shared_memory, window_size):

    raylib.SetConfigFlags(rl.FLAG_WINDOW_RESIZABLE)
    raylib.InitWindow(window_size[0], window_size[1], b"RPG Online")
    # rl.toggle_fullscreen()
    raylib.SetWindowPosition(100,100)
    
    raylib.SetTargetFPS(0)

    rl.hide_cursor()

    """
    LOADING IN TEXTURES AND FONTS, ETC...

    from what I understand, all textures must be loaded here and not on any other file. Not sure why.
    """

    cursorTexture = rl.load_texture("Textures\\Mouse\\dwarven_gauntlet.png")

    tiles = {'water_tile' : rl.load_texture("Textures\\topdown_tiles\\tiles\\deep0\\straight\\0\\0.png"),
        'shallow_tile' : rl.load_texture("Textures\\topdown_tiles\\tiles\\shallow0\\straight\\0\\0.png"),
        'sand_tile' : rl.load_texture("Textures\\topdown_tiles\\tiles\\beach0\\straight\\0\\0.png"),
        'grass_tile' : rl.load_texture("Textures\\topdown_tiles\\tiles\\grass0\\straight\\0\\0.png"),
        'forest_tile' : rl.load_texture("Textures\\topdown_tiles\\Forest.png"),
        'rock_tile' : rl.load_texture("Textures\\topdown_tiles\\Mountain.png")}
    
    npc = rl.load_texture("Textures\orb_red.png")

    written_font = rl.load_font("Font\Caveat-VariableFont_wght.ttf")
    name_font = rl.load_font("Font\LilitaOne-Regular.ttf")

    player_textures = {
        "click" : rl.load_texture("Textures\Click\glow.png"),
        "healthframe" : rl.load_texture("Textures\Healthbar\\bar.png"),
        "healthbar" : rl.load_texture("Textures\Healthbar\\bar2.png"),
        "Energybar" : rl.load_texture("Textures\Healthbar\Energybar.png"),
        "Magicbar" : rl.load_texture("Textures\Healthbar\Magicbar.png"),
        "player" : rl.load_texture("Textures\Player\character2.png"),

        "name_font" : name_font
    }

    menu_textures = {
        "written_font" : written_font,
        
        "pack" : rl.load_texture("Textures\Menu\\farm tool icons calciumtrice.png"),
        "inventory" : rl.load_texture("Textures\Menu\WoodPlank.png"),
        "parchment" : rl.load_texture("Textures\Menu\scroll.png")
    }

    palm = rl.load_texture("Textures\Environment\palmtree.png")


    # Place Holder
    player = Player('', 0, 0, player_textures)
    player.updates = default.updates
    player.stats = default.stats
    
    # Instances
    player_manager = PlayerManager.PlayerManager(player, player_textures)
    menu = Menu.Menu(window_size, menu_textures)
    render = Render.Render(player, tiles, palm, player_textures, npc, cursorTexture, menu, window_size)
    input = GamePlayInput.GamePlayInput(player, render.camera)

    while not raylib.WindowShouldClose():
        # -------------Draw-------------------

        render.draw_call(player_manager)

        # -------------Mechanics-------------------

        # Menu
        menu.logic(render)
        
        # Updating Player Stats
        player_manager.update_all_players_list(shared_memory)

        input.GamePlayInput_call(render.chunk_data, shared_memory)

        render.center_camera()

        player_manager.move_players()

        if rl.get_screen_width() != window_size[0] or rl.get_screen_height() != window_size[1]:
            window_size[0] = rl.get_screen_width()
            window_size[1] = rl.get_screen_height()
            render.camera.offset = rl.Vector2(window_size[0]/2 - PLAYER_WIDTH/2, window_size[1]/2)

        # updating my current coordinates to the server
        shared_memory['player'] = player.updates

    shared_memory['running'] = False

    raylib.CloseWindow()

def main() -> int:
    window_size = [
        1200,
        800
    ]
    
    # Logging in or creating account
    while True:
        intent = input("Login (0) or Create an Account (1)")
        username = input("Username: ")
        password = input("Password: ")

        # True Spawning Point
        default = ObjectInfo(username,4416,-768)
        
        manager = multiprocessing.Manager()
        shared_memory = manager.dict()
        shared_memory["player"] = default.updates
        shared_memory["playersupdate"] = manager.list([{}])  # Use a managed list for nested data
        shared_memory["playersinfo"] = manager.list([{}])
        shared_memory["npcs"] = [{}]
        shared_memory["user"] = username
        shared_memory["stats"] = default.stats
        shared_memory["running"] = True
        shared_memory["login_successful"] = ""


        communicationloop = multiprocessing.Process(target=client_communication_loop, args=(shared_memory, (username, password, intent)))
        communicationloop.start()

        # Waiting to see if login was successful or not
        while shared_memory["login_successful"] == "":
            ...

        # print(shared_memory["login_successful"])

        if shared_memory["login_successful"] == False:
            communicationloop.join()

        if shared_memory["login_successful"] == True:
            break

    game_loop(default, shared_memory, window_size)

    communicationloop.join()

    return 0

if __name__ == "__main__":
    exit(main())