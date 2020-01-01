import utils
import math
from sprite import Sprite

class GameObject:
    def __init__(self, id, x, y, sp, pic, rpic = -1, d = 0):
        self.x = x
        self.y = y
        self.death_time = d
        self.id = id
        self.remove_spr = rpic
        if pic.rotable:
            self.pic = pic.copy()
        else:
            self.pic = pic
        self.speed = sp
        self.stay = True
        self.way_x = x
        self.way_y = y
        self.phase_tick = utils.get_tick_count()
        self.action_tick = self.phase_tick
        self.phase = 1
        self.angle = 0
        self.always_show = False
        self.old_x = 0
        self.old_y = 0
        self.hits = 0
        self.max_hits = 0
        self.world = None

    def move(self, ax, ay):
        if ax < self.world.minx:
            ax = self.world.minx
        if ay < self.world.miny:
            ay = self.world.miny
        if ax > self.world.maxx:
            ax = self.world.maxx
        if ay > self.world.maxy:
            ay = self.world.maxy
        self.way_x = ax
        self.way_y = ay
        self.old_x = self.x
        self.old_y = self.y
        self.stay = (self.way_x == self.x) and (self.way_y == self.y)

    def move_forward(self, n):
        self.move(self.x - round(n * math.sin(math.radians(self.angle))), self.y - round(n * math.cos(math.radians(self.angle))))

    def draw(self, tick):
        if tick - self.phase_tick > self.pic.phase_pause:
            self.phase += ((tick - self.phase_tick) // self.pic.phase_pause)
            while self.phase > self.pic.num_phases:
                self.phase -= self.pic.num_phases
            self.phase_tick = tick
        if self.world.map is None:
            self.pic.draw(self.x - self.world.startx, self.y - self.world.starty, self.phase, self.angle)
        