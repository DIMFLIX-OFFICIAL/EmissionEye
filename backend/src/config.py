from environs import Env
from pathlib import Path

env = Env()
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
BACKEND_ROOT: Path = Path(__file__).resolve().parent.parent
BACKEND_SRC_ROOT: Path = Path(__file__).resolve().parent

GEOJSON_PATH = BACKEND_SRC_ROOT / "data" / "geo.json"
FACTORIES_PATH = BACKEND_SRC_ROOT / "data" / "factory.json"


env.read_env(PROJECT_ROOT / ".env")
API_HOST = env.str("API_HOST")
API_PORT = env.int("API_PORT")
API_OPENWEATHERMAP = env.str("API_OPENWEATHERMAP")
API_OPENWEATHERMAP_CITY = env.str("API_OPENWEATHERMAP_CITY")
API_OPENWEATHERMAP_URL = f'http://api.openweathermap.org/data/2.5/weather?q={API_OPENWEATHERMAP_CITY}&appid={API_OPENWEATHERMAP}&units=metric'

SENSORS = [
    [56.330159, 43.838768],
	[56.350876, 43.867143],
	[56.362262, 43.824527],
	[56.325948, 43.881740],
	[56.323318, 43.926926],
	[56.325135, 43.939295],
	[56.327625, 43.993482],
	[56.319879, 43.989700],
	[56.306278, 43.984580],
	[56.303926, 43.982918],
	[56.313443, 44.064395],
	[56.311626, 44.048620],
	[56.272970, 43.923368],
	[56.261943, 43.892960],
	[56.231673, 43.853605],
	[56.291888, 44.002923],
	[56.273580, 43.979648],
	[56.257103, 43.980366],
	[56.231803, 43.944712]
]

GEOJSON_DATA = {
    "type": "FeatureCollection", 
    "features": []
}

FACTORIES = {}
