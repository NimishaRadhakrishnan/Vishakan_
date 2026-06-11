import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class DiseasePrediction(Base):
    __tablename__ = "disease_predictions"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    
    # Prediction Outputs
    disease_name = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    severity = Column(String(50), nullable=False)  # Low, Medium, High
    recommended_products = Column(JSON, nullable=True)  # List of product names/dicts
    image_path = Column(String(255), nullable=True)  # Path to saved uploaded image
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    farmer = relationship("Farmer", back_populates="disease_predictions")
