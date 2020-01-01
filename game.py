import utils
from gameworld import StarEscortWorld
from engine2d import Engine2D

lives = 3
world = None

class Game:
    def __init__(self):
        self.left = 91
        self.top = 47
        self.width = 840
        self.height = 655
        self.caption = "Star Escort"

        self.engine = Engine2D()
        self.engine.caption = "Star Escort"
        self.engine.show_fps = True
        self.engine.windowed = True

    def start(self):
        self.engine.init(self)
        world = StarEscortWorld(utils.get_tick_count(), self.engine)
        self.engine.set_game_world(world)

    def stop(self):
        self.engine.shut_down()

    def process(self):
        self.engine.process()

game = Game()
game.start()
game.process()
game.stop()
del game