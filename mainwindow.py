# mainwindow.py
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog
from canvas import Canvas
from utils import save_annotation_nifti

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.canvas = Canvas(400, 400)

        download_button = QPushButton("Download Annotation")
        download_button.clicked.connect(self.download_nifti)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(download_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.setWindowTitle("Nifty Annotation")

    def download_nifti(self):
        options = QFileDialog.Options()
        # Set the default file extension to .nii.gz
        file_path, _ = QFileDialog.getSaveFileName(self, "Save NIfTI File", "", "NIfTI Files (*.nii.gz)", options=options)
        if file_path:
            save_annotation_nifti(self.canvas.annotation_matrix, self.canvas.nifti_header, file_path)
