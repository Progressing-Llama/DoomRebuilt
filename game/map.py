import numpy as np

from game.models import Line, Rectangle

MAP = """
#########################
#*#*****#*********#*****#
#*###*#*#*#######*#*###*#
#*****#*#*****#***#*#***#
#####*#*#####*#*###*#*###
#***#*#*#***#*#*#***#***#
#*#*#*#*#*#*#*#*#*#####*#
#*#***#***#*#***#*****#*#
#*#########*#########*#*#
#*******#*********#***#*#
###*###*#*#######*#*###*#
#***#***#*#*****#*#*****#
#*###*###*#*###*#*#####*#
#*****#*****#***#*******#
#########################
"""

def find_tile_vertex_corners(grid_str: str, target: str = "*"):
    """
    Finds the exact (row, col) grid vertex coordinates where the boundary of the
    shape turns. Tiles are treated as unit squares [r, r+1] x [c, c+1].
    """
    lines = [list(line) for line in grid_str.strip().splitlines() if line]
    h, w = len(lines), len(lines[0])

    # Collect coordinates of target tiles
    tiles = {
        (r, c)
        for r in range(h)
        for c in range(w)
        if lines[r][c] == target
    }

    # Potential vertices range from (0, 0) to (h, w)
    corners = []

    for y in range(h + 1):
        for x in range(w + 1):
            # Check 4 quadrant tiles meeting at vertex (y, x)
            # tl: Top-Left, tr: Top-Right, bl: Bottom-Left, br: Bottom-Right
            tl = (y - 1, x - 1) in tiles
            tr = (y - 1, x) in tiles
            bl = (y, x - 1) in tiles
            br = (y, x) in tiles

            count = sum([tl, tr, bl, br])

            # Case 1: 1 or 3 neighboring tiles -> always a 90° corner
            if count in (1, 3):
                corner_type = "exterior (90°)" if count == 1 else "interior (270°)"
                corners.append((x, y))

            # Case 2: 2 diagonally opposite tiles -> self-intersecting / saddle corner
            elif count == 2 and ((tl and br) or (tr and bl)):
                corners.append((x, y))

    return corners

def map_builder(map_str, cam_pos, render_dist=300):
    walls = []

    map_str = map_str.split("\n")
    map_str_ = []
    for i, s in enumerate(map_str):
        if len(s) == 0:
            continue
        map_str_.append(s)

    map_str = map_str_

    for j, line in enumerate(map_str):
        exit_break = False
        for i, char in enumerate(line):
            if char == "*":
                for k in [0, 1]:
                    if abs(np.linalg.norm([i, j, k]) - np.linalg.norm(cam_pos)) < render_dist:
                        walls.append(Rectangle((i, j, k), (i + 1, j + 1, k)))
                    else:
                        exit_break = True

                if exit_break:
                    continue

                walls.append(Rectangle((i, j, 0), (i + 1, j, 1)))
                walls.append(Rectangle((i, j, 0), (i, j + 1, 1)))

    return walls

