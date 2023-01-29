from pygame import (key, rect, K_w, K_UP, K_a, K_LEFT,
                    K_s, K_DOWN, K_d, K_RIGHT, mouse)
from scripts.object import Object
from settings import (CHUNK_WIDTH, CHUNK_HEIGHT,
                      CAMERA_OFFSET, PLAYER_SPEED, BLOCK_PIXEL_SIZE)
from scripts.tiles import TILES

# TODO: I NEED TO MAKE COLLISION AND GRAVITY (LOL)


def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))


class Player(Object):
    def __init__(self, app, pos, spr):
        self.app = app
        super().__init__(spr, pos, self.app.camera)
        self.rect: rect.Rect = rect.Rect(self.pos[0],
                                         self.pos[1],
                                         self.spr.get_width(),
                                         self.spr.get_height())
        self.currentblock = 0
        self.selected_block_chunky = 0
        self.selected_block_chunkx = 0

    def change_block(self, y: int):
        self.currentblock = (self.currentblock+y) % len(TILES)

    def move(self, dt):
        keys = key.get_pressed()

        xmov: int = 0
        ymov: int = 0
        if keys[K_w] or keys[K_UP]:
            ymov = -1

        if keys[K_a] or keys[K_LEFT]:
            xmov = -1

        if keys[K_s] or keys[K_DOWN]:
            ymov = 1

        if keys[K_d] or keys[K_RIGHT]:
            xmov = 1

        self.pos[0] += xmov*PLAYER_SPEED*dt*0.1
        self.pos[1] += ymov*PLAYER_SPEED*dt*0.1
        self.rect.x = self.pos[0]  # Maybe round or int this?
        self.rect.y = self.pos[1]
        self.app.tile_manager.set_centerpos(int(self.pos[0]))
        self.camera.update_pos((int(self.pos[0] + CAMERA_OFFSET),
                                int(self.pos[1] + CAMERA_OFFSET)))
        # Maybe make it CHUNK_HEIGHT?
        # I think making these int does kinda solve screen tearing/player
        # just moving 1 pixel too high up sometimes

    def block_calc(self, mpos):
        if mouse.get_pressed()[0]:
            outofbounds = False
            blockx = int(mpos[0] + self.pos[0] + CAMERA_OFFSET)//BLOCK_PIXEL_SIZE
            blocky = int((mpos[1] + self.pos[1] + CAMERA_OFFSET)//BLOCK_PIXEL_SIZE)

            if clamp(0, blocky, CHUNK_HEIGHT-1) != blocky:
                outofbounds = True

            try:
                selected_chunk = self.app.tile_manager.loaded_chunks[blockx // CHUNK_WIDTH]
            except KeyError:
                outofbounds = True

            if not outofbounds:
                self.selected_block_chunkx = blockx % CHUNK_WIDTH
                self.selected_block_chunky = blocky
                selected_chunk["tiledata"][self.selected_block_chunky][
                    self.selected_block_chunkx] = self.currentblock

                selected_chunk[
                    "lightdata"] = self.app.tile_manager.generate_lightdata(
                        selected_chunk["tiledata"], blockx//CHUNK_WIDTH)
                selected_chunk["image"] = self.app.tile_manager.render_chunk(
                    selected_chunk["tiledata"], selected_chunk["lightdata"])

    def update(self, dt, mpos):
        self.move(dt)
        self.block_calc(mpos)

    def draw(self, surf):
        pos_to_draw = (self.pos[0] - self.camera.pos[0],
                       self.pos[1] - self.camera.pos[1])
        # draw.circle(surf, "red", pos_to_draw, 20)
        surf.blit(self.spr, pos_to_draw)
