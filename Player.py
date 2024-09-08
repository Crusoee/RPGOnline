import raylib
import pyray as rl
import math

from CONSTANTS import SCREEN_WIDTH, SCREEN_HEIGHT

class Player():
    def __init__(self, color, locsize, speed):
        self.speed = speed
        self.color = color
        self.orig_col = color
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

    def move(self):
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


        if raylib.IsKeyDown(raylib.KEY_A):
            self.color = rl.Color(0, 0, 0, 0)
        else:
            self.color = self.orig_col

    def collision(collidable_objects):
        for object in collidable_objects:
            if 
