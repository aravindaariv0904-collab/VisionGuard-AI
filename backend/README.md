# VisionGuard AI Backend Service

An Explainable AI Image Authenticity Detection Platform API. Built with **FastAPI (Python 3.12/3.13)**, **Supabase (Auth, DB, Storage)**, and **PyTorch (EfficientNet-B0 & Grad-CAM)**.

---

## 📂 Backend Project Structure

```
backend/
├── app/
│   ├── api/             # API Router endpoints (auth, predict, batch, etc.)
│   ├── core/            # Global configuration & security middleware
│   ├── database/        # Database clients & SQL migrations schema
│   ├── schemas/         # Pydantic data request/response validators
│   ├── services/        # AI predictor, Grad-CAM, & storage services
│   ├── tests/           # Integration & API test suites
│   ├── __init__.py
│   └── main.py          # Server main setup file
├── static/              # Storage local fallback for offline development
├── Dockerfile           # Backend containerization blueprint
├── requirements.txt     # Python package requirements
├── .env.example         # Template config file
└── README.md            # Project and setup documentation
```

---

## 🚀 Getting Started

### 1. Requirements
Ensure you have **Python 3.12+** installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables Setup
Copy the example file to `.env`:
```bash
cp .env.example .env
```
Update the `.env` parameters with your Supabase credentials. If running 100% offline, the backend automatically falls back to in-memory caching and mock storage simulation, so you can still run the server with the placeholder configurations.

### 4. Run the API Server
To start the FastAPI development server:
```bash
uvicorn app.main:app --reload --port 8000
```
Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser to inspect the Swagger UI interactive API documentation.

---

## 🛠️ Docker Deployment

To build and run the backend inside a Docker container:
```bash
# Build
docker build -t visionguard-backend .

# Run
docker run -p 8000:8000 --env-file .env visionguard-backend
```

---

## 🛡️ Database & Storage (Supabase)

The migration schema script located at [01_schema.sql](app/database/migrations/01_schema.sql) automates the configuration of the Supabase PostgreSQL database:
* **Profiles Syncing:** An active PostgreSQL trigger (`on_auth_user_created`) automatically copies user registrations from Supabase `auth.users` to `public.users`.
* **Row Level Security (RLS):** All tables enforce RLS policies preventing unauthorized reads/writes.
* **Storage Buckets:** Buckets `original-images`, `heatmaps`, `reports`, `batch-images`, and `avatars` are created with policies allowing users to upload and view their own files.

---

## 🧠 Explainable AI & Grad-CAM

The predictor layer located at [prediction_service.py](app/services/prediction_service.py):
1. Runs classification using a PyTorch-based **EfficientNet-B0** binary classifier.
2. Extracts feature maps from the final convolutional block (`features[-1]`).
3. Computes the backpropagated gradients of the score with respect to target activations.
4. Generates a 2D **Grad-CAM** heatmap overlay highlighting image regions that influenced the model decision.

---

## 🧪 Testing

We use `pytest` for automated test suites:
```bash
pytest app/tests/
```
The test suite validates:
* User registration proxy
* Local JWT signature parsing & verification
* Multi-part form image uploads
* AI result serialization & Grad-CAM outputs
* Paginated user scan history query
* Asynchronous batch jobs processing
* Admin dashboard authorizations
