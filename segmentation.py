# segmentation.py
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QBrush

def calculate_brush_radius(brush_size, image_width, image_height, matrix_width, matrix_height):
    """
    Calculate the brush radius to be consistent for both drawing and rendering.
    
    :param brush_size: Size of the brush in pixels
    :param image_width: Width of the display image
    :param image_height: Height of the display image
    :param matrix_width: Width of the annotation matrix
    :param matrix_height: Height of the annotation matrix
    :return: Scaled brush radius
    """
    scale_x = image_width / matrix_width
    scale_y = image_height / matrix_height
    return int(brush_size * min(scale_x, scale_y) / 2)

def bresenham_line(x0, y0, x1, y1):
    """
    Bresenham's line algorithm to generate points between two coordinates.
    
    :param x0: Starting x-coordinate
    :param y0: Starting y-coordinate
    :param x1: Ending x-coordinate
    :param y1: Ending y-coordinate
    :return: List of (x, y) points between the start and end points
    """
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    
    return points

def update_annotation_matrix(annotation_matrix, last_pos, pos, brush_size, background_image, current_slice_index):
    """
    Update the annotation matrix by drawing a line from the last position to the current position.
    
    :param annotation_matrix: 3D numpy array for storing annotations
    :param last_pos: QPoint for the last mouse position
    :param pos: QPoint for current mouse position
    :param brush_size: Size of the brush for annotation
    :param background_image: QImage for the background image dimensions
    :param current_slice_index: Current index of the slice being annotated
    """
    if annotation_matrix is not None:
        # Calculate brush radius consistently with rendering
        brush_radius = calculate_brush_radius(
            brush_size, background_image.width(), background_image.height(),
            annotation_matrix.shape[1], annotation_matrix.shape[0]
        )

        x0 = int(last_pos.x() * annotation_matrix.shape[1] / background_image.width())
        y0 = int(last_pos.y() * annotation_matrix.shape[0] / background_image.height())
        x1 = int(pos.x() * annotation_matrix.shape[1] / background_image.width())
        y1 = int(pos.y() * annotation_matrix.shape[0] / background_image.height())

        # Generate points between last_pos and pos using Bresenham's line algorithm
        line_points = bresenham_line(x0, y0, x1, y1)

        for x_center, y_center in line_points:
            for y_offset in range(-brush_radius, brush_radius + 1):
                for x_offset in range(-brush_radius, brush_radius + 1):
                    x = x_center + x_offset
                    y = y_center + y_offset
                    if 0 <= x < annotation_matrix.shape[1] and 0 <= y < annotation_matrix.shape[0]:
                        # Use a circular brush for a smoother effect
                        if (x_offset**2 + y_offset**2) <= brush_radius**2:
                            annotation_matrix[y, x, current_slice_index] = 1

def render_annotation_from_matrix(annotation_image, annotation_matrix, pen_color, brush_size, current_slice_index):
    """
    Render the annotation from the annotation matrix onto the annotation image.
    
    :param annotation_image: QImage to draw the annotations
    :param annotation_matrix: 3D numpy array for storing annotations
    :param pen_color: QColor for the pen
    :param brush_size: Size of the brush for drawing
    :param current_slice_index: Current index of the slice being annotated
    """
    if annotation_matrix is not None:
        # Clear the annotation image to fully transparent
        annotation_image.fill(Qt.transparent)

        slice_segmentation = annotation_matrix[:, :, current_slice_index]
        height, width = slice_segmentation.shape

        # Calculate the brush radius for consistent rendering
        brush_radius_scaled = calculate_brush_radius(
            brush_size, annotation_image.width(), annotation_image.height(), width, height
        )

        with QPainter(annotation_image) as painter:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(pen_color))
            painter.setOpacity(pen_color.alphaF())  # Set opacity using QColor's alpha

            for y in range(height):
                for x in range(width):
                    if slice_segmentation[y, x] == 1:
                        screen_x = int(x * annotation_image.width() / width)
                        screen_y = int(y * annotation_image.height() / height)
                        
                        # Debug: Check drawing points and sizes
                        print(f"Drawing at screen ({screen_x}, {screen_y}) with radius {brush_radius_scaled}")
                        
                        # Draw an ellipse (filled circle) with consistent scaling
                        painter.drawEllipse(screen_x - brush_radius_scaled, screen_y - brush_radius_scaled, brush_radius_scaled * 2, brush_radius_scaled * 2)
