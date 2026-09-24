import sys
import cv2
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QFileDialog, QVBoxLayout, QWidget
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CV Lab 1 - Image Viewer")
        self.resize(720, 640)

        self.image_bgr = None        # original image loaded via OpenCV (BGR)
        self.display_buffer = None   # keeps a reference alive for QImage
        self.is_gray = False

        # --- Widgets ---
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setStyleSheet("border: 1px solid gray;")

        self.open_button = QPushButton("Open Image")
        self.toggle_button = QPushButton("Toggle Grayscale / Color")
        self.toggle_button.setEnabled(False)

        self.open_button.clicked.connect(self.open_image)
        self.toggle_button.clicked.connect(self.toggle_grayscale)

        # --- Layout ---
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.open_button)
        layout.addWidget(self.toggle_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )
        if not file_path:
            return

        image = cv2.imread(file_path)
        if image is None:
            self.image_label.setText("Failed to load image.")
            return

        self.image_bgr = image
        self.is_gray = False
        self.toggle_button.setEnabled(True)
        self.render_image(self.image_bgr)

    def toggle_grayscale(self):
        if self.image_bgr is None:
            return

        self.is_gray = not self.is_gray
        if self.is_gray:
            gray = cv2.cvtColor(self.image_bgr, cv2.COLOR_BGR2GRAY)
            self.render_image(gray)
        else:
            self.render_image(self.image_bgr)

    def render_image(self, cv_image):
        """Convert an OpenCV (NumPy) image to QPixmap and show it in the label."""
        if cv_image.ndim == 2:
            # Grayscale image
            self.display_buffer = cv_image.copy()  # keep a live reference
            h, w = self.display_buffer.shape
            bytes_per_line = w
            qimg = QImage(
                self.display_buffer.data, w, h, bytes_per_line,
                QImage.Format_Grayscale8
            )

        else:
            # Color image: convert BGR -> RGB for correct display
            self.display_buffer = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            h, w, ch = self.display_buffer.shape
            bytes_per_line = ch * w
            qimg = QImage(
                self.display_buffer.data, w, h, bytes_per_line,
                QImage.Format_RGB888
            )

        pixmap = QPixmap.fromImage(qimg)
        pixmap = pixmap.scaled(
            self.image_label.width(), self.image_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageViewer()
    window.show()
    sys.exit(app.exec())
