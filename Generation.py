import random
import pyray as rl


def landmark_generation():
    landmarks = []
    for _ in range(1000):
        # Generate random integers
        x = random.randint(-2000, 2000)
        y = random.randint(-2000, 2000)
        width = random.randint(20, 100)
        height = random.randint(20, 100)
        
        # Write the integers to the file as a formatted string
        landmarks.append([x,y,width,height])
    return landmarks

def color_generation():
    colors = []
    for _ in range(1000):
        # Generate random integers
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        a = random.randint(0, 255)
        
        # Write the integers to the file as a formatted string
        colors.append([r,g,b,a])
    return colors

def unpack_landmarks(landmarks):
    unpacked_landmarks = []
    for i in landmarks:
        unpacked_landmarks.append(rl.Rectangle(i[0],i[1],i[2],i[3]))
    return unpacked_landmarks

def unpack_colors(colors):
    unpacked_colors = []
    for i in colors:
        unpacked_colors.append(rl.Color(i[0],i[1],i[2],i[3]))
    return unpacked_colors
