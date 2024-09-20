# menu/file.py
from PyQt5.QtWidgets import QFileDialog
from utils.segmentation_utils.convert_matrix_for_save import save_segmentation_nifti
import nibabel as nib

def load_nifti(main_window):
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(
        main_window,
        "Load NIfTI File",
        "",
        "NIfTI Files (*.nii *.nii.gz)",
        options=options
    )

    return file_path

def load_segmentation(main_window):
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(
        main_window,
        "Load Segmentation File",
        "",
        "NIfTI Files (*.nii *.nii.gz)",
        options=options
    )
    if file_path:
        nifti_img = nib.load(file_path)
        return nifti_img.get_fdata()
    
    return None

def save_segmentation(main_window, segmentation_matrix, affine, header):
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getSaveFileName(
        main_window,
        "Save Segmentation File",
        "",
        "NIfTI Files (*.nii.gz)",
        options=options
    )
    if file_path:
        save_segmentation_nifti(
            segmentation_matrix,
            affine,
            header,
            file_path
        )
