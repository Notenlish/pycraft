from pygame import font, image
from settings import FONT_SIZE
from scripts.tiles import TILES
font.init()


class Resources:
    def __init__(self):
        self.menufont = font.Font("appdata/misc/joystix monospace.ttf", FONT_SIZE)

    def loadtextures(self):
        self.playertextures = {
            "idle": image.load("appdata/player/idle.png").convert_alpha()
            }
        self.tile_sprs = {}
        for i in TILES:
            self.tile_sprs[i.value] = image.load("appdata/tiles/"+str(i.value)+".png")
        print(self.tile_sprs)
