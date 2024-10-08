import pyproj
from lat_lon_parser import parse


geod = pyproj.Geod(ellps='WGS84')

class GeoPoint:
    def __init__(self, latitude:float, longitude:float) -> None:
        self.latitude = latitude
        self.longitude = longitude


class GeoROI:
    def __init__(self, top_left: GeoPoint, bottom_right: GeoPoint) -> None:
        self.top_left = top_left
        self.bottom_right = bottom_right

class GeoCalcs:
    @staticmethod
    def get_euclidean_distance_in_meters(p1:GeoPoint, p2:GeoPoint) -> float:
        _, _, distance = geod.inv(p1.longitude, p1.latitude, p2.longitude, p2.latitude)
        return distance

    @staticmethod
    def get_avg_width_of_roi(p1:GeoPoint, p2:GeoPoint) -> float:
        avg_lat = (p1.latitude + p2.latitude) / 2

        width = geod.inv(p1.longitude, avg_lat, p2.longitude, avg_lat)
        return width

    @staticmethod
    def get_next_coords_in_a_distance(p1:GeoPoint, azimuth:float, distance: float) -> tuple[any, any, any]:
        coordinates = geod.fwd(p1.longitude, p1.latitude, azimuth, distance)

        return coordinates