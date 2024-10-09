import os
# os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox --disable-gpu"

from datetime import datetime
from PyQt5.QtWebChannel import QWebChannel
import numpy as np
import sys
from PyQt5.QtCore import Qt, QDate, pyqtSlot, QUrl, QObject
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QLineEdit, QApplication, QDateEdit, \
    QGroupBox, QGridLayout
from SatImageDownloader import SatImageDownloader
from lat_lon_parser import parse
from geo_utils import GeoPoint, GeoCalcs
import json


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.meta_records = {}

        self.center_latitude = 58.2
        self.center_longitude = 22.2

        self.sat_image_resolution = 10.5
        self.coordinate_pairs = []

        self.setGeometry(50, 50, 1600, 900)
        self.setWindowTitle("Sat Image Downloader")

        self.sat_img = SatImageDownloader()
        self.sat_img.set_resolution(self.sat_image_resolution)

        self.meta_records.update({'resolution': self.sat_image_resolution})
        self.meta_records.update({'coordinates': self.coordinate_pairs})

        self.sat_image_query_start = datetime.today()
        self.sat_image_query_end = datetime.today()

        label_height = 30
        label_width = 180

        self.image_sat = np.zeros((480, 480), dtype=np.uint8)

        self.web_engine_view = QtWebEngineWidgets.QWebEngineView()
        self.web_engine_view.resize(480, 480)


        self.download_btn = QPushButton("Download")
        self.download_btn.setFixedSize(label_width, label_height)
        self.download_btn.clicked.connect(self.image_download_btn_callback)

        self.sat_image_holder =QLabel()

        self.image_preview_box = QGroupBox("Image preview")
        self.image_preview_box.setFixedSize(400, 400)
        self.preview_layout = QHBoxLayout()
        self.preview_layout.addWidget(self.sat_image_holder)
        self.image_preview_box.setLayout(self.preview_layout)

        group_box_title_font = QFont()
        group_box_title_font.setWeight(8)

        label_font = QFont()
        label_font.setWeight(14)

        geo_location_group = QGroupBox("Geo location")
        geo_location_group.setFont(group_box_title_font)
        geo_location_group.setFixedSize(400, 120)

        location_inputs_grid = QGridLayout()

        self.latitude_label = QLabel("Latitude")
        self.latitude_label.setFixedSize(label_width, label_height)

        self.geo_location_lat = QLineEdit()
        place_holder_lat = "58°16'21.29N"
        self.geo_location_lat.setPlaceholderText(place_holder_lat)
        self.geo_location_lat.textChanged.connect(self.geo_lat_changed_callback)
        self.geo_location_lat.setFixedSize(label_width, label_height)

        self.longitude_label = QLabel("Longitude")
        self.longitude_label.setFixedSize(label_width, label_height)

        self.geo_location_lon = QLineEdit()
        place_holder_lon = "22°13'58.72E"
        self.geo_location_lon.setPlaceholderText(place_holder_lon)
        self.geo_location_lon.textChanged.connect(self.geo_lon_changed_callback)
        self.geo_location_lon.setFixedSize(label_width, label_height)

        location_inputs_grid.addWidget(self.latitude_label, 0, 0)
        location_inputs_grid.addWidget(self.geo_location_lat, 0, 1)
        location_inputs_grid.addWidget(self.longitude_label, 1, 0)
        location_inputs_grid.addWidget(self.geo_location_lon, 1, 1)
        geo_location_group.setLayout(location_inputs_grid)


        # Channel receiver
        self.channel = QWebChannel(self.web_engine_view.page())
        self.pyqt_handler = CoordinateReceiver(self.geo_location_lat, self.geo_location_lon)
        self.channel.registerObject('pyObj', self.pyqt_handler)

        # Date range boxes
        date_range_group = QGroupBox("Date range")
        date_range_group.setFont(group_box_title_font)
        date_range_group.setFixedSize(400, 120)

        self.start_date_label = QLabel("From")
        self.start_date_label.setFont(label_font)
        self.start_date_label.setFixedSize(200, 30)
        self.start_date_cal = QDateEdit(calendarPopup=True)
        self.start_date_cal.setDate(QDate.currentDate())
        self.start_date_cal.setFont(label_font)
        self.start_date_cal.dateChanged.connect(self.start_date_changed_callback)

        self.end_date_label = QLabel("To")
        self.end_date_label.setFont(label_font)
        self.end_date_label.setFixedSize(200, 30)
        self.end_date_cal = QDateEdit(calendarPopup=True)
        self.end_date_cal.setDate(QDate.currentDate())
        self.end_date_cal.setFont(label_font)
        self.end_date_cal.dateChanged.connect(self.end_date_changed_callback)

        date_range_layout = QGridLayout()
        date_range_layout.addWidget(self.start_date_label, 0, 0)
        date_range_layout.addWidget(self.start_date_cal, 0, 1)

        date_range_layout.addWidget(self.end_date_label, 1, 0)
        date_range_layout.addWidget(self.end_date_cal, 1, 1)

        date_range_group.setLayout(date_range_layout)


        pixmap = QPixmap()
        pixmap.convertFromImage(
            QImage(self.image_sat.data, self.image_sat.shape[1], self.image_sat.shape[0], self.image_sat.strides[0], QImage.Format.Format_RGB888))

        self.sat_image_holder.setPixmap(pixmap)
        self.sat_image_holder.resize(100, 100)

        # Setup main layout
        self.image_preview_v_layout = QVBoxLayout()
        self.image_preview_v_layout.addWidget(geo_location_group)
        self.image_preview_v_layout.addWidget(date_range_group)
        self.image_preview_v_layout.addWidget(self.image_preview_box)
        self.image_preview_v_layout.addWidget(self.download_btn)


        # Update the map view
        self.update_map()

        # Generate the main layout of UI
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.web_engine_view)
        self.layout.addLayout(self.image_preview_v_layout)

        self.setLayout(self.layout)
        self.show()

    def update_map(self):
        abs_html_path = '/home/dhanushka/Developments/SatImageClassifier/leaflet_map.html'
        self.web_engine_view.setUrl(QUrl.fromLocalFile(os.path.abspath(abs_html_path )))
        self.web_engine_view.page().setWebChannel(self.channel)

    def update_preview(self, image):
        pixmap = QPixmap()
        pixmap.convertFromImage(
            QImage(self.image_sat.data, self.image_sat.shape[1], self.image_sat.shape[0], self.image_sat.strides[0], QImage.Format.Format_RGB888))

        self.sat_image_holder.setPixmap(pixmap)

    def geo_lon_changed_callback(self, text):
    #     updated_coordinate = parse(text)
    #     self.center_longitude = updated_coordinate
    #     self.update_map()
        self.get_roi_coordinates()

    def geo_lat_changed_callback(self, text):
    #     updated_coordinate = parse(text)
    #     self.center_latitude = updated_coordinate
    #     self.update_map()
        self.get_roi_coordinates()

    def end_date_changed_callback(self, date):
        self.sat_image_query_end = date.toString('yyyy-MM-dd')
        self.sat_img.set_date_range(self.sat_image_query_start, self.sat_image_query_end)

    def start_date_changed_callback(self, date):
        self.sat_image_query_start = date.toString('yyyy-MM-dd')
        self.sat_img.set_date_range(self.sat_image_query_start, self.sat_image_query_end)

    def get_roi_coordinates(self):
        self.current_lat = 0
        self.current_lng = 0

        if self.geo_location_lat.text() != "":
            self.current_lat  = float(self.geo_location_lat.text())

        if self.geo_location_lon.text() != "":
            self.current_lng = float(self.geo_location_lon.text())

        if abs(self.current_lng) > 0 and abs(self.current_lat) > 0:
            center_point = GeoPoint(self.current_lat , self.current_lng)

            # Get the next geo coordinates pair in 5632 meters.
            _, top_left_lat, _ = GeoCalcs.get_next_coords_in_a_distance(center_point, 0, 2785)
            _, btm_right_lat, _ = GeoCalcs.get_next_coords_in_a_distance(center_point, 180, 2785)

            top_left_lon, _, _ = GeoCalcs.get_next_coords_in_a_distance(center_point, 90, 2900)
            btm_right_lon, _, _ = GeoCalcs.get_next_coords_in_a_distance(center_point, 270, 2900)

            self.top_left_roi = GeoPoint(top_left_lat, top_left_lon)
            self.btm_right_roi = GeoPoint(btm_right_lat, btm_right_lon)

    def image_download_btn_callback(self):
        _ = self.sat_img.download_image_data(self.top_left_roi, self.btm_right_roi)

        self.image_sat = self.sat_img.download_preview_thumbnail(self.top_left_roi, self.btm_right_roi)
        self.update_preview(self.image_sat )

        coordinates = [self.current_lat, self.current_lng]
        self.coordinate_pairs.append(coordinates)

        metadata_obj = json.dumps(self.meta_records)

        with open("metadata.json", "w") as outfile:
            outfile.write(metadata_obj)

class CoordinateReceiver(QObject):
    def __init__(self, label_lat, label_lon):
        super().__init__()

        self.label_lat = label_lat
        self.label_lon = label_lon

    @pyqtSlot(str, str)
    def updateCoordinates(self, lat, lng):
        self.label_lat.setText(f"{lat}")
        self.label_lon.setText(f"{lng}")

def run_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
