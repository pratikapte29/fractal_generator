#!/usr/bin/env python3
"""
Working Fractal Generator - Fixed version without complex imports
"""

import sys
import os
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QGroupBox, QLabel, 
                             QComboBox, QSpinBox, QDoubleSpinBox, QPushButton,
                             QProgressBar, QGraphicsView, QGraphicsScene,
                             QMessageBox, QGraphicsPixmapItem, QFileDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QImage, QPainter
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image
import time
from fractals.mandelbrot import MandelbrotGenerator
from fractals.julia import JuliaGenerator
from fractals.barnsley_fern import BarnsleyFernGenerator
from fractals.burning_ship import BurningShipGenerator
from fractals.dragon_curve import DragonGenerator
from fractals.koch_snowflake import KochGenerator
from fractals.newton import NewtonGenerator
from fractals.sierpinski import SierpinskiGenerator

class TestPatternGenerator:
    """Simple test pattern for debugging"""
    
    @staticmethod
    def generate(width=800, height=600, **kwargs):
        # Create a simple test pattern
        x = np.linspace(0, 4*np.pi, width)
        y = np.linspace(0, 4*np.pi, height)
        X, Y = np.meshgrid(x, y)
        
        # Sine wave pattern
        result = np.sin(X) * np.cos(Y) * 50 + 50
        
        return result

class FractalGenerator:
    """Main fractal generator with embedded generators"""
    
    def __init__(self):
        self.color_schemes = {
            'Classic': plt.cm.hot,
            'Hot': plt.cm.hot,
            'Cool': plt.cm.cool,
            'Viridis': plt.cm.viridis,
            'Plasma': plt.cm.plasma,
            'Rainbow': plt.cm.rainbow,
            'Grayscale': plt.cm.gray
        }
        
        self.generators = {
            'Mandelbrot Set': MandelbrotGenerator(),
            'Julia Set': JuliaGenerator(),
            "Koch Snowflake": KochGenerator(),
            "Sierpinski": SierpinskiGenerator(),
            "Dragon Curve": DragonGenerator(),
            "Barnsley Fern": BarnsleyFernGenerator(),
            "Newton": NewtonGenerator(),
            "Burning Ship": BurningShipGenerator(),
            'Test Pattern': TestPatternGenerator()
        }
    
    def generate_fractal(self, fractal_type, **params):
        """Generate fractal based on type"""
        if fractal_type in self.generators:
            return self.generators[fractal_type].generate(**params)
        else:
            raise ValueError(f"Unsupported fractal type: {fractal_type}")
    
    def apply_colormap(self, data, color_scheme='Classic'):
        """Apply color scheme to fractal data"""
        colormap = self.color_schemes.get(color_scheme, plt.cm.hot)
        
        if data.max() > data.min():
            normalized = (data - data.min()) / (data.max() - data.min())
        else:
            normalized = data
            
        colored_data = colormap(normalized)
        rgb_data = (colored_data[:, :, :3] * 255).astype(np.uint8)
        
        return rgb_data
    
    def create_fractal_image(self, fractal_type, **params):
        """Complete fractal generation pipeline"""
        start_time = time.time()
        
        color_scheme = params.pop('color_scheme', 'Classic')
        
        print(f"Generating {fractal_type}...")
        fractal_data = self.generate_fractal(fractal_type, **params)
        colored_image = self.apply_colormap(fractal_data, color_scheme)
        
        generation_time = time.time() - start_time
        print(f"Generation completed in {generation_time:.2f} seconds")
        
        return colored_image, fractal_data

class FractalGenerationThread(QThread):
    """Thread for generating fractals"""
    
    progress_update = pyqtSignal(int)
    generation_complete = pyqtSignal(np.ndarray, np.ndarray)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, fractal_type, params):
        super().__init__()
        self.fractal_type = fractal_type
        self.params = params
        self.generator = FractalGenerator()
        self.generation_time = 0
    
    def run(self):
        try:
            start_time = time.time()
            self.progress_update.emit(10)
            
            colored_image, raw_data = self.generator.create_fractal_image(
                self.fractal_type, **self.params
            )
            
            self.generation_time = time.time() - start_time
            self.progress_update.emit(100)
            self.generation_complete.emit(colored_image, raw_data)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class FractalGeneratorUI(QMainWindow):
    """Main UI class"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fractal Generator - Working Version")
        self.setGeometry(100, 100, 1200, 800)
        
        self.current_image = None
        self.current_raw_data = None
        self.generation_thread = None
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 8px;
                margin: 5px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 5px;
                padding: 8px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:disabled {
                background-color: #333333;
                color: #666666;
            }
            QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                min-height: 20px;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel
        left_panel = QWidget()
        left_panel.setFixedWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        # Title
        title_label = QLabel("Fractal Generator")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #ffffff; margin: 10px;")
        left_layout.addWidget(title_label)
        
        # Fractal selection
        selection_group = QGroupBox("Fractal Type")
        selection_layout = QVBoxLayout(selection_group)
        
        self.fractal_combo = QComboBox()
        self.fractal_combo.addItems([
            "Select Fractal Type...",
            "Mandelbrot Set",
            "Julia Set",
            "Koch Snowflake",
            "Sierpinski",
            "Dragon Curve",
            "Barnsley Fern",
            "Newton",
            "Burning Ship",
            "Test Pattern"
        ])
        selection_layout.addWidget(self.fractal_combo)
        left_layout.addWidget(selection_group)
        
        # Parameters
        self.create_parameter_groups(left_layout)
        
        # Control buttons
        self.create_control_buttons(left_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)
        
        left_layout.addStretch()
        
        # Right panel
        right_panel = self.create_display_panel()
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
    
    def create_parameter_groups(self, layout):
        """Create parameter input groups"""
        
        # Complex plane parameters
        self.complex_group = QGroupBox("Complex Plane Parameters")
        complex_layout = QGridLayout(self.complex_group)
        
        complex_layout.addWidget(QLabel("X Min:"), 0, 0)
        self.x_min = QDoubleSpinBox()
        self.x_min.setRange(-10.0, 10.0)
        self.x_min.setValue(-2.0)
        self.x_min.setDecimals(3)
        self.x_min.setSingleStep(0.1)
        complex_layout.addWidget(self.x_min, 0, 1)
        
        complex_layout.addWidget(QLabel("X Max:"), 0, 2)
        self.x_max = QDoubleSpinBox()
        self.x_max.setRange(-10.0, 10.0)
        self.x_max.setValue(2.0)
        self.x_max.setDecimals(3)
        self.x_max.setSingleStep(0.1)
        complex_layout.addWidget(self.x_max, 0, 3)
        
        complex_layout.addWidget(QLabel("Y Min:"), 1, 0)
        self.y_min = QDoubleSpinBox()
        self.y_min.setRange(-10.0, 10.0)
        self.y_min.setValue(-2.0)
        self.y_min.setDecimals(3)
        self.y_min.setSingleStep(0.1)
        complex_layout.addWidget(self.y_min, 1, 1)
        
        complex_layout.addWidget(QLabel("Y Max:"), 1, 2)
        self.y_max = QDoubleSpinBox()
        self.y_max.setRange(-10.0, 10.0)
        self.y_max.setValue(2.0)
        self.y_max.setDecimals(3)
        self.y_max.setSingleStep(0.1)
        complex_layout.addWidget(self.y_max, 1, 3)
        
        complex_layout.addWidget(QLabel("Max Iterations:"), 2, 0)
        self.max_iterations = QSpinBox()
        self.max_iterations.setRange(10, 1000)
        self.max_iterations.setValue(100)
        complex_layout.addWidget(self.max_iterations, 2, 1, 1, 3)
        
        # Julia set parameters
        self.julia_group = QGroupBox("Julia Set Constants")
        julia_layout = QGridLayout(self.julia_group)
        
        julia_layout.addWidget(QLabel("C Real:"), 0, 0)
        self.c_real = QDoubleSpinBox()
        self.c_real.setRange(-2.0, 2.0)
        self.c_real.setValue(-0.7)
        self.c_real.setDecimals(5)
        self.c_real.setSingleStep(0.001)
        julia_layout.addWidget(self.c_real, 0, 1)
        
        julia_layout.addWidget(QLabel("C Imaginary:"), 0, 2)
        self.c_imag = QDoubleSpinBox()
        self.c_imag.setRange(-2.0, 2.0)
        self.c_imag.setValue(0.27015)
        self.c_imag.setDecimals(5)
        self.c_imag.setSingleStep(0.001)
        julia_layout.addWidget(self.c_imag, 0, 3)

        # Geometric parameters (for Koch snowflake)
        self.geometric_group = QGroupBox("Geometric Parameters")
        geometric_layout = QGridLayout(self.geometric_group)

        geometric_layout.addWidget(QLabel("Depth:"), 0, 0)
        self.depth = QSpinBox()
        self.depth.setRange(1, 8)
        self.depth.setValue(5)
        geometric_layout.addWidget(self.depth, 0, 1)

        geometric_layout.addWidget(QLabel("Size:"), 0, 2)
        self.size = QDoubleSpinBox()
        self.size.setRange(50.0, 500.0)
        self.size.setValue(250.0)
        self.size.setDecimals(1)
        geometric_layout.addWidget(self.size, 0, 3)

        geometric_layout.addWidget(QLabel("Line Width:"), 1, 0)
        self.line_width = QSpinBox()
        self.line_width.setRange(1, 5)
        self.line_width.setValue(1)
        geometric_layout.addWidget(self.line_width, 1, 1, 1, 3)

        # Special parameters (for Sierpinski and other special fractals)
        self.special_group = QGroupBox("Special Parameters")
        special_layout = QGridLayout(self.special_group)

        # Method selection for Sierpinski
        special_layout.addWidget(QLabel("Method:"), 0, 0)
        self.sierpinski_method = QComboBox()
        self.sierpinski_method.addItems(["recursive", "chaos_game"])
        special_layout.addWidget(self.sierpinski_method, 0, 1)

        # Number of points for chaos game
        special_layout.addWidget(QLabel("Points:"), 0, 2)
        self.num_points = QSpinBox()
        self.num_points.setRange(1000, 100000)
        self.num_points.setValue(50000)
        special_layout.addWidget(self.num_points, 0, 3)
        
        # Display settings
        self.display_group = QGroupBox("Display Settings")
        display_layout = QGridLayout(self.display_group)
        
        display_layout.addWidget(QLabel("Width:"), 0, 0)
        self.width = QSpinBox()
        self.width.setRange(100, 2000)
        self.width.setValue(600)
        display_layout.addWidget(self.width, 0, 1)
        
        display_layout.addWidget(QLabel("Height:"), 0, 2)
        self.height = QSpinBox()
        self.height.setRange(100, 2000)
        self.height.setValue(400)
        display_layout.addWidget(self.height, 0, 3)
        
        display_layout.addWidget(QLabel("Color Scheme:"), 1, 0)
        self.color_scheme = QComboBox()
        self.color_scheme.addItems(["Classic", "Hot", "Cool", "Viridis", "Plasma", "Rainbow", "Grayscale"])
        display_layout.addWidget(self.color_scheme, 1, 1, 1, 3)
        
        # Add groups to layout
        layout.addWidget(self.complex_group)
        layout.addWidget(self.julia_group)
        layout.addWidget(self.geometric_group)
        layout.addWidget(self.special_group)
        layout.addWidget(self.display_group)
        
        # Initially hide parameter groups
        self.hide_all_parameter_groups()
    
    def create_control_buttons(self, layout):
        """Create control buttons"""
        self.generate_button = QPushButton("Generate Fractal")
        self.generate_button.setEnabled(False)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #2d7d2d;
                font-weight: bold;
                min-height: 35px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3d8d3d;
            }
            QPushButton:disabled {
                background-color: #333333;
            }
        """)
        layout.addWidget(self.generate_button)
        
        # Secondary buttons
        button_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset")
        self.save_button = QPushButton("Save")
        self.save_button.setEnabled(False)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)
    
    def create_display_panel(self):
        """Create display panel"""
        display_group = QGroupBox("Fractal Display")
        display_layout = QVBoxLayout(display_group)
        
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setStyleSheet("""
            QGraphicsView {
                border: 2px solid #555555;
                border-radius: 5px;
                background-color: #1a1a1a;
            }
        """)
        
        self.graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        
        # Status
        self.status_label = QLabel("Select fractal type and click Generate")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #aaaaaa; padding: 5px;")
        
        display_layout.addWidget(self.graphics_view)
        display_layout.addWidget(self.status_label)
        
        return display_group
    
    def hide_all_parameter_groups(self):
        """Hide all parameter groups"""
        self.complex_group.setVisible(False)
        self.julia_group.setVisible(False)
        self.geometric_group.setVisible(False)
        self.special_group.setVisible(False)
        self.display_group.setVisible(True)  # Always show display
    
    def show_parameters_for_fractal(self, fractal_type):
        """Show relevant parameters"""
        self.hide_all_parameter_groups()
        
        if fractal_type in ["Mandelbrot Set", "Julia Set"]:
            self.complex_group.setVisible(True)
            if fractal_type == "Julia Set":
                self.julia_group.setVisible(True)
        elif fractal_type in ["Koch Snowflake", "Sierpinski Triangle"]:
            self.geometric_group.setVisible(True)
            if fractal_type == "Sierpinski Triangle":
                self.special_group.setVisible(True)
    
        self.display_group.setVisible(True)
    
    def connect_signals(self):
        """Connect signals"""
        self.fractal_combo.currentTextChanged.connect(self.on_fractal_changed)
        self.generate_button.clicked.connect(self.on_generate_clicked)
        self.reset_button.clicked.connect(self.on_reset_clicked)
        self.save_button.clicked.connect(self.on_save_clicked)
    
    def on_fractal_changed(self, fractal_type):
        """Handle fractal type change"""
        if fractal_type != "Select Fractal Type...":
            self.generate_button.setEnabled(True)
            self.show_parameters_for_fractal(fractal_type)
        else:
            self.generate_button.setEnabled(False)
            self.hide_all_parameter_groups()
    
    def on_generate_clicked(self):
        """Handle generate button click"""
        if self.generation_thread and self.generation_thread.isRunning():
            return
        
        fractal_type = self.fractal_combo.currentText()
        params = self.get_current_parameters()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.generate_button.setEnabled(False)
        self.status_label.setText(f"Generating {fractal_type}...")
        
        self.generation_thread = FractalGenerationThread(fractal_type, params)
        self.generation_thread.progress_update.connect(self.progress_bar.setValue)
        self.generation_thread.generation_complete.connect(self.on_generation_complete)
        self.generation_thread.error_occurred.connect(self.on_generation_error)
        self.generation_thread.start()
    
    def get_current_parameters(self):
        """Get current parameters from UI"""
        params = {
            'width': self.width.value(),
            'height': self.height.value(),
            'color_scheme': self.color_scheme.currentText()
        }
        
        fractal_type = self.fractal_combo.currentText()
        
        if fractal_type in ["Mandelbrot Set", "Julia Set"]:
            params.update({
                'x_min': self.x_min.value(),
                'x_max': self.x_max.value(),
                'y_min': self.y_min.value(),
                'y_max': self.y_max.value(),
                'max_iterations': self.max_iterations.value()
            })
            
            if fractal_type == "Julia Set":
                params.update({
                    'c_real': self.c_real.value(),
                    'c_imag': self.c_imag.value()
                })
        elif fractal_type in ["Koch Snowflake", "Sierpinski"]:
            params.update({
                'depth': self.depth.value(),
                'size': self.size.value(),
                'line_width': self.line_width.value()
            })
            
            if fractal_type == "Sierpinski":
                params.update({
                    'method': self.sierpinski_method.currentText(),
                    'num_points': self.num_points.value()
                })
                
                return params
    
    @pyqtSlot(np.ndarray, np.ndarray)
    def on_generation_complete(self, colored_image, raw_data):
        """Handle generation complete"""
        self.current_image = colored_image
        self.current_raw_data = raw_data
        
        # Convert to QPixmap
        height, width, channel = colored_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(colored_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        # Display
        self.graphics_scene.clear()
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.graphics_scene.addItem(pixmap_item)
        self.graphics_view.fitInView(pixmap_item, Qt.KeepAspectRatio)
        
        # Update UI
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        self.save_button.setEnabled(True)
        
        generation_time = getattr(self.generation_thread, 'generation_time', 0)
        self.status_label.setText(f"Generated {width}x{height} fractal in {generation_time:.2f}s")
    
    @pyqtSlot(str)
    def on_generation_error(self, error_message):
        """Handle generation error"""
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        self.status_label.setText("Generation failed!")
        QMessageBox.critical(self, "Generation Error", f"Error:\n{error_message}")
    
    def on_reset_clicked(self):
        """Reset parameters"""
        self.x_min.setValue(-2.0)
        self.x_max.setValue(2.0)
        self.y_min.setValue(-2.0)
        self.y_max.setValue(2.0)
        self.max_iterations.setValue(100)
        self.c_real.setValue(-0.7)
        self.c_imag.setValue(0.27015)
        self.width.setValue(600)
        self.height.setValue(400)
        self.color_scheme.setCurrentIndex(0)

        self.sierpinski_method.setCurrentIndex(0)  # recursive
        self.num_points.setValue(50000)
    
    def on_save_clicked(self):
        """Save fractal image"""
        if self.current_image is None:
            QMessageBox.information(self, "No Image", "Please generate a fractal first.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Fractal", "", "PNG Files (*.png);;JPG Files (*.jpg)"
        )
        
        if filename:
            try:
                img = Image.fromarray(self.current_image)
                img.save(filename)
                QMessageBox.information(self, "Success", f"Saved to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Error: {str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Dark theme
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(43, 43, 43))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(74, 74, 74))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = FractalGeneratorUI()
    window.show()
    
    print("✓ Fractal Generator started successfully!")
    print("Select a fractal type and click Generate to test.")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()