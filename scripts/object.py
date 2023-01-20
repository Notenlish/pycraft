from pygame import rect

class Object:
    def __init__(self, spr, pos, camera, size=None):
        self.spr = spr
        self.pos = pos
        self.camera = camera
        self.rect = rect.Rect(pos[0], pos[1], size[0], size[1]) if size is not None else rect.Rect(pos[0], pos[1], self.spr.get_width(), self.spr.get_height())

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def draw(self, surf, camera_pos):
        surf.blit(self.spr, (self.pos[0]-camera_pos[0],
                             self.pos[1]-camera_pos[1]))
