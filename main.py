import sys

import numpy as np
import pygame

from contols.Key import Key
from engine import Engine

# 1. Initialize Pygame
pygame.init()

# 2. Set up display constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
FPS = 60

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Basic Pygame Window")

# Set up the clock to control the frame rate
clock = pygame.time.Clock()

# Define some colors (RGB)
WHITE = (255, 255, 255)
BLUE = (0, 120, 255)
engine = Engine(screen, 200)

def render_text(screen, text, pos, font_size=24, color=(0, 0, 0)):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

up = Key(pygame.K_UP)
down = Key(pygame.K_DOWN)
left = Key(pygame.K_LEFT)
right = Key(pygame.K_RIGHT)
space = Key(pygame.K_SPACE)

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

    # Rotation: Left/Right arrows turn your view (yaw)
    rot_speed = -0.03
    if left.is_pressed():
        engine.rotate_camera(yaw_delta=-rot_speed)
    if right.is_pressed():
        engine.rotate_camera(yaw_delta=rot_speed)

    if up.is_pressed():
        engine.rotate_camera(pitch_delta=rot_speed)
    if down.is_pressed():
        engine.rotate_camera(pitch_delta=-rot_speed)

    # -------------------------------------------------------------
    # True camera direction vectors on the ground plane
    # -------------------------------------------------------------
    # Looking down the +Z axis when yaw = 0:
    forward = np.array([-np.sin(engine.yaw), 0.0, np.cos(engine.yaw)], dtype=np.float32)

    # Perpendicular vector pointing to the camera's RIGHT:
    # Notice the signs: when yaw=0 (forward is +Z), right is (+1, 0, 0)
    strafe_right = np.array([np.cos(engine.yaw), 0.0, np.sin(engine.yaw)], dtype=np.float32)

    move_speed = 5.0

    # Forward / Back
    if w.is_pressed():
        engine.cam_pos += forward * move_speed

    if s.is_pressed():
        engine.cam_pos -= forward * move_speed

    # Strafe Left / Right
    if d.is_pressed():
        engine.cam_pos += strafe_right * move_speed
    if a.is_pressed():
        engine.cam_pos -= strafe_right * move_speed

    if space.is_pressed():
        engine.jump_event()

    p.on_pressed_down(engine.switch_perspective)

    # --- Drawing / Rendering ---
    # Fill the background with white
    screen.fill(WHITE)

    engine.run()

    # Update the full display surface to the screen
    pygame.display.flip()

    # --- Frame Rate Control ---
    clock.tick(FPS)

# 4. Safely Quit Pygame
pygame.quit()
sys.exit()