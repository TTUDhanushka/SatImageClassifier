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



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.center_latitude = 58.2
        self.center_longitude = 22.2

        self.setGeometry(50, 50, 1600, 900)
        self.setWindowTitle("Sat Image Downloader")

        self.sat_img = SatImageDownloader()
        self.sat_img.set_resolution(11)

        self.sat_image_query_start = datetime.today()
        self.sat_image_query_end = datetime.today()

        label_height = 30
        label_width = 180

        self.image_sat = np.zeros((640, 480), dtype=np.uint8)

        self.web_engine_view = QtWebEngineWidgets.QWebEngineView()
        self.web_engine_view.resize(640, 480)




        self.mouse_coord = QLabel()

        # Channel receiver
        self.channel = QWebChannel(self.web_engine_view.page())
        self.pyqt_handler = CoordinateReceiver(self.mouse_coord)
        self.channel.registerObject('pyObj', self.pyqt_handler)


        self.calc_width_btn = QPushButton("Get Width")
        self.calc_width_btn.setFixedSize(label_width, label_height)
        self.calc_width_btn.clicked.connect(self.calc_width_btn_callback)

        self.download_btn = QPushButton("Download")
        self.download_btn.setFixedSize(label_width, label_height)
        self.download_btn.clicked.connect(self.image_download_btn_callback)

        self.sat_image_holder =QLabel()

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
        self.image_preview_v_layout.addWidget(self.mouse_coord)
        self.image_preview_v_layout.addWidget(self.calc_width_btn)
        self.image_preview_v_layout.addWidget(self.download_btn)

        self.image_preview_v_layout.addWidget(self.sat_image_holder)


        # Update the map view
        self.update_map()

        # Generate the main layout of UI
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.web_engine_view)
        self.layout.addLayout(self.image_preview_v_layout)

        self.setLayout(self.layout)
        self.show()

    def update_map(self):
        # self.map_request = folium.Map(
        #     location=[self.center_latitude, self.center_longitude],
        #     zoom_start=10
        # )
        #
        # data = io.BytesIO()
        # self.map_request.save(data, close_file=False)
        #
        # self.web_engine_view.setHtml(data.getvalue().decode())

        abs_html_path = '/home/dhanushka/Developments/SatImageClassifier/leaflet_map.html'

        if os.path.exists(abs_html_path):
            print(f"file exists")
        else:
            print(f"File not exist")

        self.web_engine_view.setUrl(QUrl.fromLocalFile(os.path.abspath(abs_html_path )))
        # self.web_engine_view.setHtml(abs_html_path)
        self.web_engine_view.page().setWebChannel(self.channel)

    def update_preview(self, image):
        pixmap = QPixmap()
        pixmap.convertFromImage(
            QImage(self.image_sat.data, self.image_sat.shape[1], self.image_sat.shape[0], self.image_sat.strides[0], QImage.Format.Format_RGB888))

        self.sat_image_holder.setPixmap(pixmap)

    def geo_lon_changed_callback(self, text):
        updated_coordinate = parse(text)
        self.center_longitude = updated_coordinate
        self.update_map()

    def geo_lat_changed_callback(self, text):
        updated_coordinate = parse(text)
        self.center_latitude = updated_coordinate
        self.update_map()

    def end_date_changed_callback(self, date):
        self.sat_image_query_end = date.toString('yyyy-MM-dd')
        self.sat_img.set_date_range(self.sat_image_query_start, self.sat_image_query_end)

    def start_date_changed_callback(self, date):
        self.sat_image_query_start = date.toString('yyyy-MM-dd')
        self.sat_img.set_date_range(self.sat_image_query_start, self.sat_image_query_end)

    def calc_width_btn_callback(self):
        width = GeoCalcs.get_avg_width_of_roi(self.p1, self.p2)
        # print(f"Width in meters {width}")

        # Get the next geo coordinates pair in 7680 meters.
        coord = GeoCalcs.get_next_coords_in_a_distance(self.p1, 0, 7680)
        print(f"Coordinates pair {coord}")

    def image_download_btn_callback(self):

        # TODO 512px x 512 px images should be generated from the geo map. Max resolution is 11m per pixel. which represents 5632 m.


        dec_p1_lon = parse("22°13'58.72E")
        dec_p1_lat = parse("58°16'21.29N")

        self.p1 = GeoPoint(dec_p1_lat, dec_p1_lon)

        dec_p2_lon = parse("22°39'54.73E")
        dec_p2_lat = parse("58° 8'6.75N")

        self.p2 = GeoPoint(dec_p2_lat, dec_p2_lon)

        _ = self.sat_img.download_image_data(self.p1, self.p2)

        self.image_sat = self.sat_img.download_preview_thumbnail(self.p1, self.p2)

        self.update_preview(self.image_sat )


class CoordinateReceiver(QObject):
    def __init__(self, label):
        super().__init__()

        self.label = label

    @pyqtSlot(str, str)
    def updateCoordinates(self, lat, lng):
        # print(f"Coordinates: {lat}, {lng}")
        self.label.setText(f"Coordinates: {lat}, {lng}")

def run_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
