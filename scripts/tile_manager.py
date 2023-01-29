from pygame import surface, draw
from typing import Dict
from settings import (CHUNK_RADIUS, CHUNK_WIDTH,
                      CHUNK_HEIGHT, BLOCK_PIXEL_SIZE,
                      CHUNK_GROUND_BASE, PERLIN_MULTIPLIER,
                      SKY_COLOR)
from scripts.tiles import TILES, TRANSPARENT_BLOCKS
from os import listdir, remove
import opensimplex
import json
import random
import time
import threading


def threaded(fn):
    def wrapper(*args, **kwargs):
        # we make it a daemon thread so that the thread is
        # deleted when the main thread exits
        thread = threading.Thread(
            target=fn, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread
    return wrapper


def clamp_chunk_width(val):
    return max(0, min(val, CHUNK_WIDTH-1))


def clamp_chunk_height(val):
    return max(0, min(val, CHUNK_HEIGHT-1))


class TileManager:
    def __init__(self, app, tile_sprs, camera):
        self.app = app
        self.tile_sprs = tile_sprs
        self.camera = camera
        self.centerpos = 0
        self.loaded_chunks: Dict[str, dict] = {}
        self.generated_chunks = []
        self.chunkradius = CHUNK_RADIUS
        self.testmode = False
        self.thread = None
        self.inmap = False

    def load_map(self):
        with open("world/info.json", "r") as f:
            map_data = json.load(f)

        self.centerpos = map_data["player"]["chunkpos"]
        self.app.player.pos = map_data["player"]["playerpos"]
        self.generated_chunks = map_data["generated_chunks"]
        self.seed = map_data["map_seed"]
        opensimplex.seed(self.seed)
        self.inmap = True

        self.thread = self.manage_chunks()

    def loadchunk(self, chunkpos):
        try:
            with open("world/chunks/"+f"{chunkpos}.chunk",
                      "r") as chunkfile:
                chunkdata = json.load(chunkfile)
                self.loaded_chunks[chunkpos] = {
                    "tiledata": chunkdata["tiledata"],
                    "entitydata": chunkdata["entitydata"],
                    "lightdata": chunkdata["lightdata"],
                    "image": self.render_chunk(
                        chunkdata["tiledata"], chunkdata["lightdata"])
                    }
                print(f"LOADED CHUNK {chunkpos}")
                self.generated_chunks.append(chunkpos)
                return True
        except FileNotFoundError:
            return FileNotFoundError

    def draw(self, surf):
        for x in range(self.centerpos - (CHUNK_WIDTH//2),
                       self.centerpos + (CHUNK_WIDTH//2)):
            try:
                surf.blit(self.loaded_chunks[x]["image"],
                      (x*CHUNK_WIDTH*BLOCK_PIXEL_SIZE - self.camera.pos[0],
                       -self.camera.pos[1]))
            except KeyError:  # hasnt been generated yet
                draw.rect(surf, "black", (x*CHUNK_WIDTH*BLOCK_PIXEL_SIZE-self.camera.pos[0], -self.camera.pos[1], CHUNK_WIDTH*BLOCK_PIXEL_SIZE, CHUNK_HEIGHT*BLOCK_PIXEL_SIZE))

    def set_centerpos(self, new_x: int):
        self.calc_centerpos(new_x)

    def calc_centerpos(self, new_x):
        self.centerpos = new_x//(CHUNK_WIDTH*BLOCK_PIXEL_SIZE)  # update pos

    @threaded
    def manage_chunks(self):
        while self.inmap:
            center_chunkx = self.centerpos
            for x in range(center_chunkx - self.chunkradius,
                           center_chunkx + self.chunkradius):
                if self.loaded_chunks.get(x):  # Chunk Found
                    pass
                else:  # chunk not found
                    # if we generated it already
                    if x in self.generated_chunks:
                        self.loadchunk(x)
                    else:  # we havent generated the chunk before
                        self.generate_new_chunk(x)
                        # I dont need to call threading.Thread since
                        # the function uses @threaded wrapper

            chunkstounload = []
            for chunk in self.loaded_chunks:
                # if chunk is far away
                if (abs(chunk - center_chunkx) > self.chunkradius):
                    chunkstounload.append(chunk)

            for c in chunkstounload:
                self.unload_chunk(c)

            time.sleep(1/60)
        print("CHUNK_GENERATOR THREAD will kill itself")

    def unload_all_chunks(self):
        self.inmap = False
        self.thread.join()
        chunks = list(self.loaded_chunks.keys()).copy()
        for c in chunks:
            self.unload_chunk(c)
        print("UNLOADED EVERYTHING")

        with open("world/info.json", "w") as file:
            data = {}
            data["player"] = {
                "chunkpos": self.centerpos,
                "playerpos": self.app.player.pos,
                "inventory": [],
                }
            data["generated_chunks"] = self.generated_chunks
            data["map_seed"] = self.seed
            json.dump(data, file)

        if self.testmode:
            self.delete_all_chunks()

    def unload_chunk(self, chunkpos):
        self.loaded_chunks[chunkpos]
        try:
            with open("world/chunks/"+f"{chunkpos}.chunk",
                      "w") as chunkfile:
                self.loaded_chunks[chunkpos].pop("image")
                # idk if this is a good way to remove image from chunk
                json.dump(self.loaded_chunks[chunkpos], chunkfile)

            self.loaded_chunks.pop(chunkpos)
            print(f"UNLOADED CHUNK: {chunkpos}")
        except FileNotFoundError:
            return FileNotFoundError

    def calc_block(self, x, y, ground_level, biome_tile, biome_tile2):
        filled = True
        block_to_use = 11
        if y < ground_level:  # air
            filled = False

        if filled:
            # to determine if its a cave
            noise_val = opensimplex.noise2(x=x/CHUNK_WIDTH,
                                           y=y*3/CHUNK_HEIGHT)
            if ((noise_val > -0.9 and noise_val < -0.6) or
                    (noise_val > 0.7)):  # cave
                block_to_use = TILES.AIR.value
            else:
                if y == ground_level:
                    block_to_use = biome_tile
                if y > ground_level:
                    if y > ground_level*1.3:
                        block_to_use = TILES.STONE.value
                    else:
                        block_to_use = biome_tile2
        if not filled:
            block_to_use = TILES.AIR.value
        return block_to_use

    def get_plant_types(self, biome_tile):
        grassland = [TILES.GRASS_PLANT, TILES.GRASS_PLANT,
                     TILES.GRASS_PLANT, TILES.GRASS_PLANT,
                     TILES.RED_FLOWER, TILES.YELLOW_FLOWER]

        desert = [TILES.DEAD_SHRUB, TILES.AIR]
        arctic = [TILES.AIR]

        if biome_tile == TILES.GRASS_BLOCK.value:
            return grassland
        elif biome_tile == TILES.SAND.value:
            return desert
        elif biome_tile == TILES.SNOW_BLOCK.value:
            return arctic

    def can_place_structure(self, x, y, biome_tile, chunkdata, horizontal, vertical):
        # TODO: instead of doing it like this just make
        # it 2 for loops.
        result = []
        for el1 in horizontal:
            for el2 in vertical:
                result.append((clamp_chunk_width(el1),
                               clamp_chunk_height(el2)))
        can_place = True
        if chunkdata[y][x] == biome_tile:
            for nearx, neary in result:
                tile = chunkdata[neary][nearx]
                if (tile != TILES.AIR.value):
                    can_place = False
                    break
        else:
            can_place = False
        return can_place

    def generate_vegetation(self, chunkdata, biome_tile):
        for _ in range(2):
            # I dont want to create a new cache just so tree leaves
            # dont cut out so I'm just gonna make it from 1 to 6
            x = random.randint(1, CHUNK_WIDTH-2)
            for y in range(0, CHUNK_HEIGHT):
                # current_tile = chunkdata[y][x]
                if biome_tile == TILES.GRASS_BLOCK.value:
                    can_place = self.can_place_structure(
                        x, y, biome_tile, chunkdata,
                        [x-1, x, x+1], [y-1, y-2, y-3, y-4])

                    if can_place:
                        self.place_tree(chunkdata, x, y)
                        break  # stop going down
                elif biome_tile == TILES.SAND.value:
                    can_place = self.can_place_structure(
                        x, y, biome_tile, chunkdata, [x], [y-1, y-2, y-3])
                    if can_place:
                        self.place_cactus(chunkdata, x, y)
                        break
                else:  # not a biome that has vegetation
                    break
        plant_types = self.get_plant_types(biome_tile)
        for x in range(0, CHUNK_WIDTH):
            for y in range(0, CHUNK_HEIGHT):
                if (chunkdata[y][x] == biome_tile and
                   chunkdata[y-1][x] == TILES.AIR.value):
                    if random.choice([True, False]):
                        chunkdata[y-1][x] = random.choice(plant_types).value
                    break  # stop going down

    def place_cactus(self, chunkdata, x, y):
        yval = clamp_chunk_height(y-1)
        xval = clamp_chunk_width(x)
        chunkdata[yval][xval] = TILES.CACTUS.value
        yval = clamp_chunk_height(y-2)
        xval = clamp_chunk_width(x)
        chunkdata[yval][xval] = TILES.CACTUS.value

    def place_tree(self, chunkdata, x, y):
        chunkdata[clamp_chunk_height(
            y-1)][clamp_chunk_width(x)] = TILES.LOG.value
        chunkdata[clamp_chunk_height(
            y-2)][clamp_chunk_width(x)] = TILES.LOG.value
        chunkdata[clamp_chunk_height(
            y-3)][clamp_chunk_width(x)] = TILES.LOG.value
        chunkdata[clamp_chunk_height(
            y-3)][clamp_chunk_width(x-1)] = TILES.LEAVES.value
        chunkdata[clamp_chunk_height(
            y-3)][clamp_chunk_width(x+1)] = TILES.LEAVES.value
        chunkdata[clamp_chunk_height(
            y-4)][clamp_chunk_width(x-1)] = TILES.LEAVES.value
        chunkdata[clamp_chunk_height(
            y-4)][clamp_chunk_width(x)] = TILES.LEAVES.value
        chunkdata[clamp_chunk_height(
            y-4)][clamp_chunk_width(x+1)] = TILES.LEAVES.value

    def calculate_biome(self, val):
        if val < -0.5:
            return TILES.SNOW_BLOCK.value, TILES.SNOW_BLOCK.value
        if val > 0.5:
            return TILES.SAND.value, TILES.SAND.value
        else:
            return TILES.GRASS_BLOCK.value, TILES.DIRT.value

    def generate_chunk_terrain(self, chunkpos):
        chunkdata = [[] for x in range(CHUNK_HEIGHT)]
        xstart, xend = chunkpos * CHUNK_WIDTH, (chunkpos+1) * CHUNK_WIDTH
        tile_x = 0
        biome_tile, biome_tile2 = self.calculate_biome(opensimplex.noise2(x=xstart/CHUNK_WIDTH/6, y=4))
        for x in range(xstart, xend):
            x *= 0.6
            ground_level = opensimplex.noise2(x=x/CHUNK_WIDTH/2, y=5)
            ground_level = int(ground_level * PERLIN_MULTIPLIER)
            ground_level = CHUNK_GROUND_BASE - ground_level

            for y in range(CHUNK_HEIGHT):
                block_to_use = self.calc_block(x, y, ground_level, biome_tile, biome_tile2)
                chunkdata[y].append(block_to_use)
            tile_x += 1

        self.generate_ores(chunkdata)
        self.generate_vegetation(chunkdata, biome_tile)

        for x in range(0, CHUNK_WIDTH):  # bedrock
            chunkdata[CHUNK_HEIGHT-1][x] = TILES.BEDROCK.value

        return chunkdata

    def generate_lightdata(self, tiledata):
        # 15 = completely dark
        lightdata = [[None]*CHUNK_WIDTH for _ in range(CHUNK_HEIGHT)]
        lightdata[0] = [0]*CHUNK_WIDTH
        x, y = 0, 0
        for line in lightdata:
            x = 0
            for lightval in line:
                if lightval is None:
                    value_to_add = 0
                    blocks = [(x, y), (x, y-1), (x-1, y), (x+1, y)]
                    for xval, yval in blocks:
                        yval = clamp_chunk_height(yval)
                        foundblock = True
                        if xval < 0 or xval >= CHUNK_WIDTH:  # out of bounds
                            try:
                                block = self.loaded_chunks[xval//CHUNK_WIDTH]["tiledata"]
                            except KeyError:
                                foundblock = False
                        else:
                            block = tiledata[yval][xval]
                        if foundblock:
                            if block not in TRANSPARENT_BLOCKS:
                                value_to_add += 1  # make it darker

                    lightval = lightdata[y-1][x] + value_to_add
                    lightdata[y][x] = lightval
                x += 1
            y += 1
        return lightdata

    def generate_new_chunk(self, chunkpos):
        start_time = time.time()
        print(f"Started generating chunk {chunkpos} with thread")
        tiledata = self.generate_chunk_terrain(chunkpos)
        lightdata = self.generate_lightdata(tiledata)
        self.loaded_chunks[chunkpos] = {
                    "tiledata": tiledata,  # maybe np array?
                    "entitydata": [],  # array([])}
                    "lightdata": lightdata,  # TODO: add func
                    "image": self.render_chunk(tiledata, lightdata)
                    }
        self.generated_chunks.append(chunkpos)
        print(f"generated chunk {chunkpos} in {time.time()-start_time} seconds")

    def generate_ores(self, chunkdata):
        # we have added every block now we can create ores, trees etc.
        for _ in range(10):
            val = random.randint(0, 9)
            xpos = random.randint(0, CHUNK_WIDTH-1)
            ypos = random.randint(0, CHUNK_HEIGHT-1)
            if chunkdata[ypos][xpos] == TILES.STONE.value:
                orex, orey = xpos, ypos
                # place iron
                ore_direction = [random.choice([-1, 0, 1]),
                                 random.choice([-1, 0, 1])]
                length = random.choice([1, 2, 3])
                size_multiplier = random.choice([0, 1])

                ore = self.generate_ore_type(val, orey)

                for i in range(length):
                    for xs in range(orex-size_multiplier, orex+size_multiplier):
                        for ys in range(orey-size_multiplier, orey+size_multiplier):
                            try:
                                ys = ys + (i*ore_direction[1])
                                xs = xs + (i*ore_direction[0])
                                if chunkdata[ys][xs] == TILES.STONE.value:
                                    row = chunkdata[ys]
                                    row[xs] = ore
                            except IndexError:  # If it goes beyond chunk bound
                                pass

    def generate_ore_type(self, val, y):
        # coal will be everywhere and if the val is 4 or lower
        # iron will be everywhere too and occurs if the val == 5 and 6
        # gold will be if y<= CHUNK_HEIGHT*0.7 and val == 7
        # diamons will be if y<= CHUNK_HEIGHT*0.7 and val == 8
        if val <= 3:
            return TILES.COAL_ORE.value
        if val >= 4 and val <= 7:
            return TILES.IRON_ORE.value
        if val == 8 and y >= CHUNK_HEIGHT*0.8:
            return TILES.GOLD_ORE.value
        if val == 9 and y >= CHUNK_HEIGHT*0.8:
            return TILES.DIAMOND_ORE.value
        return random.choice([TILES.COAL_ORE.value, TILES.IRON_ORE.value])

    def render_chunk(self, terraindata, lightdata):
        chunk_surf = surface.Surface((CHUNK_WIDTH*BLOCK_PIXEL_SIZE,
                                      CHUNK_HEIGHT*BLOCK_PIXEL_SIZE))
        chunk_surf.fill(SKY_COLOR)
        opacity_surf = surface.Surface((16, 16))
        opacity_surf.fill("black")

        x, y = 0, 0
        for line in terraindata:
            x = 0
            for tile in line:
                light_level = lightdata[y][x]
                opacity_surf.set_alpha(light_level*17)
                tile_surf = self.tile_sprs[tile].copy()
                tile_surf.blit(opacity_surf, (0, 0))

                chunk_surf.blit(tile_surf, (
                    x*BLOCK_PIXEL_SIZE, y*BLOCK_PIXEL_SIZE))
                x += 1
            y += 1
        draw.line(chunk_surf, (0, 25, 255), (0, 0),
                  (0, CHUNK_HEIGHT*BLOCK_PIXEL_SIZE), 2)

        return chunk_surf

    def reset_map(self):
        self.inmap = False
        self.thread.join()

        self.loaded_chunks = {}
        self.generated_chunks = []
        self.delete_all_chunks()

        self.inmap = True
        self.thread = self.manage_chunks()

    def delete_all_chunks(self):
        path = "world/chunks/"
        chunkfiles = listdir(path)
        for f in chunkfiles:
            remove(path+f)
        print("DELETED EVERY CHUNK")

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
