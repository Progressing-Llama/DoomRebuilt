import numpy as np
import pygame

class Line:
    def __init__(self, start, end):
        self.start = start
        self.end = end

        self.start = np.array(self.start)
        self.end = np.array(self.end)

        self.id = hash((start, end))
        self.id2 = hash((end, start))

        self.angle_x = 0
        self.angle_y = 0

    def is_duplicate(self, other):
        return self.id == other.id or self.id == other.id2

    def rotate_x(self, angle):
        self.angle_x += angle  # Track total rotation

        vertices = np.array([self.start, self.end])
        c, s = np.cos(angle), np.sin(angle)
        # Transposed for row-vector multiplication
        r_matrix = np.array([[1, 0, 0], [0, c, s], [0, -s, c]])
        self.start, self.end = np.dot(vertices, r_matrix)

    def rotate_y(self, angle):
        self.angle_y += angle

        vertices = np.array([self.start, self.end])
        c, s = np.cos(angle), np.sin(angle)
        r_matrix = np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])
        self.start, self.end = np.dot(vertices, r_matrix)

class Cube:

    def __init__(self, screen: pygame.Surface, w):
        self.w = w

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.vertices_norm = [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]

        self.lines = []
        self.generate_lines()

        self.z_axis = Line((0, 0, 0), (0, 0, 1))
        self.x_axis = Line((0, 0, 0), (1, 0, 0))
        self.y_axis = Line((0, 0, 0), (0, 1, 0))

        print(f"There are {len(self.lines)} lines in the cube.")

        self.vertices = np.array(self.vertices_norm) * w

        self.screen = screen

        self.perspective = True

        self.camera_dist = 200

        self.camera_x = self.screen_width / 2
        self.camera_y = self.screen_height / 2

    def find_neighbors(self, v):
        neighbors = []

        for v_ in self.vertices_norm:
            c = 0
            for i in range(0, 3):
                if v[i] == v_[i]:
                    c += 1

            if c == 2:
                neighbors.append(v_)

        return neighbors

    def rotate_x(self, angle):
        for line in self.lines:
            line.rotate_x(angle)

    def rotate_y(self, angle):
        for line in self.lines:
            line.rotate_y(angle)

    def line_exists(self, line):
        for l in self.lines:
            if l.is_duplicate(line):
                return True
        return False

    def generate_lines(self):
        for i, v in enumerate(self.vertices_norm):
            neighbors = self.find_neighbors(v)
            for n in neighbors:
                line = Line(v, n)
                if not self.line_exists(line):
                    self.lines.append(line)

    def set_camera_dist(self, camera_dist_delta):
        self.camera_dist += camera_dist_delta

    def set_camera_pos(self, camera_pos_delta):
        self.camera_x += camera_pos_delta[0]
        self.camera_y += camera_pos_delta[1]

    def project_3d_to_2d(
            self,
            point_3d,
            screen_width=None,
            screen_height=None,
            fov=400,
            ortho_scale=1.0,
    ):
        if screen_width is None:
            screen_width = self.screen_width
        if screen_height is None:
            screen_height = self.screen_height

        x, y, z = point_3d

        perspective = self.perspective
        camera_dist = self.camera_dist

        if perspective:
            depth = camera_dist + z
            if depth <= 1:
                depth = 1.0
            scale = fov / depth
        else:
            # Orthographic projection: constant scale, ignores z depth
            scale = ortho_scale

        # Map center-relative coordinates to Pygame screen coordinates (-y keeps +Y pointing up)
        screen_x = int(self.camera_x + (x * scale))
        screen_y = int(self.camera_y - (y * scale))

        return (screen_x, screen_y)

    def switch_perspective(self):
        self.perspective = not self.perspective

    def draw(self):
        w = self.w

        for line in self.lines:
            center = np.array((self.screen_width // 2, self.screen_height // 2))

            start = ((line.start - 0.5) * w).tolist()
            end = ((line.end - 0.5) * w).tolist()

            start = self.project_3d_to_2d(start)
            end = self.project_3d_to_2d(end)

            pygame.draw.line(self.screen, (0, 0, 0), start, end, 1)

        w = 50

        for axis in [self.x_axis, self.y_axis, self.z_axis]:

            start = ((axis.start - 0.5) * w).tolist()
            end = ((axis.end - 0.5) * w).tolist()

            start = self.project_3d_to_2d(start)
            end = self.project_3d_to_2d(end)

            pygame.draw.line(self.screen, axis.end * 255, start, end, 1)



