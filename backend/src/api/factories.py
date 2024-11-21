import json
import copy
from fastapi import Request
from fastapi.responses import JSONResponse

from .routers import unprotected

import src.config as cfg


@unprotected.post("/get_factories")
async def get_factories(request: Request):
    factories = copy.deepcopy(cfg.FACTORIES)
    
    for factory in factories["features"]:
        factory["geometry"]["coordinates"].reverse()

    return JSONResponse(json.dumps(factories))
