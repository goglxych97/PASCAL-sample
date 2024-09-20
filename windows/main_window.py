# windows/main_window.py
from canvas.canvas import Canvas
from menu.file import load_nifti, load_segmentation, save_segmentation
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAction, QComboBox, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QScrollBar, QSizePolicy, QVBoxLayout,
    QWidget
)
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self, nifti_file_path=None):
        super().__init__()

        self.setWindowTitle("NIfTI Segmentation")
        self.setMinimumSize(620, 620)
        self.resize(620, 620)  # Mainwindow init-size
        self.canvas = Canvas()
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setMinimumSize(540, 540)  # Canvas init-size

        if nifti_file_path:
            self.canvas.set_background_image_from_nifti(nifti_file_path)
        self.canvas.slice_changed.connect(self.update_scroll_bar)

        # Menu bar
        self.menu_bar = self.menuBar()
        self.create_menu()

        # Dropdown: Brush size
        brush_size_label = QLabel("Brush Size:")
        brush_size_dropdown = QComboBox()
        brush_sizes = ['1px', '2px', '4px', '8px', '16px', '32px']
        brush_size_dropdown.addItems(brush_sizes)
        brush_size_dropdown.setCurrentIndex(3)  # Default: '8px'
        brush_size_dropdown.currentIndexChanged.connect(self.change_brush_size)

        # Dropdown: Brush color
        brush_color_label = QLabel("Brush Color:")
        brush_color_dropdown = QComboBox()
        brush_colors = ['Clear', 'Red', 'Green', 'Blue', 'Yellow', 'Sky Blue', 'Purple']
        brush_color_dropdown.addItems(brush_colors)
        brush_color_dropdown.setCurrentIndex(1)  # Default: 'Red'
        brush_color_dropdown.currentIndexChanged.connect(self.change_brush_color)

        # Button: Clear all
        clear_all_button = QPushButton("Clear All")
        clear_all_button.clicked.connect(self.clear_all_segmentations)

        # Scroll bar for navigating slices
        self.scroll_bar = QScrollBar(Qt.Vertical)
        self.scroll_bar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.scroll_bar.setMinimumWidth(20)
        self.scroll_bar.valueChanged.connect(self.scroll_to_slice)
        self.scroll_bar.setMinimum(0)
        if self.canvas.nifti_data is not None:
            self.scroll_bar.setMaximum(self.canvas.nifti_data.shape[2] - 1)
            self.scroll_bar.setValue(self.canvas.current_slice_index)  # Init scroll value to current slice

        # Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(brush_size_label)
        button_layout.addWidget(brush_size_dropdown)
        button_layout.addWidget(brush_color_label)
        button_layout.addWidget(brush_color_dropdown)
        button_layout.addWidget(clear_all_button)

        # Layout for Canvas and Scrollbar
        image_and_scroll_layout = QHBoxLayout()
        image_and_scroll_layout.addWidget(self.canvas)
        image_and_scroll_layout.addWidget(self.scroll_bar)

        # Layout for buttons over the image and scroll layout
        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addLayout(image_and_scroll_layout)

        # Set the central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def create_menu(self):
        file_menu = self.menu_bar.addMenu('File')

        load_nifti_action = QAction('Load NIfTI File', self)
        load_nifti_action.triggered.connect(self.load_nifti_file)
        file_menu.addAction(load_nifti_action)

        load_segmentation_action = QAction('Load Segmentation', self)
        load_segmentation_action.triggered.connect(self.load_segmentation)
        file_menu.addAction(load_segmentation_action)

        save_nifti_action = QAction('Save Segmentation', self)
        save_nifti_action.triggered.connect(self.save_nifti_file)
        file_menu.addAction(save_nifti_action)

    def resizeEvent(self, event):
        self.scroll_bar.setFixedHeight(self.canvas.height())  # Set scrollbar height to canvas height
        super().resizeEvent(event)

    def change_brush_size(self, index):
        brush_sizes = [1, 2, 4, 8, 16, 32]
        brush_size = brush_sizes[index]
        self.canvas.set_brush_size(brush_size)

    def change_brush_color(self, index):
        brush_color_values = [0, 1, 2, 3, 4, 5, 6]  # 0 is 'Clear'
        brush_color_value = brush_color_values[index]
        self.canvas.set_brush_color_value(brush_color_value)

    def clear_all_segmentations(self):
        self.canvas.clear_all_segmentations()

    def scroll_to_slice(self, value):
        if self.canvas.nifti_data is not None:
            max_index = self.canvas.nifti_data.shape[2] - 1
            new_index = max_index - value
            self.canvas.current_slice_index = min(max(0, new_index), max_index)
            self.canvas.update_slice()

    def update_scroll_bar(self, new_index):
        max_index = self.canvas.nifti_data.shape[2] - 1
        self.scroll_bar.setValue(max_index - new_index)

    def save_nifti_file(self):
        save_segmentation(self, self.canvas.segmentation_matrix, self.canvas.nifti_affine, self.canvas.nifti_header)

    def load_nifti_file(self):
        file_path = load_nifti(self)
        if file_path:
            self.canvas.set_background_image_from_nifti(file_path)
            self.scroll_bar.setMaximum(self.canvas.nifti_data.shape[2] - 1)
            self.canvas.current_slice_index = min(self.canvas.current_slice_index, self.canvas.nifti_data.shape[2] - 1)
            self.scroll_bar.setValue(self.canvas.current_slice_index)  # Sync scrollbar value

    def load_segmentation(self):
        """
        Load a segmentation NIfTI file.
        """
        segmentation_data = load_segmentation(self)
        if segmentation_data is not None:
            if segmentation_data.shape == self.canvas.segmentation_matrix.shape:  # Check dimensions.
                self.canvas.segmentation_matrix = segmentation_data.astype(np.int32)
                self.canvas.update_slice()
            else:
                print("Error: The dimensions of the segmentation file do not match the current NIfTI Image.")
