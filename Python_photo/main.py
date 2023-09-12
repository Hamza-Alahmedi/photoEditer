from PyQt5.QtWidgets import *
import cv2
from PyQt5 import uic
from PyQt5.QtGui import QImage, QPixmap, QPen, QMouseEvent, QPainter
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter
import filters
import numpy as np


class MyGUI(QMainWindow):
    def __init__(self):
        super(MyGUI, self).__init__()
        uic.loadUi("MyUI.ui", self)
        self.setWindowTitle("Photo Editer Program")
        self.show()

        self.original_label = self.findChild(QLabel, "original_label")

        ######
        ## ########
        self.drawing = False
        self.last_point = QPoint()
        ## ########
        ## ########
        self._x = 0
        self._y = 0
        ## ########
        self.last_x = None
        self.last_y = None
        self.text = None
        self.color = None
        self.font_ = None
        self.fontface = None

        # Find the QAction for loading image
        self.action_load_image = self.findChild(QAction, "actionload_image")
        self.brightness_slider = self.findChild(QSlider, "horizontalSlider_2")
        self.blur_slider = self.findChild(QSlider, "horizontalSlider")
        self.save_action = self.findChild(QAction, "actionSave_")
        self.save_action.setShortcut("Crtl+s")

        self.median_filter_radio = self.findChild(QRadioButton, "radioButton_14")
        self.bilateral_filter_radio = self.findChild(QRadioButton, "radioButton_18")
        self.Gaussian_filter_radio = self.findChild(QRadioButton, "radioButton_13")
        self.filter4 = self.findChild(QRadioButton, "radioButton_15")
        self.filter5 = self.findChild(QRadioButton, "radioButton_16")
        self.filter6 = self.findChild(QRadioButton, "radioButton_17")
        self.no_filter = self.findChild(QRadioButton, "noFilterRadio")
        self.no_filter.setChecked(True)

        self.undo_action = self.findChild(QAction, "actionUndu")
        self.draw_button = self.findChild(QPushButton, "drawButton")
        self.addtxt_button = self.findChild(QPushButton, "addtxtButton")
        self.crop_button = self.findChild(QPushButton, "cropbutton")
        self.left_button = self.findChild(QPushButton, "leftbtn")
        self.right_button = self.findChild(QPushButton, "rightbtn")

        # draw_button.clicked.connect(self.draw)
        self.addtxt_button.clicked.connect(self.addText)
        self.crop_button.clicked.connect(self.cropImage)
        self.left_button.clicked.connect(self.turnLeft)
        self.right_button.clicked.connect(self.turnRight)

        self.undo_action.setShortcut("Ctrl+Z")

        # Connect the action to the load_image method
        self.action_load_image.setShortcut("Ctrl+o")
        self.action_load_image.triggered.connect(self.load_image)
        # connect blur slider to method
        self.blur_slider.valueChanged.connect(self.change_blur)
        # connect radio buttons to methods
        self.median_filter_radio.toggled.connect(self.update_filter)
        self.bilateral_filter_radio.toggled.connect(self.update_filter)
        self.Gaussian_filter_radio.toggled.connect(self.update_filter)
        self.filter4.toggled.connect(self.update_filter)
        self.filter5.toggled.connect(self.update_filter)
        self.filter6.toggled.connect(self.update_filter)
        self.no_filter.toggled.connect(self.update_filter)
        # connect slider to method
        self.filter_slider = self.findChild(QSlider, "filterProp1_slider_2")
        self.filter_slider.valueChanged.connect(self.adjust_filter)

        self.filter_slider.setTickInterval(2)
        # Initialize parameters for image changes
        self.brightness = 0
        self.blur = 0
        self.filter_value = 0
        self.modified_image = None
        self.selected_filter = None
        self.base_image = None
        # connect the undo with method
        self.undo_action.triggered.connect(self.undo)

        # Connect the slider to the brightness_change method
        self.brightness_slider.setMinimum(-100)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setTickInterval(10)
        self.brightness_slider.setTickPosition(QSlider.TicksBelow)
        self.brightness_slider.valueChanged.connect(self.brightness_change)

    ######################################
    def cropImage(self):
        if self.modified_image is not None:
            roi = cv2.selectROI(
                "Crop Image", self.modified_image, fromCenter=False, showCrosshair=False
            )
            if all(roi):
                x, y, w, h = roi
                cropped = self.modified_image[y : y + h, x : x + w]
                self.modified_image = cropped.copy()
                self.image_with_filters = (
                    cropped.copy()
                )  # Update the image copy for filters
                self.display_image()
                self.apply_filter()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            text, ok = QInputDialog.getText(self, "Text Input", "Enter some text:")
            if ok and self.modified_image is not None:
                color = QColorDialog.getColor()
                if color.isValid():
                    red = color.red()
                    green = color.green()
                    blue = color.blue()
                    font, ok = QFontDialog.getFont()
                    if ok:
                        font_size = font.pointSize() / 10
                        fontface = cv2.FONT_HERSHEY_SIMPLEX

                        x = event.pos().x()
                        y = event.pos().y()

                        cv2.putText(
                            self.modified_image,
                            text,
                            (x, y),
                            fontface,
                            font_size,
                            (red, green, blue),
                            2,
                        )

                        self.display_image()

    def addText(self):
        try:
            if self.modified_image is not None:
                cv2.setMouseCallback("image", self.mousePressEvent)
                self.apply_filter()
        except Exception as e:
            pass

    def load_image(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_path:
            try:
                self.base_image = cv2.imread(file_path)  # Original unaltered image
                self.image_with_filters = (
                    self.base_image.copy()
                )  # Image copy for applying filters
                self.modified_image = (
                    self.base_image.copy()
                )  # Image copy for displaying modifications
                self.original_path = file_path
                self.display_image()
            except Exception as e:
                print(e)

    def test(self):
        print("changed")

    def brightness_change(self, value):
        brightness = value / 100.0
        try:
            # Add weighted does the actual job of changing the brightness level
            # Need to convert to same data type for this operation
            self.modified_image = cv2.addWeighted(
                self.base_image.astype(float),
                1.0 + brightness,
                self.modified_image.astype(float),
                0,
                0,
            )
            # Clip the values to [0, 255] and change it back to uint8
            self.modified_image = np.clip(self.modified_image, 0, 255).astype("uint8")
            self.image_with_filters = self.modified_image.copy()
            # Apply the selected filter (if any)
            self.apply_filter()
            # Display the modified image
            self.display_image()
        except Exception as e:
            print("Error:", e)

    def change_blur(self, value):
        min_blur = 0.1
        max_blur = 5.0

        blur_value = max(min(value / 10.0, max_blur), min_blur)

        try:
            # Apply blur to modified_image only
            self.modified_image = cv2.GaussianBlur(self.base_image, (0, 0), blur_value)
            # Call apply_filter here if you want to reapply filter after changing blur
            self.image_with_filters = self.modified_image.copy()
            self.apply_filter()
            self.display_image()
        except Exception as e:
            print("Error:", e)

    def display_image(self, image=None):
        if image is None:
            image = self.modified_image

        modified_image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(
            modified_image_rgb, width, height, bytes_per_line, QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(q_image)
        self.original_label.setPixmap(pixmap)
        ############################

    def undo(self):
        if self.original_path:
            confirmation = QMessageBox.question(
                self,
                "Undo Confirmation",
                "Are you sure you want to undo all changes?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if confirmation == QMessageBox.Yes:
                self.modified_image = cv2.imread(self.original_path)
                self.display_image()

    def turnLeft(self):
        if self.modified_image is not None:
            self.modified_image = cv2.rotate(
                self.modified_image, cv2.ROTATE_90_COUNTERCLOCKWISE
            )
            self.image_with_filters = self.modified_image.copy()
            self.apply_filter()
            self.display_image()

    def turnRight(self):
        if self.modified_image is not None:
            self.modified_image = cv2.rotate(
                self.modified_image, cv2.ROTATE_90_CLOCKWISE
            )
            self.image_with_filters = self.modified_image.copy()
            self.apply_filter()
            self.display_image()

    #########################

    def update_filter(self):
        try:
            if self.median_filter_radio.isChecked():
                self.selected_filter = "Median"
            elif self.bilateral_filter_radio.isChecked():
                self.selected_filter = "GreyScale"
            elif self.Gaussian_filter_radio.isChecked():
                self.selected_filter = "Cold"
            elif self.filter4.isChecked():
                self.selected_filter = "Laplacian"
            elif self.filter5.isChecked():
                self.selected_filter = "Sobal"
            elif self.filter6.isChecked():
                self.selected_filter = "Warm"
            elif self.no_filter.isChecked():
                self.selected_filter = None
            else:
                self.selected_filter = None
            self.apply_filter()
        except Exception as e:
            print("Error:", e)

    def adjust_filter(self, value):
        # Set the minimum and maximum filter sizes
        min_filter_size = 3
        max_filter_size = 99

        # Ensure value is odd
        if value % 2 == 0:
            value += 1

        # Clamp the value within the specified range
        filter_size = max(min(value, max_filter_size), min_filter_size)

        # Update the filter value
        self.filter_value = filter_size

        # Apply the updated filter
        self.apply_filter()

    def apply_filter(self):
        self.modified_image = self.image_with_filters.copy()

        if self.selected_filter == "Median":
            self.modified_image = filters.median_filter(
                self.modified_image, self.filter_value
            )
        elif self.selected_filter == "GreyScale":
            self.modified_image = filters.dark_colors_filter(self.modified_image)

        elif self.selected_filter == "Cold":
            self.modified_image = filters.cold_filter(
                self.modified_image, self.filter_value
            )
        elif self.selected_filter == "Laplacian":
            self.modified_image = filters.increase_contrast(
                self.modified_image, self.filter_value
            )
        elif self.selected_filter == "Sobal":
            self.modified_image = filters.sobel_filter(self.modified_image)
        elif self.selected_filter == "Warm":
            self.modified_image = filters.warm_filter(
                self.modified_image, self.filter_value
            )

        self.display_image()


def main():
    app = QApplication([])
    window = MyGUI()
    app.exec_()


if __name__ == "__main__":
    main()
