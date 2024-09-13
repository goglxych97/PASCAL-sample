#uploadscreen.py 
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class UploadScreen(QWidget):
    nifti_loaded = pyqtSignal(str)  # Signal to emit the file path

    def __init__(self):
        """
        Initialize the UI.
        """
        super().__init__()
        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        """
        Set up the user interface.
        """
        layout = QVBoxLayout() 
        self.label = QLabel("Upload NIfTI by click the button below or drag & drop", self)
        layout.addWidget(self.label)
        upload_button = QPushButton("Upload NIfTI File")
        upload_button.clicked.connect(self.upload_file)
        layout.addWidget(upload_button)
        self.setLayout(layout)
        self.setWindowTitle("NIfTI Segmentation")

    def upload_file(self):
        """
        File dialog to select a NIfTI file.
        """
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
        """
        Load the NIfTI file and emit a signal with the file path.
        :param file_path: Path to the NIfTI file
        """
        self.nifti_loaded.emit(file_path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        Handle drag enter events.
        :param event: QDragEnterEvent object
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """
        Handle file drop events.
        :param event: QDropEvent object
        """
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(('.nii', '.nii.gz')):
                self.process_nifti_file(file_path)
                break

