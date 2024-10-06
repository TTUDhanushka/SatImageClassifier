# !/usr/bin/env python3
"""

"""
import sys
from PyQt6.QtWidgets import QApplication
from SatImageDownloader import SatImageDownloader, GeoPoint
from lat_lon_parser import parse
import pyproj
from gui import MainWindow

geod = pyproj.Geod(ellps='WGS84')

def get_euclidean_distance_in_meters(p1:GeoPoint, p2:GeoPoint) -> float:
    _, _, distance = geod.inv(p1.longitude, p1.latitude, p2.longitude, p2.latitude)

    return distance

def get_width_of_roi(p1:GeoPoint, p2:GeoPoint) -> float:
    width = get_euclidean_distance_in_meters()
    return width


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
