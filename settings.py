from pygame import RESIZABLE, SCALED

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HIGHT = 500, 500
FLAGS = SCALED | RESIZABLE

CHUNK_RADIUS = 5
CHUNK_WIDTH = 8
CHUNK_HEIGHT = 64
CHUNK_GROUND_BASE = int(CHUNK_HEIGHT - (CHUNK_HEIGHT * 0.7))

PERLIN_MULTIPLIER = 10
BLOCK_PIXEL_SIZE = 16  # size of each block in terms of pixels

FONT_SIZE = 18

CAMERA_OFFSET = - WINDOW_WIDTH//2

PLAYER_SPEED = 3

SKY_COLOR = (99, 155, 255)
