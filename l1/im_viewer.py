import sys
import cv2
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QFileDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QSlider, QScrollArea
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CV Lab 1 - Interactive Image Viewer")
        self.resize(1024, 768)

        self.image_bgr = None
        self.display_buffer = None

        # --- Widgets ---
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #222; color: white;")
        
        # Place the label inside a QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_label)
        # Prevent the scroll area from resizing the widget to its own size,
        # which allows the scrollbars to appear when the image gets large.
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignCenter)

        self.open_button = QPushButton("Open Image")
        self.open_button.clicked.connect(self.open_image)

        # Scale slider (10% to 200%)
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(10, 200)
        self.scale_slider.setValue(100)
        self.scale_label = QLabel("Scale: 100%")
        self.scale_label.setMinimumWidth(90)
        
        # Rotate slider (0° to 360°)
        self.rotate_slider = QSlider(Qt.Horizontal)
        self.rotate_slider.setRange(0, 360)
        self.rotate_slider.setValue(0)
        self.rotate_label = QLabel("Rotate: 0°")
        self.rotate_label.setMinimumWidth(90)
        
        # Flip buttons
        self.flip_h_btn = QPushButton("Flip Horizontal")
        self.flip_v_btn = QPushButton("Flip Vertical")
        self.flip_h_btn.setCheckable(True)
        self.flip_v_btn.setCheckable(True)

        # Connect signals
        self.scale_slider.valueChanged.connect(self.on_transform_changed)
        self.rotate_slider.valueChanged.connect(self.on_transform_changed)
        self.flip_h_btn.clicked.connect(self.on_transform_changed)
        self.flip_v_btn.clicked.connect(self.on_transform_changed)

        # Disable transform controls until an image is loaded
        self.set_controls_enabled(False)

        # --- Layout ---
        control_layout = QVBoxLayout()
        
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(self.scale_label)
        scale_layout.addWidget(self.scale_slider)
        
        rotate_layout = QHBoxLayout()
        rotate_layout.addWidget(self.rotate_label)
        rotate_layout.addWidget(self.rotate_slider)
        
        flip_layout = QHBoxLayout()
        flip_layout.addWidget(self.flip_h_btn)
        flip_layout.addWidget(self.flip_v_btn)
        
        control_layout.addWidget(self.open_button)
        control_layout.addLayout(scale_layout)
        control_layout.addLayout(rotate_layout)
        control_layout.addLayout(flip_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.scroll_area, stretch=1)
        main_layout.addLayout(control_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def set_controls_enabled(self, enabled):
        self.scale_slider.setEnabled(enabled)
        self.rotate_slider.setEnabled(enabled)
        self.flip_h_btn.setEnabled(enabled)
        self.flip_v_btn.setEnabled(enabled)

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
            self.image_label.resize(self.image_label.sizeHint())
            return

        self.image_bgr = image
        self.set_controls_enabled(True)
        
        # Reset controls to default state for the new image
        self.scale_slider.blockSignals(True)
        self.rotate_slider.blockSignals(True)
        self.flip_h_btn.blockSignals(True)
        self.flip_v_btn.blockSignals(True)
        
        self.scale_slider.setValue(100)
        self.rotate_slider.setValue(0)
        self.flip_h_btn.setChecked(False)
        self.flip_v_btn.setChecked(False)
        self.scale_label.setText("Scale: 100%")
        self.rotate_label.setText("Rotate: 0°")
        
        self.scale_slider.blockSignals(False)
        self.rotate_slider.blockSignals(False)
        self.flip_h_btn.blockSignals(False)
        self.flip_v_btn.blockSignals(False)
        
        self.apply_transforms()

    def on_transform_changed(self):
        """Update labels and trigger a re-render when a slider or button is adjusted."""
        scale_val = self.scale_slider.value()
        rotate_val = self.rotate_slider.value()
        
        self.scale_label.setText(f"Scale: {scale_val}%")
        self.rotate_label.setText(f"Rotate: {rotate_val}°")
        
        self.apply_transforms()

    def apply_transforms(self):
        """
        Reads all current control states and applies them strictly to a 
        fresh copy of the original image, so degradations do not compound.
        """
        if self.image_bgr is None:
            return
            
        img = self.image_bgr.copy()
        
        # 1. Flip
        flip_h = self.flip_h_btn.isChecked()
        flip_v = self.flip_v_btn.isChecked()
        
        if flip_h and flip_v:
            img = cv2.flip(img, -1)
        elif flip_h:
            img = cv2.flip(img, 1)
        elif flip_v:
            img = cv2.flip(img, 0)
            
        # 2. Scale
        scale_factor = self.scale_slider.value() / 100.0
        if scale_factor != 1.0:
            interpolation = cv2.INTER_LINEAR if scale_factor > 1.0 else cv2.INTER_AREA
            img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=interpolation)
            
        # 3. Rotate (Unclipped)
        angle = self.rotate_slider.value()
        if angle != 0:
            (h, w) = img.shape[:2]
            (cX, cY) = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
            
            cos = abs(M[0, 0])
            sin = abs(M[0, 1])
            new_w = int((h * sin) + (w * cos))
            new_h = int((h * cos) + (w * sin))
            
            M[0, 2] += (new_w / 2) - cX
            M[1, 2] += (new_h / 2) - cY
            
            img = cv2.warpAffine(img, M, (new_w, new_h))
            
        self.render_image(img)

    def render_image(self, cv_image):
        """Convert an OpenCV image to a QPixmap and show it in the label at true size."""
        if cv_image.ndim == 2:
            self.display_buffer = cv_image.copy()
            h, w = self.display_buffer.shape
            bytes_per_line = w
            qimg = QImage(
                self.display_buffer.data, w, h, bytes_per_line,
                QImage.Format_Grayscale8
            )
        else:
            self.display_buffer = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            h, w, ch = self.display_buffer.shape
            bytes_per_line = ch * w
            qimg = QImage(
                self.display_buffer.data, w, h, bytes_per_line,
                QImage.Format_RGB888
            )

        pixmap = QPixmap.fromImage(qimg)
        self.image_label.setPixmap(pixmap)
        
        # Crucial for QScrollArea with setWidgetResizable(False):
        # We must manually resize the widget to match the pixmap's size.
        self.image_label.resize(pixmap.size())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageViewer()
    window.show()
    sys.exit(app.exec())
