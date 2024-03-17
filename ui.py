#!/usr/bin/env python

from PySide6.QtCore import Qt, Slot, QSize, QTimer
from PySide6.QtWidgets import (QWidget, QApplication, QLabel, QPushButton, QVBoxLayout)
from PySide6.QtGui import QImage, QPixmap
import cv2
import sys

class MainApp(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.video_size = QSize(1024, 768)
        self.setup_ui()
        self.setup_camera()
        self.rotation = 0

    def setup_ui(self):
        """Initialize widgets.
        """
        self.image_label = QLabel()
        self.image_label.setFixedSize(self.video_size)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)

        self.rotate_button = QPushButton("Rotate")
        self.rotate_button.clicked.connect(self.rotate)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.image_label)
        self.main_layout.addWidget(self.quit_button)
        self.main_layout.addWidget(self.rotate_button)

        self.setLayout(self.main_layout)

    def setup_camera(self):
        """Initialize camera.
        """
        self.capture = cv2.VideoCapture(0)
        
        self.timer = QTimer()
        # attach a periodic timer (30 ms) with callback to update video stream
        self.timer.timeout.connect(self.display_video_stream)
        self.timer.start(30)

    def display_video_stream(self):
        """Read frame from camera and repaint QLabel widget.
        """
        _, self.frame = self.capture.read()
        
        # rotate if needed
        columns = self.video_size.width()
        rows = self.video_size.height()
        
        # set the rotation coordinate to the center of the image
        M = cv2.getRotationMatrix2D(((columns-1)/2.0,(rows-1)/2.0), self.rotation,1)
        self.frame = cv2.warpAffine(self.frame,M,(self.video_size.width(),self.video_size.height()))
        
        # convert to RGB image
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        image = QImage(self.frame, self.frame.shape[1], self.frame.shape[0], 
                       self.frame.strides[0], QImage.Format_RGB888)
        
        # scale image to fit QLabel
        image.scaled(self.video_size, Qt.KeepAspectRatio)
        self.image_label.setPixmap(QPixmap.fromImage(image))

    @Slot()
    def rotate(self):
        """Rotate video streamm, the image rotation happens in the display video stream
        """
        self.rotation = self.rotation + 90
        if self.rotation == 360:
            self.rotation = 0
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainApp()
    win.show()
    sys.exit(app.exec_())