# !/usr/bin/env python3

"""
Description: Download satellite images from SentinelHub or Copernicus Dataspace.

Author: Dhanushka Liyanage
Created on: 2024-08-09
"""

import os
from sentinelhub import (
    SHConfig,
    DownloadRequest)


class GeoPoint:
    def __len__(self, latitude, longitude) -> None:
        self.latitude = latitude
        self.longitude = longitude


class GeoROI:
    def __init__(self, top_left: GeoPoint, bottom_right: GeoPoint) -> None:
        self.top_left = top_left
        self.bottom_right = bottom_right


class SatImageDownloader:
    def __init__(self, source: str, download_folder: str, location: GeoPoint) -> None:
        self.datasource = source
        self.download_folder = download_folder

        self.service_url = 'https://sh.dataspace.copernicus.eu'
        self.sh_client_id = 'sh-4d27e480-8282-40a1-b813-4f347461046e'
        self.sh_client_secret = 'JMUazIE6z4B0e6MWXBOfIyrPco3QP79s'

        self.has_valid_credentials = self.check_credentials()

    def check_credentials(self) -> bool:
        config = SHConfig()

        config.sh_client_id = self.sh_client_id
        config.sh_client_secret = self.sh_client_secret

        credential_status = True if config.sh_client_id or config.sh_client_secret else False

        return credential_status

