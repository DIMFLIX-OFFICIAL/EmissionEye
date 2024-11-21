import json
import numpy as np
import requests
from tqdm import tqdm
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from numba import njit

import geojson
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union

from .. import config as cfg
from .rsdm import RSDM


class GeoJSONGenerator:
    def __init__(self, img_data, center_lat, center_lon):
        self.img_data = img_data
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.cell_size_lat = 1 / 111320
        self.cell_size_lon = 1 / (111320 * np.cos(np.radians(center_lat)))

    @staticmethod
    @njit
    def calculate_group_indices(color_values):
        max_value = 255
        return np.clip((color_values / max_value) * 8, 0, 7).astype(np.int32)

    def create_geojson_from_img_data(self):
        rows, cols = self.img_data.shape[0:2]
        
        # Получаем цветовые значения и рассчитываем индексы групп
        color_values = self.img_data[:, :, 0]
        group_indices = self.calculate_group_indices(color_values)

        # Инициализируем массивы для хранения полигонов по группам
        polygons_by_group = [[] for _ in range(8)]

        # Генерируем полигоны для всех пикселей без использования tqdm
        for y in range(rows):
            for x in range(cols):
                if np.sum(self.img_data[y, x]) != (255 + 255 + 255 + 255):
                    lat_min = self.center_lat + (rows / 2 - y) * self.cell_size_lat
                    lat_max = self.center_lat + (rows / 2 - (y + 1)) * self.cell_size_lat
                    lon_min = self.center_lon + (x - cols / 2) * self.cell_size_lon
                    lon_max = self.center_lon + (x - cols / 2 + 1) * self.cell_size_lon

                    polygon = Polygon([
                        (lon_min, lat_min),
                        (lon_max, lat_min),
                        (lon_max, lat_max),
                        (lon_min, lat_max),
                        (lon_min, lat_min),
                    ])

                    group_index = group_indices[y, x]
                    polygons_by_group[group_index].append(polygon)

        features = []
        
        # Обработка полигонов по группам с использованием многопоточности
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.process_polygons, group_index, polygons): group_index 
                       for group_index, polygons in enumerate(polygons_by_group) if polygons}

            for future in futures:
                features.extend(future.result())

        return geojson.FeatureCollection(features)

    def process_polygons(self, group_index, polygons):
        merged_polygon = unary_union(polygons)

        if isinstance(merged_polygon, (Polygon, MultiPolygon)):
            merged_polygon = merged_polygon.simplify(0.0001, preserve_topology=True)
            color = self.get_color_by_area(group_index)

            if isinstance(merged_polygon, MultiPolygon):
                return [geojson.Feature(
                            geometry=geojson.Polygon([list(poly.exterior.coords)]),
                            properties={"group": group_index, "color": color}
                        ) for poly in merged_polygon.geoms]
            elif isinstance(merged_polygon, Polygon):
                return [geojson.Feature(
                            geometry=geojson.Polygon([list(merged_polygon.exterior.coords)]),
                            properties={"group": group_index, "color": color}
                        )]

        return []

    def get_color_by_area(self, group):
        r = int(255 * (1 - (group) / 8))
        g = int(255 * (group / 8))
        return r, g, 0


class WeatherChecker:
    def __init__(self):
        self.weather_data = None

    def fetch_weather(self):
        response = requests.get(cfg.API_OPENWEATHERMAP_URL)

        if response.status_code == 200:
            weather_data = response.json()
            temperature = weather_data['main']['temp']
            temperature_min = weather_data['main']['temp_min'] + 273.15
            temperature_max = weather_data['main']['temp_max'] + 273.15
            wind_direction = weather_data['wind']['deg']
            wind_speed = weather_data['wind']['speed']
            humidity = weather_data['main']['humidity']
            clouds = weather_data['clouds']['all']
            weather_conditions = [w['main'] for w in weather_data['weather']]
            
            result = {
                'temperature': temperature,
                'temperature_min': temperature_min,
                'temperature_max': temperature_max,
                'humidity': humidity,
                'wind_direction': wind_direction,
                'wind_speed': wind_speed,
                'clouds': clouds,
                'weather_conditions': weather_conditions
            }
            self.weather_data = result
        else:
            self.weather_data = {
                'temperature': 0,
                'temperature_min': 0,
                'temperature_max': 0,
                'humidity': 70,
                'wind_direction': 0,
                'wind_speed': 0,
                'clouds': 0,
                'weather_conditions': []
            }

    def check_conditions(self):
        temp = self.weather_data["temperature"]
        humidity = self.weather_data["humidity"]
        clouds = self.weather_data["clouds"]
        wind_speed = self.weather_data["wind_speed"]
        weather_conditions = self.weather_data["weather_conditions"]

        if (
            temp > 20.00
            and 30 < humidity < 70
            and "Clear" in weather_conditions
            and wind_speed < 5
        ):
            return "A"

        if clouds > 70:
            return "B"

        if 30 > clouds > 70 and any(w in ["Snow", "Rain"] for w in weather_conditions):
            return "C"

        if (
            (
                self.weather_data["temperature_max"]
                - self.weather_data["temperature_min"]
                <= 3
            )
            and humidity > 70
            and "Clear" in weather_conditions
        ):
            return "D"

        if (
            temp < 0
            and -15 < self.weather_data["temperature_min"] < temp < clouds > 70
            and humidity > 70
        ):
            return "E"

        if temp < 0 and humidity > 90 and clouds > 70 and wind_speed < 2:
            return "F"

        return "A"


class GeoJSONApp:
    def __init__(self, img_data_path="factory.json"):
        with open(img_data_path, "r") as f:
            self.geojson_data = json.load(f)

    def run(self):
        weather_checker = WeatherChecker()

        logger.info("я тут")
        weather_checker.fetch_weather()

        logger.info("я тут1")
        results_cat = weather_checker.check_conditions()

        model = RSDM(
            wspd=weather_checker.weather_data["wind_speed"],
            wdir=weather_checker.weather_data["wind_direction"],
            ambient_temp=weather_checker.weather_data["temperature"],
            pgcat=results_cat,
            source_elevation=60,
            source_diameter=2.5,
            source_velocity=17.5,
            x_length=50_000,
            y_length=50_000,
        )

        model.run_model()
        data = model.update_image()

        all_geojson_data = []

        def process_feature(feature):
            coordinates = feature["geometry"]["coordinates"][::-1]
            generator = GeoJSONGenerator(data, coordinates[0], coordinates[1])
            return generator.create_geojson_from_img_data()

        # Используем ThreadPoolExecutor для распараллеливания
        with ThreadPoolExecutor() as executor:
            all_geojson_data = list(tqdm(executor.map(process_feature, self.geojson_data["features"][:3]), total=len(self.geojson_data["features"][:3])))

        cfg.GEOJSON_DATA = all_geojson_data
        with open(cfg.GEOJSON_PATH, 'w') as f:
            f.write(json.dumps(all_geojson_data))
