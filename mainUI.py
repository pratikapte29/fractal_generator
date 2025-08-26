import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QGroupBox, QLabel, 
                             QComboBox, QSpinBox, QDoubleSpinBox, QPushButton,
                             QSlider, QColorDialog, QProgressBar, QGraphicsView,
                             QGraphicsScene, QFrame, QSizePolicy, QFileDialog,
                             QMessageBox, QGraphicsPixmapItem)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap
import numpy as np
from PIL import Image
import time

# Import the fractal generator
from fractal_generator import FractalGenerator

class FractalGenerationThread(QThread):
    """Thread for generating fractals without blocking the UI"""
    
    progress_update = pyqtSignal(int)
    generation_complete = pyqtSignal(np.ndarray, np.ndarray)  # colored_image, raw_data
    error_occurred = pyqtSignal(str)
    
    def __init__(self, fractal_type, params):
        super().__init__()
        self.fractal_type = fractal_type
        self.params = params
        self.generator = FractalGenerator()
    
    def run(self):
        try:
            self.progress_update.emit(10)
            
            # Generate fractal
            colored_image, raw_data = self.generator.create_fractal_image(
                self.fractal_type, **self.params
            )
            
            self.progress_update.emit(100)
            self.generation_complete.emit(colored_image, raw_data)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class FractalGeneratorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Fractal Generator")
        self.setGeometry(100, 100, 1400, 900)
        
        # Current fractal data
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
            QPushButton:pressed {
                background-color: #3a3a3a;
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
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel for controls
        left_panel = QWidget()
        left_panel.setFixedWidth(420)
        left_layout = QVBoxLayout(left_panel)
        
        # Title
        title_label = QLabel("Advanced Fractal Generator")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #ffffff; margin: 10px;")
        left_layout.addWidget(title_label)
        
        # Fractal selection
        self.create_fractal_selection(left_layout)
        
        # Parameter inputs
        self.create_parameter_groups(left_layout)
        
        # Control buttons
        self.create_control_buttons(left_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2d7d2d;
                border-radius: 3px;
            }
        """)
        left_layout.addWidget(self.progress_bar)
        
        left_layout.addStretch()
        
        # Right panel for fractal display
        right_panel = self.create_display_panel()
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
    def create_fractal_selection(self, layout):
        """Create fractal type selection dropdown"""
        selection_group = QGroupBox("Fractal Type")
        selection_layout = QVBoxLayout(selection_group)
        
        self.fractal_combo = QComboBox()
        self.fractal_combo.addItems([
            "Select Fractal Type...",
            "Mandelbrot Set",
            "Julia Set",
            "Koch Snowflake",
            "Sierpinski Triangle",
            "Dragon Curve",
            "Barnsley Fern",
            "Newton Fractal",
            "Burning Ship"
        ])
        selection_layout.addWidget(self.fractal_combo)
        
        layout.addWidget(selection_group)
        
    def create_parameter_groups(self, layout):
        """Create parameter input groups for different fractals"""
        
        # Complex Fractals (Mandelbrot, Julia, Newton, etc.)
        self.complex_group = QGroupBox("Complex Plane Parameters")
        complex_layout = QGridLayout(self.complex_group)
        
        # Bounds
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
        
        # Iterations and escape radius
        complex_layout.addWidget(QLabel("Max Iterations:"), 2, 0)
        self.max_iterations = QSpinBox()
        self.max_iterations.setRange(10, 10000)
        self.max_iterations.setValue(100)
        complex_layout.addWidget(self.max_iterations, 2, 1)
        
        complex_layout.addWidget(QLabel("Escape Radius:"), 2, 2)
        self.escape_radius = QDoubleSpinBox()
        self.escape_radius.setRange(1.0, 100.0)
        self.escape_radius.setValue(2.0)
        self.escape_radius.setDecimals(1)
        complex_layout.addWidget(self.escape_radius, 2, 3)
        
        # Julia Set specific parameters
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
        
        # Add preset button for Julia sets
        self.julia_preset_button = QPushButton("Load Preset")
        julia_layout.addWidget(self.julia_preset_button, 1, 0, 1, 2)
        
        self.julia_preset_combo = QComboBox()
        self.julia_preset_combo.addItems([
            "Dragon", "Rabbit", "Lightning", "Spiral", "Seahorse"
        ])
        julia_layout.addWidget(self.julia_preset_combo, 1, 2, 1, 2)
        
        # Newton fractal specific parameters
        self.newton_group = QGroupBox("Newton Fractal Options")
        newton_layout = QGridLayout(self.newton_group)
        
        newton_layout.addWidget(QLabel("Polynomial:"), 0, 0)
        self.polynomial_combo = QComboBox()
        self.polynomial_combo.addItems(["cubic", "quartic", "sine"])
        newton_layout.addWidget(self.polynomial_combo, 0, 1)
        
        newton_layout.addWidget(QLabel("Tolerance:"), 0, 2)
        self.tolerance = QDoubleSpinBox()
        self.tolerance.setRange(1e-10, 1e-3)
        self.tolerance.setValue(1e-6)
        self.tolerance.setDecimals(10)
        self.tolerance.setSingleStep(1e-7)
        newton_layout.addWidget(self.tolerance, 0, 3)
        
        # Geometric Fractals (Koch, Sierpinski, Dragon, etc.)
        self.geometric_group = QGroupBox("Geometric Parameters")
        geometric_layout = QGridLayout(self.geometric_group)
        
        geometric_layout.addWidget(QLabel("Iterations/Depth:"), 0, 0)
        self.depth = QSpinBox()
        self.depth.setRange(1, 15)
        self.depth.setValue(5)
        geometric_layout.addWidget(self.depth, 0, 1)
        
        geometric_layout.addWidget(QLabel("Size/Length:"), 0, 2)
        self.size = QDoubleSpinBox()
        self.size.setRange(10.0, 1000.0)
        self.size.setValue(300.0)
        self.size.setDecimals(1)
        geometric_layout.addWidget(self.size, 0, 3)
        
        geometric_layout.addWidget(QLabel("Start X:"), 1, 0)
        self.start_x = QDoubleSpinBox()
        self.start_x.setRange(-1000.0, 1000.0)
        self.start_x.setValue(0.0)
        self.start_x.setDecimals(1)
        geometric_layout.addWidget(self.start_x, 1, 1)
        
        geometric_layout.addWidget(QLabel("Start Y:"), 1, 2)
        self.start_y = QDoubleSpinBox()
        self.start_y.setRange(-1000.0, 1000.0)
        self.start_y.setValue(0.0)
        self.start_y.setDecimals(1)
        geometric_layout.addWidget(self.start_y, 1, 3)
        
        geometric_layout.addWidget(QLabel("Angle:"), 2, 0)
        self.angle = QDoubleSpinBox()
        self.angle.setRange(0.0, 360.0)
        self.angle.setValue(0.0)
        self.angle.setDecimals(1)
        self.angle.setSuffix("°")
        geometric_layout.addWidget(self.angle, 2, 1)
        
        geometric_layout.addWidget(QLabel("Line Width:"), 2, 2)
        self.line_width = QSpinBox()
        self.line_width.setRange(1, 10)
        self.line_width.setValue(1)
        geometric_layout.addWidget(self.line_width, 2, 3)
        
        # Special parameters for specific fractals
        self.special_group = QGroupBox("Special Parameters")
        special_layout = QGridLayout(self.special_group)
        
        # For Sierpinski Triangle
        special_layout.addWidget(QLabel("Method:"), 0, 0)
        self.sierpinski_method = QComboBox()
        self.sierpinski_method.addItems(["recursive", "chaos_game"])
        special_layout.addWidget(self.sierpinski_method, 0, 1)
        
        # For Barnsley Fern and chaos methods
        special_layout.addWidget(QLabel("Num Points:"), 0, 2)
        self.num_points = QSpinBox()
        self.num_points.setRange(1000, 1000000)
        self.num_points.setValue(100000)
        special_layout.addWidget(self.num_points, 0, 3)
        
        # Display Settings
        self.display_group = QGroupBox("Display Settings")
        display_layout = QGridLayout(self.display_group)
        
        display_layout.addWidget(QLabel("Width:"), 0, 0)
        self.width = QSpinBox()
        self.width.setRange(100, 4000)
        self.width.setValue(800)
        display_layout.addWidget(self.width, 0, 1)
        
        display_layout.addWidget(QLabel("Height:"), 0, 2)
        self.height = QSpinBox()
        self.height.setRange(100, 4000)
        self.height.setValue(600)
        display_layout.addWidget(self.height, 0, 3)
        
        display_layout.addWidget(QLabel("Color Scheme:"), 1, 0)
        self.color_scheme = QComboBox()
        self.color_scheme.addItems([
            "Classic", "Hot", "Cool", "Viridis", "Plasma", "Rainbow", "Grayscale", "Custom"
        ])
        display_layout.addWidget(self.color_scheme, 1, 1, 1, 2)
        
        self.color_button = QPushButton("Custom Colors")
        display_layout.addWidget(self.color_button, 1, 3)
        
        # Add all groups to layout (initially hidden)
        layout.addWidget(self.complex_group)
        layout.addWidget(self.julia_group)
        layout.addWidget(self.newton_group)
        layout.addWidget(self.geometric_group)
        layout.addWidget(self.special_group)
        layout.addWidget(self.display_group)
        
        # Hide all parameter groups initially
        self.hide_all_parameter_groups()
        
    def create_control_buttons(self, layout):
        """Create control buttons"""
        button_layout = QVBoxLayout()
        
        # Main generate button
        self.generate_button = QPushButton("Generate Fractal")
        self.generate_button.setEnabled(False)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #2d7d2d;
                font-weight: bold;
                min-height: 40px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3d8d3d;
            }
            QPushButton:disabled {
                background-color: #333333;
            }
        """)
        button_layout.addWidget(self.generate_button)
        
        # Secondary buttons in a row
        secondary_buttons = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset")
        self.save_button = QPushButton("Save Image")
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_out_button = QPushButton("Zoom Out")
        
        self.save_button.setEnabled(False)
        self.zoom_in_button.setEnabled(False)
        self.zoom_out_button.setEnabled(False)
        
        secondary_buttons.addWidget(self.reset_button)
        secondary_buttons.addWidget(self.save_button)
        secondary_buttons.addWidget(self.zoom_in_button)
        secondary_buttons.addWidget(self.zoom_out_button)
        
        button_layout.addLayout(secondary_buttons)
        layout.addLayout(button_layout)
        
    def create_display_panel(self):
        """Create the fractal display area"""
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
        
        # Enable mouse interaction
        self.graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
        from PyQt5.QtGui import QPainter
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        
        # Status info
        status_layout = QHBoxLayout()
        
        self.zoom_label = QLabel("Zoom: 100%")
        self.coordinates_label = QLabel("Coordinates: (0, 0)")
        self.generation_time_label = QLabel("Generation Time: --")
        
        status_layout.addWidget(self.zoom_label)
        status_layout.addWidget(self.coordinates_label)
        status_layout.addWidget(self.generation_time_label)
        status_layout.addStretch()
        
        display_layout.addWidget(self.graphics_view)
        display_layout.addLayout(status_layout)
        
        return display_group
        
    def hide_all_parameter_groups(self):
        """Hide all parameter groups"""
        self.complex_group.setVisible(False)
        self.julia_group.setVisible(False)
        self.newton_group.setVisible(False)
        self.geometric_group.setVisible(False)
        self.special_group.setVisible(False)
        self.display_group.setVisible(False)
        
    def show_parameters_for_fractal(self, fractal_type):
        """Show relevant parameter groups based on fractal type"""
        self.hide_all_parameter_groups()
        
        # Always show display settings
        self.display_group.setVisible(True)
        
        complex_fractals = ["Mandelbrot Set", "Julia Set", "Newton Fractal", "Burning Ship"]
        geometric_fractals = ["Koch Snowflake", "Sierpinski Triangle", "Dragon Curve", "Barnsley Fern"]
        
        if fractal_type in complex_fractals:
            self.complex_group.setVisible(True)
            
            if fractal_type == "Julia Set":
                self.julia_group.setVisible(True)
            elif fractal_type == "Newton Fractal":
                self.newton_group.setVisible(True)
                
        elif fractal_type in geometric_fractals:
            self.geometric_group.setVisible(True)
            
            if fractal_type in ["Sierpinski Triangle", "Barnsley Fern"]:
                self.special_group.setVisible(True)
                
    def connect_signals(self):
        """Connect UI signals"""
        self.fractal_combo.currentTextChanged.connect(self.on_fractal_changed)
        self.generate_button.clicked.connect(self.on_generate_clicked)
        self.reset_button.clicked.connect(self.on_reset_clicked)
        self.save_button.clicked.connect(self.on_save_clicked)
        self.color_button.clicked.connect(self.on_color_clicked)
        self.julia_preset_button.clicked.connect(self.on_julia_preset_clicked)
        
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
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.generate_button.setEnabled(False)
        
        # Start generation in separate thread
        self.generation_thread = FractalGenerationThread(fractal_type, params)
        self.generation_thread.progress_update.connect(self.progress_bar.setValue)
        self.generation_thread.generation_complete.connect(self.on_generation_complete)
        self.generation_thread.error_occurred.connect(self.on_generation_error)
        self.generation_thread.start()
        
    def get_current_parameters(self):
        """Extract current parameter values from UI"""
        params = {
            'width': self.width.value(),
            'height': self.height.value(),
            'color_scheme': self.color_scheme.currentText()
        }
        
        # Add parameters based on fractal type
        fractal_type = self.fractal_combo.currentText()
        
        if fractal_type in ["Mandelbrot Set", "Julia Set", "Newton Fractal", "Burning Ship"]:
            params.update({
                'x_min': self.x_min.value(),
                'x_max': self.x_max.value(),
                'y_min': self.y_min.value(),
                'y_max': self.y_max.value(),
                'max_iterations': self.max_iterations.value(),
                'escape_radius': self.escape_radius.value()
            })
            
            if fractal_type == "Julia Set":
                params.update({
                    'c_real': self.c_real.value(),
                    'c_imag': self.c_imag.value()
                })
            elif fractal_type == "Newton Fractal":
                params.update({
                    'polynomial': self.polynomial_combo.currentText(),
                    'tolerance': self.tolerance.value()
                })
                
        elif fractal_type in ["Koch Snowflake", "Sierpinski Triangle", "Dragon Curve", "Barnsley Fern"]:
            params.update({
                'depth': self.depth.value(),
                'size': self.size.value(),
                'start_x': self.start_x.value(),
                'start_y': self.start_y.value(),
                'angle': self.angle.value(),
                'line_width': self.line_width.value()
            })
            
            if fractal_type == "Sierpinski Triangle":
                params['method'] = self.sierpinski_method.currentText()
                params['num_points'] = self.num_points.value()
            elif fractal_type == "Barnsley Fern":
                params['num_points'] = self.num_points.value()
        
        return params
        
    @pyqtSlot(np.ndarray, np.ndarray)
    def on_generation_complete(self, colored_image, raw_data):
        """Handle completed fractal generation"""
        self.current_image = colored_image
        self.current_raw_data = raw_data
        
        # Convert numpy array to QPixmap and display
        height, width, channel = colored_image.shape
        bytes_per_line = 3 * width
        
        # Create QImage from numpy array
        from PyQt5.QtGui import QImage
        q_image = QImage(colored_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # Convert to QPixmap
        q_pixmap = QPixmap.fromImage(q_image)
        
        # Clear scene and add new image
        self.graphics_scene.clear()
        pixmap_item = QGraphicsPixmapItem(q_pixmap)
        self.graphics_scene.addItem(pixmap_item)
        self.graphics_view.fitInView(pixmap_item, Qt.KeepAspectRatio)
        
        # Hide progress bar and enable buttons
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.zoom_in_button.setEnabled(True)
        self.zoom_out_button.setEnabled(True)
        
        # Update generation time
        if hasattr(self.generation_thread, 'generation_time'):
            self.generation_time_label.setText(f"Generation Time: {self.generation_thread.generation_time:.2f}s")
        
    @pyqtSlot(str)
    def on_generation_error(self, error_message):
        """Handle generation errors"""
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        
        QMessageBox.critical(self, "Generation Error", f"Error generating fractal:\n{error_message}")
        
    def on_reset_clicked(self):
        """Reset parameters to defaults"""
        # Reset complex parameters
        self.x_min.setValue(-2.0)
        self.x_max.setValue(2.0)
        self.y_min.setValue(-2.0)
        self.y_max.setValue(2.0)
        self.max_iterations.setValue(100)
        self.escape_radius.setValue(2.0)
        
        # Reset Julia parameters
        self.c_real.setValue(-0.7)
        self.c_imag.setValue(0.27015)
        
        # Reset geometric parameters
        self.depth.setValue(5)
        self.size.setValue(300.0)
        self.start_x.setValue(0.0)
        self.start_y.setValue(0.0)
        self.angle.setValue(0.0)
        self.line_width.setValue(1)
        
        # Reset display parameters
        self.width.setValue(800)
        self.height.setValue(600)
        self.color_scheme.setCurrentIndex(0)
        
    def on_save_clicked(self):
        """Handle save image button click"""
        if self.current_image is None:
            QMessageBox.information(self, "No Image", "Please generate a fractal first.")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Fractal Image", "", "PNG Files (*.png);;JPG Files (*.jpg);;All Files (*)"
        )
        
        if filename:
            try:
                img = Image.fromarray(self.current_image)
                img.save(filename)
                QMessageBox.information(self, "Success", f"Fractal saved as {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Error saving image:\n{str(e)}")
        
    def on_color_clicked(self):
        """Handle custom color selection"""
        color = QColorDialog.getColor()
        if color.isValid():
            print(f"Selected color: {color.name()}")
            
    def on_julia_preset_clicked(self):
        """Load Julia set preset constants"""
        preset_name = self.julia_preset_combo.currentText()
        
        # Import Julia generator to get presets
        try:
            from fractals.julia import JuliaGenerator
            julia_gen = JuliaGenerator()
            constants = julia_gen.get_interesting_constants()
            
            if preset_name in constants:
                real, imag = constants[preset_name]
                self.c_real.setValue(real)
                self.c_imag.setValue(imag)
        except ImportError:
            pass

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(43, 43, 43))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(74, 74, 74))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = FractalGeneratorUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()