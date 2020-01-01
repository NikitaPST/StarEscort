import utils
import random
import math
import pygame
from sprite import Sprite
from gameobject import GameObject

class GameWorld:
    def __init__(self, tick, engine, amnx, amny, amxx, amxy):
        self.last_tick = tick
        self.minx = amnx
        self.miny = amny
        self.maxx = amxx
        self.maxy = amxy
        self.startx = 0
        self.starty = 0
        self.sprites = []
        self.objects = []
        self.passiveObj = []
        self.texts = []
        self.engine = engine
        self.map = None

    def __del__(self):
        for sprite in self.sprites:
            del sprite
        del self.sprites

        for obj in self.objects:
            del obj
        del self.objects

        for obj in self.passiveObj:
            del obj
        del self.passiveObj

    def add_sprite(self, filename, n_phases = 1, rotable = False):
        s = Sprite(filename, self.engine, n_phases, rotable)
        self.sprites.append(s)

    def add_obj(self, active, id, x, y, sp, ns, hits, rem = -1, d = 0):
        if ns >= len(self.sprites):
            raise Exception("No sprite #" + ns)
        o = GameObject(id, x, y, sp, self.sprites[ns], rem, d)
        o.world = self
        o.max_hits = hits
        o.hits = hits
        if o.pic.rotable:
            o.pic.turn(0)
        if active:
            self.objects.append(o)
        else:
            self.passiveObj.append(o)

    def turn_obj(self, o, angle, stop = False):
        self.objects[o].angle += angle
        while self.objects[o].angle >= 360:
            self.objects[o].angle -= 360
        while self.objects[o].angle < 0:
            self.objects[o].angle += 360
        self.objects[o].pic.turn(self.objects[o].angle)
        if not self.objects[o].stay:
            if stop:
                self.stop()
            else:
                l = round(math.sqrt((self.objects[o].way_x - self.objects[o].x)**2 + (self.objects[o].way_y - self.objects[o].y)**2))
                self.objects[o].move_forward(l)

    def move_obj(self, n, ax, ay):
        if n >= len(self.objects) or n < 0:
            return
        o = self.objects[n]
        if ax < self.minx:
            ax = self.minx
        if ay < self.miny:
            ay = self.miny
        if ax > self.maxx:
            ax = self.maxx
        if ay > self.maxy:
            ay = self.maxy
        o.way_x = ax
        o.way_y = ay
        o.old_x = o.x
        o.old_y = o.y
        o.stay = (o.way_x == o.x) and (o.way_y == o.y)

    def move_forward(self, o, n):
        self.move_obj(o, self.objects[o].x - round(n * math.sin(math.radians(self.objects[o].angle))), self.objects[o].y - round(n * math.cos(math.radians(self.objects[o].angle))))

    def process(self, tick):
        i = 0
        while i < len(self.passiveObj):
            if self.passiveObj[i].death_time != 0 and self.passiveObj[i].death_time <= tick:
                self.remove_obj(False, i)
            else:
                i+= 1

        for obj in self.passiveObj:
            obj.draw(tick)

        # Particle

        # Update position
        for obj in reversed(self.objects):
            if not obj.stay:
                s = obj.speed * (tick - self.last_tick) / 100
                d = math.sqrt((obj.way_x-obj.x)**2 + (obj.way_y - obj.y)**2)
                sx = (obj.way_x - obj.x) / d
                sy = (obj.way_y - obj.y) / d
                if obj.way_x > obj.x:
                    obj.x = min(round(sx * s + obj.x), obj.way_x)
                else:
                    obj.x = max(round(sx * s + obj.x), obj.way_x)
                if obj.way_y > obj.y:
                    obj.y = min(round(sy * s + obj.y), obj.way_y)
                else:
                    obj.y = max(round(sy * s + obj.y), obj.way_y)
            obj.stay = obj.stay or ((obj.way_x == obj.x) or (obj.way_y == obj.y))
            # Scroll world

        for obj in reversed(self.objects):
            obj.draw(tick)

        i = 0
        while i < len(self.objects):
            if self.objects[i].death_time > 0 and self.objects[i].death_time <= tick:
                self.objects[i].remove_spr = -1
                self.remove_obj(True, i)
            else:
                i+= 1

        # Texts

        # Static

        self.last_tick = tick

class StarEscortWorld(GameWorld):
    def __init__(self, tick, engine):
        super().__init__(tick, engine, 0, 0, 15000, 3000)
        self.startx = 700
        self.starty = 1000
        self.shoot_time = 0
        self.alien_time = utils.get_tick_count()
        self.game_lost = False

        super().add_sprite('Images/Ship.bmp', 2, True)   # 0
        super().add_sprite('Images/st1.bmp')    # 1
        super().add_sprite('Images/st2.bmp')    # 2
        super().add_sprite('Images/st3.bmp')    # 3
        super().add_sprite('Images/st4.bmp')    # 4
        super().add_sprite('Images/st5.bmp')    # 5
        super().add_sprite('Images/Base.bmp')    # 6
        super().add_sprite('Images/Trans.bmp', 1, True)   # 7
        super().add_sprite('Images/Rocket.bmp', 1, True)   # 8
        super().add_sprite('Images/Alien1.bmp', 2, True)   # 9
        super().add_sprite('Images/Alien2.bmp', 1)   # 10
        super().add_sprite('Images/Missile1.bmp', 1, True)   # 11
        super().add_sprite('Images/Bang1.bmp')    # 12
        super().add_sprite('Images/Bang2.bmp')    # 13
        super().add_sprite('Images/Bang3.bmp')    # 14
        super().add_sprite('Images/Sparkle.bmp')    # 15
        super().add_sprite('Images/Sparkle2.bmp')    # 16
        
        for i in range(1700):
            super().add_obj(False, 0, random.randint(0,14950), random.randint(0,2950), 0, random.randint(1,5), 1)

        super().add_obj(False, 0, 1000, 1350, 0, 6, 1000)
        super().add_obj(False, 0, 10000, 1350, 0, 6, 1000)

        super().add_obj(True, 1, 1150, 1250, 30, 0, 50, 13)
        super().turn_obj(0, -90)

        super().add_obj(True, 2, 1000, 1350, 6, 7, 150, 12)
        super().turn_obj(1, -90)

    def __del__(self):
        return super().__del__()

    def process(self, tick):
        self.engine.read_immediate_kbd()
        if self.engine.keys[pygame.K_ESCAPE]:
            return False

        # Win/Lose Conditions
        if self.engine.keys[pygame.K_UP]:
            super().move_forward(0, 40)
        if self.engine.keys[pygame.K_LEFT]:
            super().turn_obj(0, 4)
        if self.engine.keys[pygame.K_RIGHT]:
            super().turn_obj(0, -4)

        super().process(tick)
        return True