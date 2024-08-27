# !/usr/bin/env python3

"""
Description: Download satellite images from SentinelHub or Copernicus Dataspace.

Author: Dhanushka Liyanage
Created on: 2024-08-09
"""

import os
import numpy as np
from sentinelhub import (
    SHConfig,
    BBox,
    CRS,
    DataCollection,
    SentinelHubRequest,
    MimeType,
    DownloadRequest,
    bbox_to_dimensions)
from PIL import Image
import matplotlib.pyplot as plt


class GeoPoint:
    def __len__(self, latitude, longitude) -> None:
        self.latitude = latitude
        self.longitude = longitude


class GeoROI:
    def __init__(self, top_left: GeoPoint, bottom_right: GeoPoint) -> None:
        self.top_left = top_left
        self.bottom_right = bottom_right


class SatImageDownloader:
    def __init__(self, source: str, download_folder: str) -> None:
        self.datasource = source
        self.download_folder = download_folder

        self.service_url = 'https://services.sentinel-hub.com'
        self.sh_client_id = 'c9fc1bc1-8ff1-4c9c-8a54-1ca1d1342a1d'
        self.sh_client_secret = 'mpF1veLus2oQoKr9BoN4CfWsRrno4VUN'

        # Credentials saved as a profile.
        self.profile = 'sentinel_data'

        self.config = self.get_config()

    def get_config(self) -> SHConfig:
        config = SHConfig()

        config.sh_base_url = 'https://services.sentinel-hub.com'
        config.sh_token_url = 'https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token'
        config.sh_client_id = self.sh_client_id
        config.sh_client_secret = self.sh_client_secret

        credential_status = True if config.sh_client_id or config.sh_client_secret else False

        # config.

        if credential_status:
            config.save(self.profile)

        return config

    def download_image_data(self):
        resolution = 60
        kuressaare_bbox_coords_wgs84 = (23.02, 58.69, 25.23, 57.95)
        kuressaare_bbox = BBox(bbox=kuressaare_bbox_coords_wgs84, crs=CRS.WGS84)
        kuressaare_img_size = bbox_to_dimensions(kuressaare_bbox, resolution=resolution)

        evalscript = "return [2.5 * B12, 2.5 * B04, 2.5 * B02]"

        request_true_color = SentinelHubRequest(evalscript=evalscript,
                                                input_data=[SentinelHubRequest.input_data(
                                                    data_collection=DataCollection.SENTINEL2_L1C,
                                                    time_interval=("2024-02-18", "2024-02-20"),
                                                )],
                                                responses=[SentinelHubRequest.output_response(
                                                    "default", MimeType.PNG)],
                                                bbox=kuressaare_bbox,
                                                size=kuressaare_img_size,
                                                config=self.config
                                                )

        true_color_images = request_true_color.get_data()

        image_1 = true_color_images[0]

        pil_image = Image.fromarray(image_1)

        plt.imshow(pil_image)
        plt.show()
