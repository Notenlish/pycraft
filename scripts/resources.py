from pygame import font, image, Surface
from settings import FONT_SIZE, SKY_COLOR
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
            tile_surf = image.load("appdata/tiles/"+str(i.value)+".png"
                                   ).convert()
            # tile_surf.set_colorkey((0, 0, 0, 0))
            self.tile_sprs[i.value] = tile_surf
