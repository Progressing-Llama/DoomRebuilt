import pygame


class Key:
    def __init__(self, key):
        self.key = key
        self.last_press = None

        self.debounce = 0.8
        self.state = False

    def is_pressed(self):
        if self.last_press is None:
            self.last_press = pygame.time.get_ticks()

        if pygame.time.get_ticks() - self.last_press < self.debounce:
            return False

        return pygame.key.get_pressed()[self.key]

    def is_released(self):
        return not self.is_pressed()

    def on_pressed_down(self, func):
        if self.is_pressed() != self.state:
            self.state = not self.state

            if self.state:
                func()