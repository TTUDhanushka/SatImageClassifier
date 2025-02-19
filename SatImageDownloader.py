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
    bbox_to_dimensions,
    MosaickingOrder,
    pixel_to_utm,
    transform_point, get_utm_crs)

from PIL import Image
from geo_utils import GeoPoint

class SatImageDownloader:
    def __init__(self) -> None:

        self.service_url = 'https://services.sentinel-hub.com'
        self.sh_client_id = 'c72e8dc6-7d8a-4d59-9944-eb181165994b'
        self.sh_client_secret = 'PQPZeX7yJ35iXSTMhJz0A82rL1cRuJlx'

        # Credentials saved as a profile.
        self.profile = 'sentinel_data'

        # Default initialization
        self.resolution = 10
        self.thumbnail_resolution = 15

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

        if credential_status:
            config.save(self.profile)

        return config

    def set_resolution(self, resolution: float) -> None:
        if self.resolution != resolution:
            self.resolution = resolution

    def set_date_range(self, start_date: datetime, end_date: datetime):
        self.start_date = start_date
        self.end_date = end_date

    def download_image_data(self, center_point_coordinates: GeoPoint) -> Image:

        # UTM coordinates
        center_crs = get_utm_crs(center_point_coordinates.longitude, center_point_coordinates.latitude)
        center_utm = transform_point((center_point_coordinates.longitude, center_point_coordinates.latitude), CRS.WGS84, center_crs)

        print(f"Center coordinates in UTM: {center_utm} and crs{center_crs}")

        # utm bounding box for pixels
        pixel_coordinates = pixel_to_utm(256, 256, transform=[center_utm[0], 10, 0, center_utm[1], 0, 10])
        wgs_84_coordinates_1 = transform_point(pixel_coordinates, center_crs, CRS.WGS84, True)
        print(f"1. Pixel coordinates in UTM: {pixel_coordinates} and WGS84 coordinates {wgs_84_coordinates_1}")

        pixel_coordinates = pixel_to_utm(-256, -256, transform=[center_utm[0], 10, 0, center_utm[1], 0, 10])
        wgs_84_coordinates_2 = transform_point(pixel_coordinates, center_crs, CRS.WGS84)
        print(f"2. Pixel coordinates in UTM: {pixel_coordinates} and WGS84 coordinates {wgs_84_coordinates_2}")


        geo_bbox = BBox(bbox=(wgs_84_coordinates_1[0], wgs_84_coordinates_1[1], wgs_84_coordinates_2[0], wgs_84_coordinates_2[1]), crs=CRS.WGS84)
        satellite_img_size = bbox_to_dimensions(geo_bbox, resolution=(10, 10))

        print(f"Image size {satellite_img_size}")

        evalscript = """
                    //VERSION=3
                    function setup() {
                        return {
                            input: ["B04", "B03", "B02"], // RGB bands
                            output: {
                                id: "default",
                                bands: 3,
                                sampleType: SampleType.FLOAT32
                            }
                        };
                    }
            
                    function evaluatePixel(sample) {
                        return [2.5* sample.B04, 2.5* sample.B03, 2.5* sample.B02];
                    }
        """

        request_true_color = SentinelHubRequest(data_folder='downloaded_data',
                                                evalscript=evalscript,
                                                input_data=[SentinelHubRequest.input_data(
                                                    data_collection=DataCollection.SENTINEL2_L1C,
                                                    time_interval=(self.start_date, self.end_date),
                                                    mosaicking_order=MosaickingOrder.LEAST_CC,
                                                )],
                                                responses=[SentinelHubRequest.output_response(
                                                    "default", MimeType.TIFF)],
                                                bbox=geo_bbox,
                                                size=satellite_img_size,
                                                config=self.config
                                                )

        true_color_images = request_true_color.get_data(save_data=True)

        downloaded_sat_image = true_color_images[0]
        return downloaded_sat_image


    def download_preview_thumbnail(self, center_point_coordinates: GeoPoint):

        # UTM coordinates
        center_crs = get_utm_crs(center_point_coordinates.longitude, center_point_coordinates.latitude)
        center_utm = transform_point((center_point_coordinates.longitude, center_point_coordinates.latitude), CRS.WGS84, center_crs)

        print(f"Center coordinates in UTM: {center_utm} and crs{center_crs}")

        # utm bounding box for pixels
        pixel_coordinates = pixel_to_utm(256, 256, transform=[center_utm[0], 10, 0, center_utm[1], 0, 10])
        wgs_84_coordinates_1 = transform_point(pixel_coordinates, center_crs, CRS.WGS84, True)
        print(f"1. Pixel coordinates in UTM: {pixel_coordinates} and WGS84 coordinates {wgs_84_coordinates_1}")

        pixel_coordinates = pixel_to_utm(-256, -256, transform=[center_utm[0], 10, 0, center_utm[1], 0, 10])
        wgs_84_coordinates_2 = transform_point(pixel_coordinates, center_crs, CRS.WGS84)
        print(f"2. Pixel coordinates in UTM: {pixel_coordinates} and WGS84 coordinates {wgs_84_coordinates_2}")

        geo_bbox = BBox(bbox=(wgs_84_coordinates_1[0], wgs_84_coordinates_1[1], wgs_84_coordinates_2[0], wgs_84_coordinates_2[1]), crs=CRS.WGS84)
        satellite_img_size = bbox_to_dimensions(geo_bbox, resolution=self.thumbnail_resolution)

        evalscript = "return [2.5 * B04, 2.5 * B03, 2.5 * B02]"

        request_true_color = SentinelHubRequest(evalscript=evalscript,
                                                input_data=[SentinelHubRequest.input_data(
                                                    data_collection=DataCollection.SENTINEL2_L1C,
                                                    time_interval=(self.start_date, self.end_date),
                                                    mosaicking_order=MosaickingOrder.LEAST_CC,
                                                )],
                                                responses=[SentinelHubRequest.output_response(
                                                    "default", MimeType.PNG)],
                                                bbox=geo_bbox,
                                                size=satellite_img_size,
                                                config=self.config
                                                )

        true_color_images = request_true_color.get_data(save_data=False)

        downloaded_sat_image = true_color_images[0]
        return downloaded_sat_image
