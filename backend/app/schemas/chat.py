from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChatQuery(BaseModel):
    question: str = Field(..., min_length=2, examples=["My paddy leaves are yellow, what do I do?"])

class ChatResponse(BaseModel):
    answer: str
    recommended_products: List[str]
    context_sources: List[str]

class VoiceResponse(BaseModel):
    text_response: str
    audio_response: str  # Base64 encoded audio string
    language_detected: str

class AnalyticsDashboard(BaseModel):
    total_farmers: int
    products_recommended: int
    disease_detections: int
    chatbot_usage: int

class ProductTrend(BaseModel):
    product_name: str
    count: int

class DiseaseTrend(BaseModel):
    disease_name: str
    count: int

class FarmerActivity(BaseModel):
    date: str
    count: int

class FullAnalytics(BaseModel):
    dashboard: AnalyticsDashboard
    top_products: List[ProductTrend]
    common_diseases: List[DiseaseTrend]
    farmer_activity: List[FarmerActivity]
