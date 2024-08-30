# utils.py
import numpy as np
import nibabel as nib

def save_annotation_nifti(annotation_matrix, nifti_header, file_path):
    """
    Save the annotation matrix as a NIfTI file.
    
    :param annotation_matrix: 3D numpy array containing the annotation data
    :param nifti_header: NIfTI header from the original NIfTI file
    :param file_path: Path where the NIfTI file should be saved
    """
    if not file_path.endswith('.nii.gz'):
        file_path += '.nii.gz'  # Ensure the file has the correct extension
    
    # Create a NIfTI image with the annotation data and the header
    annotation_img = nib.Nifti1Image(annotation_matrix, affine=np.eye(4), header=nifti_header)
    
    # Save the NIfTI file in compressed format
    nib.save(annotation_img, file_path)
