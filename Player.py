import raylib
import pyray as rl
import math
from SimplexNoise import simplex_noise
import Render

from CONSTANTS import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE

class Player():
    def __init__(self, color, locsize, speed):
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

    def collision(self, collidable_objects):
        for object in collidable_objects:
            if raylib.CheckCollisionRecs(self.locsize, collidable_objects):
                if self.prev_locsize.x + self.prev_locsize.x <= collidable_objects.x:
                    self.locsize.x = collidable_objects.x - self.locsize.width
                
                if self.prev_locsize.x >= collidable_objects.x + collidable_objects.width:
                    self.locsize.x = collidable_objects.x + collidable_objects.width
                
                if self.prev_locsize.y + self.prev_locsize.y <= collidable_objects.y:
                    self.locsize.y = collidable_objects.y - self.locsize.height
                
                if self.prev_locsize.y >= collidable_objects.y + collidable_objects.height:
                    self.locsize.y = collidable_objects.y + collidable_objects.height

    def move(self, collidable_objects):

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

        # collision
        self.collision(collidable_objects)

        self.camera.target.x = self.locsize.x
        self.camera.target.y = self.locsize.y

        self.prev_locsize = self.locsize



