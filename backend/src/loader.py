import json
from fastapi import FastAPI
from concurrent.futures import ThreadPoolExecutor
from starlette.middleware.cors import CORSMiddleware
from src.gaussian_distribution.process import GeoJSONApp

from . import config as cfg

executor = ThreadPoolExecutor(max_workers=1)
app: FastAPI = FastAPI(debug=True)
gd: GeoJSONApp = GeoJSONApp(cfg.BACKEND_SRC_ROOT / "data" / "factory.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open(cfg.GEOJSON_PATH, "r") as f:
    cfg.GEOJSON_DATA = json.load(f) 

with open(cfg.FACTORIES_PATH, "r", encoding="utf-8") as f:
    cfg.FACTORIES = json.load(f)
