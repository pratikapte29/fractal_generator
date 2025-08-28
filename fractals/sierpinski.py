import numpy as np
import math
import random
from PIL import Image, ImageDraw

class SierpinskiGenerator:
    """Sierpinski Triangle generator - thread-safe version using PIL"""
    
    def __init__(self):
        """Initialize the generator"""
        pass
    
    def generate(self, width=800, height=600, depth=7, size=300.0, 
                 start_x=0.0, start_y=0.0, method='recursive', 
                 num_points=50000, **kwargs):
        """Generate Sierpinski triangle using specified method"""
        
        if method == 'chaos_game':
            return self._chaos_game_method(width, height, size, start_x, start_y, num_points)
        else:
            return self._recursive_method(width, height, depth, size, start_x, start_y)
    
    def _recursive_method(self, width, height, depth, size, start_x, start_y):
        """Generate Sierpinski triangle using recursive subdivision"""
        
        # Create a PIL image with black background
        img = Image.new('RGB', (width, height), 'black')
        draw = ImageDraw.Draw(img)
        
        # Calculate initial triangle vertices (centered in image)
        center_x = width // 2 + start_x
        center_y = height // 2 + start_y
        triangle_height = size * math.sqrt(3) / 2
        
        vertices = [
            (center_x - size/2, center_y - triangle_height/3),
            (center_x + size/2, center_y - triangle_height/3),
            (center_x, center_y + 2*triangle_height/3)
        ]
        
        # Generate Sierpinski triangle recursively
        self._draw_sierpinski_recursive(draw, vertices, depth)
        
        # Convert PIL image to numpy array
        img_array = np.array(img)
        
        # Convert to grayscale for fractal data
        grayscale = np.mean(img_array, axis=2)
        
        return grayscale
    
    def _chaos_game_method(self, width, height, size, start_x, start_y, num_points):
        """Generate Sierpinski triangle using chaos game method"""
        
        # Create a PIL image with black background
        img = Image.new('RGB', (width, height), 'black')
        draw = ImageDraw.Draw(img)
        
        # Calculate triangle vertices (centered in image)
        center_x = width // 2 + start_x
        center_y = height // 2 + start_y
        triangle_height = size * math.sqrt(3) / 2
        
        vertices = [
            (center_x - size/2, center_y - triangle_height/3),
            (center_x + size/2, center_y - triangle_height/3),
            (center_x, center_y + 2*triangle_height/3)
        ]
        
        # Starting point (random point inside triangle)
        current_x = center_x
        current_y = center_y
        
        # Chaos game algorithm
        for i in range(num_points):
            # Choose random vertex
            vertex_idx = random.randint(0, 2)
            target_x, target_y = vertices[vertex_idx]
            
            # Move halfway to chosen vertex
            current_x = (current_x + target_x) / 2
            current_y = (current_y + target_y) / 2
            
            # Skip first few points to avoid initial bias
            if i > 100:
                # Draw a small point
                x, y = int(current_x), int(current_y)
                if 0 <= x < width and 0 <= y < height:
                    # Draw a small square for better visibility
                    draw.rectangle([x-1, y-1, x+1, y+1], fill='white')
        
        # Convert PIL image to numpy array
        img_array = np.array(img)
        
        # Convert to grayscale for fractal data
        grayscale = np.mean(img_array, axis=2)
        
        return grayscale
    
    def _draw_sierpinski_recursive(self, draw, vertices, depth):
        """Recursively draw Sierpinski triangle"""
        if depth == 0:
            # Draw filled triangle
            triangle_points = [(int(v[0]), int(v[1])) for v in vertices]
            draw.polygon(triangle_points, fill='white', outline='white')
            return
        
        # Calculate midpoints of each side
        midpoints = [
            ((vertices[0][0] + vertices[1][0]) / 2, (vertices[0][1] + vertices[1][1]) / 2),
            ((vertices[1][0] + vertices[2][0]) / 2, (vertices[1][1] + vertices[2][1]) / 2),
            ((vertices[2][0] + vertices[0][0]) / 2, (vertices[2][1] + vertices[0][1]) / 2)
        ]
        
        # Create three smaller triangles
        triangle1 = [vertices[0], midpoints[0], midpoints[2]]
        triangle2 = [midpoints[0], vertices[1], midpoints[1]]
        triangle3 = [midpoints[2], midpoints[1], vertices[2]]
        
        # Recursively draw each triangle
        self._draw_sierpinski_recursive(draw, triangle1, depth - 1)
        self._draw_sierpinski_recursive(draw, triangle2, depth - 1)
        self._draw_sierpinski_recursive(draw, triangle3, depth - 1)
