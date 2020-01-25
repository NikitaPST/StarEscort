import utils
import random
import math
import pygame
from sprite import Sprite
from gameobject import GameObject
from gametext import GameText
from staticimage import StaticImage

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
        self.controls = []
        self.engine = engine
        self.map = None
        self.not_near = 75

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

        for text in self.texts:
            del text
        del self.texts

        for control in self.controls:
            del control
        del self.controls

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

    def add_static_image(self, id, x, y, ns):
        if ns >= len(self.sprites):
            raise Exception("No sprite #" + ns)
        o = StaticImage(id, x, y, self.sprites[ns])
        o.world = self
        if o.pic.rotable:
            o.pic.turn(0)
        self.controls.append(o)

    def remove_obj(self, active, n):
        if active:
            if self.objects[n].remove_spr != -1:
                self.add_obj(False, 0, self.objects[n].x, self.objects[n].y, 0, self.objects[n].remove_spr, 0, -1, utils.get_tick_count() + 500)
            del self.objects[n]
        else:
            del self.passiveObj[n]

    def turn_obj(self, o, angle, stop = False):
        # Should time sync
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

    def turn_obj_angle(self, o, angle, stop):
        if self.objects[o].angle == angle:
            return
        self.objects[o].angle = angle
        while angle >= 360:
            self.objects[o].angle -= 360
        while angle < 0:
            self.objects[o].angle += 360
        self.objects[o].pic.turn(self.objects[o].angle)
        if not self.objects[o].stay:
            if stop:
                self.stop()
            else:
                l = round(math.sqrt((self.objects[o].way_x - self.objects[o].x)**2 + (self.objects[o].way_y - self.objects[o].y)**2))
                self.objects[o].move_forward(l)

    def turn_obj_to(self, o, o1):
        if self.objects[o1].y == self.objects[o].y:
            if self.objects[o1].x == self.objects[o].x:
                a = 90
            else:
                a = 270
        else:
            a = 180 + round(math.atan((self.objects[o1].x - self.objects[o].x)/(self.objects[o1].y - self.objects[o].y)) / math.pi * 180)

        if self.objects[o].y > self.objects[o1].y:
            a -= 180
        while a >= 360:
            a -= 360
        while a < 0:
            a += 360

        self.turn_obj_angle(o, a, False)

    def move_obj(self, n, ax, ay):
        if n >= len(self.objects) or n < 0:
            return
        o = self.objects[n]
        if ax < self.minx:
            ay = utils.crop_y_by_x((o.x,o.y), (ax,ay), self.minx)
            ax = self.minx
        if ay < self.miny:
            ax = utils.crop_x_by_y((o.x,o.y), (ax,ay), self.miny)
            ay = self.miny
        if ax > self.maxx:
            ay = utils.crop_y_by_x((o.x,o.y), (ax,ay), self.maxx)
            ax = self.maxx
        if ay > self.maxy:
            ax = utils.crop_x_by_y((o.x,o.y), (ax,ay), self.maxy)
            ay = self.maxy
        o.way_x = ax
        o.way_y = ay
        o.old_x = o.x
        o.old_y = o.y
        o.stay = (o.way_x == o.x) and (o.way_y == o.y)

    def move_forward(self, o, n):
        self.move_obj(o, self.objects[o].x - round(n * math.sin(math.radians(self.objects[o].angle))), self.objects[o].y - round(n * math.cos(math.radians(self.objects[o].angle))))

    def finish_move(self, n):
        self.objects[n].x = self.objects[n].way_x
        self.objects[n].y = self.objects[n].way_y
        self.objects[n].stay = True

    def add_text(self, text, color, ax, ay):
        t = GameText(self.engine, text, None, color, ax, ay)
        self.texts.append(t)


    def process(self, tick):
        i = 0
        while i < len(self.passiveObj):
            if self.passiveObj[i].death_time != 0 and self.passiveObj[i].death_time <= tick:
                self.remove_obj(False, i)
            else:
                i+= 1

        for obj in self.passiveObj:
            obj.draw(tick)

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
            obj.stay = obj.stay or ((obj.way_x == obj.x) and (obj.way_y == obj.y))
            # Scroll world
            if obj.always_show:
                if obj.x < self.startx + self.not_near + obj.pic.phase_width // 2:
                    self.startx = max(self.minx, obj.x - self.not_near - obj.pic.phase_width // 2)
                if obj.y < self.starty + self.not_near + obj.pic.height // 2:
                    self.starty = max(self.miny, obj.y - self.not_near - obj.pic.height // 2)
                if obj.x > self.startx + self.engine.game.width - obj.pic.phase_width // 2 - self.not_near:
                    self.startx = min(self.maxx - self.engine.game.width, obj.x + self.not_near + obj.pic.phase_width // 2 - self.engine.game.width)
                if obj.y > self.starty + self.engine.game.height - obj.pic.height // 2 - self.not_near:
                    self.starty = min(self.maxy - self.engine.game.height, obj.y + self.not_near + obj.pic.height // 2 - self.engine.game.height)

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
        for text in self.texts:
            text.draw()

        # Conrols
        for control in self.controls:
            if control.is_visible:
                control.draw(tick)

        self.last_tick = tick

class StarEscortWorld(GameWorld):
    def __init__(self, tick, engine):
        super().__init__(tick, engine, 0, 0, 15000, 3000)
        self.startx = 700
        self.starty = 1000
        self.shoot_time = 0
        self.alien_time = utils.get_tick_count()
        self.game_lost = False
        self.lives_ship = 3
        self.lives_trans = 3

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
        super().add_sprite('Images/ShipIcon.bmp')    # 17
        super().add_sprite('Images/TransIcon.bmp')      # 18
        
        for i in range(1700):
            super().add_obj(False, 0, random.randint(0,14950), random.randint(0,2950), 0, random.randint(1,5), 1)

        super().add_obj(False, 0, 1000, 1350, 0, 6, 1000)
        super().add_obj(False, 0, 10000, 1350, 0, 6, 1000)

        super().add_obj(True, 1, 1150, 1250, 30, 0, 50, 13)
        super().turn_obj(0, -90)
        self.objects[0].always_show = True

        super().add_obj(True, 2, 1000, 1350, 6, 7, 50, 12)
        super().turn_obj(1, -90)

        super().add_static_image('ShipIcon1', 12, 15, 17)
        super().add_static_image('ShipIcon2', 35, 15, 17)
        super().add_static_image('ShipIcon3', 59, 15, 17)
        super().add_static_image('TransIcon3', 815, 15, 18)
        super().add_static_image('TransIcon2', 789, 15, 18)
        super().add_static_image('TransIcon1', 767, 15, 18)

    def __del__(self):
        return super().__del__()

    def process(self, tick):
        self.engine.read_immediate_kbd()
        if self.engine.keys[pygame.K_ESCAPE]:
            return False

        # Win/Lose Conditions
        if self.game_lost:
            super().process(tick)
            return True
        
        if self.objects[1].x >= 10000:
            if len(self.texts) == 0:
                super().add_text('Win! Transport reached its destination!', (255,0,0), self.engine.game.width // 2, 200)
            super().process(tick)
            return True

        # Keyboard events
        if self.engine.keys[pygame.K_UP]:
            super().move_forward(0, 40)
        if self.engine.keys[pygame.K_LEFT]:
            super().turn_obj(0, 4)
        if self.engine.keys[pygame.K_RIGHT]:
            super().turn_obj(0, -4)
        if self.engine.keys[pygame.K_SPACE] and (tick - self.shoot_time > 200):
            super().add_obj(True, 3, self.objects[0].x, self.objects[0].y, 60, 8, 1, 14, tick + 7000)
            super().turn_obj(len(self.objects) - 1, self.objects[0].angle)
            super().move_forward(len(self.objects) - 1, 65)
            super().finish_move(len(self.objects) - 1)
            super().move_forward(len(self.objects) - 1, 3000)
            self.shoot_time = tick

        # Move transport
        super().move_forward(1, 20)

        # Spawn enemies
        if tick - self.alien_time > 10000:
            ax = random.randint(450, 700)
            if random.random() < 0.5:
                ax = -ax
            ay = random.randint(300, 450)
            if random.random() < 0.5:
                ay = -ay
            if random.random() <= 0.5:
                super().add_obj(True, 4, self.objects[0].x + ax, self.objects[0].y + ay, 20, 9, 10, -1)
            else:
                super().add_obj(True, 5, self.objects[0].x + ax, self.objects[0].y + ay, 15, 10, 25, -1)
            self.alien_time = tick

        # Move enemies
        for i in range(len(self.objects)):
            obj = self.objects[i]
            if not (4 <= obj.id <= 5):
                continue
            dfight = obj.dist(self.objects[0])
            dtrans = obj.dist(self.objects[1])
            c = 0 if dfight + random.randint(0, 200) < dtrans * 2 + random.randint(0, 150) else 1
            super().turn_obj_to(i, c)
            obj.move_forward(40)
            if (tick - obj.action_tick > 1000) and (obj.dist(self.objects[c]) < 600):
                obj.action_tick = tick
                super().add_obj(True, 6, obj.x, obj.y, 60, 11, 1, 14, tick + 7000)
                super().turn_obj(len(self.objects)-1, obj.angle)
                super().move_forward(len(self.objects) - 1, 65)
                super().finish_move(len(self.objects) - 1)
                super().move_forward(len(self.objects) - 1, 3000)

        for obj in self.objects:
            if 4 <= obj.id <= 5:
                obj.collide_damage(3, 5, 5)
                obj.collide_damage(1, 25, 25)
                obj.collide_damage(2, 25, 25)
            elif obj.id == 6:
                obj.collide_damage(3, 5, 5)
                obj.collide_damage(1, 5, 5)
                obj.collide_damage(2, 5, 5)

        i = 0
        while i<len(self.objects):
            if self.objects[i].hits <= 0:
                if self.objects[i].id == 2:
                    self.lives_trans -= 1
                    if self.lives_trans < 0:
                        self.game_lost = True
                        super().add_text('You lost transport ship...', (255, 0, 0), self.engine.game.width // 2, 200)
                        super().remove_obj(True, i)
                    else:
                        self.objects[i].hits = 50
                        self.controls[self.lives_trans+3].is_visible = False
                elif self.objects[i].id == 1:
                    self.lives_ship -= 1
                    if self.lives_ship < 0:
                        self.game_lost = True
                        super().add_text('You died...', (255, 0, 0), self.engine.game.width // 2, 200)
                        super().remove_obj(True, i)
                    else:
                        self.objects[i].hits = 50
                        self.controls[self.lives_ship].is_visible = False
                else:
                    super().remove_obj(True, i)
            else:
                i += 1

        super().process(tick)
        return True