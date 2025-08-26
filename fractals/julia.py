import numpy as np 

class JuliaGenerator:
    """Simple Julia set generator"""
    
    @staticmethod
    def generate(width=800, height=600, x_min=-2.0, x_max=2.0, 
                 y_min=-2.0, y_max=2.0, max_iterations=100,
                 c_real=-0.7, c_imag=0.27015, **kwargs):
        
        x = np.linspace(x_min, x_max, width)
        y = np.linspace(y_min, y_max, height)
        X, Y = np.meshgrid(x, y)
        Z = X + 1j * Y
        
        c = complex(c_real, c_imag)
        result = np.zeros((height, width))
        
        for i in range(height):
            for j in range(width):
                z = Z[i, j]
                for n in range(max_iterations):
                    if abs(z) > 2:
                        break
                    z = z*z + c
                result[i, j] = n
        
        return result