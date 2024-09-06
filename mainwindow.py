from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QScrollBar, QHBoxLayout, QSpacerItem, QSizePolicy, QComboBox, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from canvas import Canvas
from utils import save_annotation_nifti
import numpy as np
import nibabel as nib  # Import nibabel for NIfTI handling

class MainWindow(QMainWindow):
    def __init__(self, nifti_file_path=None, shape=(540, 540)):
        super().__init__()

        width = shape[0]
        height = shape[1]

        # Initialize the Canvas
        self.canvas = Canvas(width, height)
        self.canvas.set_brush_size(8)  # Set initial brush size to 8
        if nifti_file_path:
            self.canvas.set_background_image_from_nifti(nifti_file_path)

        # Connect the canvas signal to the slot that updates the scroll bar
        self.canvas.slice_changed.connect(self.update_scroll_bar)

        # Initialize Buttons
        load_nifti_button = QPushButton("Load NIfTI Files")
        download_button = QPushButton("Download Segmentation")
        load_segmentation_button = QPushButton("Load Segmentation")

        # Set buttons fixed sizes
        button_width = 150  # Fixed width
        button_height = 40  # Fixed height
        load_nifti_button.setFixedSize(button_width, button_height)
        download_button.setFixedSize(button_width, button_height)
        load_segmentation_button.setFixedSize(button_width, button_height)

        # Font for labels
        label_font = QFont()
        label_font.setPointSize(8)  # Smaller font size

        # Brush Size label
        brush_size_label = QLabel("Brush Size:")
        brush_size_label.setFont(label_font)
        brush_size_label.setAlignment(Qt.AlignLeft)

        # Brush size dropdown menu
        brush_size_dropdown = QComboBox()
        brush_sizes = ['1 px', '2 px', '4 px', '8 px', '16 px', '32 px']
        brush_size_dropdown.addItems(brush_sizes)
        brush_size_dropdown.setFixedSize(button_width, button_height)
        brush_size_dropdown.setCurrentIndex(3)  # Set the default selection to "8 px"
        brush_size_dropdown.currentIndexChanged.connect(self.change_brush_size)

        # Brush Color label
        brush_color_label = QLabel("Brush Color:")
        brush_color_label.setFont(label_font)
        brush_color_label.setAlignment(Qt.AlignLeft)

        # Brush color dropdown menu
        brush_color_dropdown = QComboBox()
        brush_colors = ['Clear', 'Red', 'Green', 'Blue', 'Yellow', 'Sky Blue', 'Purple']
        brush_color_dropdown.addItems(brush_colors)
        brush_color_dropdown.setFixedSize(button_width, button_height)
        brush_color_dropdown.currentIndexChanged.connect(self.change_brush_color)

        # Empty label to align "Clear All" button
        empty_label = QLabel()
        empty_label.setFixedSize(button_width, 20)  # Make sure the empty label aligns well with the ComboBox

        # Clear All Button
        clear_all_button = QPushButton("Clear All")
        clear_all_button.setFixedSize(button_width, button_height)
        clear_all_button.clicked.connect(self.clear_all_annotations)  # Clear all annotations when clicked

        # Slice Selector ComboBox
        self.slice_selector = QComboBox()
        self.slice_selector.setFixedSize(100, 25)  # Small size for right corner placement
        self.slice_selector.addItems([str(i) for i in range(self.canvas.nifti_data.shape[2])])  # Add slice numbers
        self.slice_selector.currentIndexChanged.connect(self.change_slice)  # Connect to change slice function
        self.update_slice_selector()  # Initialize the slice selector coloring

        # Connect buttons to respective functions
        load_nifti_button.clicked.connect(self.load_nifti_file)
        download_button.clicked.connect(self.download_nifti)
        load_segmentation_button.clicked.connect(self.load_segmentation)

        # Initialize the Scroll Bar
        self.scroll_bar = QScrollBar(Qt.Vertical)
        self.scroll_bar.setMaximum(self.canvas.nifti_data.shape[2] - 1)  # Max value = number of slices - 1
        self.scroll_bar.setValue(self.canvas.current_slice_index)
        self.scroll_bar.valueChanged.connect(self.scroll_to_slice)  # Connect to slice scrolling function

        # Layout Setup for Buttons and Brush Size
        button_layout = QHBoxLayout()
        button_layout.addWidget(load_nifti_button)
        button_layout.addWidget(download_button)
        button_layout.addWidget(load_segmentation_button)

        # Create vertical layout for brush size label and dropdown
        brush_size_layout = QVBoxLayout()
        brush_size_layout.addWidget(brush_size_label)  # Add Brush Size label
        brush_size_layout.addWidget(brush_size_dropdown)  # Add the brush size dropdown menu

        # Create vertical layout for brush color label and dropdown
        brush_color_layout = QVBoxLayout()
        brush_color_layout.addWidget(brush_color_label)  # Add Brush Color label
        brush_color_layout.addWidget(brush_color_dropdown)  # Add the brush color dropdown menu

        # Create a vertical layout for Clear All button
        clear_all_layout = QVBoxLayout()
        clear_all_layout.addWidget(empty_label)  # Add empty label for alignment
        clear_all_layout.addWidget(clear_all_button)  # Add the Clear All button

        # Create a horizontal layout for the dropdowns and Clear All button
        dropdown_layout = QHBoxLayout()
        dropdown_layout.addLayout(brush_size_layout)  # Add brush size layout
        dropdown_layout.addLayout(brush_color_layout)  # Add brush color layout
        dropdown_layout.addLayout(clear_all_layout)  # Add the Clear All layout

        # Create a vertical layout for the canvas and control elements
        layout = QVBoxLayout()

        # Add slice selector combo box to the layout
        top_right_layout = QHBoxLayout()
        top_right_layout.addWidget(self.slice_selector, alignment=Qt.AlignRight)  # Align to the right top corner

        # Combine top right layout with main canvas layout
        layout.addLayout(top_right_layout)

        # Add spacers to center the canvas vertically
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Spacer above
        layout.addWidget(self.canvas, alignment=Qt.AlignCenter)  # Center the canvas
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Spacer below
        
        # Add dropdown layout and button layout at the bottom
        layout.addLayout(dropdown_layout)
        layout.addLayout(button_layout)

        # Combine Canvas, Scroll Bar, and Main Layout Horizontally
        container_layout = QHBoxLayout()
        container_layout.addLayout(layout)
        container_layout.addWidget(self.scroll_bar)

        # Set the Main Window Layout
        container = QWidget()
        container.setLayout(container_layout)
        self.setCentralWidget(container)

        self.setWindowTitle("NIfTI Segmentation")
        self.setFixedSize(width + 50, height + 200)

    def change_brush_size(self, index):
        """
        Change the brush size based on the dropdown selection.
        :param index: Index of the selected item in the dropdown.
        """
        brush_sizes = [1, 2, 4, 8, 16, 32]  # Corresponding brush sizes
        brush_size = brush_sizes[index]
        self.canvas.set_brush_size(brush_size)

    def change_brush_color(self, index):
        """
        Change the brush color based on the dropdown selection.
        :param index: Index of the selected item in the dropdown.
        """
        brush_color_values = [0, 1, 2, 3, 4, 5, 6]  # 0은 Clear에 해당
        brush_color_value = brush_color_values[index]
        print(f"Brush color changed to value: {brush_color_value}")  # 디버그용 출력
        self.canvas.set_brush_color_value(brush_color_value)

    def clear_all_annotations(self):
        """
        Clear all annotations and reset the annotation matrix.
        """
        self.canvas.clear_all_annotations()
        self.update_slice_selector()  # Update combo box coloring after clearing

    def scroll_to_slice(self, value):
        max_index = self.canvas.nifti_data.shape[2] - 1 if self.canvas.nifti_data is not None else 0
        self.canvas.current_slice_index = min(max(0, value), max_index)
        self.canvas.update_slice()
        self.update_slice_selector()  # Update combo box coloring

    def update_scroll_bar(self, new_index):
        self.scroll_bar.setValue(new_index)

    def change_slice(self, index):
        """
        Change the slice based on the combobox selection.
        :param index: Index of the selected slice.
        """
        self.canvas.current_slice_index = index
        self.canvas.update_slice()
        self.update_slice_selector()  # Update combo box coloring

    def update_slice_selector(self):
        """
        Update the slice selector combo box colors based on the presence of segmentation in each slice.
        """
        for i in range(self.canvas.nifti_data.shape[2]):
            if np.any(self.canvas.annotation_matrix[:, :, i] != 0):  # Check if there is any annotation in the slice
                self.slice_selector.setItemData(i, QColor('red'), Qt.ForegroundRole)  # Set text color to red
            else:
                self.slice_selector.setItemData(i, QColor('black'), Qt.ForegroundRole)  # Set text color to black

    def download_nifti(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save NIfTI Format", "", "NIfTI Files (*.nii.gz)", options=options)
        if file_path:
            save_annotation_nifti(
                self.canvas.annotation_matrix,
                self.canvas.nifti_affine,
                self.canvas.nifti_header,
                file_path
            )

    def load_nifti_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load NIfTI File", "", "NIfTI Files (*.nii *.nii.gz)", options=options)
        if file_path:
            self.canvas.set_background_image_from_nifti(file_path)
            
            # Update scroll bar
            self.scroll_bar.setMaximum(self.canvas.nifti_data.shape[2] - 1)
            self.canvas.current_slice_index = min(self.canvas.current_slice_index, self.canvas.nifti_data.shape[2] - 1)
            self.scroll_bar.setValue(self.canvas.current_slice_index)

            # Adjust the window size
            new_width = max(self.canvas.nifti_data.shape[1], 540)
            new_height = max(self.canvas.nifti_data.shape[0], 540)
            self.setFixedSize(new_width + 50, new_height + 200)
            self.update_slice_selector()  # Update the slice selector after loading

    def load_segmentation(self):
        """
        Load a segmentation NIfTI file and update the annotation matrix.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Segmentation File", "", "NIfTI Files (*.nii *.nii.gz)", options=options)
        if file_path:
            nifti_img = nib.load(file_path)
            segmentation_data = nifti_img.get_fdata()

            # Check if segmentation dimensions match the canvas dimensions
            if segmentation_data.shape == self.canvas.annotation_matrix.shape:
                self.canvas.annotation_matrix = segmentation_data.astype(np.int32)  # Ensure it's in int32 format
                self.canvas.update_slice()  # Update the slice display
                print(f"Loaded segmentation from {file_path} and updated annotation matrix.")
                self.update_slice_selector()  # Update the slice selector after loading segmentation
            else:
                print("Error: The dimensions of the segmentation file do not match the current NIfTI data.")
