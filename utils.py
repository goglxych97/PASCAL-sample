#utils.py
import nibabel as nib


def save_annotation_nifti(annotation_matrix, nifti_affine, nifti_header, file_path):
    """
    Save the annotation matrix as a NIfTI file.
    :param annotation_matrix: 3D numpy array containing annotation data
    :param nifti_affine: Affine transformation matrix from the original NIfTI file
    :param nifti_header: Header information from the original NIfTI file
    :param file_path: Path where the NIfTI file should be saved
    """
    if not file_path.endswith('.nii.gz'):
        file_path += '.nii.gz'

    # Create a new NIfTI image
    annotation_img = nib.Nifti1Image(annotation_matrix, affine=nifti_affine, header=nifti_header)

    # Save the NIfTI image
    nib.save(annotation_img, file_path)
