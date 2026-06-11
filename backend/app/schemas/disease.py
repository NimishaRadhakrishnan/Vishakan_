from pydantic import BaseModel
from typing import List
from backend.app.schemas.product import ProductResponse

class DiseaseDetectResponse(BaseModel):
    disease_name: str
    confidence: float
    severity: str  # Low, Medium, High
    recommended_products: List[ProductResponse]
    dosage: str
    prevention: str
    description: str
    healthy_vs_infected_comparison: str
