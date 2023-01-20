
class camera:
    def __init__(self, pos):
        self.pos = pos

    def update_pos(self, pos):
        self.pos = pos

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
