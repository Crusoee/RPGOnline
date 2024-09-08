import pyray as rl
import raylib

def get_rectangle(data):
    return rl.Rectangle(data[0]['x'],data[0]['y'],40,80)