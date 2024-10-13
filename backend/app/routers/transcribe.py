from pydantic import BaseModel
from models import Results
from fastapi import APIRouter, Request
import logging
logger = logging.getLogger(__name__)

router = APIRouter()

class ResultModel(BaseModel):
    file_name: str
    transcription: str
    confidence_score: str

# @router.post("/transcribe", status_code=200)
# def transcribe_audio():
#     return {"message": "Transcription successful!"}


# @router.get("/transcriptions", status_code=200)
# def get_transcriptions():
#     return {"transcriptions": []}


# @router.get("/search", status_code=200)
# def search_transcriptions(query: str):
#     return {"results": []}

@router.post("/results", status_code=200)
def test_db(result: ResultModel, request: Request):
    db_client = request.app.state.db_client
    session = db_client.session  # Access the actual session object
    db_result = Results(
        file_name=result.file_name,
        transcription=result.transcription,
        confidence_score=result.confidence_score,
    )
    try:
        session.add(db_result)
        session.commit()
        session.refresh(db_result)
    except Exception as e:
        session.rollback()
        logger.error(f"Error while adding result to the database: {e}")
        raise
    return db_result

@router.get("/results/all")
def read_results(request: Request):
    db_client = request.app.state.db_client
    session = db_client.session  # Access the actual session object
    try:
        results = session.query(Results).all()
        return results
    except Exception as e:
        logger.error(f"Error while fetching results from the database: {e}")
        raise