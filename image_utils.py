# image_utils.py
import numpy as np

def normalize_image_data(image_data):
    """
    Normalize the image to the range [0, 255].
    :param image_data: 2D numpy array
    :return: Normalized 2D numpy array of type uint8.
    """
    if np.max(image_data) == np.min(image_data):
        return np.zeros_like(image_data, dtype=np.uint8) # Prevent division by zero if the image is flat
 
    normalized_data = 255 * (image_data - np.min(image_data)) / (np.max(image_data) - np.min(image_data))

    return normalized_data.astype(np.uint8)
