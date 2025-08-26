import numpy as np
import math
from PIL import Image, ImageDraw

class KochGenerator:
    """Koch Snowflake generator - thread-safe version using PIL"""
    
    @staticmethod
    def generate(width=800, height=600, depth=5, size=300.0, 
                 start_x=0.0, start_y=0.0, angle=0.0, line_width=1, **kwargs):
        """Generate Koch snowflake using PIL (thread-safe)"""
        
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
        
        # Apply rotation if specified
        if angle != 0:
            vertices = KochGenerator._rotate_points(vertices, angle, (center_x, center_y))
        
        # Generate Koch curves for each side of the triangle
        all_points = []
        for i in range(3):
            start_point = vertices[i]
            end_point = vertices[(i + 1) % 3]
            koch_points = KochGenerator._koch_curve(start_point, end_point, depth)
            all_points.extend(koch_points[:-1])  # Exclude last point to avoid duplication
        
        # Draw the snowflake
        if all_points and len(all_points) > 1:
            # Convert to list of tuples for PIL
            points_list = [(int(p[0]), int(p[1])) for p in all_points]
            
            # Close the shape by adding the first point at the end
            points_list.append(points_list[0])
            
            # Draw lines connecting all points
            for i in range(len(points_list) - 1):
                draw.line([points_list[i], points_list[i + 1]], 
                         fill='white', width=line_width)
        
        # Convert PIL image to numpy array
        img_array = np.array(img)
        
        # Convert to grayscale for fractal data
        grayscale = np.mean(img_array, axis=2)
        
        return grayscale
    
    @staticmethod
    def _koch_curve(start, end, depth):
        """Generate Koch curve between two points"""
        if depth == 0:
            return [start, end]
        
        # Calculate the four points of the Koch curve
        p1 = start
        p5 = end
        
        # Point 1/3 along the line
        p2 = (
            p1[0] + (p5[0] - p1[0]) / 3,
            p1[1] + (p5[1] - p1[1]) / 3
        )
        
        # Point 2/3 along the line
        p4 = (
            p1[0] + 2 * (p5[0] - p1[0]) / 3,
            p1[1] + 2 * (p5[1] - p1[1]) / 3
        )
        
        # Calculate the peak point (equilateral triangle)
        dx = p4[0] - p2[0]
        dy = p4[1] - p2[1]
        
        # Rotate 60 degrees counterclockwise
        p3 = (
            p2[0] + dx * math.cos(math.pi/3) - dy * math.sin(math.pi/3),
            p2[1] + dx * math.sin(math.pi/3) + dy * math.cos(math.pi/3)
        )
        
        # Recursively generate Koch curves for each segment
        curve1 = KochGenerator._koch_curve(p1, p2, depth - 1)
        curve2 = KochGenerator._koch_curve(p2, p3, depth - 1)
        curve3 = KochGenerator._koch_curve(p3, p4, depth - 1)
        curve4 = KochGenerator._koch_curve(p4, p5, depth - 1)
        
        # Combine curves (remove duplicate points)
        result = curve1[:-1] + curve2[:-1] + curve3[:-1] + curve4
        return result
    
    @staticmethod
    def _rotate_points(points, angle_degrees, center):
        """Rotate points around a center"""
        angle = math.radians(angle_degrees)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        cx, cy = center
        
        rotated = []
        for x, y in points:
            # Translate to origin
            x -= cx
            y -= cy
            
            # Rotate
            new_x = x * cos_a - y * sin_a
            new_y = x * sin_a + y * cos_a
            
            # Translate back
            new_x += cx
            new_y += cy
            
            rotated.append((new_x, new_y))
        
        return rotated
    
    @staticmethod
    def _koch_curve(start, end, depth):
        """Generate Koch curve between two points"""
        if depth == 0:
            return [start, end]
        
        # Calculate the four points of the Koch curve
        p1 = start
        p5 = end
        
        # Point 1/3 along the line
        p2 = (
            p1[0] + (p5[0] - p1[0]) / 3,
            p1[1] + (p5[1] - p1[1]) / 3
        )
        
        # Point 2/3 along the line
        p4 = (
            p1[0] + 2 * (p5[0] - p1[0]) / 3,
            p1[1] + 2 * (p5[1] - p1[1]) / 3
        )
        
        # Calculate the peak point (equilateral triangle)
        dx = p4[0] - p2[0]
        dy = p4[1] - p2[1]
        
        # Rotate 60 degrees counterclockwise
        p3 = (
            p2[0] + dx * math.cos(math.pi/3) - dy * math.sin(math.pi/3),
            p2[1] + dx * math.sin(math.pi/3) + dy * math.cos(math.pi/3)
        )
        
        # Recursively generate Koch curves for each segment
        curve1 = KochGenerator._koch_curve(p1, p2, depth - 1)
        curve2 = KochGenerator._koch_curve(p2, p3, depth - 1)
        curve3 = KochGenerator._koch_curve(p3, p4, depth - 1)
        curve4 = KochGenerator._koch_curve(p4, p5, depth - 1)
        
        # Combine curves (remove duplicate points)
        result = curve1[:-1] + curve2[:-1] + curve3[:-1] + curve4
        return result
    
    @staticmethod
    def _rotate_points(points, angle_degrees, center):
        """Rotate points around a center"""
        angle = math.radians(angle_degrees)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        cx, cy = center
        
        rotated = []
        for x, y in points:
            # Translate to origin
            x -= cx
            y -= cy
            
            # Rotate
            new_x = x * cos_a - y * sin_a
            new_y = x * sin_a + y * cos_a
            
            # Translate back
            new_x += cx
            new_y += cy
            
            rotated.append((new_x, new_y))
        
        return rotated