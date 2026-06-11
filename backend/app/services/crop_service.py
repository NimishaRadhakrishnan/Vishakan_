import os
import pickle
import numpy as np
import logging
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from backend.app.core.config import settings
from backend.app.services.product_service import product_service
from backend.app.models.recommendation import CropRecommendation
from backend.app.models.product import Product

logger = logging.getLogger(__name__)

# List of supported crops
CROPS = [
    "Rice", "Banana", "Coconut", "Turmeric", "Pepper", "Cardamom",
    "Mango", "Jackfruit", "Arecanut", "Tapioca", "Sugarcane", "Drumstick"
]

class CropService:
    def __init__(self):
        self.model_path = "backend/app/ml_models/crop_model.pkl"
        self.model_payload = None
        self._load_model()
        
    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.model_payload = pickle.load(f)
                logger.info("Successfully loaded Crop Recommendation ML Model.")
            except Exception as e:
                logger.error(f"Error loading Crop Recommendation ML model: {e}")
        else:
            logger.warning(f"Crop model not found at {self.model_path}. Running with rule-based fallback engine.")

    def predict_crop(
        self,
        db: Session,
        farmer_id: int,
        soil_type: str,
        n: float,
        p: float,
        k: float,
        ph: float,
        temp: float,
        hum: float,
        rain: float
    ) -> Dict[str, Any]:
        """
        Predict crop based on soil parameters and environmental parameters.
        Saves prediction record in PostgreSQL.
        """
        recommended_crop = None
        confidence = 0.0
        model_name = "Rule-based Fallback Engine"
        
        # ML Inference if model exists
        if self.model_payload:
            try:
                model = self.model_payload["model"]
                le = self.model_payload["label_encoder"]
                model_name = self.model_payload.get("model_name", "ML Model")
                
                # Predict
                features = np.array([[n, p, k, ph, temp, hum, rain]])
                pred_encoded = model.predict(features)[0]
                recommended_crop = le.inverse_transform([pred_encoded])[0]
                
                # Probabilities for confidence
                if hasattr(model, "predict_proba"):
                    probs = model.predict_proba(features)[0]
                    confidence = float(np.max(probs)) * 100
                else:
                    confidence = float(self.model_payload.get("accuracy", 0.9)) * 100
            except Exception as e:
                logger.error(f"Error during crop ML inference: {e}. Falling back to rules.")
                recommended_crop = None

        # Rule-based fallback if ML failed or not loaded
        if not recommended_crop:
            model_name = "Rule-based Agronomist Rules (Fallback)"
            if n > 110:
                recommended_crop = "Sugarcane"
                confidence = 85.0
            elif rain > 200:
                recommended_crop = "Rice" if ph <= 6.5 else "Cardamom"
                confidence = 90.0
            elif temp > 30 and rain < 150:
                recommended_crop = "Coconut"
                confidence = 88.0
            elif ph < 5.8:
                recommended_crop = "Turmeric"
                confidence = 82.0
            elif soil_type.lower() in ["clay", "alluvial"]:
                recommended_crop = "Banana"
                confidence = 87.0
            else:
                recommended_crop = "Mango"
                confidence = 78.0

        # Heuristic Expected Yield
        yields = {
            "Rice": "4.5 to 6.2 tons/hectare",
            "Banana": "30 to 45 tons/hectare",
            "Sugarcane": "80 to 110 tons/hectare",
            "Coconut": "8000 to 12000 nuts/hectare",
            "Turmeric": "20 to 25 tons/hectare",
            "Pepper": "1.5 to 2.5 tons/hectare",
            "Cardamom": "250 to 500 kg/hectare",
            "Tapioca": "35 to 50 tons/hectare",
            "Mango": "8 to 15 tons/hectare",
            "Jackfruit": "15 to 25 tons/hectare",
            "Arecanut": "1.2 to 2.0 tons/hectare",
            "Drumstick": "40 to 50 tons/hectare"
        }
        expected_yield = yields.get(recommended_crop, "3.5 to 5.0 tons/hectare")
        
        # Get alternative crops
        alternatives = [c for c in CROPS if c != recommended_crop][:3]
        
        # Suitable Vishakan Products for the recommended crop
        recommended_products = product_service.recommend_products(db, crop_name=recommended_crop)
        
        # Save to DB
        rec_products_data = [{"id": p.id, "name": p.product_name, "category": p.category} for p in recommended_products]
        db_rec = CropRecommendation(
            farmer_id=farmer_id,
            soil_type=soil_type,
            nitrogen=n,
            phosphorus=p,
            potassium=k,
            ph=ph,
            temperature=temp,
            humidity=hum,
            rainfall=rain,
            recommended_crop=recommended_crop,
            confidence_score=round(confidence, 2),
            recommended_products=rec_products_data
        )
        db.add(db_rec)
        db.commit()
        db.refresh(db_rec)

        return {
            "recommended_crop": recommended_crop,
            "confidence_score": round(confidence, 2),
            "expected_yield": expected_yield,
            "top_3_alternative_crops": alternatives,
            "recommended_products": recommended_products,
            "model_used": model_name
        }

    @staticmethod
    def analyze_soil_health(
        db: Session,
        n: float,
        p: float,
        k: float,
        ph: float,
        organic_carbon: float,
        soil_type: str
    ) -> Dict[str, Any]:
        """
        Analyze soil nutrient status, compute health score, and suggest corrections.
        """
        score = 100.0
        deficiencies = []
        excess = []
        
        # Evaluation of nitrogen (N)
        if n < 50:
            deficiencies.append("Nitrogen (Low)")
            score -= 15
        elif n > 120:
            excess.append("Nitrogen (Excess)")
            score -= 10
            
        # Evaluation of phosphorus (P)
        if p < 25:
            deficiencies.append("Phosphorus (Low)")
            score -= 15
        elif p > 60:
            excess.append("Phosphorus (Excess)")
            score -= 10

        # Evaluation of potassium (K)
        if k < 40:
            deficiencies.append("Potassium (Low)")
            score -= 15
        elif k > 100:
            excess.append("Potassium (Excess)")
            score -= 10

        # Evaluation of pH
        if ph < 5.5:
            deficiencies.append("pH Acidic")
            score -= 20
        elif ph > 7.8:
            deficiencies.append("pH Alkaline")
            score -= 20
            
        # Evaluation of Organic Carbon
        if organic_carbon < 0.5:
            deficiencies.append("Organic Carbon (Low)")
            score -= 25
        elif organic_carbon < 0.8:
            deficiencies.append("Organic Carbon (Moderate)")
            score -= 10
            
        # Clamp score to [10, 100]
        score = float(max(10, score))
        
        # Determine recommended products based on deficiencies
        prod_names = []
        if "Nitrogen (Low)" in deficiencies:
            prod_names.append("V-NITRO")
        if "Phosphorus (Low)" in deficiencies:
            prod_names.append("V-PHOS")
        if "Potassium (Low)" in deficiencies:
            prod_names.append("V-SOL-K")
        if "Organic Carbon (Low)" in deficiencies or "Organic Carbon (Moderate)" in deficiencies:
            prod_names.extend(["V-HUME", "V-RICH"])
            
        # Always recommend BIO-NPK and V-ZYME GR for general soil health boost
        prod_names.extend(["BIO-NPK", "V-ZYME GR"])
        prod_names = list(set(prod_names)) # unique
        
        recommended_products = product_service.get_products_by_names(db, prod_names)
        
        # Map soil type to suitable crops
        crop_mappings = {
            "loamy": ["Banana", "Turmeric", "Sugarcane", "Drumstick"],
            "clay": ["Rice", "Banana", "Tapioca"],
            "sandy": ["Coconut", "Groundnut", "Jackfruit"],
            "silt": ["Rice", "Banana", "Arecanut"],
            "black": ["Cotton", "Sugarcane", "Groundnut"],
            "red": ["Mango", "Arecanut", "Pepper", "Cardamom"],
            "laterite": ["Cardamom", "Pepper", "Coconut"],
            "alluvial": ["Rice", "Banana", "Sugarcane", "Turmeric"]
        }
        suitable_crops = crop_mappings.get(soil_type.lower(), ["Coconut", "Mango", "Arecanut"])
        
        # Generate custom fertilization plan text
        plan = (
            f"Your Soil Health Score is {score}%. "
            f"Based on the chemical profile: "
        )
        if deficiencies:
            plan += f"Deficiencies detected in: {', '.join(deficiencies)}. "
            plan += "To correct these, we recommend applying: "
            plan += f"{', '.join([p.product_name for p in recommended_products if p.product_name in ['V-NITRO', 'V-PHOS', 'V-SOL-K', 'V-HUME']])}. "
        else:
            plan += "Your NPK levels are well-balanced. "
            
        plan += (
            "We recommend applying BIO-NPK at 1-2 Litres per acre mixed with organic manure as a basal dressing. "
            "Incorporate V-ZYME GR granules (8 kg/acre) during land preparation to stimulate root growth."
        )

        return {
            "soil_health_score": score,
            "deficiency_report": deficiencies,
            "excess_report": excess,
            "suitable_crops": suitable_crops,
            "recommended_products": recommended_products,
            "fertilization_plan": plan
        }

    @staticmethod
    def calculate_dosage(db: Session, crop: str, product_name: str, area: float, unit: str) -> Dict[str, Any]:
        """
        Dosage Calculator service logic.
        """
        product = db.query(Product).filter(Product.product_name.ilike(product_name)).first()
        if not product:
            raise ValueError(f"Vishakan product '{product_name}' not found.")
            
        # Convert area to acres
        acres = area
        if unit.lower() == "hectares":
            acres = area * 2.47105
            
        # Calculate dosage volume
        import re
        dosage_str = product.dosage
        # Find quantity from string e.g. "2.5 ml/L water" or "10 kg/acre"
        match_ml = re.search(r"([\d.]+)\s*ml", dosage_str, re.IGNORECASE)
        match_kg = re.search(r"([\d.]+)\s*kg", dosage_str, re.IGNORECASE)
        
        water_volume = acres * 200 # Standard 200 Litres of water per acre for foliar spray
        
        if match_ml:
            ml_per_liter = float(match_ml.group(1))
            total_ml = ml_per_liter * water_volume
            # convert to Litres or ml format
            if total_ml >= 1000:
                required_qty = f"{total_ml / 1000:.2f} Litres"
            else:
                required_qty = f"{total_ml:.0f} ml"
            mixing_ratio = f"{ml_per_liter} ml per Litre of water"
        elif match_kg:
            kg_per_acre = float(match_kg.group(1))
            total_kg = kg_per_acre * acres
            required_qty = f"{total_kg:.2f} kg"
            mixing_ratio = f"{kg_per_acre} kg per acre"
        else:
            # fallback
            required_qty = f"Refer to label instructions for {product_name}"
            mixing_ratio = "Standard label instructions"

        # Calculate estimated cost
        estimated_cost = product.price * acres
        
        # Custom application schedule based on category
        cat = product.category.lower()
        if "fertilizer" in cat:
            schedule = "Apply at sowing/transplanting stage. Repeat after 30 days of growth."
        elif "fungicide" in cat or "pesticide" in cat:
            schedule = "Apply preventively or immediately on first sight of symptoms. Repeat every 10-15 days depending on severity."
        elif "stimulant" in cat:
            schedule = "Apply at pre-flowering and active fruit/grain development stages to maximize yield."
        else:
            schedule = "Apply during active growth periods according to crop needs."
            
        return {
            "required_quantity": required_qty,
            "mixing_ratio": mixing_ratio,
            "application_schedule": schedule,
            "estimated_cost": round(estimated_cost, 2),
            "water_volume_liters": round(water_volume, 1)
        }

crop_service = CropService()
