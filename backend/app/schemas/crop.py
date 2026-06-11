from pydantic import BaseModel, Field
from typing import List, Optional
from backend.app.schemas.product import ProductResponse

class CropPredictRequest(BaseModel):
    soil_type: str = Field(..., examples=["Loamy"])
    nitrogen: float = Field(..., ge=0, le=200, examples=[80.0])
    phosphorus: float = Field(..., ge=0, le=200, examples=[45.0])
    potassium: float = Field(..., ge=0, le=200, examples=[50.0])
    ph: float = Field(..., ge=0, le=14, examples=[6.5])
    temperature: float = Field(..., ge=-10, le=60, examples=[28.5])
    humidity: float = Field(..., ge=0, le=100, examples=[75.0])
    rainfall: float = Field(..., ge=0, le=1000, examples=[150.0])

class CropPredictResponse(BaseModel):
    recommended_crop: str
    confidence_score: float
    expected_yield: str  # e.g., "4.5 tons/hectare"
    top_3_alternative_crops: List[str]
    recommended_products: List[ProductResponse]
    model_used: str

class SoilHealthRequest(BaseModel):
    N: float = Field(..., ge=0, le=200, examples=[60.0])
    P: float = Field(..., ge=0, le=200, examples=[30.0])
    K: float = Field(..., ge=0, le=200, examples=[40.0])
    pH: float = Field(..., ge=0, le=14, examples=[6.5])
    OrganicCarbon: float = Field(..., ge=0, le=10, description="Organic Carbon percentage", examples=[0.55])
    soil_type: Optional[str] = Field("Loamy", examples=["Loamy"])

class SoilHealthResponse(BaseModel):
    soil_health_score: float
    deficiency_report: List[str]
    excess_report: List[str]
    suitable_crops: List[str]
    recommended_products: List[ProductResponse]
    fertilization_plan: str

class DosageCalcRequest(BaseModel):
    crop: str = Field(..., examples=["Rice"])
    product: str = Field(..., description="Name of the Vishakan Product", examples=["V-NITRO"])
    area: float = Field(..., ge=0.01, description="Area of the crop field", examples=[2.5])
    unit: str = Field("acres", description="acres or hectares", examples=["acres"])

class DosageCalcResponse(BaseModel):
    required_quantity: str  # e.g., "5.0 L" or "500 ml"
    mixing_ratio: str  # e.g., "2.5 ml per liter of water"
    application_schedule: str
    estimated_cost: float
    water_volume_liters: float
