from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.chat import ChatQuery, ChatResponse
from backend.app.services.chat_service import chat_service
from backend.app.api.auth import get_current_user
from backend.app.models.farmer import Farmer

router = APIRouter(prefix="/chatbot", tags=["AI Agronomist Chat"])

@router.post("/chat", response_model=ChatResponse)
def query_agronomist(
    req: ChatQuery,
    db: Session = Depends(get_db),
    current_user: Farmer = Depends(get_current_user)
):
    """
    RAG-powered conversational interface answering crop, dosage, disease, and product questions.
    """
    try:
        result = chat_service.query_agronomist(
            db=db,
            farmer_id=current_user.id,
            question=req.question
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing agronomist chat query: {str(e)}"
        )
