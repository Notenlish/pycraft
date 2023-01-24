from pygame import surface
from typing import Dict
from settings import (CHUNK_RADIUS, CHUNK_WIDTH,
                      CHUNK_HEIGHT, BLOCK_PIXEL_SIZE,
                      CHUNK_GROUND_BASE, PERLIN_MULTIPLIER)
from scripts.tiles import TILES
from os import listdir, remove
import opensimplex
import json
import random

# Im just gonna force it by just saving the loaded chunks in map info and
# Ig it will work?
# OK I did the test and it barely makes a dent in the memory like 0.1 mbs for
# like 11.000 chunks so yeah its not a problem


# noise is from -1 to 1
# you can put in any number of arguments so it can be 1d 2d 3d 4d etc
# but it always returns a float


class TileManager:
    def __init__(self, tile_sprs, camera):
        self.tile_sprs = tile_sprs
        self.camera = camera
        self.centerpos = 0
        self.loaded_chunks: Dict[str, dict] = {}
        self.generated_chunks = []
        self.chunkradius = CHUNK_RADIUS
        self.testmode = True
        opensimplex.random_seed()

    def load_map(self):
        with open("worlds/testworld1/info.json", "r") as f:
            map_general_data = json.load(f)

        self.centerpos = map_general_data["player"]["pos"]

        chunkpos = 0
        try:
            self.loadchunk(chunkpos)
            print(f"loaded {chunkpos} chunk")
        except FileNotFoundError:
            print("filenodsadsa")

    def loadchunk(self, chunkpos):
        try:
            with open("worlds/testworld1/chunks/"+f"{chunkpos}.json",
                      "r") as chunkfile:
                chunkdata = json.load(chunkfile)
                self.loaded_chunks[chunkpos] = {
                    "tiledata": chunkdata["tiledata"],
                    "entitydata": chunkdata["entitydata"],
                    "image": self.render_chunk(chunkdata["tiledata"])
                    }
                print(f"LOADED CHUNK {chunkpos}")
                self.generated_chunks.append(chunkpos)
                return True
        except FileNotFoundError:
            return FileNotFoundError

    def draw(self, surf):
        for x in range(self.centerpos - (CHUNK_WIDTH//2),
                       self.centerpos + (CHUNK_WIDTH//2)):
            surf.blit(self.loaded_chunks[x]["image"],
                      (x*CHUNK_WIDTH*BLOCK_PIXEL_SIZE - self.camera.pos[0],
                       -self.camera.pos[1]))

    def set_centerpos(self, new_x: int):
        self.calc(new_x)

    def calc(self, new_x):
        self.centerpos = new_x//(CHUNK_WIDTH*BLOCK_PIXEL_SIZE)  # update pos
        center_chunkx = self.centerpos
        for x in range(center_chunkx - self.chunkradius,
                       center_chunkx + self.chunkradius):
            if self.loaded_chunks.get(x):  # Chunk Found
                pass
            else:
                if x in self.generated_chunks:
                    self.loadchunk(x)
                else:
                    self.generate_new_chunk(x)
        chunkstounload = []
        for chunk in self.loaded_chunks:
            if (abs(chunk - center_chunkx) > self.chunkradius):
                chunkstounload.append(chunk)

        for c in chunkstounload:
            self.unload_chunk(c)

    def unload_all_chunks(self):
        chunks = list(self.loaded_chunks.keys()).copy()
        for c in chunks:
            self.unload_chunk(c)
        if self.testmode:
            path = "worlds/testworld1/chunks/"
            chunkfiles = listdir(path)
            for f in chunkfiles:
                remove(path+f)
        print("UNLOADED EVERYTHING")

    def unload_chunk(self, chunkpos):
        self.loaded_chunks[chunkpos]
        try:
            with open("worlds/testworld1/chunks/"+f"{chunkpos}.json",
                      "w") as chunkfile:
                self.loaded_chunks[chunkpos].pop("image")
                # idk if this is a good way to remove image from chunk
                json.dump(self.loaded_chunks[chunkpos], chunkfile)

            self.loaded_chunks.pop(chunkpos)
            print(f"UNLOADED CHUNK: {chunkpos} chunk")
        except FileNotFoundError:
            return FileNotFoundError

    def calc_block(self, x, y, ground_level):
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
                    block_to_use = TILES.GRASS.value
                if y > ground_level:
                    if y > ground_level*1.3:
                        block_to_use = TILES.STONE.value
                    else:
                        block_to_use = TILES.DIRT.value
        if not filled:
            block_to_use = TILES.AIR.value
        # if y == CHUNK_HEIGHT-1:
        #    block_to_use = TILES.BEDROCK.value
        return block_to_use

    def generate_chunk_terrain(self, chunkpos):
        chunkdata = [[] for x in range(CHUNK_HEIGHT)]
        xstart, xend = chunkpos * CHUNK_WIDTH, (chunkpos+1) * CHUNK_WIDTH
        for x in range(xstart, xend):
            print(f"WUT DA HELL {x} {xstart} {xend}")
            x *= 0.6
            ground_level = opensimplex.noise2(x=x/CHUNK_WIDTH, y=5)
            ground_level = int(ground_level * PERLIN_MULTIPLIER)
            ground_level = CHUNK_GROUND_BASE - ground_level

            for y in range(CHUNK_HEIGHT):
                block_to_use = self.calc_block(x, y, ground_level)
                chunkdata[y].append(block_to_use)

        self.generate_ores(chunkdata)

        for x in range(0, 8):  # bedrock
            chunkdata[CHUNK_HEIGHT-1][x] = TILES.BEDROCK.value

        return chunkdata

    def generate_ores(self, chunkdata):
        # we have added every block now we can create ores, trees etc.
        for _ in range(10):
            val = random.randint(0, 8)
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
                                row = chunkdata[ys + (i*ore_direction[1])]
                                row[xs + (i*ore_direction[0])] = ore
                            except IndexError:  # If it goes beyond chunk bound
                                pass

    def generate_ore_type(self, val, y):
        return TILES.IRON_ORE.value

    def generate_new_chunk(self, chunkpos):
        tiledata = self.generate_chunk_terrain(chunkpos)
        self.loaded_chunks[chunkpos] = {
                    "tiledata": tiledata,  # maybe np array?
                    "entitydata": [],  # array([])}
                    "image": self.render_chunk(tiledata)
                    }
        self.generated_chunks.append(chunkpos)
        print(f"generated chunk [{chunkpos}]")

    def render_chunk(self, terraindata):
        chunk_surf = surface.Surface((CHUNK_WIDTH*BLOCK_PIXEL_SIZE,
                                      CHUNK_HEIGHT*BLOCK_PIXEL_SIZE))
        x, y = 0, 0
        for line in terraindata:
            x = 0
            for tile in line:
                chunk_surf.blit(self.tile_sprs[tile],
                                (x*BLOCK_PIXEL_SIZE, y*BLOCK_PIXEL_SIZE))
                x += 1
            y += 1
        return chunk_surf

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
