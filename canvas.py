#canvas.py
import numpy as np
import nibabel as nib
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QPixmap, QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QLabel
from segmentation import update_annotation_matrix, render_annotation_from_matrix


class Canvas(QLabel):
    # Signal to notify when the current slice index changes
    slice_changed = pyqtSignal(int)

    def __init__(self, width, height):
        """
        Initialize the Canvas widget.
        :param width: Width of the canvas
        :param height: Height of the canvas
        """
        super().__init__()
        self.setFixedSize(width, height)
        self.background_image = QImage(width, height, QImage.Format_ARGB32)
        self.background_image.fill(Qt.white)
        self.annotation_image = QImage(width, height, QImage.Format_ARGB32)
        self.annotation_image.fill(Qt.transparent)
        self.pen_color = QColor(255, 0, 0, 255)
        self.brush_size = 10
        self.setPixmap(QPixmap.fromImage(self.background_image))
        self.last_point = QPoint()
        self.drawing = False
        self.setAcceptDrops(True)
        self.nifti_data = None
        self.nifti_affine = None
        self.nifti_header = None
        self.current_slice_index = 0
        self.annotation_matrix = None


    def set_pen_color(self, color):
        """
        Set the color of the pen used for drawing annotations.
        :param color: QColor object representing the new pen color
        """
        self.pen_color = color


    def set_brush_size(self, size):
        """
        Set the size of the brush used for drawing annotations.
        :param size: Integer representing the brush size
        """
        self.brush_size = size


    def mousePressEvent(self, event):
        """
        Handle mouse press events to start drawing annotations.
        :param event: QMouseEvent object
        """
        if event.button() == Qt.LeftButton:
            self.last_point = event.pos() # Store the starting point
            self.drawing = True # Set drawing flag to True
            self.draw_on_canvas(event.pos()) # Draw on the canvas

            # Update annotation matrix
            update_annotation_matrix( 
                self.annotation_matrix,
                self.last_point,
                event.pos(),
                self.brush_size,
                self.background_image,
                self.current_slice_index
            )

            self.last_point = event.pos() # Update last point


    def mouseMoveEvent(self, event):
        """
        Handle mouse move events to draw annotations while the mouse moves.
        :param event: QMouseEvent object
        """
        if event.buttons() & Qt.LeftButton and self.drawing:
            self.draw_on_canvas(event.pos()) # Draw on the canvas

            # Update annotation matrix
            update_annotation_matrix(
                self.annotation_matrix,
                self.last_point,
                event.pos(),
                self.brush_size,
                self.background_image,
                self.current_slice_index
            )

            self.last_point = event.pos() # Update last point


    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events to stop drawing annotations.
        :param event: QMouseEvent object
        """
        if event.button() == Qt.LeftButton:
            self.drawing = False


    def draw_on_canvas(self, pos):
        """
        Draw a line on the canvas between the last point and the current position.
        :param pos: QPoint representing the current position
        """
        canvas_pixmap = self.pixmap().copy() # Copy the current pixmap

        painter = QPainter(canvas_pixmap)
        pen = QPen(self.pen_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(self.last_point, pos)
        painter.end()

        self.setPixmap(canvas_pixmap) # Update the canvas pixmap


    def wheelEvent(self, event):
        """
        Handle mouse wheel events for scrolling through image slices.
        :param event: QWheelEvent object
        """
        if self.nifti_data is not None:
            num_slices = self.nifti_data.shape[2]
            delta = event.angleDelta().y() // 120 # Calculate scroll direction

            new_index = self.current_slice_index + delta
            if 0 <= new_index < num_slices:
                self.current_slice_index = new_index
                self.update_slice() # Update slice display

                # Emit the slice_changed signal with the new index
                self.slice_changed.emit(self.current_slice_index)


    def update_slice(self):
        """
        Update the current slice display with the corresponding background and annotation images.
        """
        slice_data = self.nifti_data[:, :, self.current_slice_index]

        # Normalize the slice data for display
        normalized_data = 255 * (slice_data - np.min(slice_data)) / (np.max(slice_data) - np.min(slice_data))
        normalized_data = normalized_data.astype(np.uint8)
        height, width = normalized_data.shape
        bytes_per_line = width

        # Convert to QImage format
        qimage = QImage(normalized_data.tobytes(), width, height, bytes_per_line, QImage.Format_Grayscale8)
        self.background_image = qimage.scaled(self.width(), self.height())
        self.annotation_image.fill(Qt.transparent)  # Clear the annotation image for the new slice

        # Render the annotation matrix onto the annotation image
        render_annotation_from_matrix(
            self.annotation_image,
            self.annotation_matrix,
            self.pen_color,
            self.brush_size,
            self.current_slice_index
        )

        self.update_display() # Update the display


    def update_display(self):
        """
        Combine the background and annotation images and update the canvas display.
        """
        combined_image = QImage(self.size(), QImage.Format_ARGB32)  # Create a new image for combining layers
        combined_image.fill(Qt.transparent)

        painter = QPainter(combined_image)
        painter.drawImage(0, 0, self.background_image)  # Draw background image
        painter.drawImage(0, 0, self.annotation_image)  # Overlay annotation image
        painter.end()  # End painting

        self.setPixmap(QPixmap.fromImage(combined_image))  # Update the canvas pixmap


    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        Handle drag enter events to accept NIfTI file drops.
        :param event: QDragEnterEvent object
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()


    def dropEvent(self, event: QDropEvent):
        """
        Handle drop events to load NIfTI files.
        :param event: QDropEvent object
        """
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(('.nii', '.nii.gz')):
                self.set_background_image_from_nifti(file_path)
            break


    def set_background_image_from_nifti(self, file_path):
        """
        Load a NIfTI file and set the background image to the middle slice.
        :param file_path: Path to the NIfTI file
        """
        nifti_img = nib.load(file_path)
        self.nifti_data = nifti_img.get_fdata()
        self.nifti_affine = nifti_img.affine
        self.nifti_header = nifti_img.header
        self.annotation_matrix = np.zeros_like(self.nifti_data)  # Initialize the segmentation matrix
        self.current_slice_index = self.nifti_data.shape[2] // 2
        self.update_slice()  # Update the slice display

        # Adjust the size of the canvas
        new_width = min(self.nifti_data.shape[1], 800)
        new_height = min(self.nifti_data.shape[0], 800)
        self.setFixedSize(new_width, new_height)

        # Adjust the main window size
        if self.parent():
            parent_window = self.parent()
            parent_window.setFixedSize(new_width + 100, new_height + 150)
