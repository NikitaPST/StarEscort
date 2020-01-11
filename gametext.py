import pygame

class GameText:
    def __init__(self, eng, txt, fnt, clr, ax, ay):
        self.engine = eng
        self.font = pygame.font.Font(fnt, 20)
        self.text = txt
        self.x = ax
        self.y = ay
        self.color = clr
        self.surface = self.font.render(self.text, True, self.color)

    def __del__(self):
        del self.surface

    def draw(self):
        self.engine.back_surface.blit(self.surface, (self.x - self.surface.get_width() // 2, self.y - self.surface.get_height() // 2))