import math
import random
import time

import numpy as np
import pygame

from game.map import map_builder, MAP, find_tile_vertex_corners
from game.models import Line, find_connected_shapes, find_closed_cycles, find_closed_cycles_as_lines


# engine.py

class Engine:
    def __init__(self, screen, w):
        self.map_lines = []
        self.load_map(MAP)
        self.screen = screen

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.perspective = True

        self.origin_x = self.screen_width / 2
        self.origin_y = self.screen_height / 2

        # Camera position and orientation (radians)
        self.cam_pos = np.array([0.0, -200.0, -300.0], dtype=np.float32)
        self.yaw = 0.0  # Turning left/right (about Y-axis)
        self.pitch = 0.0  # Looking up/down (about X-axis)

        self.w = w
        # In engine.py __init__:
        self.w = w
        for line in self.map_lines:
            line.rotate_x(math.pi / 2, origin=[0, 0, 0])

        self.jump_time = -1
        self.jump_duration = 0.5

    def project_3d_to_2d(self, point_3d, fov=400, ortho_scale=1.0):
        # 1. World to Camera Translation
        pos = np.array(point_3d, dtype=np.float32) - self.cam_pos

        # 2. Camera Yaw (turn left/right around the vertical axis Y)
        cy, sy = np.cos(self.yaw), np.sin(self.yaw)
        r_yaw = np.array([
            [cy, 0, -sy],
            [0, 1, 0],
            [sy, 0, cy]
        ])
        pos = pos @ r_yaw

        # 3. Camera Pitch (look up/down)
        cp, sp = np.cos(self.pitch), np.sin(self.pitch)
        r_pitch = np.array([
            [1, 0, 0],
            [0, cp, sp],
            [0, -sp, cp]
        ])
        pos = pos @ r_pitch

        x, y, z = pos[0], pos[1], pos[2]

        if self.perspective:
            if z <= 1.0:
                z = 1.0
            scale = fov / z
        else:
            scale = ortho_scale

        screen_x = int(self.origin_x + (x * scale))
        screen_y = int(self.origin_y - (y * scale))

        return (screen_x, screen_y)

    def run(self):
        w = self.w

        for line in self.map_lines:

            start = ((line.start - 0.5) * w).tolist()
            end = ((line.end - 0.5) * w).tolist()

            d = np.linalg.norm(np.array(start) - self.cam_pos)

            if d > 1000:
                continue

            pt1 = self.project_3d_to_2d(start)
            pt2 = self.project_3d_to_2d(end)

            pygame.draw.line(self.screen, line.color, pt1, pt2, 1)

        self.jump_controller()

    def rotate_camera(self, yaw_delta=0.0, pitch_delta=0.0):
        self.yaw += yaw_delta
        self.pitch += pitch_delta

    def load_map(self, map_str):
        self.map_lines = map_builder(map_str)
        new_lines = []

        for line in self.map_lines:
            if not self.line_exists(line, True):
                new_lines.append(line)

        self.map_lines = new_lines

        self.map_corners = find_tile_vertex_corners(map_str)
        for corner in self.map_corners:
            lower = [corner[0], corner[1], 0]
            upper = [corner[0], corner[1], 1]

            self.map_lines.append(Line(lower, upper))

        self.polgons = find_closed_cycles_as_lines(self.map_lines)

        #print(self.vertices_norm)
        #self.generate_lines()

    def set_camera_pos(self, camera_pos_delta):
        self.camera_x += camera_pos_delta[0]
        self.camera_y += camera_pos_delta[1]

    def switch_perspective(self):
        self.perspective = not self.perspective

    def find_neighbors(self, v):
        axial_neighbor_x = []
        axial_neighbor_y = []
        axial_neighbor_z = []

        for v_ in self.vertices_norm:
            c = 0
            for i in range(0, 3):
                if v[i] == v_[i]:
                    c += 1

            if c == 2:

                if v[0] != v_[0]:
                    axial_neighbor_x.append(v_)
                if v[1] != v_[1]:
                    axial_neighbor_y.append(v_)
                if v[2] != v_[2]:
                    axial_neighbor_z.append(v_)

        return axial_neighbor_x, axial_neighbor_y, axial_neighbor_z

    def line_exists(self, line, include_self=False):
        c = 0

        for l in self.map_lines:
            if l.is_duplicate(line):
                c += 1

                if not include_self or c > 1:
                    return True
        return False

    def generate_lines(self):
        v_set = set(tuple(p) for p in self.vertices_norm)

        for v in self.vertices_norm:
            x_neighbors, y_neighbors, z_neighbors = self.find_neighbors(v)

            neighbors_close = []
            for group in (x_neighbors, y_neighbors, z_neighbors):
                if not group:
                    continue

                # Calculate Euclidean distance along each individual neighbor
                diffs = np.array(group) - np.array(v)
                dists = np.linalg.norm(diffs, axis=1)

                # Select the nearest neighbor along this axis
                closest_idx = np.argmin(dists)
                closest_neighbor = group[closest_idx]

                # Ensure line doesn't skip intermediate points (e.g. 0 -> 2 when 1 exists)
                # Check along the differing coordinate axis
                diff = np.array(closest_neighbor) - np.array(v)
                axis = np.argmax(np.abs(diff))
                step = np.sign(diff[axis])

                # Optional: if points are on an integer/fixed grid, ensure adjacency
                # or verify no other point lies strictly between v and closest_neighbor
                neighbors_close.append(closest_neighbor)

            for n in neighbors_close:
                line = Line(v, n)
                if not self.line_exists(line):
                    self.map_lines.append(line)

    def rotate_x(self, angle, origin=None):

        for line in self.map_lines:
            line.rotate_x(angle, origin)

    def rotate_y(self, angle, origin=None):
        for line in self.map_lines:
            line.rotate_y(angle, origin)

    def rotate_z(self, angle, origin=None):
        for line in self.map_lines:
            line.rotate_z(angle, origin)

    def jump_event(self):
        if self.jump_time > -1:
            return

        self.jump_time = time.time()

    def jump_controller(self):
        if self.jump_time > -1:
            delta = time.time() - self.jump_time

            if time.time() > self.jump_time + self.jump_duration:
                self.jump_time = -1
            else:
                self.cam_pos += (np.array([0, self.jump_duration/2 - delta, 0])) * 25