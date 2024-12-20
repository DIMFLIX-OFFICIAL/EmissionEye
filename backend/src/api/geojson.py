import json
from fastapi import Request
from fastapi.responses import JSONResponse

from .routers import unprotected

import src.config as cfg


@unprotected.post("/get_geojson")
async def get_geojson(request: Request):
    return JSONResponse(json.dumps(cfg.GEOJSON_DATA))