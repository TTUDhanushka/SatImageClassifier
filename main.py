# !/usr/bin/env python3
"""

"""
from SatImageDownloader import SatImageDownloader, GeoPoint
from lat_lon_parser import parse
import pyproj

geod = pyproj.Geod(ellps='WGS84')

def get_euclidean_distance_in_meters(p1:GeoPoint, p2:GeoPoint) -> float:
    _, _, distance = geod.inv(p1.longitude, p1.latitude, p2.longitude, p2.latitude)

    return distance

def get_width_of_roi(p1:GeoPoint, p2:GeoPoint) -> float:
    width = get_euclidean_distance_in_meters()
    return width

def main():
    url = ''
    path = '/home/dhanushka/Datasets/SatImages'

    dec_p1_lon = parse("22°13'58.72E")
    dec_p1_lat = parse("58°16'21.29N")

    p1 = GeoPoint(dec_p1_lat, dec_p1_lon)

    dec_p2_lon = parse("22°39'54.73E")
    dec_p2_lat = parse("58° 8'6.75N")

    p2 = GeoPoint(dec_p2_lat, dec_p2_lon)

    x = get_euclidean_distance_in_meters(p1, p2)

    sat_image_downloader = SatImageDownloader(url)
    sat_image_downloader.set_resolution(15)
    sat_image_downloader.download_image_data(p1, p2)


if __name__ == '__main__':
    main()
