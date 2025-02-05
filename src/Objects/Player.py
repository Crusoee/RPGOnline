import raylib
import pyray as rl
import math

from Misc.Helper import select_player, distance
from Misc.CONSTANTS import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, CHUNK_SIZE, PLAYER_HEIGHT, PLAYER_WIDTH

from Generation.Generation import simplex_noise
import Generation.Generation as Generation

from Objects.Object import Object

class Player(Object):
    def __init__(self, name, x, y, texture):
        super().__init__(name, x, y, texture, PLAYER_WIDTH, PLAYER_HEIGHT)

        self.angle = -90
        self.animcntr = 0
        self.base = rl.Vector2(-int(PLAYER_WIDTH / 2), -PLAYER_HEIGHT)
        
        self.respawn = rl.Vector2(self.updates['x'],self.updates['y'])
        self.prev_locsize = rl.Vector2(self.updates['x'] - self.base.x,self.updates['y'] - self.base.y)

    def draw(self):

        if self.animcntr <= -4:
            self.animcntr = 0

        if self.updates['swim']:
            if self.updates['coord'] != None:
                if -135 < self.angle <= -45:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle((256 * math.floor(self.animcntr)),0,256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,self.texture['player'].width/10, self.texture['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if -45 < self.angle <= 45:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle((256 * math.floor(self.animcntr)),(256 * 3),256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,self.texture['player'].width/10, self.texture['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if 45 < self.angle <= 135:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle((256 * math.floor(self.animcntr)),(256 * 1),256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,self.texture['player'].width/10, self.texture['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if self.angle <= -135 or self.angle > 135:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle((256 * math.floor(self.animcntr)),(256 * 2),256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,self.texture['player'].width/10, self.texture['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                    
                # self.animcntr -= rl.get_frame_time() * (self.stats['swmspeed'] / 25 * self.stats['hinderedspeedmult'])
            else:
                if -135 < self.angle <= -45:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle((0),0,256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,self.texture['player'].width/10, self.texture['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if -45 < self.angle <= 45:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle((0),(256 * 3),256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,self.texture['player'].width/10, self.texture['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if 45 < self.angle <= 135:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle((0),(256 * 1),256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,self.texture['player'].width/10, self.texture['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if self.angle <= -135 or self.angle > 135:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle((0),(256 * 2),256, 150), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10 + 34,self.texture['player'].width/10, self.texture['player'].height/10 - 47), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)

                # self.animcntr = 0
        else:
            if self.updates['coord'] != None:
                if -135 < self.angle <= -45:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle((256 * math.floor(self.animcntr)),0,256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,self.texture['player'].width/10, self.texture['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if -45 < self.angle <= 45:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle((256 * math.floor(self.animcntr)),(256 * 3),256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,self.texture['player'].width/10, self.texture['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if 45 < self.angle <= 135:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle((256 * math.floor(self.animcntr)),(256 * 1),256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,self.texture['player'].width/10, self.texture['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if self.angle <= -135 or self.angle > 135:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle((256 * math.floor(self.animcntr)),(256 * 2),256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,self.texture['player'].width/10, self.texture['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                    
                # self.animcntr -= rl.get_frame_time() * (self.stats['speed'] / 25 * self.stats['hinderedspeedmult'])
            else:
                if -135 < self.angle <= -45:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle(0,0,256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,self.texture['player'].width/10, self.texture['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if -45 < self.angle <= 45:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle(0,(256 * 3),256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,self.texture['player'].width/10, self.texture['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if 45 < self.angle <= 135:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle(0,(256 * 1),256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,self.texture['player'].width/10, self.texture['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)
                if self.angle <= -135 or self.angle > 135:
                    rl.draw_texture_pro(self.texture['player'], rl.Rectangle(0,(256 * 2),256, 256), 
                                        rl.Rectangle(self.updates['x'] - 31,self.updates['y'] - 10,self.texture['player'].width/10, self.texture['player'].height/10), 
                                        rl.Vector2(0,0),
                                        0.0, 
                                        rl.WHITE)

                # self.animcntr = 0


        text_size = rl.measure_text_ex(self.texture["name_font"], self.updates['nme'], 30, 0.0)
        rl.draw_text_ex(self.texture["name_font"], self.updates['nme'], rl.Vector2(int(self.updates['x'] - (text_size.x / 2) + PLAYER_WIDTH / 2), int(self.updates['y'] - 80)), 40, 0.0, rl.BLACK)

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

        rl.draw_texture_pro(self.texture["healthframe"], rl.Rectangle(0,0,self.texture["healthframe"].width, self.texture["healthframe"].height), 
                    rl.Rectangle(base_x, base_y, 80, 20), 
                    rl.Vector2(0,0),
                    0.0, 
                    rl.WHITE)
        rl.draw_texture_pro(self.texture["healthbar"], rl.Rectangle(0,0,self.texture["healthbar"].width * health_ratio, self.texture["healthbar"].height), 
                    rl.Rectangle(base_x, base_y, 80 * health_ratio, 20), 
                    rl.Vector2(0,0),
                    0.0, 
                    rl.WHITE)
        rl.draw_texture_pro(self.texture["healthframe"], rl.Rectangle(0,0,self.texture["healthframe"].width, self.texture["healthframe"].height), 
                    rl.Rectangle(base_x, base_y + 12, 80, 20), 
                    rl.Vector2(0,0),
                    0.0, 
                    rl.WHITE)
        rl.draw_texture_pro(self.texture["Energybar"], rl.Rectangle(0,0,self.texture["Energybar"].width * energy_ratio, self.texture["Energybar"].height), 
                    rl.Rectangle(base_x, base_y + 15, 80 * energy_ratio, 10), 
                    rl.Vector2(0,0),
                    0.0, 
                    rl.WHITE)
        rl.draw_texture_pro(self.texture["Magicbar"], rl.Rectangle(0,0,self.texture["Magicbar"].width * magic_ratio, self.texture["Magicbar"].height), 
                    rl.Rectangle(base_x, base_y + 20, 80 * magic_ratio, 10), 
                    rl.Vector2(0,0),
                    0.0, 
                    rl.WHITE)

        # rl.end_shader_mode()

        # if self.attacking == True:
        #     rl.draw_circle(int(self.updates['x'] - self.base.x),int(self.updates['y'] - self.base.y / 2),self.distance,rl.Color(255,255,0,100))


    # def update_state(self):
    #     # The current noise level your character is standing on
    #     value = simplex_noise((self.updates['x'] - self.base.x) // TILE_SIZE, 
    #                     (self.updates['y'] - self.base.y) // TILE_SIZE)

    #     # Changing the speed of your player depending on what terrain their standing on
    #     if value < Generation.water:
    #         self.player.speed = self.player.stats['swmspeed'] * self.player.stats['hinderedspeedmult']
    #         self.player.updates['swim'] = True
    #     else:
    #         self.player.speed = self.player.stats['speed'] * self.player.stats['hinderedspeedmult']
    #         self.player.updates['swim'] = False

    def move(self):

        # The current noise level your character is standing on
        value = simplex_noise((self.updates['x'] - self.base.x) // TILE_SIZE, 
                        (self.updates['y'] - self.base.y) // TILE_SIZE)

        if value < Generation.water:
            self.updates['swim'] = True
        else:
            self.updates['swim'] = False

        # moving depending on if there is a updates['coord'] to follow
        if self.updates['action']['type'] != None:
            self.is_moving = distance(self.updates['x'] - self.base.x,self.updates['y'] - self.base.y, self.updates['coord'][0], self.updates['coord'][1]) > self.stats['attackingdist']
        else:
            self.is_moving = distance(self.updates['x'] - self.base.x,self.updates['y'] - self.base.y, self.updates['coord'][0], self.updates['coord'][1]) > 1.0
        
        if self.is_moving:
            self.animcntr -= rl.get_frame_time() * (self.stats['speed'] / 25 * self.stats['hinderedspeedmult'])
            # self.is_moving = True
            displaced = rl.Vector2(self.updates['coord'][0] - self.updates['x'] + self.base.x, self.updates['coord'][1] - self.updates['y'] + self.base.y)
            self.angle = math.degrees(math.atan2(-displaced.y, displaced.x))
            length = math.sqrt(displaced.x**2 + displaced.y**2)
            if length != 0:
                dir_vec = rl.Vector2(displaced.x / length, displaced.y / length)
                if value < Generation.water:
                    self.updates['x'] += dir_vec.x * self.stats['swmspeed'] * self.stats['hinderedspeedmult'] * raylib.GetFrameTime()
                    self.updates['y'] += dir_vec.y * self.stats['swmspeed'] * self.stats['hinderedspeedmult'] * raylib.GetFrameTime()
                else:
                    self.updates['x'] += dir_vec.x * self.stats['speed'] * self.stats['hinderedspeedmult'] * raylib.GetFrameTime()
                    self.updates['y'] += dir_vec.y * self.stats['speed'] * self.stats['hinderedspeedmult'] * raylib.GetFrameTime()

                # if length < 150.0 * raylib.GetFrameTime():
                #     self.updates['coord'] = None
        else:
            self.animcntr = 0
            # self.is_moving = False

    # def attack_reset(self):
    #     self.attacking = False
    #     self.hit = ''

    # def update(self, shared_memory):
    #     # If my user name that the server recognizes my client as, has my stats in its player database, give me those stats
    #     if self.updates['nme'] in shared_memory['playersinfo'][0].keys():
    #         stats = shared_memory['playersinfo'][0][self.updates['nme']]
    #         self.stats = stats