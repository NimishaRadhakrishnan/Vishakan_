from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.models.product import Product
from backend.app.schemas.product import ProductResponse

class ProductService:
    @staticmethod
    def get_products(db: Session, category: Optional[str] = None, search: Optional[str] = None) -> List[Product]:
        query = db.query(Product)
        if category:
            query = query.filter(Product.category.ilike(category))
        if search:
            query = query.filter(
                (Product.product_name.ilike(f"%{search}%")) |
                (Product.description.ilike(f"%{search}%")) |
                (Product.benefits.ilike(f"%{search}%"))
            )
        return query.all()

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def get_products_by_names(db: Session, names: List[str]) -> List[Product]:
        return db.query(Product).filter(Product.product_name.in_(names)).all()

    @staticmethod
    def recommend_products(db: Session, crop_name: str, crop_stage: Optional[str] = None, soil_type: Optional[str] = None) -> List[Product]:
        """
        Recommends products based on crop name, growth stage, and soil type.
        Prioritizes bio-fertilizers/stimulants suitable for the crop.
        """
        all_products = db.query(Product).all()
        recommended = []
        
        for p in all_products:
            # Check crop suitability
            crop_match = False
            if p.suitable_crops:
                for c in p.suitable_crops:
                    if c.lower() in [crop_name.lower(), "all crops"]:
                        crop_match = True
                        break
            else:
                crop_match = True # default to all crops if empty
            
            if not crop_match:
                continue

            # Stage filtering logic (rule-based heuristic)
            stage_match = True
            if crop_stage:
                stage = crop_stage.lower()
                cat = p.category.lower()
                if "sowing" in stage or "transplanting" in stage:
                    # Basal / root development products (like V-RICH mycorrhiza, V-PHOS)
                    stage_match = "rich" in p.product_name.lower() or "phos" in p.product_name.lower() or "fertilizer" in cat
                elif "flowering" in stage or "reproductive" in stage:
                    # Stimulants / Potash (V-COMBINE, V-BIOPOTASH, V-MIRACLE)
                    stage_match = "combine" in p.product_name.lower() or "potash" in p.product_name.lower() or "stimulant" in cat
                elif "stress" in stage or "summer" in stage:
                    stage_match = "chill" in p.product_name.lower() or "methylo" in p.product_name.lower()
            
            if stage_match:
                recommended.append(p)
                
        return recommended

product_service = ProductService()
