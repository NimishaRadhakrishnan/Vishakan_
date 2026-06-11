from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.schemas.chat import FullAnalytics, AnalyticsDashboard, ProductTrend, DiseaseTrend, FarmerActivity
from backend.app.services.analytics_service import analytics_service
from backend.app.api.auth import get_current_user, get_current_sales_or_admin
from backend.app.models.farmer import Farmer

router = APIRouter(prefix="/analytics", tags=["Analytics & Reporting"])

@router.get("/dashboard", response_model=AnalyticsDashboard)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: Farmer = Depends(get_current_user)
):
    """
    Get general dashboard KPI summary metrics.
    """
    return analytics_service.get_dashboard_summary(db)

@router.get("/top-products", response_model=List[ProductTrend])
def get_top_products(
    db: Session = Depends(get_db),
    current_user: Farmer = Depends(get_current_user)
):
    """
    Get top recommended biological products.
    """
    return analytics_service.get_top_products(db)

@router.get("/common-diseases", response_model=List[DiseaseTrend])
def get_common_diseases(
    db: Session = Depends(get_db),
    current_user: Farmer = Depends(get_current_user)
):
    """
    Get most common crop pathology detections.
    """
    return analytics_service.get_common_diseases(db)

@router.get("/farmer-activity", response_model=List[FarmerActivity])
def get_farmer_activity(
    db: Session = Depends(get_db),
    current_user: Farmer = Depends(get_current_user)
):
    """
    Get signups/platform activity trends over the last 7 days.
    """
    return analytics_service.get_farmer_activity(db)

@router.get("/all", response_model=FullAnalytics)
def get_all_analytics(
    db: Session = Depends(get_db),
    current_user: Farmer = Depends(get_current_sales_or_admin)
):
    """
    Consolidated analytics package. Requires Admin or Sales Team credentials.
    """
    dashboard = analytics_service.get_dashboard_summary(db)
    top_products = analytics_service.get_top_products(db)
    common_diseases = analytics_service.get_common_diseases(db)
    farmer_activity = analytics_service.get_farmer_activity(db)
    
    return {
        "dashboard": dashboard,
        "top_products": top_products,
        "common_diseases": common_diseases,
        "farmer_activity": farmer_activity
    }
