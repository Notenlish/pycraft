from typing import List, Tuple
from pygame import draw, font, rect


class Element:
    def __init__(self, text: str, action, height: int, font: font.Font):
        self.text: str = text
        self.action = action
        self.height: int = height
        self.surf = font.render(self.text, False, "black")
        self.width: int = self.surf.get_width()


class StartScreen:
    def __init__(self, app, font: font.Font, height: int, start_offset: int,
                 element_centerx: int):
        self.app = app
        self.elements: List[Element] = [
            Element("Start New Game", self.app.start_new_map,
                    30, font),  # change to actual func
            Element("Load Game", self.app.load_map, 30, font),
            Element("Exit", self.app.exit, 30, font)
        ]
        self.font = font
        self.height = height
        self.start_offset = start_offset
        self.element_centerx = element_centerx
        self.calculate_positions()

    def calculate_positions(self):
        e = ["element", "space"]
        for _ in range(len(self.elements)-2):
            e.append("element")
            e.append("space")
        e.append("element")

        elementheights = 0
        index = 0
        for t in e:
            if t == "element":
                elementheights += self.elements[index].height
                index += 1
        spaceheight = self.height - elementheights
        neededspaces = len(self.elements) - 1
        heightforspace = spaceheight / neededspaces
        self.elementpos = {}

        startpos = self.start_offset
        for (index, u) in enumerate(self.elements):
            self.elementpos[index] = rect.Rect(
                (self.element_centerx - u.width//2),
                startpos, u.width, u.height)

            # maybe I dont need this  # idk maybe I do
            self.elements[index].rect = self.elementpos[index]
            startpos += heightforspace + u.height

    def draw(self, surf):
        for index, pos in enumerate(self.elementpos.values()):
            draw.rect(surf, "red", pos)
            surf.blit(self.elements[index].surf, (pos[0], pos[1]))

    def change_selection(self):
        pass

    def select(self, mpos: Tuple[int, int]):
        for index, elementrect in enumerate(self.elementpos.values()):
            if elementrect.collidepoint(mpos):
                self.elements[index].action()
