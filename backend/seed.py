import csv
import json
import os
import sys

# Ensure backend directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal, engine, Base
from backend.app.models.product import Product
from backend.app.models.farmer import Farmer, UserRole
from backend.app.core.security import get_password_hash
from backend.app.core.config import settings

def parse_csv_list(val: str):
    if not val or val.lower() == 'none' or val == '':
        return []
    return [x.strip() for x in val.split(';')]

def seed_database():
    print("Initializing Database Seeding...")
    # Create tables if they do not exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # Check if products already seeded
        if db.query(Product).count() > 0:
            print("Database already contains product records. Skipping database seeding.")
        else:
            csv_path = "backend/data/products.csv"
            if not os.path.exists(csv_path):
                print(f"Error: Seed file not found at {csv_path}")
                return
            
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    crops = parse_csv_list(row['suitable_crops'])
                    diseases = parse_csv_list(row['suitable_diseases'])
                    
                    product = Product(
                        product_name=row['product_name'].strip(),
                        category=row['category'].strip(),
                        description=row['description'].strip(),
                        dosage=row['dosage'].strip(),
                        benefits=row['benefits'].strip(),
                        application_method=row['application_method'].strip(),
                        suitable_crops=crops,
                        suitable_diseases=diseases,
                        price=float(row['price']),
                        unit=row['unit'].strip()
                    )
                    db.add(product)
            db.commit()
            print(f"Database seeded with {db.query(Product).count()} products successfully.")
        
        # Seed default Admin User
        admin_mobile = "9999999999"
        existing_admin = db.query(Farmer).filter(Farmer.mobile == admin_mobile).first()
        if not existing_admin:
            hashed_pw = get_password_hash("vishakan_admin_123")
            admin = Farmer(
                name="Vishakan Admin",
                mobile=admin_mobile,
                hashed_password=hashed_pw,
                role=UserRole.ADMIN,
                district="Coimbatore",
                state="Tamil Nadu",
                language="Tamil"
            )
            db.add(admin)
            db.commit()
            print(f"Default Admin user created (Mobile: {admin_mobile}, Password: vishakan_admin_123)")
            
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

def seed_chromadb():
    print("Initializing ChromaDB Seeding...")
    try:
        # Initialize ChromaDB client
        import chromadb
        client = chromadb.PersistentClient(path=settings.VECTOR_DB_DIR)
        
        # Create or fetch collection
        collection_name = "vishakan_products"
        try:
            client.delete_collection(name=collection_name)
        except Exception:
            pass
        collection = client.create_collection(name=collection_name)
        
        db: Session = SessionLocal()
        products = db.query(Product).all()
        db.close()
        
        if not products:
            print("No products in database to seed vector store. Seed PostgreSQL first.")
            return

        documents = []
        metadatas = []
        ids = []
        
        for p in products:
            doc = (
                f"Product Name: {p.product_name}\n"
                f"Category: {p.category}\n"
                f"Description: {p.description}\n"
                f"Benefits: {p.benefits}\n"
                f"Dosage: {p.dosage}\n"
                f"Application Method: {p.application_method}\n"
                f"Crops: {', '.join(p.suitable_crops) if p.suitable_crops else 'All crops'}\n"
                f"Diseases: {', '.join(p.suitable_diseases) if p.suitable_diseases else 'None'}"
            )
            documents.append(doc)
            metadatas.append({
                "id": p.id,
                "name": p.product_name,
                "category": p.category
            })
            ids.append(f"prod_{p.id}")
        
        # Since we might run in standard offline container, we'll construct mock embeddings if Gemini key is missing.
        # LangChain or Gemini embedding classes require real API keys. If we use custom embeddings, Chroma handles
        # it natively or we can just supply simple numeric lists as embeddings to keep it working.
        
        # Check for Gemini API key
        api_key = os.getenv("GEMINI_API_KEY", settings.GEMINI_API_KEY)
        if api_key:
            print("Gemini API key detected. Generating embeddings via GoogleGenAI...")
            # We can use langchain's GoogleGenAIEmbeddings
            from langchain_google_genai import GoogleGenAIEmbeddings
            embeddings_model = GoogleGenAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
            embeddings = embeddings_model.embed_documents(documents)
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
        else:
            print("Warning: GEMINI_API_KEY not set. Seeding ChromaDB with local mock embeddings.")
            # Supply default dummy embeddings (Chroma expects float list of same dimension e.g. 768)
            mock_embeddings = [[0.1] * 768 for _ in range(len(documents))]
            collection.add(
                documents=documents,
                embeddings=mock_embeddings,
                metadatas=metadatas,
                ids=ids
            )
        
        print(f"ChromaDB seeded with {len(ids)} documents successfully.")
    except Exception as e:
        print(f"Error seeding ChromaDB: {e}")

if __name__ == "__main__":
    seed_database()
    seed_chromadb()
