import os
import pygame
import utils

class Engine2D:
    def __init__(self):
        self.coloured_back = False
        self.bk_colour = (0,0,0)
        self.fname = ""
        self.game = None
        self.last_tick = 0
        self.windowed = False
        self.back_surface = None
        self.rg_lf = 0
        self.rg_up = 0
        self.show_fps = False
        self.lpa = False
        self.lpn = -1
        self.fps_count = 0
        self.fps_tick = 0
        self.caption = ""
        self.pause_tick = 0
        self.map = None

        self.fonts = []
        self.wid = []
        self.pos = []
        self.hei = None
        
        self.game_world = None
        self.last_picked = None
        self.last_pick_num = 0
        self.last_pick_status = False

        self.active = False
        self.buf = 0
        self.keys = [False] * 0xFF
        self.mousex = 0
        self.mousey = 0
        self.mouse_buttons = [False] * 8

    def init(self, game):
        sprite = 0

        self.game = game

        os.environ["SDL_VIDEO_WINDOW_POS"] = "%d,%d" % (game.left, game.top)

        pygame.init()
        pygame.display.set_caption(self.caption)
        if self.windowed:
            self.back_surface = pygame.display.set_mode((game.width, game.height))
        else:
            self.back_surface = pygame.display.set_mode((game.width, game.height), pygame.FULLSCREEN)

        self.last_tick = utils.get_tick_count()
        self.active = True
        self.fps_tick = self.last_tick

    def set_game_world(self, game_world):
        self.game_world = game_world
        if self.map != None:
            self.map.world = game_world
            self.map.engine = self
            self.map.init()
        else:
            self.game_world.map = None

    def shut_down(self):
        pygame.display.quit()

    def process(self):
        while self.active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.active = False
                    break
            if not self.process_next_frame():
                break

    def process_next_frame(self):
        curr_tick = utils.get_tick_count()
        tick_diff = curr_tick - self.last_tick
        if (tick_diff == 0):
            return True
        self.last_tick = curr_tick
        result = self.display_frame()
        if not result:
            self.shut_down()
            return False

        return True

    def display_frame(self):
        self.back_surface.fill(self.bk_colour)
        
        if self.map is not None:
            if self.game_world is None:
                self.map.draw(0,0)
            else:
                self.map.draw(-self.game_world.start_x, -self.game_world.start_y)

        if self.game_world is not None and not self.game_world.process(self.last_tick):
            return False
        
        pygame.display.flip()

        self.fps_count += 1
        t = utils.get_tick_count()
        if t - self.fps_tick > 1000:
            if self.show_fps:
                pygame.display.set_caption("%s : %.1f FPS" % (self.caption, self.fps_count / ((t - self.fps_tick) / 1000)))
            self.fps_tick = t
            self.fps_count = 0
        return True

    def read_immediate_kbd(self):
        self.keys = [False] * 0xFF
        if pygame.key.get_focused():
            self.keys = pygame.key.get_pressed()