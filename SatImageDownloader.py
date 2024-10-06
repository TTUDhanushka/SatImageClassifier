# !/usr/bin/env python3

"""
Description: Download satellite images from SentinelHub or Copernicus Dataspace.

Author: Dhanushka Liyanage
Created on: 2024-08-09
"""

import os
import numpy as np
import datetime
from sentinelhub import (
    SHConfig,
    BBox,
    CRS,
    DataCollection,
    SentinelHubRequest,
    MimeType,
    DownloadRequest,
    bbox_to_dimensions, MosaickingOrder)
from PIL import Image
# import matplotlib.pyplot as plt


class GeoPoint:
    def __init__(self, latitude:float, longitude:float) -> None:
        self.latitude = latitude
        self.longitude = longitude


class GeoROI:
    def __init__(self, top_left: GeoPoint, bottom_right: GeoPoint) -> None:
        self.top_left = top_left
        self.bottom_right = bottom_right


class SatImageDownloader:
    def __init__(self) -> None:

        self.service_url = 'https://services.sentinel-hub.com'
        self.sh_client_id = 'c9fc1bc1-8ff1-4c9c-8a54-1ca1d1342a1d'
        self.sh_client_secret = 'mpF1veLus2oQoKr9BoN4CfWsRrno4VUN'

        # Credentials saved as a profile.
        self.profile = 'sentinel_data'

        # Default initialization
        self.resolution = 60
        self.start_date = "2024-08-18"
        self.end_date = "2024-08-22"

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

    def set_resolution(self, resolution: int) -> None:
        if self.resolution != resolution:
            self.resolution = resolution

    def set_date_range(self, start_date: datetime, end_date: datetime):
        self.start_date = start_date
        self.end_date = end_date

    def download_image_data(self, top_left_coordinates: GeoPoint,
                            bottom_right_coordinates: GeoPoint) -> Image:

        resolution = self.resolution

        kuressaare_bbox_coords_wgs84 = (top_left_coordinates.longitude,
                                        top_left_coordinates.latitude,
                                        bottom_right_coordinates.longitude,
                                        bottom_right_coordinates.latitude) # Longitude, Latitude

        kuressaare_bbox = BBox(bbox=kuressaare_bbox_coords_wgs84, crs=CRS.WGS84)
        kuressaare_img_size = bbox_to_dimensions(kuressaare_bbox, resolution=resolution)

        evalscript = "return [2.5 * B04, 2.5 * B03, 2.5 * B02]"

        request_true_color = SentinelHubRequest(data_folder='downloaded_data',
                                                evalscript=evalscript,
                                                input_data=[SentinelHubRequest.input_data(
                                                    data_collection=DataCollection.SENTINEL2_L1C,
                                                    time_interval=(self.start_date, self.end_date),
                                                    mosaicking_order=MosaickingOrder.LEAST_CC,
                                                )],
                                                responses=[SentinelHubRequest.output_response(
                                                    "default", MimeType.TIFF)],
                                                bbox=kuressaare_bbox,
                                                size=kuressaare_img_size,
                                                config=self.config
                                                )

        true_color_images = request_true_color.get_data(save_data=True)

        image_1 = true_color_images[0]

        # pil_image = Image.fromarray(image_1)
        return image_1
        # plt.imshow(pil_image)
        # plt.show()
