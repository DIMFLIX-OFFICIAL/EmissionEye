import asyncio
from contextlib import asynccontextmanager

import src.config as cfg
import uvicorn
from loguru import logger
from src.api import sensors, geojson, factories
from src.api.routers import unprotected
from src.loader import app, gd, executor

shutdown_event = asyncio.Event()

async def run_background_task():
    logger.info("Background task started!")

    while True:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(executor, gd.run)
        logger.info("Geojson has been updated successfully!")
        await asyncio.sleep(1200)


@asynccontextmanager
async def my_lifespan(_):
    logger.info("Server is running!")
    task = asyncio.create_task(run_background_task())
    
    try:
        yield
    finally:
        logger.info("Shutting down executor...")
        shutdown_event.set()
        task.cancel()
        
        try:
            await task 
        except asyncio.CancelledError:
            logger.info("Background task cancelled.")

        executor.shutdown(wait=False, cancel_futures=True)
        logger.info("Server shutdown")


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
