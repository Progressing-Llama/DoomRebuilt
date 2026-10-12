import numpy as np


class Line:
    def __init__(self, start, end):
        self.start = np.array(start, dtype=float)
        self.end = np.array(end, dtype=float)

        self.id = hash((tuple(start), tuple(end)))
        self.id2 = hash((tuple(end), tuple(start)))

        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0

        self.color = (0, 0, 0)

    def is_duplicate(self, other):
        return self.id == other.id or self.id == other.id2

    def rotate_x(self, angle, origin=None):
        """Rotates about an axis parallel to the X-axis passing through `origin`."""
        self.angle_x += angle
        c, s = np.cos(angle), np.sin(angle)
        # Transposed for row-vector multiplication: (N, 3) @ R
        r_matrix = np.array([
            [1,  0,  0],
            [0,  c,  s],
            [0, -s,  c]
        ])
        self._apply_rotation(r_matrix, origin)

    def rotate_y(self, angle, origin=None):
        """Rotates about an axis parallel to the Y-axis passing through `origin`."""
        self.angle_y += angle
        c, s = np.cos(angle), np.sin(angle)
        r_matrix = np.array([
            [ c,  0, -s],
            [ 0,  1,  0],
            [ s,  0,  c]
        ])
        self._apply_rotation(r_matrix, origin)

    def rotate_z(self, angle, origin=None):
        """Rotates about an axis parallel to the Z-axis passing through `origin`."""
        self.angle_z += angle
        c, s = np.cos(angle), np.sin(angle)
        r_matrix = np.array([
            [ c,  s,  0],
            [-s,  c,  0],
            [ 0,  0,  1]
        ])
        self._apply_rotation(r_matrix, origin)

    def _apply_rotation(self, r_matrix, origin=None):
        vertices = np.array([self.start, self.end])

        if origin is not None:
            origin = np.asarray(origin, dtype=float)
            vertices = vertices - origin

        rotated = np.dot(vertices, r_matrix)

        if origin is not None:
            rotated = rotated + origin

        self.start, self.end = rotated[0], rotated[1]

import numpy as np
from collections import defaultdict

def _round_pt(point, decimals=5):
    """Normalize coordinate tuples to mitigate floating-point drift."""
    return tuple(np.round(np.asarray(point, dtype=float), decimals=decimals))

def build_graph(lines, decimals=5):
    """
    Builds an adjacency list and edge lookup from an array of Line objects.
    Returns:
        adj: dict mapping vertex -> list of neighbor vertices
        edge_map: dict mapping (u, v) -> Line object
    """
    adj = defaultdict(set)
    edge_map = {}

    for line in lines:
        u = _round_pt(line.start, decimals)
        v = _round_pt(line.end, decimals)

        if u == v:
            continue  # ignore zero-length segments

        adj[u].add(v)
        adj[v].add(u)
        edge_map[(u, v)] = line
        edge_map[(v, u)] = line

    return adj, edge_map

def find_connected_shapes(lines, decimals=5):
    """
    Finds isolated shapes (connected components of lines).
    Returns a list of lists, where each inner list contains the Line objects of that shape.
    """
    adj, edge_map = build_graph(lines, decimals)
    visited_nodes = set()
    components = []

    for node in list(adj.keys()):
        if node not in visited_nodes:
            component_lines = []
            queue = [node]
            visited_nodes.add(node)
            seen_edges = set()

            while queue:
                curr = queue.pop(0)
                for neighbor in adj[curr]:
                    edge_key = tuple(sorted([curr, neighbor]))
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        component_lines.append(edge_map[(curr, neighbor)])

                    if neighbor not in visited_nodes:
                        visited_nodes.add(neighbor)
                        queue.append(neighbor)

            if component_lines:
                components.append(component_lines)

    return components

def find_closed_cycles(lines, decimals=5, max_cycle_len=10):
    """
    Finds simple closed cycles (polygons) within the line network.
    Returns a list of vertex paths forming closed loops: [[p1, p2, ..., p1], ...]
    """
    adj, _ = build_graph(lines, decimals)
    cycles = []

    def dfs(start, current, visited_path):
        if len(visited_path) > max_cycle_len:
            return

        for neighbor in adj[current]:
            if neighbor == start and len(visited_path) >= 3:
                cycle = tuple(visited_path + [start])
                # Canonical representation to avoid reporting reverse/shifted duplicates
                min_idx = cycle[:-1].index(min(cycle[:-1]))
                canonical_1 = cycle[min_idx:-1] + cycle[:min_idx] + (cycle[min_idx],)
                rev = tuple(reversed(cycle[:-1]))
                min_rev_idx = rev.index(min(rev))
                canonical_2 = rev[min_rev_idx:] + rev[:min_rev_idx] + (rev[min_rev_idx],)
                canonical = min(canonical_1, canonical_2)

                if canonical not in seen_cycles:
                    seen_cycles.add(canonical)
                    cycles.append(list(canonical))
            elif neighbor not in visited_path:
                dfs(start, neighbor, visited_path + [neighbor])

    seen_cycles = set()
    for node in adj:
        dfs(node, node, [node])

    return cycles


def find_closed_cycles_as_lines(lines, decimals=5, max_cycle_len=10):
    """
    Finds simple closed cycles within the line network.
    Returns:
        A list of lists, where each inner list contains the Line objects
        in sequential order forming a closed loop: [[Line1, Line2, Line3], ...]
    """
    adj, edge_map = build_graph(lines, decimals)
    cycle_lines_list = []
    seen_cycles = set()

    def dfs(start, current, visited_path):
        if len(visited_path) > max_cycle_len:
            return

        for neighbor in adj[current]:
            # Found a loop back to the start node (minimum 3 edges for a polygon)
            if neighbor == start and len(visited_path) >= 3:
                cycle_nodes = tuple(visited_path + [start])

                # Canonical representation to deduplicate reversed or shifted traversals
                nodes_only = cycle_nodes[:-1]
                min_idx = nodes_only.index(min(nodes_only))
                canonical_fwd = nodes_only[min_idx:] + nodes_only[:min_idx] + (nodes_only[min_idx],)

                rev = tuple(reversed(nodes_only))
                min_rev_idx = rev.index(min(rev))
                canonical_rev = rev[min_rev_idx:] + rev[:min_rev_idx] + (rev[min_rev_idx],)

                canonical = min(canonical_fwd, canonical_rev)

                if canonical not in seen_cycles:
                    seen_cycles.add(canonical)

                    # Convert consecutive vertex pairs into original Line instances
                    cycle_edges = [
                        edge_map[(canonical[i], canonical[i + 1])]
                        for i in range(len(canonical) - 1)
                    ]
                    cycle_lines_list.append(cycle_edges)

            elif neighbor not in visited_path:
                dfs(start, neighbor, visited_path + [neighbor])

    for node in list(adj.keys()):
        dfs(node, node, [node])

    return cycle_lines_list