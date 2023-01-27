import pygame as pg
import sys
from settings import WINDOW_SIZE, FLAGS, SKY_COLOR
from scripts.resources import Resources
from scripts.start_screen import StartScreen
from scripts.tile_manager import TileManager
from scripts.player import Player
from scripts.camera import camera


class APP:
    def __init__(self):
        self.window = pg.display.set_mode(WINDOW_SIZE, FLAGS)
        self.clock = pg.time.Clock()
        self.dt = 0
        self.res = Resources()
        self.mode = "start"
        self.mpos = (0, 0)

    def start_app(self):
        self.start_screen = StartScreen(self, self.res.menufont,
                                        120, 100, WINDOW_SIZE[0]//2)

    def load_map(self):
        self.res.loadtextures()
        self.camera = camera((0, 0))

        self.tile_manager = TileManager(self.res.tile_sprs, self.camera)
        self.tile_manager.load_map()
        self.player = Player(self, [200, 200],
                             self.res.playertextures["idle"])

        self.mode = "game"

    def start_new_map(self):
        pass

    def exit(self):
        if self.mode == "game":
            self.tile_manager.unload_all_chunks()
        sys.exit()

    def run(self):
        self.start_app()

        while True:
            self.dt = self.clock.tick(60)
            self.input()

            self.update()
            self.draw()

            pg.display.update()

    def debug_draw(self):
        self.window.blit(self.res.menufont.render(str(
            len(self.tile_manager.loaded_chunks)) +
            " chunks", False, "green"), (0, 0))
        self.window.blit(self.res.menufont.render("pos: " + str(
            self.tile_manager.centerpos), False, "green"), (0, 20))
        mbsize = str(sys.getsizeof(self.tile_manager.generated_chunks)/1024/1024)
        self.window.blit(self.res.menufont.render("Gen: {}".format(mbsize[:5]),
                                                  False, "green"), (0, 40))
        self.window.blit(self.res.menufont.render("x:{} y:{} block:{}".format(
            self.player.selected_block_chunkx,
            self.player.selected_block_chunky,
            self.player.currentblock), False, "green"), (0, 60))

    def input(self):
        self.mpos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.mode == "start":
                    self.start_screen.select(self.mpos)
            if event.type == pg.MOUSEWHEEL:
                if self.mode == "game":
                    self.player.change_block(event.y)

    def update(self):
        if self.mode == "game":
            self.player.update(self.dt, self.mpos)

    def draw(self):
        self.window.fill(SKY_COLOR)
        if self.mode == "start":
            self.start_screen.draw(self.window)
        elif self.mode == "game":
            self.tile_manager.draw(self.window)
            self.player.draw(self.window)
            self.debug_draw()


if __name__ == '__main__':
    app = APP()
    app.run()
