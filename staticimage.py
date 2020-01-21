import utils

class StaticImage:
    def __init__(self, id, x, y, pic):
        self.x = x
        self.y = y
        self.id = id
        self.pic = pic
        self.phase_tick = utils.get_tick_count()
        self.phase = 1
        self.is_visible = True
        self.world = None

    def draw(self, tick):
        if tick - self.phase_tick > self.pic.phase_pause:
            self.phase += ((tick - self.phase_tick) // self.pic.phase_pause)
            while self.phase > self.pic.num_phases:
                self.phase -= self.pic.num_phases
            self.phase_tick = tick
        self.rect = self.pic.draw(self.x, self.y, self.phase)