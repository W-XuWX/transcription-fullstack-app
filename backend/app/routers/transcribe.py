import logging
from typing import Annotated, List, Optional

import soundfile as sf
import torch
import librosa
from fastapi import APIRouter, File, Request, UploadFile, Query
from models import Results
from pydantic import BaseModel
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

router = APIRouter()


class ResultModel(BaseModel):
    file_name: str
    transcription: str


class BatchTranscriptionResponse(BaseModel):
    response: list


class SingleTranscriptionResponse(BaseModel):
    file_name: str
    transcription: str

class SearchResult(BaseModel):
    id: int
    file_name: str
    transcription: str
    highlights: List[dict]
    rank: float


@router.post("/transcribe", status_code=200, response_model=BatchTranscriptionResponse)
async def transcribe_audio_files(
    upload_files: Annotated[List[UploadFile], File()], request: Request
) -> BatchTranscriptionResponse:
    results = []

    def preprocess_audio(audio_data, request: Request):
        # Check if resampling is needed
        target_sampling_rate = 16000
        if original_sampling_rate != target_sampling_rate:
            # Resample the audio to 16kHz using librosa
            audio_data = librosa.resample(audio_data, orig_sr=original_sampling_rate, target_sr=target_sampling_rate)
        # Process the resampled audio data into features for the model
        input_features = request.app.state.processor(
            audio_data, sampling_rate=target_sampling_rate, return_tensors="pt"
        ).input_features

        return input_features

    def transcribe_audio(input_features, request: Request):
        # generate token ids
        with torch.no_grad():
            predicted_ids = request.app.state.model.generate(input_features)

        # decode the predicted token ids to get the transcription
        transcription = request.app.state.processor.batch_decode(
            predicted_ids, skip_special_tokens=True
        )[0]

        single_transcription_response = SingleTranscriptionResponse(
            file_name=file_name, transcription=transcription
        )
        return single_transcription_response

    def create_db_entry(result:SingleTranscriptionResponse, request: Request):
        db_client = request.app.state.db_client
        session = db_client.session  # Access the actual session object
        db_result = Results(
            file_name=result.file_name,
            transcription=result.transcription,
        )
        session.add(db_result)
        session.commit()
        session.refresh(db_result)
        return

    for upload_file in upload_files:
        logger.info(f"Received file: {upload_file.filename}")
        file_name = secure_filename(upload_file.filename)

        # read the audio data and sampling rate from the file
        audio_data, original_sampling_rate = sf.read(upload_file.file)

        input_features = preprocess_audio(audio_data=audio_data, request=request)
        single_transcription_response = transcribe_audio(
            input_features=input_features, request=request
        )
        create_db_entry(result=single_transcription_response, request=request)

        results.append(single_transcription_response)

    return BatchTranscriptionResponse(response=results)


@router.get("/transcriptions", status_code=200)
def get_all_transcriptions(request: Request):
    db_client = request.app.state.db_client
    session = db_client.session  # Access the actual session object
    try:
        results = session.query(Results).all()
        return results
    except Exception as e:
        logger.error(f"Error while fetching results from the database: {e}")
        raise

@router.get("/search", response_model=List[SearchResult])
async def search_transcriptions(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query"),
    limit: Optional[int] = 10,
    offset: Optional[int] = 0
):
    db_client = request.app.state.db_client
    session = db_client.session

    # Prepare search query with highlighting
    search_query = ' OR '.join(f'"{term}"' for term in q.strip().split())
    
    # SQL query using SQLite FTS5
    sql_query = """
    SELECT 
        id,
        file_name,
        transcription,
        rank,
        highlight(results_search, 2, '<mark>', '</mark>') as highlighted_text
    FROM results_search
    WHERE results_search MATCH :query
    ORDER BY rank
    LIMIT :limit OFFSET :offset
    """
    
    results = session.execute(
        sql_query,
        {
            'query': search_query,
            'limit': limit,
            'offset': offset
        }
    ).fetchall()
    
    search_results = []
    for row in results:
        # Extract highlight positions from the marked text
        highlighted_text = row.highlighted_text
        highlights = []
        pos = 0
        
        while True:
            start = highlighted_text.find('<mark>', pos)
            if start == -1:
                break
                
            end = highlighted_text.find('</mark>', start)
            text = highlighted_text[start + 6:end]
            
            # Find the actual position in the original text
            original_pos = row.transcription.lower().find(text.lower())
            if original_pos != -1:
                highlights.append({
                    'start': original_pos,
                    'end': original_pos + len(text),
                    'text': text
                })
            
            pos = end + 7
        
        search_results.append(SearchResult(
            id=row.id,
            file_name=row.file_name,
            transcription=row.transcription,
            highlights=highlights,
            rank=row.rank
        ))
    
    return search_results