import os
import logging
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from backend.app.core.config import settings
from backend.app.models.chat import ChatHistory
import chromadb

logger = logging.getLogger(__name__)

# Fallback QA dictionary for offline / mock modes
FALLBACK_QA = {
    "yellow": (
        "Yellow leaves in paddy fields are typically caused by Nitrogen deficiency or Zinc deficiency. "
        "We highly recommend applying **V-NITRO** (Azotobacter, Azospirillum bio-fertilizer) at 2.5 ml per Litre of water as a foliar spray. "
        "If you suspect zinc deficiency (little leaf/bronzing), apply **V-ZINC** at 2 ml per Litre of water during the tillering stage."
    ),
    "leaf spot": (
        "For Leaf Spot, Blast, or Blight in crops, spray **V-CURE** (Pseudomonas fluorescens) at 2.5 ml per Litre of water. "
        "If the disease severity is high, alternate with **V-BACILI** (Bacillus subtilis) at 2 ml per Litre after 7-10 days. "
        "These bio-fungicides induce systemic resistance in the plant and suppress fungal growth."
    ),
    "banana": (
        "For Banana crops, we recommend the following Vishakan Biotech regime:\n"
        "1. Root growth: Apply **V-PHOS** (phosphate solubilizing bio-fertilizer) at 2 ml/L water.\n"
        "2. Soil Nematodes: Drench the soil with **V-NEMATO** (Purpureocillium lilacinum) at 3 ml/L water.\n"
        "3. Fruit Quality & Weight: Use **V-SOL-K** (potash mobilizing bio-fertilizer) at 2 ml/L water.\n"
        "4. Yield Booster: Foliar spray **V-COMBINE** at 2 ml/L water every 15 days."
    ),
    "paddy": (
        "For paddy cultivation, apply **V-RICH** (VAM mycorrhiza) at 10 kg/acre as basal dressing. "
        "Foliar spray **V-NITRO** and **V-PHOS** at 2.5 ml/L during tillering and panicle initiation. "
        "Use **V-CURE** preventively for Blast control."
    ),
    "coconut": (
        "For Coconut palms, apply **V-RICH** (100g per palm) and **V-PHOS** basal dose. "
        "Mobilize potassium using **V-SOL-K** or **V-BIOPOTASH** for copra content and nut size. "
        "To manage Phytophthora or stem bleeding, apply **V-KRISHONATE** (potassium phosphite) as root feeding or trunk injection."
    )
}

class ChatService:
    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self._init_vector_db()

    """def _init_vector_db(self):
        try:
            self.chroma_client = chromadb.PersistentClient(path=settings.VECTOR_DB_DIR)
            # Collection name matches seed.py
            self.collection = self.chroma_client.get_collection("vishakan_products")
            logger.info("ChromaDB connection initialized for Chatbot RAG.")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}. Chatbot will run in fallback mode.")"""

    def query_agronomist(self, db: Session, farmer_id: int, question: str) -> Dict[str, Any]:
        """
        Processes query using Gemini + ChromaDB (RAG) or simulated fallback.
        Logs chat history in DB.
        """
        answer = ""
        sources = []
        recommended_products = []
        
        # 1. Check for vector matches
        context_docs = []
        if self.collection:
            try:
                # Query Chroma
                # If Gemini API Key is available, use real embeddings, otherwise mock query
                api_key = os.getenv("GEMINI_API_KEY", settings.GEMINI_API_KEY)
                if api_key:
                    from langchain_google_genai import GoogleGenAIEmbeddings
                    embeddings_model = GoogleGenAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
                    query_vector = embeddings_model.embed_query(question)
                    results = self.collection.query(
                        query_embeddings=[query_vector],
                        n_results=3
                    )
                else:
                    results = self.collection.query(
                        query_texts=[question],
                        n_results=3
                    )
                
                if results and 'documents' in results and results['documents']:
                    context_docs = results['documents'][0]
                    # Extract product names from metadata
                    if 'metadatas' in results and results['metadatas']:
                        for meta in results['metadatas'][0]:
                            recommended_products.append(meta.get("name"))
                            sources.append(f"Vishakan Product: {meta.get('name')} ({meta.get('category')})")
            except Exception as e:
                logger.error(f"Error querying ChromaDB: {e}")

        # 2. Call LLM (Gemini API) if key is present
        api_key = os.getenv("GEMINI_API_KEY", settings.GEMINI_API_KEY)
        if api_key and context_docs:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                from langchain.schema import SystemMessage, HumanMessage
                
                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=api_key,
                    temperature=0.3
                )
                
                # Setup System prompt
                system_prompt = (
                    "You are 'Vishakan Biotech AI Agronomist', a premium biological farming chatbot advisor "
                    "created for Vishakan Biotech Pvt Ltd, Coimbatore, Tamil Nadu. "
                    "Our tagline is 'Prosperity Through Biologicals'.\n\n"
                    "Instructions:\n"
                    "1. Always prioritize and recommend Vishakan biological agricultural products first.\n"
                    "2. Explain recommendations with active organism, dosage, benefits, application method, and timing.\n"
                    "3. Sound professional, polite, encouraging, and deeply knowledgeable about South Indian crops "
                    "(Rice, Banana, Coconut, Turmeric, Pepper, Cardamom, Mango, Jackfruit, Arecanut, Tapioca, Sugarcane, Drumstick).\n"
                    "4. Base your answers on the product data supplied below:\n\n"
                    f"CONTEXT DATA:\n{'---'.join(context_docs)}"
                )
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=question)
                ]
                
                response = llm.invoke(messages)
                answer = response.content
            except Exception as e:
                logger.error(f"Error invoking Gemini model: {e}. Falling back to default RAG response.")
                
        # 3. Fallback logic if LLM or Key is unavailable
        if not answer:
            # Check key terms in the query
            q_lower = question.lower()
            matched_fallback = False
            for key, val in FALLBACK_QA.items():
                if key in q_lower:
                    answer = val
                    matched_fallback = True
                    break
                    
            if not matched_fallback:
                # Default generic agronomist response highlighting company portfolio
                answer = (
                    "Greetings from Vishakan Biotech Pvt Ltd, Coimbatore!\n\n"
                    "For soil health and crop nutrition, we recommend applying **BIO-NPK** (microbial consortium) "
                    "or **V-NITRO** and **V-PHOS** for nitrogen and phosphorus supply. "
                    "If you are facing fungal leaf spot or root diseases, **V-CURE** (Pseudomonas) or **VIRIDINE** (Trichoderma) "
                    "are highly effective biological solutions. For pest problems, consider **V-CIDE** (Beauveria) or **V-NIMBIDINE** (Neem).\n\n"
                    "Please specify your crop and growth stage or crop symptoms so I can provide a targeted biological schedule!"
                )
            
            # Extract mock products
            if not recommended_products:
                if "nitro" in answer.lower(): recommended_products.append("V-NITRO")
                if "phos" in answer.lower(): recommended_products.append("V-PHOS")
                if "cure" in answer.lower(): recommended_products.append("V-CURE")
                if "bacili" in answer.lower(): recommended_products.append("V-BACILI")
                if "viridine" in answer.lower(): recommended_products.append("VIRIDINE")
                if "nemato" in answer.lower(): recommended_products.append("V-NEMATO")
                
            sources.append("Vishakan Biotech Product Catalogue (Local Fallback Database)")

        # Save to DB
        chat_log = ChatHistory(
            farmer_id=farmer_id,
            question=question,
            answer=answer
        )
        db.add(chat_log)
        db.commit()
        db.refresh(chat_log)

        return {
            "answer": answer,
            "recommended_products": recommended_products,
            "context_sources": sources
        }

chat_service = ChatService()
