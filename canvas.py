# canvas.py
import numpy as np
import nibabel as nib
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QPixmap, QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QLabel

from segmentation import update_annotation_matrix, render_annotation_from_matrix

class Canvas(QLabel):
    def __init__(self, width, height):
        super().__init__()
        self.background_image = QImage(width, height, QImage.Format_ARGB32)
        self.background_image.fill(Qt.white)
        self.annotation_image = QImage(width, height, QImage.Format_ARGB32)
        self.annotation_image.fill(Qt.transparent)
        self.pen_color = QColor(255, 0, 0, 128)  # Semi-transparent red
        self.brush_size = 10
        self.setPixmap(QPixmap.fromImage(self.background_image))
        self.last_point = QPoint()
        self.drawing = False
        self.setAcceptDrops(True)
        self.nifti_data = None
        self.nifti_header = None
        self.current_slice_index = 0
        self.annotation_matrix = None

    def set_pen_color(self, color):
        self.pen_color = color

    def set_brush_size(self, size):
        self.brush_size = size

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_point = event.pos()
            self.drawing = True
            self.draw_on_canvas(event.pos())
            update_annotation_matrix(self.annotation_matrix, self.last_point, event.pos(), self.brush_size, self.background_image, self.current_slice_index)
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drawing:
            self.draw_on_canvas(event.pos())
            update_annotation_matrix(self.annotation_matrix, self.last_point, event.pos(), self.brush_size, self.background_image, self.current_slice_index)
            self.last_point = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def draw_on_canvas(self, pos):
        """
        Draw directly on the canvas to ensure interactive updating.
        
        :param pos: The current mouse position where drawing occurs.
        """
        canvas_pixmap = self.pixmap().copy()
        painter = QPainter(canvas_pixmap)
        pen = QPen(self.pen_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(self.last_point, pos)
        painter.end()

        self.setPixmap(canvas_pixmap)  # Update the QLabel's pixmap

    def wheelEvent(self, event):
        if self.nifti_data is not None:
            num_slices = self.nifti_data.shape[2]
            delta = event.angleDelta().y() // 120

            new_index = self.current_slice_index + delta
            if 0 <= new_index < num_slices:
                self.current_slice_index = new_index
                self.update_slice()

    def update_slice(self):
        slice_data = self.nifti_data[:, :, self.current_slice_index]
        normalized_data = 255 * (slice_data - np.min(slice_data)) / (np.max(slice_data) - np.min(slice_data))
        normalized_data = normalized_data.astype(np.uint8)
        height, width = normalized_data.shape
        bytes_per_line = width
        qimage = QImage(normalized_data.tobytes(), width, height, bytes_per_line, QImage.Format_Grayscale8)
        self.background_image = qimage.scaled(self.background_image.width(), self.background_image.height())
        self.annotation_image.fill(Qt.transparent)
        render_annotation_from_matrix(self.annotation_image, self.annotation_matrix, self.pen_color, self.brush_size, self.current_slice_index)
        self.update_display()

    def update_display(self):
        combined_image = QImage(self.background_image.size(), QImage.Format_ARGB32)
        combined_image.fill(Qt.transparent)

        with QPainter(combined_image) as painter:
            painter.drawImage(0, 0, self.background_image)
            painter.drawImage(0, 0, self.annotation_image)

        self.setPixmap(QPixmap.fromImage(combined_image))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(('.nii', '.nii.gz')):
                self.set_background_image_from_nifti(file_path)
            break

    def set_background_image_from_nifti(self, file_path):
        nifti_img = nib.load(file_path)
        self.nifti_data = nifti_img.get_fdata()
        self.nifti_header = nifti_img.header
        self.annotation_matrix = np.zeros_like(self.nifti_data)
        self.current_slice_index = self.nifti_data.shape[2] // 2
        self.update_slice()

    def save_annotation_nifti(self, file_path):
        if self.annotation_matrix is not None and self.nifti_header is not None:
            annotation_img = nib.Nifti1Image(self.annotation_matrix, affine=np.eye(4), header=self.nifti_header)
            nib.save(annotation_img, file_path)
