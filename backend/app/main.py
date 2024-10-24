import logging
from contextlib import asynccontextmanager

import torch
import uvicorn
from config import get_config
from database import DBClient
from fastapi import FastAPI
from routers import transcribe
from models import Base
from transformers import WhisperForConditionalGeneration, WhisperProcessor

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_config()
    try:
        # load database
        app.state.db_client = DBClient(config)
        logger.info("Database connected successfully")

        # Create regular tables
        try:
            Base.metadata.create_all(bind=app.state.db_client.engine)
            logger.info("Base tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create base tables: {e}")
            raise

        # Initialize FTS
        try:
            app.state.db_client.init_fts()
            logger.info("FTS initialization completed")
        except Exception as e:
            logger.error(f"Failed to initialize FTS: {e}")
            raise

        # load model and processor
        app.state.processor = WhisperProcessor.from_pretrained(config.model)
        app.state.model = WhisperForConditionalGeneration.from_pretrained(config.model)
        app.state.model.config.forced_decoder_ids = app.state.processor.get_decoder_prompt_ids(
            language="english", task="transcribe"
        )
        logger.info("ML models loaded successfully")

        yield
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    finally:
        # Shutdown operations
        if hasattr(app.state, "processor"):
            del app.state.processor
        if hasattr(app.state, "model"):
            del app.state.model
        if hasattr(app.state, "db_client"):
            try:
                app.state.db_client.deinit()
                logger.info("Database connection closed successfully")
            except Exception as e:
                logger.error(f"Error during database cleanup: {e}")


app = FastAPI(lifespan=lifespan)
app.include_router(transcribe.router)


@app.get("/health", status_code=200)
def get_health():
    return {"status": "Service is healthy! ^_^"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", reload=True, port=8000)
