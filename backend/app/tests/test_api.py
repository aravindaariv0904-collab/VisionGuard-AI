import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

# Cache token globally for subsequent tests
auth_token = None
user_id = None

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_signup():
    payload = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 201
    assert "user_id" in response.json()
    assert response.json()["email"] == "testuser@example.com"

def test_login():
    global auth_token, user_id
    payload = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    
    auth_token = data["access_token"]
    user_id = data["user"]["id"]

def test_get_me():
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["role"] == "User"

def test_predict_image_unauthorized():
    # Attempt upload without token
    response = client.post("/predict")
    assert response.status_code == 401 # HTTPBearer missing token

def test_predict_image():
    # Create a small dummy image in memory
    from PIL import Image
    import io
    
    img = Image.new("RGB", (300, 300), color="blue")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    files = {"file": ("test.png", img_bytes, "image/png")}
    
    response = client.post("/predict", headers=headers, files=files)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["prediction"] in ["Real", "AI Generated"]
    assert "confidence" in data
    assert "heatmap_url" in data
    assert "overlay_url" in data
    
    # Save prediction ID to test detail endpoint
    pred_id = data["id"]
    
    # Test Detail endpoint
    detail_res = client.get(f"/prediction/{pred_id}", headers=headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == pred_id

def test_history():
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "results" in data
    assert len(data["results"]) >= 1

def test_dashboard():
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_scans" in data
    assert "real_count" in data
    assert "recent_activity" in data
    assert data["total_scans"] >= 1

def test_analytics():
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/analytics", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "accuracy_rate" in data
    assert "average_processing_time" in data
    assert "distribution" in data

def test_batch_processing():
    # Test batch file submission
    from PIL import Image
    import io
    
    img = Image.new("RGB", (100, 100), color="red")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    files = [
        ("files", ("image1.png", img_bytes, "image/png")),
        ("files", ("image2.png", img_bytes, "image/png"))
    ]
    
    response = client.post("/batch", headers=headers, files=files)
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "PENDING"
    assert data["total_images"] == 2
    
    job_id = data["job_id"]
    
    # Check status
    status_res = client.get(f"/batch/{job_id}", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["job_id"] == job_id

def test_admin_forbidden():
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/admin", headers=headers)
    assert response.status_code == 403 # Forbidden for normal user

def test_admin_success():
    # Login as admin
    payload = {
        "email": "admin@example.com",
        "password": "adminpassword123"
    }
    login_res = client.post("/auth/login", json=payload)
    admin_token = login_res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/admin", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "model_versions" in data
    assert "total_users" in data
    assert data["system_status"] == "Healthy"
