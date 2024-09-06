# mainwwindow.py
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QScrollBar, QHBoxLayout
from PyQt5.QtCore import Qt
from canvas import Canvas
from utils import save_annotation_nifti


class MainWindow(QMainWindow):
    def __init__(self, nifti_file_path=None, shape=(400, 400)):
        """
        Initialize the main window, set up the canvas, button, and scroll bar.
        
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

        # Initialize the Download Button
        download_button = QPushButton("Download Annotation")
        download_button.setFixedWidth(self.canvas.width())
        download_button.clicked.connect(self.download_nifti)

        # Initialize the Scroll Bar
        self.scroll_bar = QScrollBar(Qt.Vertical)
        self.scroll_bar.setMaximum(self.canvas.nifti_data.shape[2] - 1)
        self.scroll_bar.setValue(self.canvas.current_slice_index)
        self.scroll_bar.valueChanged.connect(self.scroll_to_slice)

        # Layout Setup
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(download_button)

        # Combine Canvas and Scroll Bar Horizontally
        container_layout = QHBoxLayout()
        container_layout.addLayout(layout)
        container_layout.addWidget(self.scroll_bar)

        # Set the Main Window Layout
        container = QWidget()
        container.setLayout(container_layout)
        self.setCentralWidget(container)

        self.setWindowTitle("NIfTI Annotation")
        self.setFixedSize(width + 100, height + 100)

    def scroll_to_slice(self, value):
        """
        Update the canvas to display the slice corresponding to the scroll bar value.
        
        :param value: The new slice index from the scroll bar
        """
        self.canvas.current_slice_index = value
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
            save_annotation_nifti(
                self.canvas.annotation_matrix,
                self.canvas.nifti_affine,
                self.canvas.nifti_header,
                file_path
            )
