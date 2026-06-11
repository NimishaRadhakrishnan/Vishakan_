from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.disease import DiseaseDetectResponse
from backend.app.services.disease_service import disease_service
from backend.app.api.auth import get_current_user
from backend.app.models.farmer import Farmer

router = APIRouter(prefix="/disease", tags=["Plant Pathology"])

@router.post("/detect", response_model=DiseaseDetectResponse)
def detect_disease(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Farmer = Depends(get_current_user)
):
    """
    Upload an image of leaf/fruit/stem/root to run AI pathology diagnosis.
    Returns predicted disease, severity, descriptions, and Vishakan bio-fungicides/pesticides.
    """
    # Simple validation of file types
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File uploaded is not a valid image format."
        )
        
    try:
        result = disease_service.detect_disease(
            db=db,
            farmer_id=current_user.id,
            image_file=image
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image diagnosis: {str(e)}"
        )
