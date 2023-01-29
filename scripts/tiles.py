from enum import Enum


class TILES(Enum):
    AIR = 0
    DIRT = 1
    GRASS_BLOCK = 2
    STONE = 3
    LOG = 4
    LEAVES = 5
    PLANKS = 6
    SAND = 7
    BEDROCK = 8
    GRAVEL = 9
    COAL_ORE = 10
    IRON_ORE = 11
    GOLD_ORE = 12
    DIAMOND_ORE = 13
    DEAD_SHRUB = 14
    GRASS_PLANT = 15
    RED_FLOWER = 16
    YELLOW_FLOWER = 17
    TREE_SAPLING = 18
    SNOW_BLOCK = 19
    CACTUS = 20


TRANSPARENT_BLOCKS = [
    TILES.AIR.value,
    TILES.LEAVES.value,
    TILES.DEAD_SHRUB.value,
    TILES.GRASS_PLANT.value,
    TILES.RED_FLOWER.value,
    TILES.YELLOW_FLOWER.value,
    TILES.TREE_SAPLING.value]
