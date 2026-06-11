import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    FARMER = "Farmer"
    SALES_TEAM = "Sales Team"

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    mobile = Column(String(15), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.FARMER, nullable=False)
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    language = Column(String(50), default="English", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    recommendations = relationship("CropRecommendation", back_populates="farmer", cascade="all, delete-orphan")
    disease_predictions = relationship("DiseasePrediction", back_populates="farmer", cascade="all, delete-orphan")
    chats = relationship("ChatHistory", back_populates="farmer", cascade="all, delete-orphan")
    voice_queries = relationship("VoiceQuery", back_populates="farmer", cascade="all, delete-orphan")
