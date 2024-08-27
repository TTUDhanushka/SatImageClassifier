# !/usr/bin/env python3
"""

"""
from SatImageDownloader import SatImageDownloader


def main():
    url = ''
    path = '/home/dhanushka/Datasets/SatImages'
    sat_image_downloader = SatImageDownloader(url, path)
    sat_image_downloader.download_image_data()


if __name__ == '__main__':
    main()
