from pydantic import BaseModel, Field
from typing import Optional, List

class ProductBase(BaseModel):
    product_name: str = Field(..., examples=["V-NITRO"])
    category: str = Field(..., examples=["Bio Fertilizer"])
    description: Optional[str] = Field(None, examples=["Azotobacter biofertilizer"])
    dosage: Optional[str] = Field(None, examples=["2.5 ml/L water"])
    benefits: Optional[str] = Field(None, examples=["Fixes atmospheric nitrogen"])
    application_method: Optional[str] = Field(None, examples=["Foliar spray or soil application"])
    suitable_crops: Optional[List[str]] = Field(None, examples=[["Rice", "Banana"]])
    suitable_diseases: Optional[List[str]] = Field(None, examples=[[]])
    price: float = Field(0.0, examples=[350.00])
    unit: str = Field("500ml", examples=["500ml"])

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

class ProductRecommendRequest(BaseModel):
    crop_name: str = Field(..., examples=["Rice"])
    crop_stage: Optional[str] = Field(None, examples=["Vegetative"])
    soil_type: Optional[str] = Field(None, examples=["Clay"])

class ProductRecommendResponse(BaseModel):
    recommended_products: List[ProductResponse]
    dosage_instructions: str
    application_schedule: str
