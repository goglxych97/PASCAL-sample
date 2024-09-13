# utils.py
from nibabel.orientations import io_orientation, ornt_transform, inv_ornt_aff
import nibabel as nib
import numpy as np

def save_segmentation_nifti(segmentation_matrix, original_affine, original_header, file_path):
    """
    Save the segmentation matrix.
    :param segmentation_matrix: 3D numpy segmentation matrix
    :param original_affine: Affine matrix from the original NIfTI 
    :param original_header: Header information from the original NIfTI
    :param file_path: Path where the NIfTI should be saved
    """
    if not file_path.endswith('.nii.gz'):
        file_path += '.nii.gz'


    canonical_img = nib.Nifti1Image(segmentation_matrix, np.eye(4)) # Create a NIfTI image in RAS orientation
    rotated_data = np.rot90(canonical_img.get_fdata(), k=1, axes=(0, 1))  # Rotate 90-degrees counterclockwise
    transformed_data = rotated_data[:, ::-1, :]  # Left-right flip

    # Back to original orientation
    ras_ornt = io_orientation(np.eye(4))
    original_ornt = io_orientation(original_affine)
    transform = ornt_transform(ras_ornt, original_ornt)
    transformed_data = nib.orientations.apply_orientation(transformed_data, transform)
    new_affine = original_affine @ inv_ornt_aff(transform, segmentation_matrix.shape)  # New affine corresponds to the original orientation

    new_img = nib.Nifti1Image(transformed_data, new_affine, original_header)  # Create a new NIfTI image with new affine
 
    nib.save(new_img, file_path)  #Save the NIfTI
