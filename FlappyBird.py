import kivy
kivy.require("1.8.0")

from random import randint
import sys

from kivy.properties import NumericProperty, ReferenceListProperty, BooleanProperty, ObjectProperty, ListProperty
from kivy.uix.image import Image
from kivy.vector import Vector
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.widget import Widget

class Background(Widget):
    image_one = ObjectProperty(Image())
    image_two = ObjectProperty(Image())

    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def update(self):
        self.image_one.pos = Vector(*self.velocity) + self.image_one.pos
        self.image_two.pos = Vector(*self.velocity) + self.image_two.pos

        if self.image_one.right <= 0:
            self.image_one.pos = (self.width, 0)
        if self.image_two.right <= 0:
            self.image_two.pos = (self.width, 0)

    def update_position(self):
        self.image_one.pos = (0, 0)
        self.image_two.pos = (self.width, 0)

class Mcnay(Widget):
    bird_image = ObjectProperty(Image())

    jump_time = NumericProperty(0.3)
    jump_height = NumericProperty(95)

    time_jumped = NumericProperty(0)

    jumping = BooleanProperty(False)

    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    normal_velocity_x = NumericProperty(0)
    normal_velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    normal_velocity = ReferenceListProperty(normal_velocity_x, normal_velocity_y)

    def __init__(self, **kwargs):
        super(Mcnay, self).__init__(**kwargs)
        if Config.getdefault('input', 'keyboard', False):
            self._keyboard = Window.request_keyboard(
                self._keyboard_closed, self, 'text')
            self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def switch_to_normal(self, dt):
        self.bird_image.source = "images/flappyup.png"
        Clock.schedule_once(self.stop_jumping, self.jump_time  * (4.0 / 5.0))

    def stop_jumping(self, dt):
        self.jumping = False
        self.bird_image.source = "images/flappy.png"
        self.velocity_y = self.normal_velocity_y

    def on_touch_down(self, touch):
        self.jumping = True
        self.bird_image.source = "images/flappynormal.png"
        self.velocity_y = self.jump_height / (self.jump_time * 60.0)
        Clock.unschedule(self.stop_jumping)
        Clock.schedule_once(self.switch_to_normal, self.jump_time  / 5.0)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self.on_touch_down(None)

    def update(self):
        self.pos = Vector(*self.velocity) + self.pos
        if self.pos[1] <= 104:
            Clock.unschedule(self.stop_jumping)
            self.bird_image.source = "images/flappynormal.png"
            self.pos = (self.pos[0], 104)

class Obstacle(Widget):
    gap_top = NumericProperty(0)
    gap_size = NumericProperty(150)

    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    marked = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(Obstacle, self).__init__(**kwargs)

    def update_position(self):
        self.gap_top = randint(self.gap_size + 112, self.height)

    def update(self):
        self.pos = Vector(*self.velocity) + self.pos

class FlappyBirdGame(Widget):
    mcnay = ObjectProperty(Mcnay())
    background = ObjectProperty(Background())
    obstacles = ListProperty([])
    score = NumericProperty(0)

    def __init__(self, **kwargs):
        super(FlappyBirdGame, self).__init__(**kwargs)
        self.mcnay.normal_velocity = [0, -4]
        self.mcnay.velocity = self.mcnay.normal_velocity
        self.background.velocity = [-2, 0]
        self.bind(size=self.size_callback)

    def remove_obstacle(self):
        self.remove_widget(self.obstacles[0])
        self.obstacles = self.obstacles[1:]

    def new_obstacle(self, remove=True):
        if remove:
            self.remove_obstacle()
        new_obstacle = Obstacle()
        new_obstacle.height = self.height
        new_obstacle.x = self.width
        new_obstacle.update_position()
        new_obstacle.velocity = [-3, 0]
        self.add_widget(new_obstacle)
        self.obstacles = self.obstacles + [new_obstacle]

    def size_callback(self, instance, value):
        for obstacle in self.obstacles:
            obstacle.height = value[1]
            obstacle.update_position()
        self.background.size = value
        self.background.update_position()

    def update(self, dt):
        self.mcnay.update()
        self.background.update()
        # Loop through and update obstacles. Replace obstacles which went off the screen.
        for obstacle in self.obstacles:
            obstacle.update()
            if obstacle.x < self.mcnay.x and not obstacle.marked:
                obstacle.marked = True
                self.score += 1
                self.new_obstacle(remove=False)
        if len(self.obstacles) == 0:
            self.new_obstacle(remove=False)
        elif self.obstacles[0].x < 0:
            self.remove_obstacle()
        # If obstacles is emply
        # See if the player collides with any obstacles
        for obstacle in self.obstacles:
            if self.mcnay.collide_widget(Widget(pos=(obstacle.x, obstacle.gap_top + 20), size=(obstacle.width, obstacle.height - obstacle.gap_top))):
                # This will be replaced later on
                sys.exit()
            if self.mcnay.collide_widget(Widget(pos=(obstacle.x, 0), size=(obstacle.width, obstacle.gap_top - obstacle.gap_size))):
                # This will also be replaced
                sys.exit()

class FlappyBirdApp(App):

    def build(self):
        game = FlappyBirdGame()
        Clock.schedule_interval(game.update, 1.0/60.0)
        return game

if __name__ == "__main__":
    FlappyBirdApp().run()
