import math
import numpy as np
from typing import List
from .disperse import iter_disp
from .visualise import generate_png

# Mapping of image quality selection to grid step (m)
grid_quality = {
    "Low": 50,
    "Medium": 25,
    "High": 10,
}

class HourMET:
    def __init__(self, hours: int, u: float, phi: float, pgcat: str) -> None:
        self.hours: int = hours
        self.u: float = u
        self.phi: float = phi
        self.pgcat: str = pgcat

class Grid:
    def __init__(self, xmin: int, xmax: int, ymin: int, ymax: int, xgap: int, ygap: int):
        self.xmin: int = xmin  # x extents (m)
        self.xmax: int = xmax
        self.ymin: int = ymin  # y extents (m)
        self.ymax: int = ymax
        self.xgap: int = xgap  # x step (m)
        self.ygap: int = ygap  # y step (m)

    def generate_grid(self) -> List[List[int]]:
        cols = int((self.xmax - self.xmin) / self.xgap) + 1
        rows = int((self.ymax - self.ymin) / self.ygap) + 1
        
        grid = [[0 for _ in range(cols)] for _ in range(rows)]
        return grid


class Source:
    def __init__(self, x: float, y: float, elevation: float, diameter: float, velocity: float, temp: float, emission: float) -> None:
        self.x: float = x                 # Stack x location (m)
        self.y: float = y                 # Stack y location (m)
        self.elevation: float = elevation  # Stack height (m)
        self.diameter: float = diameter    # Stack diameter (m)
        self.velocity: float = velocity    # Plume velocity at stack tip (m/s)
        self.temp: float = temp            # Plume temperature (C)
        self.emission: float = emission    # Stack emission rate (g/s)

    def wind_components(self, Xr, Yr, sinPHI, cosPHI):
        x = (-1 * (Xr - self.x) * sinPHI - (Yr - self.y) * cosPHI) / 1000
        y = (Xr - self.x) * cosPHI - (Yr - self.y) * sinPHI
        return x, y


class RSDM:
    __slots__ = (
        'grid', 'wspd', 'wdir', 'ambient_temp', 
        'roughness', 'pgcat', 'source',
        'x_length', 'y_length', 'xmin', 'xmax',
        'ymin', 'ymax', 'rCoords', 'rGrid', 'rDisp',
        'hCoords', 'hGrid', 'hDisp'
    )

    rGrid: List[List[int]]
    rDisp: List[List[int]]
    hGrid: List[List[int]]
    hDisp: List[List[int]]

    def __init__(self, wspd: float, wdir: float, ambient_temp: float, pgcat: str = "A", 
                source_elevation: float = 60, source_diameter: float = 2.5,
                source_velocity: float = 17.5, source_temperature: float = 200,
                source_emission: float = 3.86,
                x_length: int=5000, y_length: int=5000
                ) -> None:
        
        self.grid: int = grid_quality["High"]
        self.wspd: float = wspd
        self.wdir: float = wdir
        self.roughness: str = "urban"
        self.pgcat: str = pgcat

        self.source: Source = Source(
            x=0.0,
            y=0.0, 
            elevation=source_elevation, 
            diameter=source_diameter, 
            velocity=source_velocity, 
            temp=source_temperature, 
            emission=source_emission
        )

        self.ambient_temp: float = 273.15 + ambient_temp
        self.xmin: int = int(-(x_length / 2))
        self.xmax: int = int(x_length / 2)
        self.ymin: int = int(-(y_length / 2))
        self.ymax: int = int(y_length / 2)

        # Setup x,y grid for plan view
        self.rCoords = Grid(self.xmin, self.xmax, self.ymin, self.ymax, self.grid, self.grid)
        self.rGrid = self.rCoords.generate_grid()
        self.rDisp = self.rCoords.generate_grid()
        
        # Setup x,z plane height plume cross-section view
        self.hCoords = Grid(-2500, 2500, 0, 1000, self.grid, self.grid / 2)
        self.hGrid = self.hCoords.generate_grid()
        self.hDisp = self.hCoords.generate_grid()

    def clear_grid(self, grid) -> None:
        for row in grid:
            for i in range(len(row)):
                row[i] = 0

    @staticmethod
    def grid_max(grid: np.ndarray):
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        max_value = -1.0
        
        for y in range(rows):
            for x in range(cols):
                if grid[y][x] > max_value:
                    max_value = grid[y][x]
        
        return max_value


    def update_image(self):
        # Extract maximum value from grids
        grids_max = np.max(
            [self.grid_max(self.rGrid), self.grid_max(self.hGrid)]
        )

        # Create PNG for plan and plume views
        rImg = generate_png(np.array(self.rGrid), grids_max)
        return rImg

    def run_model(self):
        self.clear_grid(self.rGrid)
        self.clear_grid(self.hGrid)

        # Generate random meteorological data
        wdir_rad: float = self.wdir * math.pi / 180
        met_data = [HourMET(1, self.wspd, wdir_rad, self.pgcat)]

        # Run dispersion model and update internal arrays
        iter_disp(self, met_data, self.ambient_temp)
