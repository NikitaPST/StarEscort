import pygame

class Sprite:
    def __init__(self, fname, engine, n_phases, rotable):
        self.engine = engine
        self.file_name = fname
        self.num_phases = n_phases
        self.phase_pause = 250
        bitmap = pygame.image.load(fname)
        self.color_key = bitmap.get_at((0,0))[:3]
        self.width = bitmap.get_width()
        self.height = bitmap.get_height()

        self.original_surface = bitmap
        self.original_surface.set_colorkey(self.color_key)

        self.phase_height = self.height
        self.phase_width = self.width // self.num_phases
        self.rotable = rotable
        self.phased_surfaces = []
        self.rotable_surfaces = []
        for i in range(self.num_phases):
            phase_surface = pygame.Surface((self.phase_width, self.height))
            phase_surface.fill(self.color_key)
            phase_surface.set_colorkey(self.color_key)
            phase_surface.blit(self.original_surface, (0,0), (i*self.phase_width, 0, self.phase_width, self.height))
            self.phased_surfaces.append(phase_surface)
            if self.rotable:
                rotable_surface = self.phased_surfaces[i].copy()
                self.rotable_surfaces.append(rotable_surface)

    def copy(self):
        result = Sprite(self.file_name, self.engine, self.num_phases, self.rotable)
        return result

    def turn(self, angle):
        if not self.rotable:
            return
        for i in range(self.num_phases):
            self.rotable_surfaces[i] = pygame.transform.rotate(self.phased_surfaces[i], angle)

    def get_surface(self, phase):
        if self.rotable:
            return self.rotable_surfaces[phase-1]
        return self.phased_surfaces[phase-1]

    def draw(self, x, y, phase, angle):
        surface = self.get_surface(phase)
        (phase_width, phase_height) = surface.get_size()
        ax = x - phase_width // 2
        ay = y - phase_height // 2
        if ax + phase_width < 1 or ay + phase_height < 1 or ax >= self.engine.game.width or ay >= self.engine.game.height:
            return
        
        r = [0, 0, phase_width, phase_height]
        if ax <= 0:
            r[0] -= ax
            ax = 1
        if ay <= 0:
            r[1] -= ay
            ay = 1
        a = ax + phase_width - self.engine.game.width
        if a >= 0:
            r[2] = r[2] - a - 1
        a = ay + phase_height - self.engine.game.height
        if a >= 0:
            r[3] = r[3] - a - 1
        if r[2] <= 0 or r[3] <= 0:
            return

        self.engine.back_surface.blit(self.get_surface(phase), (ax, ay), tuple(r))
        #pygame.draw.circle(self.engine.back_surface, (0,255,0), (x,y), 5)
