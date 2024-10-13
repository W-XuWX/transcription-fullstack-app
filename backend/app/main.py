import logging
from contextlib import asynccontextmanager

import uvicorn
from config import get_config
from database import DBClient
from fastapi import FastAPI
from routers import transcribe

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_config()
    try:
        app.state.db_client = DBClient(config)
        logger.info("Database connected successfully")
        yield
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    finally:
        # Shutdown operations
        if hasattr(app.state, "dbclient"):
            logger.debug("Closing database connection...")
            try:
                app.state.db_client.deinit()
                logger.info("Database closed")
            except Exception as e:
                logger.error(f"Error while closing database connection: {e}")


app = FastAPI(lifespan=lifespan)
app.include_router(transcribe.router)


@app.get("/health", status_code=200)
def get_health():
    return {"status": "Service is healthy! ^_^"}

if __name__ == '__main__':
	uvicorn.run(app='main:app',host='0.0.0.0',reload=True,port=8000)