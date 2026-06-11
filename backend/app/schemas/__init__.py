from backend.app.schemas.farmer import FarmerCreate, FarmerLogin, FarmerResponse, Token, TokenData
from backend.app.schemas.product import ProductResponse, ProductRecommendRequest, ProductRecommendResponse
from backend.app.schemas.crop import CropPredictRequest, CropPredictResponse, SoilHealthRequest, SoilHealthResponse, DosageCalcRequest, DosageCalcResponse
from backend.app.schemas.disease import DiseaseDetectResponse
from backend.app.schemas.chat import ChatQuery, ChatResponse, VoiceResponse, FullAnalytics, AnalyticsDashboard, ProductTrend, DiseaseTrend, FarmerActivity

__all__ = [
    "FarmerCreate",
    "FarmerLogin",
    "FarmerResponse",
    "Token",
    "TokenData",
    "ProductResponse",
    "ProductRecommendRequest",
    "ProductRecommendResponse",
    "CropPredictRequest",
    "CropPredictResponse",
    "SoilHealthRequest",
    "SoilHealthResponse",
    "DosageCalcRequest",
    "DosageCalcResponse",
    "DiseaseDetectResponse",
    "ChatQuery",
    "ChatResponse",
    "VoiceResponse",
    "FullAnalytics",
    "AnalyticsDashboard",
    "ProductTrend",
    "DiseaseTrend",
    "FarmerActivity"
]
