from sqlalchemy import Column, Integer, String, Text, Float, JSON
from backend.app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(50), nullable=False)  # Bio Fertilizer, Bio Fungicide, Bio Pesticide, Bio Nematicide, Bio Stimulant, Other
    description = Column(Text, nullable=True)
    dosage = Column(String(100), nullable=True)
    benefits = Column(Text, nullable=True)
    application_method = Column(Text, nullable=True)
    suitable_crops = Column(JSON, nullable=True)     # List of strings e.g. ["Rice", "Banana"]
    suitable_diseases = Column(JSON, nullable=True)  # List of strings e.g. ["Blast", "Root Rot"]
    price = Column(Float, default=0.0)
    unit = Column(String(50), default="500ml")
