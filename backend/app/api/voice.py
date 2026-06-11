from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.chat import VoiceResponse
from backend.app.services.voice_service import voice_service
from backend.app.api.auth import get_current_user
from backend.app.models.farmer import Farmer

router = APIRouter(prefix="/voice", tags=["Voice Assistant"])

@router.post("/query", response_model=VoiceResponse)
def voice_query(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Farmer = Depends(get_current_user)
):
    """
    Accepts audio file upload, transcribes speech via Whisper, executes agronomist consult,
    and returns text response and base64 encoded audio response file (gTTS generated).
    """
    # Simple validation of file types
    if not audio.content_type.startswith("audio/") and not audio.filename.endswith((".wav", ".mp3", ".m4a", ".ogg", ".aac")):
         # Warn user but don't crash, since farmers can record in varying device extensions
         pass
        
    try:
        result = voice_service.process_voice_query(
            db=db,
            farmer_id=current_user.id,
            audio_file=audio
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing voice assistant command: {str(e)}"
        )
