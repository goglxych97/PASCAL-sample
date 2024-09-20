# windows/init_window.py 
# temporary script
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class InitWindow(QWidget):
    nifti_loaded = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        layout = QVBoxLayout() 
        self.label = QLabel("Upload NIfTI by click the button below or drag & drop", self)
        layout.addWidget(self.label)
        upload_button = QPushButton("Upload NIfTI File")
        upload_button.clicked.connect(self.upload_file)
        layout.addWidget(upload_button)
        self.setLayout(layout)
        self.setWindowTitle("NIfTI Segmentation")

    def upload_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
                            self,
                            "Open NIfTI File",
                            "",
                            "NIfTI Files (*.nii *.nii.gz)",
                            options=options
        )
        if file_path:
            self.process_nifti_file(file_path)

    def process_nifti_file(self, file_path):
        self.nifti_loaded.emit(file_path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(('.nii', '.nii.gz')):
                self.process_nifti_file(file_path)
                break

