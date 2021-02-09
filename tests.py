# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 12:09:53 2021

@author: rowe1
"""

import matplotlib.pyplot as plt
import math

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
        
    def draw(self, surface):
        pass
    
def create_vertices(x0, y0, x1, y1, name = "rectangle"):
    """
    Fist click is position x0, y0
    Current mouse position (or second click) is position x1, y1
    Calculates the vertex points for the given shape
    """
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1), reverse = True)
    a, b, c, d = (x0, y0), (x1, y0), (x0, y1), (x1, y1) # four corners (TL, TR, BL, BR)
    x_midpoint = (x0 + x1) / 2
    y_midpoint = (y0 + y1) / 2
    print(x0, y0, x1, y1)
    
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
        print(x0, y0, x1, y1)
        top = (x_midpoint, y0)
        left = (x0, y0 - hy)
        right = (x1, y0 - hy)
        bottom_left = (x0 + hx, y1)
        bottom_right = (x1 - hx, y1)
        
        if name == "pentagon":
            vertices = [top, right, bottom_right, bottom_left, left]
        else:
            vertices = [bottom_left, top, bottom_right, left, right]
    
    return vertices

if __name__ == "__main__":
    GET_LINE = True       # Test get all linear integer points between start and end point
    GET_EDGES = False      # Test get all lines for a list of vertices (outline of shape)
    FILL_SHAPE = False     # Test Fill in the shape (the star is a special case)
    CREATE_VERTICES = False # Test Generate shape vertices from top left and bottom right bounding box points
    
    if GET_LINE:
        plt.close('all')
        get_line_test_points = [(1, 3, 7, 11),      # low to high
                                (7, 11, 1, 3),      # high to low
                                (-17, 20, 10, 20),  # horizontal
                                (-5, 10, -5, 15),   # vertical
                                (0, 0, 0, 0),       # single point
                                (10, 20, 20, 10),
                                (0, 0, 100, 1)]     # very shallow slope
        for i in range(len(get_line_test_points)):
            x0, y0, x1, y1 = get_line_test_points[i]
            points = Shape.get_line(x0, y0, x1, y1)
            plt.figure(i)
            plt.scatter(*list(zip(*points)))
            plt.show()
    
    if GET_EDGES | FILL_SHAPE:
        plt.close('all')
        vertices = [[(0, 0), (0, 10), (10, 10), (10, 0)],    # Square
                   [(0, 0), (10, 14), (20, 0)],              # Triangle
                   [(0.5, 1.5), (5, 10), (10, 0), (5, -10)], # Floats
                   [],                                       # Empty
                   [(-5, 10), (20, 0)]                       # Line
                   ]
        shapes = []
        
        for i, v in enumerate(vertices):
            shapes.append(Shape(v))
            edges = shapes[-1].get_edges()
            plt.figure(i)
            plt.scatter(*list(zip(*edges)))
            
        if FILL_SHAPE:
            for i in range(3):            
                shape = shapes[i]
                shape.fill_shape()
                plt.figure(i)
                plt.scatter(*list(zip(*shape.nodes)))
    
    if CREATE_VERTICES:
        names = ["rectangle", "triangle1", "triangle2", "triangle3", "triangle4", "pentagon", "star"]
        plt.close('all')
        x0, y0, x1, y1 = 0, 200, 500, 0
        for name in names:
            v = create_vertices(x0, y0, x1, y1, name = name)
            shape = Shape(v)
            edges = shape.edges
            shape.fill_shape()
            plt.figure(name)
            plt.scatter(*list(zip(*shape.nodes)))
        
    
    
    