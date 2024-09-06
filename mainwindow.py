# mainwindow.py
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QScrollBar, QHBoxLayout
from PyQt5.QtCore import Qt
from canvas import Canvas
from utils import save_annotation_nifti


class MainWindow(QMainWindow):
    def __init__(self, nifti_file_path=None, shape=(400, 400)):
        """
        Initialize the main window, set up the canvas, buttons, and scroll bar.
        :param nifti_file_path: Path to the NIfTI file to load initially (optional)
        :param shape: Tuple indicating the dimensions (width, height) of the canvas
        """
        super().__init__()

        width = min(shape[0], 800)
        height = min(shape[1], 800)

        # Initialize the Canvas
        self.canvas = Canvas(width, height)
        if nifti_file_path:
            self.canvas.set_background_image_from_nifti(nifti_file_path)

        # Connect the canvas signal to the slot that updates the scroll bar
        self.canvas.slice_changed.connect(self.update_scroll_bar)

        # Initialize Buttons
        load_nifti_button = QPushButton("Load NIfTI Files")
        download_button = QPushButton("Download Segmentation")
        load_segmentation_button = QPushButton("Load Segmentation")

        # Set buttons widths
        button_width = self.canvas.width() // 3
        load_nifti_button.setFixedWidth(button_width)
        download_button.setFixedWidth(button_width)
        load_segmentation_button.setFixedWidth(button_width)

        # Connect buttons to respective functions
        load_nifti_button.clicked.connect(self.load_nifti_file)
        download_button.clicked.connect(self.download_nifti)
        load_segmentation_button.clicked.connect(self.load_segmentation)

        # Initialize the Scroll Bar
        self.scroll_bar = QScrollBar(Qt.Vertical)
        self.scroll_bar.setMaximum(self.canvas.nifti_data.shape[2] - 1)  # Max value = number of slices - 1
        self.scroll_bar.setValue(self.canvas.current_slice_index)
        self.scroll_bar.valueChanged.connect(self.scroll_to_slice)  # Connect to slice scrolling function

        # Layout Setup for Buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(load_nifti_button)
        button_layout.addWidget(download_button)
        button_layout.addWidget(load_segmentation_button)

        # Main Layout Setup
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addLayout(button_layout)

        # Combine Canvas and Scroll Bar Horizontally
        container_layout = QHBoxLayout()
        container_layout.addLayout(layout)
        container_layout.addWidget(self.scroll_bar)

        # Set the Main Window Layout
        container = QWidget()
        container.setLayout(container_layout)
        self.setCentralWidget(container)

        self.setWindowTitle("NIfTI Segmentation")
        self.setFixedSize(width + 100, height + 150)


    def scroll_to_slice(self, value):
        """
        Update the canvas to display the slice corresponding to the scroll bar value.
        :param value: The new slice index from the scroll bar
        """
        # Ensure the value is within the bounds of the data
        max_index = self.canvas.nifti_data.shape[2] - 1 if self.canvas.nifti_data is not None else 0
        self.canvas.current_slice_index = min(max(0, value), max_index)
        self.canvas.update_slice()  # Update the canvas slice


    def update_scroll_bar(self, new_index):
        """
        Update the scroll bar's value to match the current slice index in the canvas.
        :param new_index: The new slice index in the canvas
        """
        self.scroll_bar.setValue(new_index)


    def download_nifti(self):
        """
        Open a file dialog to save the annotated NIfTI file.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save NIfTI Format", "", "NIfTI Files (*.nii.gz)", options=options)
        if file_path:
            # Save the annotation
            save_annotation_nifti(
                self.canvas.annotation_matrix,
                self.canvas.nifti_affine,
                self.canvas.nifti_header,
                file_path
            )


    def load_nifti_file(self):
        """
        Open a file dialog to load a new background NIfTI file and adjust the window size accordingly.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load NIfTI File", "", "NIfTI Files (*.nii *.nii.gz)", options=options)
        if file_path:
            # Load new NIfTI file as background
            self.canvas.set_background_image_from_nifti(file_path)
            
            # Update scroll bar
            self.scroll_bar.setMaximum(self.canvas.nifti_data.shape[2] - 1)
            self.canvas.current_slice_index = min(self.canvas.current_slice_index, self.canvas.nifti_data.shape[2] - 1)
            self.scroll_bar.setValue(self.canvas.current_slice_index)

            # Adjust the window size
            new_width = self.canvas.width()
            new_height = self.canvas.height()
            self.setFixedSize(new_width + 100, new_height + 150)


    def load_segmentation(self):
        """
        Placeholder for Load Segmentation functionality. No action is taken when clicked.
        """
        pass  # Functionality removed; button remains without action
