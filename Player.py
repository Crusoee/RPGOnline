import raylib
import pyray as rl
import math
from LoadRectangle import get_rectangle

from SimplexNoise import simplex_noise
import Render
from CONSTANTS import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, CHUNK_SIZE

class Player():
    def __init__(self, color, locsize, speed):
        self.health = 10
        self.damage = 1
        self.magic = 1
        self.armor = 0

        self.speed = speed
        self.color = color

        self.prev_locsize = locsize
        self.locsize = locsize

        self.base = rl.Vector2(-locsize.width / 2, -locsize.height)
        self.coordinate = None

        self.camera = rl.Camera2D(
            rl.Vector2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2),  # Offset from the center of the screen
            rl.Vector2(self.locsize.x, self.locsize.y),      # The target position in the world
            0.0,                   # Camera rotation in degrees
            1.0                    # Camera zoom (1.0 is default)
        )

    def draw(self):
        raylib.DrawRectangleRec(self.locsize, self.color)
        if self.coordinate != None:
            raylib.DrawCircle(int(self.coordinate.x), int(self.coordinate.y), 5.0, rl.YELLOW)

    def collision(self, collidable_objects):
        for object in collidable_objects:
            if raylib.CheckCollisionRecs(self.locsize, object):
                
                # Left
                if self.prev_locsize.x + self.prev_locsize.width <= object.x:
                    self.locsize.x = object.x - self.locsize.width
                    print("left")
                    break
                # Right
                if self.prev_locsize.x >= object.x + object.width:
                    self.locsize.x = object.x + object.width
                    print("right")
                    break
                # Top
                if self.prev_locsize.y + self.prev_locsize.height <= object.y:
                    self.locsize.y = object.y - self.locsize.height
                    print("top")
                    break
                # Bottom
                if self.prev_locsize.y >= object.y + object.height:
                    self.locsize.y = object.y + object.height
                    print("botttom")
                    break

    def move(self, chunk_data):

        value = simplex_noise(self.locsize.x // TILE_SIZE, 
                        self.locsize.y // TILE_SIZE)

        if value < Render.water:
            self.speed = 150
        else:
            self.speed = 300

        if raylib.IsMouseButtonDown(raylib.MOUSE_BUTTON_RIGHT):
            mouse_position_window = rl.get_mouse_position()
            self.coordinate = rl.Vector2(
                (mouse_position_window.x - self.camera.offset.x) / self.camera.zoom + self.camera.target.x,
                (mouse_position_window.y - self.camera.offset.y) / self.camera.zoom + self.camera.target.y
            )

        if self.coordinate != None:
            displaced = rl.Vector2(self.coordinate.x - self.locsize.x + self.base.x, self.coordinate.y - self.locsize.y + self.base.y)
            length = math.sqrt(displaced.x**2 + displaced.y**2)
            if length != 0:
                dir_vec = rl.Vector2(displaced.x / length, displaced.y / length)
                self.locsize.x += dir_vec.x * self.speed * raylib.GetFrameTime()
                self.locsize.y += dir_vec.y * self.speed * raylib.GetFrameTime()
                if length < 150.0 * raylib.GetFrameTime():
                    self.coordinate = None

        self.camera.target.x = self.locsize.x
        self.camera.target.y = self.locsize.y

        self.collision(chunk_data[int(self.locsize.x // (TILE_SIZE * CHUNK_SIZE)), int(self.locsize.y // (TILE_SIZE * CHUNK_SIZE))][1])

        self.prev_locsize = self.locsize

    def select(self, shared_memory):
        if raylib.IsMouseButtonPressed(raylib.MOUSE_BUTTON_LEFT):
            mouse_position_window = rl.get_mouse_position()
            select_coordinate = rl.Vector2(
                (mouse_position_window.x - self.camera.offset.x) / self.camera.zoom + self.camera.target.x,
                (mouse_position_window.y - self.camera.offset.y) / self.camera.zoom + self.camera.target.y
            )

            for key, value in shared_memory['players'][0].items():
                if key == shared_memory['user']:
                    continue
                if raylib.CheckCollisionPointRec(select_coordinate, get_rectangle(shared_memory['players'][0][key])):
                    print(f'{shared_memory['players'][0][key][2]}, {shared_memory['players'][0][key][3]}, {shared_memory['players'][0][key][4]}, {shared_memory['players'][0][key][5]}')