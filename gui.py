import os
os.environ["XDG_SESSION_TYPE"] = "xcb"
import numpy as np
import io
import sys
import folium
from PyQt6 import QtWebEngineWidgets
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QLineEdit
from SatImageDownloader import SatImageDownloader, GeoPoint
from lat_lon_parser import parse


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.center_latitude = 58.2
        self.center_longitude = 22.2

        self.setGeometry(50, 50, 1600, 900)
        self.setWindowTitle("Sat Image Downloader")

        map_request = folium.Map(
            location=[self.center_latitude, self.center_longitude],
            zoom_start=5
        )

        self.sat_img = SatImageDownloader()
        self.sat_img.set_resolution(60)

        label_height = 30
        label_width = 180

        self.image_sat = np.zeros((640, 480), dtype=np.uint8)

        data = io.BytesIO()
        map_request.save(data, close_file=False)

        web_engine_view = QtWebEngineWidgets.QWebEngineView()
        web_engine_view.setHtml(data.getvalue().decode())
        web_engine_view.resize(640, 480)

        self.download_btn = QPushButton("Download")
        self.download_btn.setFixedSize(label_width, label_height)
        self.download_btn.clicked.connect(self.download_btn_callback)

        self.sat_image_holder =QLabel()

        self.geo_location_label = QLabel("Geo location")
        self.geo_location_label.setFixedSize(label_width, label_height)

        self.latitude_label = QLabel("Latitude")
        self.latitude_label.setFixedSize(label_width, label_height)

        self.geo_location_lat = QLineEdit()
        place_holder_lat = "58°16'21.29N"
        self.geo_location_lat.setPlaceholderText(place_holder_lat)
        self.geo_location_lat.setFixedSize(label_width, label_height)

        self.longitude_label = QLabel("Longitude")
        self.longitude_label.setFixedSize(label_width, label_height)

        self.geo_location_lon = QLineEdit()
        place_holder_lon = "22°13'58.72E"
        self.geo_location_lon.setPlaceholderText(place_holder_lon)
        self.geo_location_lon.textChanged.connect(self.geo_lon_changed_callback)
        self.geo_location_lon.setFixedSize(label_width, label_height)

        pixmap = QPixmap()
        pixmap.convertFromImage(
            QImage(self.image_sat.data, self.image_sat.shape[1], self.image_sat.shape[0], self.image_sat.strides[0], QImage.Format.Format_RGB888))

        self.sat_image_holder.setPixmap(pixmap)
        self.sat_image_holder.resize(100, 100)


        # Setup main layout
        self.image_preview_v_layout = QVBoxLayout()

        self.image_preview_v_layout.addWidget(self.geo_location_label)

        self.latitude_layout = QHBoxLayout()
        self.latitude_layout.addWidget(self.latitude_label)
        self.latitude_layout.addWidget(self.geo_location_lat)
        self.image_preview_v_layout.addLayout(self.latitude_layout)

        self.longitude_layout = QHBoxLayout()
        self.longitude_layout.addWidget(self.longitude_label)
        self.longitude_layout.addWidget(self.geo_location_lon)

        self.image_preview_v_layout.addLayout(self.longitude_layout)

        self.image_preview_v_layout.addWidget(self.sat_image_holder)
        self.image_preview_v_layout.addWidget(self.download_btn)

        self.layout = QHBoxLayout()
        self.layout.addWidget(web_engine_view)
        self.layout.addLayout(self.image_preview_v_layout)


        self.setLayout(self.layout)
        self.show()

    def update_preview(self, image):
        pixmap = QPixmap()
        pixmap.convertFromImage(
            QImage(self.image_sat.data, self.image_sat.shape[1], self.image_sat.shape[0], self.image_sat.strides[0], QImage.Format.Format_RGB888))

        self.sat_image_holder.setPixmap(pixmap)

    def geo_lon_changed_callback(self, text):
        updated_coordinate = parse(text)
        self.center_longitude = updated_coordinate
        print(f"{updated_coordinate}")

    def download_btn_callback(self):
        print(f"Clicked")

        dec_p1_lon = parse("22°13'58.72E")
        dec_p1_lat = parse("58°16'21.29N")

        p1 = GeoPoint(dec_p1_lat, dec_p1_lon)

        dec_p2_lon = parse("22°39'54.73E")
        dec_p2_lat = parse("58° 8'6.75N")

        p2 = GeoPoint(dec_p2_lat, dec_p2_lon)

        self.image_sat = self.sat_img.download_image_data(p1, p2)
        self.update_preview(self.image_sat )
