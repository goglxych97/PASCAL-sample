# segmentation.py
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush


def calculate_brush_radius(brush_size, image_width, image_height, matrix_width, matrix_height):
    """
    Calculate the scaled brush radius for consistent drawing and rendering.
    """
    scale_x = image_width / matrix_width  # Scale factor for width
    scale_y = image_height / matrix_height  # Scale factor for height

    # Return the adjusted brush radius based on minimum scaling factor
    return int(brush_size * min(scale_x, scale_y) / 3)

def bresenham_line(x0, y0, x1, y1):
    """
    Generate points between two coordinates using Bresenham's line algorithm.
    
    :return: List of (x, y) points between the start and end points
    """
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1  # Step direction for x
    sy = 1 if y0 < y1 else -1  # Step direction for y
    err = dx - dy

    while True:
        points.append((x0, y0))  # Add current point to list
        if x0 == x1 and y0 == y1:  # Stop when end point is reached
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
    Update the annotation matrix by drawing a line between two points.
    """
    if annotation_matrix is not None:
        # Calculate brush radius for consistent rendering
        brush_radius = calculate_brush_radius(
            brush_size, background_image.width(), background_image.height(),
            annotation_matrix.shape[1], annotation_matrix.shape[0]
        )

        # Convert positions to matrix coordinates
        x0 = int(last_pos.x() * annotation_matrix.shape[1] / background_image.width())
        y0 = int(last_pos.y() * annotation_matrix.shape[0] / background_image.height())
        x1 = int(pos.x() * annotation_matrix.shape[1] / background_image.width())
        y1 = int(pos.y() * annotation_matrix.shape[0] / background_image.height())

        # Generate points using Bresenham's line algorithm
        line_points = bresenham_line(x0, y0, x1, y1)

        # Update the annotation matrix with brush effect
        for x_center, y_center in line_points:
            for y_offset in range(-brush_radius, brush_radius + 1):
                for x_offset in range(-brush_radius, brush_radius + 1):
                    x = x_center + x_offset
                    y = y_center + y_offset
                    if 0 <= x < annotation_matrix.shape[1] and 0 <= y < annotation_matrix.shape[0]:
                        # Apply circular brush effect
                        if (x_offset**2 + y_offset**2) <= brush_radius**2:
                            annotation_matrix[y, x, current_slice_index] = 1

def render_annotation_from_matrix(annotation_image, annotation_matrix, pen_color, brush_size, current_slice_index):
    """
    Render the annotations from the matrix onto the annotation image.
    """
    if annotation_matrix is not None:
        annotation_image.fill(Qt.transparent)

        slice_segmentation = annotation_matrix[:, :, current_slice_index]
        height, width = slice_segmentation.shape

        # Calculate scaled brush radius for rendering
        brush_radius_scaled = calculate_brush_radius(
            brush_size, annotation_image.width(), annotation_image.height(), width, height
        )

        painter = QPainter(annotation_image)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(pen_color))

        # Draw annotations as ellipses for each point
        for y in range(height):
            for x in range(width):
                if slice_segmentation[y, x] == 1:  # If annotated
                    screen_x = int(x * annotation_image.width() / width)
                    screen_y = int(y * annotation_image.height() / height)
                    painter.drawEllipse(screen_x - brush_radius_scaled, screen_y - brush_radius_scaled, brush_radius_scaled * 2, brush_radius_scaled * 2)

        painter.end()
