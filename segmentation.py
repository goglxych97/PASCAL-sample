# segmentation.py
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtGui import QColor

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


# segmentation.py

from PyQt5.QtGui import QPainter, QPen, QColor

def render_annotation_from_matrix(annotation_image, annotation_matrix, pen_color, brush_size, current_slice_index):
    """
    Render the annotations from the matrix onto the annotation image.
    """
    if annotation_matrix is not None:
        annotation_image.fill(Qt.transparent)

        slice_segmentation = annotation_matrix[:, :, current_slice_index]
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

        painter = QPainter(annotation_image)

        # Draw paths connecting each point
        for y in range(height):
            for x in range(width):
                color_value = slice_segmentation[y, x]
                if color_value in color_map:  # Ensure the value has a corresponding color
                    pen_color = color_map[color_value]
                    painter.setPen(QPen(pen_color, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    screen_x = int(x * annotation_image.width() / width)
                    screen_y = int(y * annotation_image.height() / height)

                    # Check the 8 directions around the current pixel and connect only if the distance is 1 pixel
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue  # Skip itself
                            nx, ny = x + dx, y + dy
                            if (
                                0 <= nx < width and 0 <= ny < height and
                                slice_segmentation[ny, nx] == color_value  # Only connect pixels with the same color
                            ):
                                neighbor_screen_x = int(nx * annotation_image.width() / width)
                                neighbor_screen_y = int(ny * annotation_image.height() / height)
                                painter.drawLine(screen_x, screen_y, neighbor_screen_x, neighbor_screen_y)

        painter.end()

# segmentation.py

# segmentation.py

# segmentation.py

def update_annotation_matrix(annotation_matrix, last_pos, pos, brush_size, background_image, current_slice_index, brush_color_value):
    """
    Update the annotation matrix by drawing a line between two points.
    """
    if annotation_matrix is not None:
        # Convert positions to matrix coordinates
        x0 = int(last_pos.x() * annotation_matrix.shape[1] / background_image.width())
        y0 = int(last_pos.y() * annotation_matrix.shape[0] / background_image.height())
        x1 = int(pos.x() * annotation_matrix.shape[1] / background_image.width())
        y1 = int(pos.y() * annotation_matrix.shape[0] / background_image.height())

        # Generate points using Bresenham's line algorithm
        line_points = bresenham_line(x0, y0, x1, y1)

        # Update the annotation matrix with the color value or clear
        brush_radius = brush_size // 2  # Calculate the radius using the brush size itself
        for x_center, y_center in line_points:
            for y_offset in range(-brush_radius, brush_radius + 1):
                for x_offset in range(-brush_radius, brush_radius + 1):
                    x = x_center + x_offset
                    y = y_center + y_offset
                    if 0 <= x < annotation_matrix.shape[1] and 0 <= y < annotation_matrix.shape[0]:
                        # Apply circular brush effect
                        if (x_offset**2 + y_offset**2) <= brush_radius**2:
                            if brush_color_value == 0:
                                # Clear the annotation at this point
                                annotation_matrix[y, x, current_slice_index] = 0
                                print(f"Cleared annotation at ({y}, {x}, {current_slice_index})")
                            else:
                                # Overwrite with the new color value and ensure it is stored as an integer
                                annotation_matrix[y, x, current_slice_index] = int(brush_color_value)
                                print(f"Updated annotation matrix at ({y}, {x}, {current_slice_index}) to {brush_color_value}")  # 디버그용 출력
