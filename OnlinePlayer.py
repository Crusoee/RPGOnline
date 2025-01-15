import raylib
import pyray as rl
import math
from Helper import select_player, distance

from SimplexNoise import simplex_noise
import Render
from CONSTANTS import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, CHUNK_SIZE, PLAYER_HEIGHT, PLAYER_WIDTH

class OnlinePlayer():
    def __init__(self, locsize):

        updates =  {
                    'x' : 0,
                    'y' : 0,
                    'nme' : '',
                    'swim' : False,
                    'angle' : -90,
                    'ismoving' : 0
                }

        self.stats =    {  
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

                'inventory' : []
            }

        self.locsize = locsize

        self.base = rl.Vector2(-int(locsize.width / 2), -locsize.height)
        self.coordinate = None

    def draw(self, textures):

        if self.coordinate != None and self.attacking == False:
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

        if self.animation_cntr <= -4:
            self.animation_cntr = 0

        if self.in_water:
            if self.coordinate != None:
                self.angle = math.degrees(math.atan2(-(self.coordinate.y - self.locsize.y + self.base.y), (self.coordinate.x - self.locsize.x + self.base.x)))
                if -135 < self.angle <= -45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.animation_cntr)),0,256, 150), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if -45 < self.angle <= 45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.animation_cntr)),(256 * 3),256, 150), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if 45 < self.angle <= 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.animation_cntr)),(256 * 1),256, 150), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if self.angle <= -135 or self.angle > 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.animation_cntr)),(256 * 2),256, 150), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                    
                self.animation_cntr -= rl.get_frame_time() * (self.stats['swmspeed'] / 25 * self.stats['hinderedspeedmult'])
            else:
                if -135 < self.angle <= -45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((0),0,256, 150), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if -45 < self.angle <= 45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((0),(256 * 3),256, 150), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if 45 < self.angle <= 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((0),(256 * 1),256, 150), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if self.angle <= -135 or self.angle > 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((0),(256 * 2),256, 150), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10 + 34,textures['player'].width/10, textures['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)

                self.animation_cntr = 0
        else:
            if self.coordinate != None:
                self.angle = math.degrees(math.atan2(-(self.coordinate.y - self.locsize.y + self.base.y), (self.coordinate.x - self.locsize.x + self.base.x)))
                if -135 < self.angle <= -45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.animation_cntr)),0,256, 256), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if -45 < self.angle <= 45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.animation_cntr)),(256 * 3),256, 256), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if 45 < self.angle <= 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.animation_cntr)),(256 * 1),256, 256), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if self.angle <= -135 or self.angle > 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle((256 * math.floor(self.animation_cntr)),(256 * 2),256, 256), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                    
                self.animation_cntr -= rl.get_frame_time() * (self.stats['speed'] / 25 * self.stats['hinderedspeedmult'])
            else:
                if -135 < self.angle <= -45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle(0,0,256, 256), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if -45 < self.angle <= 45:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle(0,(256 * 3),256, 256), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if 45 < self.angle <= 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle(0,(256 * 1),256, 256), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if self.angle <= -135 or self.angle > 135:
                    rl.draw_texture_pro(textures['player'], rl.Rectangle(0,(256 * 2),256, 256), 
                                        rl.Rectangle(self.locsize.x - 31,self.locsize.y - 10,textures['player'].width/10, textures['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)

                self.animation_cntr = 0

        text_size = rl.measure_text_ex(textures["name_font"], self.name, 30, 0.0)
        rl.draw_text_ex(textures["name_font"], self.name, rl.Vector2(int(self.locsize.x - (text_size.x / 2) + PLAYER_WIDTH / 2), int(self.locsize.y - 80)), 40, 0.0, rl.BLACK)

        # Ensure health ratio is clamped between 0 and 1
        health_ratio = max(0, min(1, self.stats['hlth'] / self.stats['mhlth']))
        energy_ratio = max(0, min(1, self.stats['energy'] / self.stats['maxenergy']))
        magic_ratio = max(0, min(1, self.stats['mgc'] / self.stats['maxmgc']))
        # Calculate base position for the health bar
        base_x = int(self.locsize.x  - 40 + PLAYER_WIDTH // 2)
        base_y = int(self.locsize.y  - 40)

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

    def move(self):
        # The current noise level your character is standing on
        value = simplex_noise((self.locsize.x - self.base.x) // TILE_SIZE, 
                        (self.locsize.y - self.base.y) // TILE_SIZE)

        # Changing the speed of your player depending on what terrain their standing on
        if value < Render.water:
            self.in_water = True
        else:
            self.in_water = False
        
        # moving depending on if there is a coordinate to follow
        if self.coordinate != None:
            self.is_moving = True
            displaced = rl.Vector2(self.coordinate.x - self.locsize.x + self.base.x, self.coordinate.y - self.locsize.y + self.base.y)
            length = math.sqrt(displaced.x**2 + displaced.y**2)
            if length != 0:
                dir_vec = rl.Vector2(displaced.x / length, displaced.y / length)
                self.locsize.x += dir_vec.x * self.speed * raylib.GetFrameTime()
                self.locsize.y += dir_vec.y * self.speed * raylib.GetFrameTime()
        else:
            self.is_moving = False