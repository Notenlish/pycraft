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
            tile_surf = image.load("appdata/tiles/"+str(i.value)+".png").convert_alpha()
            new_surf = Surface(tile_surf.get_size())
            # fill transparent parts withskycolor
            new_surf.fill(SKY_COLOR)
            new_surf.blit(tile_surf, (0, 0))
            self.tile_sprs[i.value] = new_surf
