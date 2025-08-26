import numpy as np
from numba import jit
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fractal_generator import BaseFractalGenerator

class MandelbrotGenerator(BaseFractalGenerator):
    """Generator for Mandelbrot Set fractal"""
    
    def __init__(self):
        super().__init__()
        self.name = "Mandelbrot Set"
    
    def generate(self, width=800, height=600, x_min=-2.0, x_max=2.0, 
                 y_min=-2.0, y_max=2.0, max_iterations=100, escape_radius=2.0, **kwargs):
        """Generate Mandelbrot set"""
        
        # Create coordinate arrays
        x = np.linspace(x_min, x_max, width)
        y = np.linspace(y_min, y_max, height)
        X, Y = np.meshgrid(x, y)
        
        # Create complex plane
        C = X + 1j * Y
        
        # Generate Mandelbrot set
        mandelbrot_data = self._mandelbrot_set(C, max_iterations, escape_radius)
        
        return mandelbrot_data
    
    @staticmethod
    @jit(nopython=True)
    def _mandelbrot_set(C, max_iterations, escape_radius):
        """Optimized Mandelbrot calculation using Numba"""
        height, width = C.shape
        result = np.zeros((height, width), dtype=np.float64)
        
        for i in range(height):
            for j in range(width):
                c = C[i, j]
                z = 0 + 0j
                
                for n in range(max_iterations):
                    if abs(z) > escape_radius:
                        break
                    z = z*z + c
                
                # Color based on iteration count
                if n == max_iterations - 1:
                    result[i, j] = 0  # Inside set (black)
                else:
                    # Smooth coloring
                    result[i, j] = n + 1 - np.log2(np.log2(abs(z)))
                    
        return result
    
    def get_default_params(self):
        """Get default parameters for Mandelbrot set"""
        return {
            'width': 800,
            'height': 600,
            'x_min': -2.0,
            'x_max': 2.0,
            'y_min': -2.0,
            'y_max': 2.0,
            'max_iterations': 100,
            'escape_radius': 2.0
        }
    
    def zoom_to_point(self, center_x, center_y, zoom_factor, current_params):
        """Create new parameters for zooming to a specific point"""
        current_width = current_params['x_max'] - current_params['x_min']
        current_height = current_params['y_max'] - current_params['y_min']
        
        new_width = current_width / zoom_factor
        new_height = current_height / zoom_factor
        
        return {
            **current_params,
            'x_min': center_x - new_width / 2,
            'x_max': center_x + new_width / 2,
            'y_min': center_y - new_height / 2,
            'y_max': center_y + new_height / 2
        }