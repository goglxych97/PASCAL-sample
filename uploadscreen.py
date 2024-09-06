#uploadscreen.py 
import nibabel as nib
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent


class UploadScreen(QWidget):
    # Signal to emit the file path and shape when a NIfTI file is loaded
    nifti_loaded = pyqtSignal(str, tuple)

    def __init__(self):
        """
        Initialize the UploadScreen widget and set up the UI.
        """
        super().__init__()
        self.init_ui()
        self.setAcceptDrops(True)


    def init_ui(self):
        """
        Set up the user interface layout and elements.
        """
        layout = QVBoxLayout() 

        self.label = QLabel("Upload NIfTI by click the button below or drag & drop", self)
        layout.addWidget(self.label)

        # Button to upload NIfTI file
        upload_button = QPushButton("Upload NIfTI File")
        upload_button.clicked.connect(self.upload_file)
        layout.addWidget(upload_button)

        self.setLayout(layout)
        self.setWindowTitle("NIfTI Segmentation")


    def upload_file(self):
        """
        Open a file dialog to select a NIfTI file for uploading.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open NIfTI File", "", "NIfTI Files (*.nii *.nii.gz)", options=options)
        if file_path:
            self.process_nifti_file(file_path)  # Process the selected NIfTI file


    def process_nifti_file(self, file_path):
        """
        Load the NIfTI file and emit a signal with the file path and shape.
        :param file_path: Path to the selected NIfTI file
        """
        nifti_img = nib.load(file_path)
        nifti_data = nifti_img.get_fdata()
        shape = nifti_data.shape
        self.nifti_loaded.emit(file_path, shape)


    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        Handle drag enter events to accept file drops.
        :param event: QDragEnterEvent object
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            

    def dropEvent(self, event: QDropEvent):
        """
        Handle file drop events to upload NIfTI files.
        :param event: QDropEvent object
        """
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(('.nii', '.nii.gz')):
                self.process_nifti_file(file_path)
                break

