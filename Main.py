import pyray as rl
import raylib as raylib
import multiprocessing


from Player import Player
from CONSTANTS import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, CHUNK_SIZE, NUM_CHUNKS, PLAYER_WIDTH,PLAYER_HEIGHT
from Client import client_communication_loop
import Render
from Menu import Menu
 
# --- main ---
def game_loop(player, shared_memory):
    raylib.SetConfigFlags(rl.FLAG_WINDOW_RESIZABLE)
    raylib.InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, b"RPG Online")
    # rl.toggle_fullscreen()
    raylib.SetWindowPosition(100,100)
    
    raylib.SetTargetFPS(0)

    rl.hide_cursor()

    """
    LOADING IN TEXTURES AND FONTS, ETC...
    """

    render_texture = rl.load_render_texture(SCREEN_WIDTH, SCREEN_HEIGHT)

    player_shaders = {
        "invert_text" : rl.load_shader("", "invert_text.fs")
    }

    cursorTexture = rl.load_texture("Mouse\dwarven_gauntlet.png")

    tiles = {'water_tile' : rl.load_texture("topdown_tiles\\tiles\\deep0\\straight\\0\\0.png"),
        'shallow_tile' : rl.load_texture("topdown_tiles\\tiles\\shallow0\\straight\\0\\0.png"),
        'sand_tile' : rl.load_texture("topdown_tiles\\tiles\\beach0\\straight\\0\\0.png"),
        'grass_tile' : rl.load_texture("topdown_tiles\\tiles\\grass0\\straight\\0\\0.png"),
        'forest_tile' : rl.load_texture("topdown_tiles\\Forest.png"),
        'rock_tile' : rl.load_texture("topdown_tiles\\Mountain.png")}
    
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

    chunk_data = {}

    menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, menu_textures)

    while not raylib.WindowShouldClose():
        # -------------Draw-------------------
        raylib.BeginDrawing()
        # raylib.BeginTextureMode(render_texture)
        raylib.ClearBackground(rl.RAYWHITE)
        raylib.BeginMode2D(player.camera)

        Render.draw_tiles(player, chunk_data, tiles)

        Render.draw_npcs(shared_memory, npc)

        Render.draw_players(shared_memory, player_textures)


        player.draw(player_textures, player_shaders)

        # for jim in chunk_data[int(player.locsize.x // (TILE_SIZE * CHUNK_SIZE)), int(player.locsize.y // (TILE_SIZE * CHUNK_SIZE))][1]:
        #     raylib.DrawRectangleRec(jim, rl.GREEN)

        raylib.EndMode2D()
        # raylib.EndTextureMode()
        # raylib.BeginDrawing()

        rl.draw_texture_rec(render_texture.texture, rl.Rectangle(0,0,render_texture.texture.width, -render_texture.texture.height),rl.Vector2(0,0),rl.WHITE)

        # 105 fps
        rl.draw_text(f"fps: {1 / (raylib.GetFrameTime() + .00000000001)}", SCREEN_WIDTH - 180, 50, 40, rl.BLACK)
        rl.draw_text(f"X: {player.locsize.x // TILE_SIZE}, Y: {player.locsize.y // TILE_SIZE}", SCREEN_WIDTH - 200, 100, 30, rl.BLACK)

        Render.draw_info(player)

        menu.render(player)

        # rl.draw_texture_v(cursorTexture, rl.get_mouse_position(), rl.WHITE)

        rl.draw_texture_pro(cursorTexture, rl.Rectangle(0,0,cursorTexture.width, cursorTexture.height), 
                            rl.Rectangle(rl.get_mouse_position().x,rl.get_mouse_position().y,cursorTexture.width + 20, cursorTexture.height + 20), 
                            rl.Vector2(0,0),
                            0.0, 
                            rl.WHITE)

        raylib.EndDrawing()

        # -------------Mechanics-------------------

        # Menu
        menu.logic(player)
        
        # Updating Player Stats
        player.update(shared_memory)

        # Gui/World Interaction
        player.select(shared_memory)

        # Moving and Colliding Player
        player.move(chunk_data, shared_memory)

        # updating my current coordinates to the server
        shared_memory['player'] = {'x' : player.locsize.x,
                               'y' : player.locsize.y,
                               'nme' : player.name,
                               'swim' : player.in_water,
                               'angle' : player.angle,
                                'ismoving' : player.is_moving,
                                'animcntr' : player.animation_cntr,
                               'action' : player.action}

    shared_memory['running'] = False

    rl.unload_shader(player_shaders['invert_text'])
    rl.unload_render_texture(render_texture)

    raylib.CloseWindow()

def main() -> int:
    
    while True:
        intent = input("Login (0) or Create an Account (1)")
        username = input("Username: ")
        password = input("Password: ")

        player = Player(rl.SKYBLUE, rl.Rectangle(500, 500, PLAYER_WIDTH, PLAYER_HEIGHT), 500, username)
        
        manager = multiprocessing.Manager()
        shared_memory = manager.dict()
        shared_memory["player"] = {'x' : player.locsize.x,
                                'y' : player.locsize.y,
                                'nme' : username,
                                'swim' : player.in_water,
                                'angle' : player.angle,
                                'ismoving' : player.is_moving,
                                'animcntr' : player.animation_cntr,
                                'action' : player.action}
        shared_memory["playersupdate"] = manager.list([{}])  # Use a managed list for nested data
        shared_memory["playersinfo"] = manager.list([{}])
        shared_memory["npcs"] = [{}]
        shared_memory["user"] = username
        shared_memory["stats"] = player.stats
        shared_memory["running"] = True
        shared_memory["login_successful"] = ""


        communicationloop = multiprocessing.Process(target=client_communication_loop, args=(shared_memory, (username, password, intent)))
        communicationloop.start()

        # Waiting to see if login was successful or not
        while shared_memory["login_successful"] == "":
            ...

        print(shared_memory["login_successful"])

        if shared_memory["login_successful"] == False:
            communicationloop.join()

        if shared_memory["login_successful"] == True:
            break

    game_loop(player, shared_memory)

    communicationloop.join()



    return 0

if __name__ == "__main__":
    exit(main())