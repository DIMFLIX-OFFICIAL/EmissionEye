import json
from fastapi import Request
from fastapi.responses import JSONResponse

from .routers import unprotected

import src.config as cfg


@unprotected.post("/get_sensors")
async def get_my_account_info(request: Request):
    return JSONResponse(json.dumps(dict(
        marks=cfg.SENSORS
    )))