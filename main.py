import sys
import pygame

from cube import Cube

# 1. Initialize Pygame
pygame.init()

# 2. Set up display constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Basic Pygame Window")

# Set up the clock to control the frame rate
clock = pygame.time.Clock()

# Define some colors (RGB)
WHITE = (255, 255, 255)
BLUE = (0, 120, 255)
cube = Cube(screen, 50)

class Key:
    def __init__(self, key):
        self.key = key
        self.last_press = None

        self.debounce = 0.4
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

def render_text(screen, text, pos, font_size=24, color=(0, 0, 0)):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

up = Key(pygame.K_UP)
down = Key(pygame.K_DOWN)
left = Key(pygame.K_LEFT)
right = Key(pygame.K_RIGHT)

w = Key(pygame.K_w)
s = Key(pygame.K_s)
a = Key(pygame.K_a)
d = Key(pygame.K_d)

p = Key(pygame.K_p)

# 3. Main Game Loop
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Game Logic / Updates ---

    if up.is_pressed():
        cube.rotate_y(0.01)

    if down.is_pressed():
        cube.rotate_y(-0.01)

    if left.is_pressed():
        cube.rotate_x(0.01)

    if right.is_pressed():
        cube.rotate_x(-0.01)

    if w.is_pressed():
        cube.set_camera_dist(10)

    if s.is_pressed():
        cube.set_camera_dist(-10)

    if a.is_pressed():
        cube.set_camera_pos((10, 0))

    if d.is_pressed():
        cube.set_camera_pos((-10, 0))

    p.on_pressed_down(cube.switch_perspective)

    # --- Drawing / Rendering ---
    # Fill the background with white
    screen.fill(WHITE)

    render_text(screen, "Perspective: " + str(cube.perspective), (10, 10))

    render_text(screen, "Camera Distance: " + str(cube.camera_dist), (10, 40))

    render_text(screen, "Camera Position: " + str((cube.camera_x, cube.camera_y)), (10, 70))

    render_text(screen, "Controls", (10, 130))
    render_text(screen, "w/s: Camera Distance", (10, 160))
    render_text(screen, "a/d: Camera Position", (10, 190))
    render_text(screen, "up/down: Rotate Y", (10, 220))
    render_text(screen, "left/right: Rotate X", (10, 250))
    render_text(screen, "p: Switch Perspective", (10, 280))

    cube.draw()

    # Update the full display surface to the screen
    pygame.display.flip()

    # --- Frame Rate Control ---
    clock.tick(FPS)

# 4. Safely Quit Pygame
pygame.quit()
sys.exit()