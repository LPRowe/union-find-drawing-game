import pygame
import time
import math
import matplotlib.pyplot as plt
import numpy as np

# Add removal (erase and mark all groups affected by erase)
# Delete all nodes in those groups, and re-add them back in one by one

# TODO:
# 1. add mouse tracking, 1 click and 2 click -> create vertices
# 2. add shape selection by keyboard input
#    add shape icon based on current shape in top right corner
# 3. add union find data structure to keep track of which groups are connected
# 4. add color based on union find data structure group id
# 5. add eraser tool to shape selection and have union find update all related nodes

# [SOLVED] 1. why is union find running so slow? unnecessary cycle? numpy?
# [CHECK ARR UPDATE] 2. why is union find not updating surface every action? seemingly random

# add a paint fill button (right click)
# add color brightness adjust with mouse scroll

class UnionFind():
    """
    Non-standard implementation of union find.
    Each shape's nodes are connected like a network.
    When shapes overlap, their two networks merge together into a larger group (network) of nodes.
    
    Serves a second function to create a pygame surface to display the current shapes
    where shapes of the same color belong to the same group.
    
    params:
        surface_shape (num_rows, num_cols) of the drawing plane
        brightness int [0, 255] controls how bright the shapes are
        color_wheel tuple of (R, G, B) tuples where R, G, B are integers [0, 255] 
    """
    def __init__(self, surface_shape, brightness, color_wheel):
        self.group_id = 0
        self.group = {}
        self.id = {}
        
        self.colors = color_wheel
        self.R, self.C = surface_shape
        self.arr = np.array([[(0,)*3 for _ in range(self.C)] for _ in range(self.R)]) # row, column, RGB
        self.brightness = brightness
        self.surface = pygame.surfarray.make_surface(self.arr)
        
    def update_arr(self):
        """
        Updates the array for all nodes affected by most recent union.
        """
        for node_id in self.group:
            color = self.colors[node_id % len(self.colors)]
            print(node_id, color)
            for x, y in self.group[node_id]:
                self.arr[x][y] = color
        print('x')
        self.update_surface()
    
    def update_surface(self):
        """
        Creates a pygame surface of the array.
        """
        self.surface = pygame.surfarray.make_surface(self.arr)
    
    def normalize_brightness(self):
        """
        Converts all pixels that are on to the same intensity.
        """
        for i in range(self.R):
            for j in range(self.C):
                if sum(self.arr[i][j]) != 0:
                    c = self.brightness / math.sqrt(sum(self.arr[i][j][k]**2 for k in range(3)))
                    for k in range(3):
                        self.arr[i][j][k] *= c
        
    def union(self, a, b):
        """Union nodes a and b"""
        A, B = a in self.id, b in self.id
        if A and B and self.id[a] != self.id[b]:
            self.merge(a, b)
        elif A or B:
            self.add(a, b)
        else:
            self.create(a, b)
        return self.id[a] if a in self.id else self.id[b]
    
    def merge(self, a, b):
        """Nodes a and b both belong to a group, merge the smaller group with the larger group."""
        obs, targ = sorted((self.id[a], self.id[b]), key = lambda i: len(self.group[i]))
        for node in self.group[obs]:
            self.id[node] = targ
        self.group[targ] |= self.group[obs]
        del self.group[obs]
    
    def add(self, a, b):
        """Node a or node b does not have a group.  Add the new node to the existing group."""
        a, b = (a, b) if a in self.id else (b, a)
        targ = self.id[a]
        self.id[b] = targ
        self.group[targ] |= {b}
    
    def create(self, a, b):
        """Neither node a nor b belong to a group.  Create a new group {a, b}."""
        self.group[self.group_id] = {a, b}
        self.id[a] = self.id[b] = self.group_id
        self.group_id += 1

class Shape():
    def __init__(self, vertices):
        self.vertices = vertices      # List of vertices of the shape (order matters)
        self.edges = self.get_edges() # Set of nodes that make the outline of the shape
        self.nodes = self.edges       # Set of edge nodes, vertex nodes, and nodes to fill in the shape
    
    @staticmethod
    def get_line(x0, y0, x1, y1):
        """Recursively finds all integer points that connect (x0, y0) to (x1, y1)"""
        def helper(x0, y0, x1, y1):
            nonlocal seen, points
            a, b, c, d = int(round(x0, 0)), int(round(y0, 0)), int(round(x1, 0)), int(round(y1, 0))
            h = (a, b, c, d)
            if h not in seen:
                seen.add(h)
                points |= {(a, b), (c, d)}
                if a == c and b == d:
                    return None
                xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
                helper(x0, y0, xm, ym)
                helper(xm, ym, x1, y1)
        seen = set()
        points = {(x0, y0), (x1, y1)}
        helper(x0, y0, x1, y1)
        return points
    
    @staticmethod
    def get_centroid(vertices):
        X = Y = 0
        for v in vertices:
            X += v[0]
            Y += v[1]
        return (X / len(vertices), Y / len(vertices))
    
    @staticmethod
    def get_neighbors(x, y):
        """
        y: int row
        x: int column
        returns 4-directionaly adjacent neighbors to (x, y)
        """
        return ((x+1, y), (x-1, y), (x, y+1), (x, y-1))
    
    def get_edges(self):
        """Returns all points that connect the vertices (including the vertices themselves)"""
        if not self.vertices:
            print("Shape must have vertices before edges can be drawn")
            return [(0, 0)]
        edges = set()
        for (x0, y0), (x1, y1) in zip(self.vertices, self.vertices[1:] + [self.vertices[0]]):
            edges |= self.get_line(x0, y0, x1, y1)
        return edges
    
    def fill_shape(self):
        """
        Shapes such as stars, squares, triangles can be filled in with points.
        fill_shape should not be called on a line or freehand shape.
        
        Performs BFS from the central point of the shape (average of all vertices).
        Returns all visited points, never going outside of the edge boundary.
        """
        if len(self.edges) < 3:
            raise Exception("A shape must have at least 3 edges in order to be filled")
        elif len(self.vertices) < 3:
            raise Exception(f"Shape has {len(self.vertices)} vertices, must have at least 3 to be filled.")
            
        X, Y = self.get_centroid(self.vertices)
        
        if self.get_centroid in self.edges:
            raise Exception(f"Shape is too small or thin to fill.")
        
        q = [(int(X), int(Y))]
        visited = self.edges
        while q:
            next_level = []
            for node in q:
                for neighbor in self.get_neighbors(*node):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_level.append(neighbor)
            q = next_level
        self.nodes |= visited
    
def create_vertices(x0, y0, x1, y1, name = "rectangle"):
    """
    Fist click is position x0, y0
    Current mouse position (or second click) is position x1, y1
    Calculates the vertex points for the given shape
    """
    if name == "free":
        return [(x0, y0), (x1, y1)]
    
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1), reverse = False)
    if x0 == x1: x1 += 1
    if y0 == y1: y0 += 1
    
    a, b, c, d = (x0, y0), (x1, y0), (x0, y1), (x1, y1) # four corners (TL, TR, BL, BR)
    x_midpoint = (x0 + x1) / 2
    y_midpoint = (y0 + y1) / 2
    
    if name == "rectangle":
        vertices = [a, b, d, c]
    elif name == "triangle1":
        vertices = [(x_midpoint, y0), c, d]
    elif name == "triangle2":
        vertices = [(x_midpoint, y1), a, b]
    elif name == "triangle3":
        vertices = [(x0, y_midpoint), b, d]
    elif name == "triangle4":
        vertices = [(x1, y_midpoint), a, c]
    elif name in ["pentagon", "star"]:
        theta = 36 * math.pi / 180
        hy= (x_midpoint - x0) * math.tan(theta) * (y0 - y1) / (x1 - x0)
        hx = (y_midpoint - y1) * math.tan(theta / 2) * (x1 - x0) / (y0 - y1)
        top = (x_midpoint, y0)
        left = (x0, y0 - hy)
        right = (x1, y0 - hy)
        bottom_left = (x0 + hx, y1)
        bottom_right = (x1 - hx, y1)
        if name == "pentagon":
            vertices = [top, right, bottom_right, bottom_left, left]
        else:
            vertices = [bottom_left, top, bottom_right, left, right]
    else:
        vertices = [(x0, y0), (x1, y1)]
    
    return vertices
    

class Game():
    def __init__(self, **kwargs):
        pygame.init()
        for key in kwargs:
            self.__dict__[key] = kwargs[key]
        self.SURFACE = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        
        self.active = True           # True when the game is running
        self.left_click_down = False # monitor status of left click
        
        # Cycle through shape to draw
        self.shapes = ["rectangle", "triangle1", "triangle2", "triangle3", "triangle4", 
                       "pentagon", "star", "free"]
        self.shape_id = 0
        
        # Record drawn shapes in a Union Find data structure
        self.uf = UnionFind(surface_shape = (self.WIDTH, self.HEIGHT),
                            brightness = self.BRIGHTNESS,
                            color_wheel = self.COLOR_WHEEL)
        
        # Store temporary shapes (outlined but not drawn here)
        self.shape_outline = set()
        
        # Inputs are locked until time > input_lock
        self.input_lock = -1
        
    def temporary_lock(self):
        self.input_lock = time.time() + self.LOCK_TIME
        
    def run(self):
        
        while self.active:
            time.sleep(self.SLEEP_TIME)
            
            self.get_events()
            
            keys = pygame.key.get_pressed()
            mouse = pygame.mouse.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            t = time.time()
            
            # Change mode (shape) by up or down arrow
            if t >= self.input_lock:
                if keys[pygame.K_UP]:
                    self.shape_id = (self.shape_id + 1) % len(self.shapes)
                    self.temporary_lock()
                    print(self.shapes[self.shape_id])
                    # TODO: update icon
                elif keys[pygame.K_DOWN]:
                    self.shape_id = (self.shape_id - 1) % len(self.shapes)
                    self.temporary_lock()
                    print(self.shapes[self.shape_id])
                    # TODO: update shape icon
            
            if not self.left_click_down and mouse[0]:
                print('a')
                self.left_click_down = True
                self.temporary_lock()
                x0, y0 = mouse_pos
            elif self.left_click_down and mouse[0]:
                x1, y1 = mouse_pos
                x1 = max(0, min(self.WIDTH - 2, x1))
                y1 = max(0, min(self.HEIGHT - 2, y1))
                vertices = create_vertices(x0, y0, x1, y1, name = self.shapes[self.shape_id])
                self.shape_outline = vertices[:]
                shape = Shape(vertices)
            elif self.left_click_down and not mouse[0]:
                print('c')
                # release to draw shape; use try and catch to handle errors from too small of shape
                self.left_click_down = False
                self.shape_outline = set()
                if self.shape_id <= -1: # only fill shapes do not fill star or free hand drawings
                    try: shape.fill_shape()
                    except: pass # Shape is too small/thin do not fill
                print('c1')
                # add the shape's nodes to the union find data structure
                for node in shape.nodes:
                    node = (int(node[0]), int(node[1]))
                    self.uf.union(node, node)
                    ids = set()
                    for neighbor in Shape.get_neighbors(*node):
                        ids.add(self.uf.union(node, neighbor))
                self.uf.update_arr()
                
                print(np.sum(self.uf.arr))
            
            self.draw()
    
        pygame.quit()
        
    def get_events(self):
        """Gets key and mouse inputs.  Deactivates game if input action was quit."""
        self.events = pygame.event.poll()
        if self.events.type == pygame.QUIT:
            self.active = False
        self.keys_press = pygame.key.get_pressed()
        self.mouse_press = pygame.mouse.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()

    def draw(self):
        # blit shapes already made and merged
        self.SURFACE.blit(self.uf.surface, (0, 0))
        
        
        # blit oultine of shape being considered (use pygame.draw)
        if self.shape_outline:
            pygame.draw.lines(self.SURFACE, (200, 200, 200), True, 
                               self.shape_outline, 5)
            
        pygame.display.flip()


if __name__ == "__main__":
    a, b, c = 51, 153, 255
    color_wheel = ((c, a, a), (c, b, a), (c, c, a), (b, c, a), (a, c, a), 
                   (a, c, b), (a, c, c), (a, b, c), (a, a, c), 
                   (b, a, c), (c, a, c), (c, a, b), (b, b, b))
    
    settings = {"WIDTH": 800,
                "HEIGHT": 800,
                "HEADER_RATIO": 0.15,
                "SLEEP_TIME": 0,
                "LOCK_TIME": 0.2,
                "COLOR_WHEEL": color_wheel,
                "BRIGHTNESS": 200 # intensity of shapes colors [0, 255]
                }
    
    g = Game(**settings)
    g.run()
    
    