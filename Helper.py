import pyray as rl
import raylib
import math
from CONSTANTS import PLAYER_HEIGHT, PLAYER_WIDTH

def select_player(data):
    return rl.Rectangle(data['x'] - 25,data['y'] - 25,PLAYER_WIDTH + 50,PLAYER_HEIGHT + 50)

def dict_set(setto, setfrom, setlist):
    if setlist not in setfrom.keys() or setto not in setfrom.keys():
        print("item not in list")
        raise KeyError
    
    for key in setlist:
        setto[key] = setfrom[key]

    return setto

def distance(x1,y1,x2,y2):
    return math.sqrt(abs((x2 - x1)**2 + (y2 - y1)**2))