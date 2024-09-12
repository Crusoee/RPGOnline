import pyray as rl
import raylib
import math

def get_rectangle(data):
    return rl.Rectangle(data['x'],data['y'],40,80)

def dict_set(setto, setfrom, setlist):
    if setlist not in setfrom.keys() or setto not in setfrom.keys():
        print("item not in list")
        raise KeyError
    
    for key in setlist:
        setto[key] = setfrom[key]

    return setto

def distance(x1,y1,x2,y2):
    return abs(math.sqrt(x1**2 + y1**2) - math.sqrt(x2**2 + y2**2))