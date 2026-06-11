from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.crop import CropPredictRequest, CropPredictResponse, SoilHealthRequest, SoilHealthResponse
from backend.app.services.crop_service import crop_service
from backend.app.api.auth import get_current_user
from backend.app.models.farmer import Farmer

router = APIRouter(prefix="/crop", tags=["Crop & Soil Advisory"])

@router.post("/predict-crop", response_model=CropPredictResponse)
def predict_crop(
    req: CropPredictRequest,
    db: Session = Depends(get_db),
    current_user: Farmer = Depends(get_current_user)
):
    """
    Predict optimal crop and return matching Vishakan products based on NPK, pH, and climate metrics.
    """
    result = crop_service.predict_crop(
        db=db,
        farmer_id=current_user.id,
        soil_type=req.soil_type,
        n=req.nitrogen,
        p=req.phosphorus,
        k=req.potassium,
        ph=req.ph,
        temp=req.temperature,
        hum=req.humidity,
        rain=req.rainfall
    )
    return result

@router.post("/soil-health", response_model=SoilHealthResponse)
def analyze_soil(
    req: SoilHealthRequest,
    db: Session = Depends(get_db),
    current_user: Farmer = Depends(get_current_user)
):
    """
    Analyzes soil nutrient levels (NPK, pH, Organic Carbon) and returns deficiencies, score, and corrections.
    """
    result = crop_service.analyze_soil_health(
        db=db,
        n=req.N,
        p=req.P,
        k=req.K,
        ph=req.pH,
        organic_carbon=req.OrganicCarbon,
        soil_type=req.soil_type or "Loamy"
    )
    return result
