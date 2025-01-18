import raylib
import pyray as rl
import math
from Helper import select_player, distance

from Generation import simplex_noise
import Generation
from CONSTANTS import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, CHUNK_SIZE, PLAYER_HEIGHT, PLAYER_WIDTH

class Player():
    def __init__(self, x, y, name):

        # self.updates['nme'] = name

        # pixel_coordx = x
        # pixel_coordy = y

        # self.speed = 500

        # self.angle = -90
        # self.animation_cntr = 0

        # self.attacking = False
        # self.is_moving = False
        # self.in_water = False


        # self.locsize = rl.Rectangle(pixel_coordx, pixel_coordy, PLAYER_WIDTH, PLAYER_HEIGHT)

        self.coordinate = None
        # self.can_move = True
        
        self.updates = {
                    'x' : x,
                    'y' : y,
                    'nme' : name,
                    'swim' : False,
                    'angle' : -90,
                    'ismoving' : False,
                    'isattacking' : False, 
                    'animcntr' : 0,
                    'canmove' : True,

                    'action' : {
                            'type' : None,
                            'target' :None,
                            'x' : None,
                            'y' : None,
                        }
                }
        
        self.respawn = rl.Vector2(self.updates['x'],self.updates['y'])
        self.base = rl.Vector2(-int(PLAYER_WIDTH / 2), -PLAYER_HEIGHT)
        self.prev_locsize = rl.Vector2(self.updates['x'] - self.base.x,self.updates['y'] - self.base.y)
        
        self.stats = {
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

    def draw(self, textures):

        if self.coordinate != None and self.updates['isattacking'] == False:
            # raylib.DrawCircle(int(self.coordinate.x), int(self.coordinate.y), 5.0, rl.YELLOW)
            # rl.draw_texture(textures["click"],int(self.coordinate.x), int(self.coordinate.y),rl.YELLOW)
            shrink_factor = 0.2  # For example, shrink to 50% of original size

            # Calculate new width and height after shrinking
            new_width = textures["click"].width * shrink_factor
            new_height = textures["click"].height * shrink_factor

            # Center the destination rectangle
            rl.draw_texture_pro(
                textures["click"], 
                rl.Rectangle(0, 0, textures["click"].width, textures["click"].height),  # Full source rectangle
                rl.Rectangle(
                    int(self.coordinate.x) - new_width / 2, 
                    int(self.coordinate.y) - new_height / 2, 
                    new_width, 
                    new_height
                ), 
                rl.Vector2(0, 0),  # Origin for rotation
                0.0, 
                rl.Color(255,255,255,255)
            )

        # raylib.DrawRectangleRec(self.prev_locsize, rl.BROWN)
        # if self.in_water:
        #     raylib.DrawRectangleRec(rl.Rectangle(self.updates['x'],self.updates['y'] + PLAYER_HEIGHT / 2,PLAYER_WIDTH,PLAYER_HEIGHT / 2), self.color)
        # else:
        # raylib.DrawRectangleRec(self.locsize, self.color)

        if self.updates['animcntr'] <= -4:
            self.updates['animcntr'] = 0

        if self.updates['swim']:
            if self.coordinate != None:
                self.updates['angle'] = math.degrees(math.atan2(-(self.coordinate.y - self.updates['y'] + self.base.y), (self.coordinate.x - self.updates['x'] + self.base.x)))
                if -135 < self.updates['angle'] <= -45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.updates['animcntr'])),0,256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if -45 < self.updates['angle'] <= 45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.updates['animcntr'])),(256 * 3),256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if 45 < self.updates['angle'] <= 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.updates['animcntr'])),(256 * 1),256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if self.updates['angle'] <= -135 or self.updates['angle'] > 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.updates['animcntr'])),(256 * 2),256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                    
                self.updates['animcntr'] -= rl.get_frame_time() * (self.stats['swmspeed'] / 25 * self.stats['hinderedspeedmult'])
            else:
                if -135 < self.updates['angle'] <= -45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((0),0,256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if -45 < self.updates['angle'] <= 45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((0),(256 * 3),256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if 45 < self.updates['angle'] <= 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((0),(256 * 1),256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if self.updates['angle'] <= -135 or self.updates['angle'] > 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((0),(256 * 2),256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)

                self.updates['animcntr'] = 0
        else:
            if self.coordinate != None:
                self.updates['angle'] = math.degrees(math.atan2(-(self.coordinate.y - self.updates['y'] + self.base.y), (self.coordinate.x - self.updates['x'] + self.base.x)))
                if -135 < self.updates['angle'] <= -45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.updates['animcntr'])),0,256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if -45 < self.updates['angle'] <= 45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.updates['animcntr'])),(256 * 3),256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if 45 < self.updates['angle'] <= 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.updates['animcntr'])),(256 * 1),256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if self.updates['angle'] <= -135 or self.updates['angle'] > 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.updates['animcntr'])),(256 * 2),256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                    
                self.updates['animcntr'] -= rl.get_frame_time() * (self.stats['speed'] / 25 * self.stats['hinderedspeedmult'])
            else:
                if -135 < self.updates['angle'] <= -45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle(0,0,256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if -45 < self.updates['angle'] <= 45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle(0,(256 * 3),256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if 45 < self.updates['angle'] <= 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle(0,(256 * 1),256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if self.updates['angle'] <= -135 or self.updates['angle'] > 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle(0,(256 * 2),256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)

                self.updates['animcntr'] = 0


        text_size = rl.measure_text_ex(textures["name_font"], self.updates['nme'], 30, 0.0)
        rl.draw_text_ex(textures["name_font"], self.updates['nme'], rl.Vector2(int(self.updates['x'] - (text_size.x / 2) + PLAYER_WIDTH / 2), int(self.updates['y'] - 80)), 40, 0.0, rl.BLACK)

        # Ensure health ratio is clamped between 0 and 1
        health_ratio = max(0, min(1, self.stats['hlth'] / self.stats['mhlth']))
        energy_ratio = max(0, min(1, self.stats['energy'] / self.stats['maxenergy']))
        magic_ratio = max(0, min(1, self.stats['mgc'] / self.stats['maxmgc']))
        # Calculate base position for the health bar
        base_x = int(self.updates['x']  - 40 + PLAYER_WIDTH // 2)
        base_y = int(self.updates['y']  - 40)
        # Draw the health bar
        # rl.draw_rectangle(base_x, base_y, 80, 20, rl.RED)  # Background
        # rl.draw_rectangle(base_x, base_y, int(80 * health_ratio), 20, rl.GREEN)  # Health bar

        rl.draw_texture_pro(textures["healthframe"], rl.Rectangle(0,0,textures["healthframe"].width, textures["healthframe"].height), 
                    rl.Rectangle(base_x, base_y, 80, 20), 
                    rl.Vector2(0,0),
                    0.0, 
                    rl.WHITE)
        rl.draw_texture_pro(textures["healthbar"], rl.Rectangle(0,0,textures["healthbar"].width * health_ratio, textures["healthbar"].height), 
                    rl.Rectangle(base_x, base_y, 80 * health_ratio, 20), 
                    rl.Vector2(0,0),
                    0.0, 
                    rl.WHITE)
        rl.draw_texture_pro(textures["healthframe"], rl.Rectangle(0,0,textures["healthframe"].width, textures["healthframe"].height), 
                    rl.Rectangle(base_x, base_y + 12, 80, 20), 
                    rl.Vector2(0,0),
                    0.0, 
                    rl.WHITE)
        rl.draw_texture_pro(textures["Energybar"], rl.Rectangle(0,0,textures["Energybar"].width * energy_ratio, textures["Energybar"].height), 
                    rl.Rectangle(base_x, base_y + 15, 80 * energy_ratio, 10), 
                    rl.Vector2(0,0),
                    0.0, 
                    rl.WHITE)
        rl.draw_texture_pro(textures["Magicbar"], rl.Rectangle(0,0,textures["Magicbar"].width * magic_ratio, textures["Magicbar"].height), 
                    rl.Rectangle(base_x, base_y + 20, 80 * magic_ratio, 10), 
                    rl.Vector2(0,0),
                    0.0, 
                    rl.WHITE)

        # rl.end_shader_mode()

        # if self.attacking == True:
        #     rl.draw_circle(int(self.updates['x'] - self.base.x),int(self.updates['y'] - self.base.y / 2),self.distance,rl.Color(255,255,0,100))


    def update_state(self):
        # The current noise level your character is standing on
        value = simplex_noise((self.updates['x'] - self.base.x) // TILE_SIZE, 
                        (self.updates['y'] - self.base.y) // TILE_SIZE)

        # Changing the speed of your player depending on what terrain their standing on
        if value < Generation.water:
            self.player.speed = self.player.stats['swmspeed'] * self.player.stats['hinderedspeedmult']
            self.player.updates['swim'] = True
        else:
            self.player.speed = self.player.stats['speed'] * self.player.stats['hinderedspeedmult']
            self.player.updates['swim'] = False

    def attack_reset(self):
        self.attacking = False
        self.hit = ''

    def update(self, shared_memory):
        # If my user name that the server recognizes my client as, has my stats in its player database, give me those stats
        if self.updates['nme'] in shared_memory['playersinfo'][0].keys():
            stats = shared_memory['playersinfo'][0][self.updates['nme']]
            self.stats = stats