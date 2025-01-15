import pyray as rl
import raylib

"""
MENUS
"""

class IndexButton:
    
    def __init__(self, box: rl.Rectangle, reference_button = None, color = rl.BLUE, is_on = False):
        self.color = color
        self.is_on = is_on
        self.box = box
        self.reference_button = reference_button

    def is_button_on(self):
        return self.is_on
    
    def press_button(self):
        if (self.reference_button == None or self.reference_button.is_on) and self.is_on == False:
            self.is_on = True
    
    def render(self):
        if (self.reference_button == None or self.reference_button.is_on) and self.is_on == False:
            raylib.DrawRectangleRec(self.box, self.color)

class OnOffButton:
    def __init__(self, box: rl.Rectangle, texture: rl.Texture, is_on = False):
        self.texture = texture
        self.is_on = is_on
        self.box = box
    
    def press_button(self):
        if self.is_on:
            self.is_on = False
        else:
            self.is_on = True

class Menu:
    

    stats = False
    stats_scroll = 0.0

    # location = False

    inventory = False


    def __init__(self, screen_width, screen_height, menu_textures):
        self.buttons = []
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.menu_textures = menu_textures
        self.stats_button = OnOffButton(rl.Rectangle(30,30,250,80), menu_textures["parchment"])
        self.location_button = OnOffButton(rl.Rectangle(screen_width - menu_textures['parchment'].width,0,250,80), menu_textures["parchment"])
        self.buttons.append(self.stats_button)
        
        
    def render(self,player):

        self.menu_textures['inventory']

        rl.draw_texture_pro(self.menu_textures['inventory'], 
                                rl.Rectangle(0,0,self.menu_textures['inventory'].width,self.menu_textures['inventory'].height), 
                                rl.Rectangle(0,0,self.menu_textures['inventory'].width * 2,self.menu_textures['inventory'].height * 2), 
                                rl.Vector2(0,0), 0.0, rl.WHITE) 
        
        rl.draw_texture_pro(self.menu_textures['pack'], 
                                rl.Rectangle(0,0,64,64), 
                                rl.Rectangle(0,100,64 * 3,64 * 3), 
                                rl.Vector2(0,0), 0.0, rl.WHITE) 

        if self.stats_button.is_on:
            rl.draw_texture_pro(self.menu_textures["parchment"], 
                                rl.Rectangle(0,0,self.menu_textures["parchment"].width,self.menu_textures["parchment"].height), 
                                rl.Rectangle(30,30,250,600), 
                                rl.Vector2(0,0), 0.0, rl.WHITE)    

            if raylib.GetMouseWheelMove() > 0:
                self.stats_scroll += 10
            elif raylib.GetMouseWheelMove() < 0:
                self.stats_scroll -= 10

            cntr = 50 + self.stats_scroll
            for key, item in player.stats.items():
                cntr += 22
                if 50 < cntr < 500:
                    rl.draw_text_ex(self.menu_textures["written_font"], f"{key}: {player.stats[key]}", rl.Vector2(65, cntr), 40, 0.0, rl.BLACK)
        else:
            rl.draw_texture_pro(self.menu_textures["parchment"], 
                                rl.Rectangle(0,0,self.menu_textures["parchment"].width,140), 
                                rl.Rectangle(30,30,250,80), 
                                rl.Vector2(0,0), 0.0, rl.WHITE) 
            rl.draw_text_ex(self.menu_textures["written_font"], "...", rl.Vector2(50, 20), 40, 0.0, rl.BLACK)


        # if self.location_button.is_on:
        #     rl.draw_texture_pro(self.menu_textures["parchment"], 
        #                         rl.Rectangle(0,0,self.menu_textures["parchment"].width,self.menu_textures["parchment"].height), 
        #                         rl.Rectangle(self.screen_width - self.menu_textures["parchment"].width,0,250,600), 
        #                         rl.Vector2(0,0), 0.0, rl.WHITE)    
        # else:
        #     rl.draw_texture_pro(self.menu_textures["parchment"], 
        #                         rl.Rectangle(0,0,self.menu_textures["parchment"].width,140), 
        #                         rl.Rectangle(self.screen_width - self.menu_textures["parchment"].width,0,250,80), 
        #                         rl.Vector2(0,0), 0.0, rl.WHITE) 
        #     rl.draw_text_ex(self.menu_textures["written_font"], "...", rl.Vector2(self.screen_width - self.menu_textures["parchment"].width - 50, 20), 40, 0.0, rl.BLACK)

        # if rl.gui_button(rl.Rectangle(0,30,70,20), "Stats"):
        #     if self.stats:
        #         self.stats = False
        #     else:
        #         self.stats = True

        # if rl.gui_button(rl.Rectangle(self.screen_width - 70,30,70,20), "Inventory"):
        #     self.inventory = True

        if self.inventory:
                
            inventory = rl.gui_grid(rl.Rectangle(self.screen_width - 150,30,150,self.screen_height - 100), "Inventory", 1.1, 8, rl.get_mouse_position())
            print(inventory)

            # if inventory == 0:
            #     self.stats = False


        # for button in self.buttons:
        #     button.render()

    def logic(self, player):

        if not self.buttons[0].is_on:
            if raylib.GetMouseWheelMove() > 0 and player.zoom < 1.5:
                player.zoom += 0.1
                player.camera.zoom = player.zoom
            elif raylib.GetMouseWheelMove() < 0 and player.zoom > 1.0:
                player.zoom -= 0.1
                player.camera.zoom = player.zoom

        if raylib.IsMouseButtonPressed(raylib.MOUSE_BUTTON_LEFT):
            mouse_coord = rl.get_mouse_position()
            for button in self.buttons:
                if raylib.CheckCollisionPointRec(mouse_coord, button.box):
                    button.press_button()
        ...

    ...