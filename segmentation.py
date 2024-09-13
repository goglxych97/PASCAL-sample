# segmentation.py
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen

def bresenham_line(x0, y0, x1, y1):
    """
    Generate points between two coordinates using Bresenham's line algorithm.
    :param x0: Integer, x-coordinate of the start point
    :param y0: Integer, y-coordinate of the start point
    :param x1: Integer, x-coordinate of the end point
    :param y1: Integer, y-coordinate of the end point
    :return: List of (x, y) points between the start and end points
    """
    points = []  # List to store all points
    dx = abs(x1 - x0)  # Difference in x-coords
    dy = abs(y1 - y0)  # Difference in y-coords
    sx = 1 if x0 < x1 else -1  # Step direction for x
    sy = 1 if y0 < y1 else -1  # Step direction for y
    err = dx - dy  # Initialize the error term

    while True:
        points.append((x0, y0))  # Add the point to the points list
        if x0 == x1 and y0 == y1:  # If end, break the loop
            break
        e2 = err * 2  # Calculate double the error term to determine the next step
        # Adjust x-coordinate and error term
        if e2 > -dy:
            err -= dy  # Subtract dy from the error term
            x0 += sx
        # Adjust y-coordinate and error term
        if e2 < dx:
            err += dx  # Add dx to the error term
            y0 += sy
    
    return points


def render_segmentation_from_matrix(segmentation_image, segmentation_matrix, brush_color, current_slice_index):
    """
    Render the segmentations from the matrix.
    :param segmentation_image: QImage object to draw the segmentation
    :param segmentation_matrix: 3D numpy array containing segmentation
    :param brush_color: QColor object for the brush color
    :param current_slice_index: Index for current slice to render
    """
    if segmentation_matrix is not None:
        segmentation_image.fill(Qt.transparent)
        slice_segmentation = segmentation_matrix[:, :, current_slice_index]
        height, width = slice_segmentation.shape
        # Define color mapping
        color_map = {
            1: QColor('red'),
            2: QColor('green'),
            3: QColor('blue'),
            4: QColor('yellow'),
            5: QColor('skyblue'),
            6: QColor('purple')
        }
        painter = QPainter(segmentation_image)
        # Draw paths connecting each point
        for y in range(height):
            for x in range(width):
                color_value = slice_segmentation[y, x]
                if color_value in color_map:  # Ensure the value has a corresponding color
                    brush_color = color_map[color_value]
                    painter.setPen(QPen(brush_color, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    screen_x = int(x * segmentation_image.width() / width)
                    screen_y = int(y * segmentation_image.height() / height)
                    # Check the 8 directions around the current pixel and connect
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue  # Skip
                            nx, ny = x + dx, y + dy
                            if (
                                0 <= nx < width and 0 <= ny < height and
                                slice_segmentation[ny, nx] == color_value  # Only connect pixels with the same color
                            ):
                                neighbor_screen_x = int(nx * segmentation_image.width() / width)
                                neighbor_screen_y = int(ny * segmentation_image.height() / height)
                                painter.drawLine(screen_x, screen_y, neighbor_screen_x, neighbor_screen_y)
        painter.end()


def update_segmentation_matrix(segmentation_matrix, last_pos, pos, brush_size, background_image, current_slice_index, brush_color_value):
    """
    Update the segmentation matrix by drawing a line between points.
    :param segmentation_matrix: 3D numpy array to update with segmentation data
    :param last_pos: QPoint for the starting point
    :param pos: QPoint for the ending point
    :param brush_size: Brush size in pixels
    :param background_image: QImage object for the background image
    :param current_slice_index: Index for current slice to update
    :param brush_color_value: Integer for the color value of the brush
    """
    if segmentation_matrix is not None:
        # Convert positions to matrix coordinates
        x0 = int(last_pos.x() * segmentation_matrix.shape[1] / background_image.width())
        y0 = int(last_pos.y() * segmentation_matrix.shape[0] / background_image.height())
        x1 = int(pos.x() * segmentation_matrix.shape[1] / background_image.width())
        y1 = int(pos.y() * segmentation_matrix.shape[0] / background_image.height())
        # Generate points using Bresenham's algorithm
        line_points = bresenham_line(x0, y0, x1, y1)
        # Update the segmentation matrix
        brush_radius = brush_size // 2
        for x_center, y_center in line_points:
            for y_offset in range(-brush_radius, brush_radius + 1):
                for x_offset in range(-brush_radius, brush_radius + 1):
                    x = x_center + x_offset
                    y = y_center + y_offset
                    if 0 <= x < segmentation_matrix.shape[1] and 0 <= y < segmentation_matrix.shape[0]:
                        # Apply circular brush effect
                        if (x_offset**2 + y_offset**2) <= brush_radius**2:
                            if brush_color_value == 0:
                                # Clear the segmentation at this point
                                segmentation_matrix[y, x, current_slice_index] = 0
                            else:
                                # Overwrite with the new color value and ensure it is stored as an integer
                                segmentation_matrix[y, x, current_slice_index] = int(brush_color_value)
