from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.schemas.product import ProductResponse, ProductRecommendRequest, ProductRecommendResponse
from backend.app.schemas.crop import DosageCalcRequest, DosageCalcResponse
from backend.app.services.product_service import product_service
from backend.app.services.crop_service import crop_service
from backend.app.api.auth import get_current_user
from backend.app.models.farmer import Farmer

router = APIRouter(prefix="/products", tags=["Product Catalog"])

@router.get("/", response_model=List[ProductResponse])
def read_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Farmer = Depends(get_current_user)
):
    """
    Get all Vishakan products. Optional filters: category, search keyword.
    """
    return product_service.get_products(db, category=category, search=search)

@router.get("/{product_id}", response_model=ProductResponse)
def read_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: Farmer = Depends(get_current_user)
):
    """
    Get detailed information for a specific product by ID.
    """
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.post("/recommend", response_model=ProductRecommendResponse)
def recommend_products(
    req: ProductRecommendRequest,
    db: Session = Depends(get_db),
    current_user: Farmer = Depends(get_current_user)
):
    """
    Recommends specific Vishakan biological products for a crop at a specific growth stage and soil type.
    """
    products = product_service.recommend_products(
        db,
        crop_name=req.crop_name,
        crop_stage=req.crop_stage,
        soil_type=req.soil_type
    )
    
    # Construct instructions
    instruct = f"Apply recommended biological inputs for {req.crop_name} during growth stage: '{req.crop_stage or 'All'}'. "
    if products:
        instruct += f"Specifically, apply {products[0].product_name} according to the dosage directions."
        
    schedule = "Basal application for root health, followed by foliar sprays during vegetative expansion and pre-flowering stages."
    
    return {
        "recommended_products": products,
        "dosage_instructions": instruct,
        "application_schedule": schedule
    }

@router.post("/dosage-calculator", response_model=DosageCalcResponse)
def calculate_dosage(
    req: DosageCalcRequest,
    db: Session = Depends(get_db),
    current_user: Farmer = Depends(get_current_user)
):
    """
    Calculates exact required biological product volume, estimated cost, water volume, and schedule.
    """
    try:
        res = crop_service.calculate_dosage(
            db,
            crop=req.crop,
            product_name=req.product,
            area=req.area,
            unit=req.unit
        )
        return {
            "required_quantity": res["required_quantity"],
            "mixing_ratio": res["mixing_ratio"],
            "application_schedule": res["application_schedule"],
            "estimated_cost": res["estimated_cost"],
            "water_volume_liters": res["water_volume_liters"]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
