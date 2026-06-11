# Vishakan Biotech Smart Farming Assistant Backend

This repository houses the production-ready FastAPI backend for **Vishakan Biotech Smart Farming Assistant**, developed specifically for **Vishakan Biotech Pvt Ltd, Coimbatore, Tamil Nadu**.

Our platform operates under the core tagline: **"Prosperity Through Biologicals"**, prioritizing botanical and bio-organic inputs for crop advisory, soil correction, and disease treatment.

---

## 🚀 Key Features

1. **Authentication System**: Secure JWT token registration, login, and Role-Based Access Control (Admin, Farmer, Sales Team).
2. **Crop Recommendation**: Multi-model classification (Random Forest, XGBoost, LightGBM) selecting the highest accuracy model for matching soil/climate with the best cash/food crops and matching Vishakan inputs.
3. **Product Advisor**: Dynamic biological recommendation engine mapped to crops, soils, and growth stages.
4. **Plant Disease Detection**: Computer vision classification using EfficientNetB0 (TensorFlow transfer learning) to scan plant tissue and suggest bio-fungicides/pesticides.
5. **Soil Health Analysis**: Diagnostic report tracking NPK, pH, and Organic Carbon to generate a customized fertilizing and amendment schedule.
6. **Dosage Calculator**: Accurate area-based measurement computing required bio-input volume, mixing instructions, and estimated farm costs.
7. **Voice Assistant**: Integrated Whisper Speech-to-Text and gTTS Text-to-Speech support for regional languages (Tamil, Malayalam, Telugu, Kannada, English).
8. **AI Agronomist Chatbot**: Retrieval-Augmented Generation (RAG) using LangChain, Google Gemini, and ChromaDB vector store.
9. **Analytics Reporting**: Business intelligence endpoints compiling crop, disease, chatbot, and signup trends via SQLAlchemy aggregations.

---

## 🛠 Tech Stack

- **Framework**: Python 3.11, FastAPI, Pydantic, Uvicorn
- **ORM & DB**: SQLAlchemy, Alembic, PostgreSQL, SQLite (for testing)
- **Vector DB**: ChromaDB
- **ML / Deep Learning**: Scikit-Learn, XGBoost, LightGBM, TensorFlow (EfficientNetB0)
- **Generative AI / Voice**: LangChain, Google Gemini, OpenAI Whisper, gTTS
- **Task Broker**: Redis, Celery (for background task queues)
- **Containerization**: Docker, Docker Compose

---

## 📂 Project Structure

```text
vishakan_backend/
├── backend/
│   ├── app/
│   │   ├── api/             # API Endpoints (auth, crop, disease, products, chatbot, voice, analytics)
│   │   ├── core/            # App configurations, database connections, security helpers, celery config
│   │   ├── models/          # SQLAlchemy Database Models (Farmer, Product, CropRecommendation, etc.)
│   │   ├── schemas/         # Pydantic schemas for request/response validation
│   │   ├── services/        # Service layer containing core business, ML, and RAG logic
│   │   ├── ml_models/       # Serialized models (.pkl, .h5) & training scripts
│   │   ├── vector_db/       # ChromaDB vector store files
│   │   ├── data/            # Static datasets (products.csv, leaf scan uploads)
│   │   └── main.py          # Central app initialization
│   ├── tests/               # Pytest automated test files (auth, service layers)
│   ├── Dockerfile           # Multi-stage image build
│   ├── docker-compose.yml   # Stack composition orchestration
│   ├── requirements.txt     # Locked production dependencies
│   ├── .env.example         # System environmental variables template
│   ├── alembic.ini          # Alembic migrations configuration
│   └── seed.py              # Script to seed database and ChromaDB vector store
└── README.md
```

---

## ⚙️ Local Setup Instructions

### Prerequisites
- Python 3.11+ installed.
- PostgreSQL and Redis servers running locally (if not using Docker).

### Step 1: Clone and Configure Environment
1. Copy the environment configuration template:
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Populate the `.env` variables (e.g. `DATABASE_URL`, `REDIS_URL`, and your `GEMINI_API_KEY`). If the Gemini API key is left blank, the app will execute in a highly detailed mock/offline mode automatically.

### Step 2: Establish Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### Step 3: Train Machine Learning Models
Generate synthetic datasets and serialize the ML classifiers locally:
```bash
# Train Crop Recommendation Model (RF, XGBoost, LightGBM)
python backend/app/ml_models/train_crop_model.py

# Build/Compile Plant Pathology Model (EfficientNetB0)
python backend/app/ml_models/train_disease_model.py
```

### Step 4: Seed PostgreSQL Database & ChromaDB Vector Store
Initialize the database tables and populate product records + embeddings:
```bash
python backend/seed.py
```
*Note: A default Admin User is created on seeding:*
- **Mobile**: `9999999999`
- **Password**: `vishakan_admin_123`

### Step 5: Run FastAPI Server
Start the development server:
```bash
uvicorn backend.app.main:app --reload --port 8000
```
- Interactive API Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Redoc Reference Manual: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🐳 Running with Docker

Orchestrate the entire backend infrastructure (FastAPI, Postgres, Redis, Celery Worker) using a single command:

1. Ensure Docker is running.
2. Build and launch containers:
   ```bash
   docker-compose up --build
   ```
The application will automatically perform schema creation, database seeding, vector store generation, and spin up on [http://localhost:8000](http://localhost:8000).

---

## 🧪 Running Automated Tests

Run the complete automated unit/integration test suite:
```bash
pytest backend/tests/ -v
```
*The test suite utilizes in-memory SQLite instances to run instantly without affecting your live PostgreSQL databases.*

---

## ☁️ Production Deployment Guide

### Option 1: AWS Deployment (EC2 + RDS + ElastiCache)
1. **Database**: Spin up an AWS RDS PostgreSQL instance. Configure `DATABASE_URL` in environment variables.
2. **Caching**: Setup AWS ElastiCache Redis. Configure `REDIS_URL`.
3. **Application**: Launch an EC2 instance (Ubuntu), clone repository, configure `.env` using RDS and ElastiCache connections.
4. **Proxy**: Install Nginx as a reverse proxy forwarding requests from port 80/443 to port 8000.
5. **SSL**: Configure free SSL certificates via `certbot` (Let's Encrypt).
6. **Process Manager**: Run the application under `systemd` using `gunicorn`:
   ```bash
   gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

### Option 2: Render
1. Create a **Web Service** on Render linking your GitHub repository.
2. Choose **Docker** as the environment (Render will automatically detect the `Dockerfile`).
3. Add a Render **PostgreSQL database** and Render **Redis instance**.
4. Bind environment variables under the service settings:
   - `DATABASE_URL` (link to Postgres)
   - `REDIS_URL` (link to Redis)
   - `GEMINI_API_KEY`
   - `SECRET_KEY`

### Option 3: Railway
1. Create a New Project on Railway.
2. Select **Deploy from GitHub repo**.
3. Click "New" -> "Database" -> "Add PostgreSQL" and "Add Redis".
4. Railway automatically injects connection strings into variables. Map them inside the Web Service environment variables tab.
5. Expose port `8000` under Web settings.
