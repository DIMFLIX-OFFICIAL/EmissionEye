import asyncio
from contextlib import asynccontextmanager

import src.config as cfg
import uvicorn
from loguru import logger
from src.api import sensors
from src.api.routers import unprotected
from src.loader import app


@asynccontextmanager
async def my_lifespan(_):
    logger.info("Начало работы сервера!")
    yield
    logger.info("Завершение работы сервера!")


def start():
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        logger.debug("uvloop installed")
    except Exception:
        logger.debug("uvloop not installed")

    app.router.lifespan_context = my_lifespan
    app.include_router(unprotected, prefix="/api")
    uvicorn.run(app, host=cfg.API_HOST, port=cfg.API_PORT)


if __name__ == "__main__":
    start()
