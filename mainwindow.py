# mainwindow.py
from canvas import Canvas
from utils import save_segmentation_nifti
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox, QFileDialog, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QScrollBar, QSizePolicy, QVBoxLayout,
    QWidget
)
import numpy as np
import nibabel as nib

class MainWindow(QMainWindow):
    def __init__(self, nifti_file_path=None):
        super().__init__()

        self.setWindowTitle("NIfTI Segmentation")
        self.setMinimumSize(620, 620) 
        self.resize(620, 620)  # Initial size for main window

        # Initialize the Canvas
        self.canvas = Canvas()
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setMinimumSize(540, 540)  # Initial size for the canvas
        if nifti_file_path:
            self.canvas.set_background_image_from_nifti(nifti_file_path)
        self.canvas.slice_changed.connect(self.update_scroll_bar)  # Connect canvas signal to the slot

        # Dropdown: Brush size
        brush_size_label = QLabel("Brush Size:")
        brush_size_dropdown = QComboBox()
        brush_sizes = ['1 px', '2 px', '4 px', '8 px', '16 px', '32 px']
        brush_size_dropdown.addItems(brush_sizes)
        brush_size_dropdown.setCurrentIndex(3)  # Default : '8 px'
        brush_size_dropdown.currentIndexChanged.connect(self.change_brush_size)

        # Dropdown: Brush color
        brush_color_label = QLabel("Brush Color:")
        brush_color_dropdown = QComboBox()
        brush_colors = ['Clear', 'Red', 'Green', 'Blue', 'Yellow', 'Sky Blue', 'Purple']
        brush_color_dropdown.addItems(brush_colors)
        brush_color_dropdown.setCurrentIndex(1)  # Default : 'Red'
        brush_color_dropdown.currentIndexChanged.connect(self.change_brush_color)

        # Button: Clear all
        clear_all_button = QPushButton("Clear All")
        clear_all_button.clicked.connect(self.clear_all_segmentations)

        # Button: Load NIfTI File
        load_nifti_button = QPushButton("Load NIfTI File")
        load_nifti_button.clicked.connect(self.load_nifti_file)

        # Button: Save Segmentation
        save_button = QPushButton("Save Segmentation")
        save_button.clicked.connect(self.save_nifti)

        # Button: Load segmentation button
        load_segmentation_button = QPushButton("Load Segmentation")
        load_segmentation_button.clicked.connect(self.load_segmentation)

        # Scroll bar for navigating slices
        self.scroll_bar = QScrollBar(Qt.Vertical)
        self.scroll_bar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.scroll_bar.setMinimumWidth(20)
        self.scroll_bar.valueChanged.connect(self.scroll_to_slice)
        self.scroll_bar.setMinimum(0)
        if self.canvas.nifti_data is not None:
            self.scroll_bar.setMaximum(self.canvas.nifti_data.shape[2] - 1)
            self.scroll_bar.setValue(self.canvas.current_slice_index)  # Initial scrollbar value to current slice

        # Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(brush_size_label)
        button_layout.addWidget(brush_size_dropdown)
        button_layout.addWidget(brush_color_label)
        button_layout.addWidget(brush_color_dropdown)
        button_layout.addWidget(clear_all_button)
        button_layout.addWidget(load_nifti_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(load_segmentation_button)

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


    def resizeEvent(self, event):
        """
        Handle resize events.
        """
        self.canvas.resize(self.size().width() - 80, self.size().height() - 80)  # Resize canvas dynamically
        self.scroll_bar.setFixedHeight(self.canvas.height())  # Set scrollbar height to canvas height
        super().resizeEvent(event)

    def change_brush_size(self, index):
        """
        Change the brush size.
        :param index: Selected item index in the dropdown.
        """
        brush_sizes = [1, 2, 4, 8, 16, 32]
        brush_size = brush_sizes[index]
        self.canvas.set_brush_size(brush_size)

    def change_brush_color(self, index):
        """
        Change the brush color.
        :param index: Selected item index in the dropdown.
        """
        brush_color_values = [0, 1, 2, 3, 4, 5, 6]  # 0 is 'Clear'
        brush_color_value = brush_color_values[index]
        self.canvas.set_brush_color_value(brush_color_value)

    def clear_all_segmentations(self):
        """
        Clear all segmentations and reset the segmentation matrix.
        """
        self.canvas.clear_all_segmentations()

    def scroll_to_slice(self, value):
        """
        Scroll to a different slice.
        :param value: New value index from the scroll bar.
        """
        if self.canvas.nifti_data is not None:
            max_index = self.canvas.nifti_data.shape[2] - 1
            new_index = max_index - value
            self.canvas.current_slice_index = min(max(0, new_index), max_index)
            self.canvas.update_slice()

    def update_scroll_bar(self, new_index):
        """
        Update the scroll bar.
        :param new_index: Current index of the slice to display.
        """
        max_index = self.canvas.nifti_data.shape[2] - 1
        self.scroll_bar.setValue(max_index - new_index)

    def save_nifti(self):
        """
        Save the segmentation as a NIfTI file.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
                            self,
                            "Save NIfTI Format",
                            "",
                            "NIfTI Files (*.nii.gz)",
                            options=options
        )
        if file_path:
            save_segmentation_nifti(
                self.canvas.segmentation_matrix,
                self.canvas.nifti_affine,
                self.canvas.nifti_header,
                file_path
            )

    def load_nifti_file(self):
        """
        Load a new NIfTI file and update the canvas.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
                            self,
                            "Load NIfTI File",
                            "",
                            "NIfTI Files (*.nii *.nii.gz)",
                            options=options
        )
        if file_path:
            self.canvas.set_background_image_from_nifti(file_path)
            self.scroll_bar.setMaximum(self.canvas.nifti_data.shape[2] - 1)
            self.canvas.current_slice_index = min(self.canvas.current_slice_index, self.canvas.nifti_data.shape[2] - 1)
            self.scroll_bar.setValue(self.canvas.current_slice_index)  # Sync scrollbar value with current slice

    def load_segmentation(self):
        """
        Load a segmentation NIfTI file.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
                            self,
                            "Load Segmentation File",
                            "",
                            "NIfTI Files (*.nii *.nii.gz)",
                            options=options
        )
        if file_path:
            nifti_img = nib.load(file_path)
            segmentation_data = nifti_img.get_fdata()
            if segmentation_data.shape == self.canvas.segmentation_matrix.shape:   # Check dimensions.
                self.canvas.segmentation_matrix = segmentation_data.astype(np.int32)
                self.canvas.update_slice()
            else:
                print("Error: The dimensions of the segmentation file do not match the current NIfTI Image.")
