# canvas.py
from functools import lru_cache
from cache_utils import slice_cache
from image_utils import normalize_image_data 
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QColor, QDragEnterEvent, QDropEvent, QImage, QPainter, QPixmap
from PyQt5.QtWidgets import QLabel, QSizePolicy
from segmentation import update_segmentation_matrix, render_segmentation_from_matrix
import numpy as np
import nibabel as nib

class Canvas(QLabel):
    slice_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(540, 540)
        self.background_image = None
        self.segmentation_image = None
        self.brush_color = QColor(255, 0, 0, 255)
        self.brush_size = 8
        self.brush_color_value = 1
        self.last_point = QPoint()
        self.drawing = False
        self.setAcceptDrops(True)
        self.nifti_data = None
        self.nifti_affine = None
        self.nifti_header = None
        self.current_slice_index = 0
        self.segmentation_matrix = None


    def resizeEvent(self, event):
        """
        Handle resize events.
        """
        super().resizeEvent(event)
        if self.nifti_data is not None:
            self.update_slice()

    def set_background_image_from_nifti(self, file_path):
        """
        Load a NIfTI and set the background.
        :param file_path: NIfTI file path
        """
        nifti_img = nib.load(file_path)
        self.nifti_data = np.rot90(nib.as_closest_canonical(nifti_img).get_fdata(), k=1)[:, ::-1, :]
        self.nifti_affine = nifti_img.affine
        self.nifti_header = nifti_img.header
        self.segmentation_matrix = np.zeros_like(self.nifti_data, dtype=np.int32)  # Initialize segmentation matrix
        self.current_slice_index = self.nifti_data.shape[2] // 2

        self.render_cached_slice.cache_clear()
        self.render_cached_segmentation.cache_clear()
        self.update_slice()

    @lru_cache(maxsize=100)
    def render_cached_slice(self, slice_index, size):
        """
        Render the cached slice image.
        :param slice_index: Slice index
        :param size: Desired size for scaling
        :return: QImage of the rendered slice
        """
        slice_data = self.nifti_data[:, :, slice_index]
        normalized_data = normalize_image_data(slice_data) # Normalize slice data
        height, width = normalized_data.shape
        bytes_per_line = width
        qimage = QImage(normalized_data.tobytes(), width, height, bytes_per_line, QImage.Format_Grayscale8)  # Convert to QImage format and scale it

        return qimage.scaled(size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)

    @slice_cache(maxsize=100)
    def render_cached_segmentation(self, slice_index, size):
        """
        Render the cached segmentation image.
        :param slice_index: Slice index
        :param size: Desired size for scaling
        :return: QImage of the rendered segmentation
        """
        segmentation_image = QImage(size[0], size[1], QImage.Format_ARGB32)
        segmentation_image.fill(Qt.transparent)

        render_segmentation_from_matrix(
            segmentation_image,
            self.segmentation_matrix,
            self.brush_color,
            slice_index,
        )

        return segmentation_image
    
    def update_slice(self):
        """
        Update the current slice display.
        """
        if self.nifti_data is None:
            return 

        size_tuple = (self.size().width(), self.size().height())
        self.background_image = self.render_cached_slice(self.current_slice_index, size_tuple)
        self.segmentation_image = self.render_cached_segmentation(self.current_slice_index, size_tuple)
        self.update_display() 

    def update_display(self):
        """
        Combine the background and segmentation and update the canvas display.
        """
        if self.background_image is None or self.segmentation_image is None:
            return

        combined_image = QImage(self.size(), QImage.Format_ARGB32)  # New image for combining layers
        combined_image.fill(Qt.transparent)
        painter = QPainter(combined_image)
        painter.drawImage(self.rect(), self.background_image)  # Draw scaling background
        painter.drawImage(self.rect(), self.segmentation_image)  # Draw scaling segmentation
        painter.end()  # End painting

        self.setPixmap(QPixmap.fromImage(combined_image))  # Update canvas pixmap

    def mousePressEvent(self, event):
        """
        Handle mouse press events.
        :param event: QMouseEvent object
        """
        if event.button() == Qt.LeftButton:
            self.last_point = self.translate_mouse_position(event.pos())  # Store starting point
            self.drawing = True
            self.draw_segmentation(event.pos())
            self.last_point = self.translate_mouse_position(event.pos())  # Update last point

    def mouseMoveEvent(self, event):
        """
        Handle mouse move events.
        :param event: QMouseEvent object
        """
        if event.buttons() & Qt.LeftButton and self.drawing:
            self.draw_segmentation(event.pos())
            self.last_point = self.translate_mouse_position(event.pos())  # Update last point

    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events.
        :param event: QMouseEvent object
        """
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def translate_mouse_position(self, pos):
        """
        Translate the mouse position.
        :param pos: QPoint from mouse event
        :return: Translated QPoint
        """
        if self.background_image is None:
            return pos
        
        x_ratio = self.background_image.width() / self.width()
        y_ratio = self.background_image.height() / self.height()

        return QPoint(int(pos.x() * x_ratio), int(pos.y() * y_ratio))

    def draw_segmentation(self, pos):
        """
        Update the segmentation matrix and render it.
        :param pos: Current position QPoint
        """
        pos = self.translate_mouse_position(pos)  # Translate position
        update_segmentation_matrix(  # Update segmentation
            self.segmentation_matrix,
            self.last_point,
            pos,
            self.brush_size,
            self.background_image,
            self.current_slice_index,
            self.brush_color_value
        )
        self.render_cached_segmentation.cache_invalidate(self.current_slice_index)
        size_tuple = (self.size().width(), self.size().height())
        self.segmentation_image = self.render_cached_segmentation(self.current_slice_index, size_tuple)
        self.update_display() 
        #self.render_cached_segmentation.cache_clear()  # Clear cached segmentation
        #self.update_slice()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        Handle drag enter events.
        :param event: QDragEnterEvent object
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """
        Handle drop events.
        :param event: QDropEvent object
        """
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(('.nii', '.nii.gz')):
                self.set_background_image_from_nifti(file_path)
            break

    def set_brush_color(self, color):
        """
        Set the color of the brush.
        :param color: QColor object for the color
        """
        self.brush_color = color

    def set_brush_size(self, size):
        """
        Set the size of the brush.
        :param size: Brush size in pixels
        """
        self.brush_size = size
        if self.nifti_data is not None:
            self.update_slice()

    def set_brush_color_value(self, color_value):
        """
        Set the color value of the brush.
        :param color_value: Integer for the brush (color) value
        """
        self.brush_color_value = color_value

    def wheelEvent(self, event):
        """
        Handle mouse wheel events.
        :param event: QWheelEvent object
        """
        if self.nifti_data is not None:
            num_slices = self.nifti_data.shape[2]
            delta = event.angleDelta().y() // 120

            new_index = self.current_slice_index + delta
            if 0 <= new_index < num_slices:
                self.current_slice_index = new_index
                self.update_slice()
                self.slice_changed.emit(self.current_slice_index)  # Emit slice_changed signal with new index

    def clear_all_segmentations(self):
        """
        Clear all segmentations and reset the segmentation matrix to zeros.
        """
        if self.segmentation_matrix is not None:
            self.segmentation_matrix.fill(0)

        self.render_cached_segmentation.cache_clear()  # Clear cached segmentation
        self.segmentation_image.fill(Qt.transparent)
        self.update_display()