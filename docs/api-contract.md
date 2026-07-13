# API Contract - VisionGuard AI

This document defines the API contract between the React frontend and the FastAPI backend. All backend endpoints satisfy these schemas and behavioral contracts.

---

## 🔒 Authentication & Authorization

All endpoints except `/auth/signup`, `/auth/login`, and `/health` require a valid JWT token in the `Authorization` header:
`Authorization: Bearer <JWT_TOKEN>`

Roles: `User` and `Admin`.

---

### 1. User Sign Up
* **Endpoint:** `POST /auth/signup`
* **Content-Type:** `application/json`
* **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "strongpassword123",
    "full_name": "John Doe"
  }
  ```
* **Success Response (201 Created):**
  ```json
  {
    "user_id": "d3b07384-d113-4956-a534-7c5e5d3cd3d2",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "User",
    "message": "User registered successfully. Please verify your email."
  }
  ```
* **Error Response (400 Bad Request):**
  ```json
  {
    "detail": "Email already registered"
  }
  ```

---

### 2. User Login
* **Endpoint:** `POST /auth/login`
* **Content-Type:** `application/json`
* **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "strongpassword123"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "def456...",
    "token_type": "bearer",
    "user": {
      "id": "d3b07384-d113-4956-a534-7c5e5d3cd3d2",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "User"
    }
  }
  ```
* **Error Response (401 Unauthorized):**
  ```json
  {
    "detail": "Invalid credentials"
  }
  ```

---

### 3. User Logout
* **Endpoint:** `POST /auth/logout`
* **Headers:** `Authorization: Bearer <JWT_TOKEN>`
* **Success Response (200 OK):**
  ```json
  {
    "message": "Successfully logged out"
  }
  ```

---

### 4. Get Current User Profile
* **Endpoint:** `GET /auth/me`
* **Headers:** `Authorization: Bearer <JWT_TOKEN>`
* **Success Response (200 OK):**
  ```json
  {
    "id": "d3b07384-d113-4956-a534-7c5e5d3cd3d2",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "User",
    "created_at": "2026-07-13T00:00:00Z"
  }
  ```

---

## 🖼️ Image Prediction & Analysis

### 5. Upload & Predict Image
* **Endpoint:** `POST /predict`
* **Headers:** `Authorization: Bearer <JWT_TOKEN>`
* **Content-Type:** `multipart/form-data`
* **Request Form-Data:**
  * `file`: (Binary image file)
* **Success Response (200 OK):**
  ```json
  {
    "id": "f5195e7c-a496-4db0-9b48-d3e91129ea5b",
    "prediction": "AI Generated",
    "confidence": 97.8,
    "heatmap_url": "https://<supabase-url>/storage/v1/object/public/heatmaps/f5195e7c_heatmap.png",
    "overlay_url": "https://<supabase-url>/storage/v1/object/public/heatmaps/f5195e7c_overlay.png",
    "processing_time": 0.42,
    "model_version": "1.0.0",
    "created_at": "2026-07-13T05:58:10Z"
  }
  ```
* **Error Response (400 Bad Request):**
  ```json
  {
    "detail": "Invalid file format. Only JPG, PNG, WEBP are supported."
  }
  ```

---

### 6. Get Single Prediction Details
* **Endpoint:** `GET /prediction/{id}`
* **Headers:** `Authorization: Bearer <JWT_TOKEN>`
* **Success Response (200 OK):**
  ```json
  {
    "id": "f5195e7c-a496-4db0-9b48-d3e91129ea5b",
    "original_image_url": "https://<supabase-url>/storage/v1/object/public/original-images/f5195e7c.png",
    "prediction": "AI Generated",
    "confidence": 97.8,
    "heatmap_url": "https://<supabase-url>/storage/v1/object/public/heatmaps/f5195e7c_heatmap.png",
    "overlay_url": "https://<supabase-url>/storage/v1/object/public/heatmaps/f5195e7c_overlay.png",
    "processing_time": 0.42,
    "model_version": "1.0.0",
    "created_at": "2026-07-13T05:58:10Z"
  }
  ```

---

### 7. Get Prediction History
* **Endpoint:** `GET /history`
* **Headers:** `Authorization: Bearer <JWT_TOKEN>`
* **Query Parameters:**
  * `page` (optional, default: 1)
  * `limit` (optional, default: 10)
* **Success Response (200 OK):**
  ```json
  {
    "total": 45,
    "page": 1,
    "limit": 10,
    "results": [
      {
        "id": "f5195e7c-a496-4db0-9b48-d3e91129ea5b",
        "original_image_url": "https://...",
        "prediction": "AI Generated",
        "confidence": 97.8,
        "created_at": "2026-07-13T05:58:10Z"
      }
    ]
  }
  ```

---

## 📦 Batch Uploads

### 8. Start Async Batch Job
* **Endpoint:** `POST /batch`
* **Headers:** `Authorization: Bearer <JWT_TOKEN>`
* **Content-Type:** `multipart/form-data`
* **Request Form-Data:**
  * `files`: (Multiple binary image files OR a ZIP file containing images)
* **Success Response (202 Accepted):**
  ```json
  {
    "job_id": "8ca6d98c-8f9d-476c-9418-f2b7a37bf7c9",
    "status": "PENDING",
    "total_images": 5,
    "message": "Batch processing started asynchronously."
  }
  ```

---

### 9. Check Batch Job Status
* **Endpoint:** `GET /batch/{job_id}`
* **Headers:** `Authorization: Bearer <JWT_TOKEN>`
* **Success Response (200 OK):**
  ```json
  {
    "job_id": "8ca6d98c-8f9d-476c-9418-f2b7a37bf7c9",
    "status": "PROCESSING",
    "total_images": 5,
    "processed_images": 2,
    "results": [
      {
        "id": "e932b1ff-...",
        "prediction": "Real",
        "confidence": 99.1,
        "status": "SUCCESS"
      }
    ]
  }
  ```

---

## 📊 Dashboard & Analytics

### 10. Get User Dashboard Summary
* **Endpoint:** `GET /dashboard`
* **Headers:** `Authorization: Bearer <JWT_TOKEN>`
* **Success Response (200 OK):**
  ```json
  {
    "total_scans": 150,
    "real_count": 90,
    "ai_generated_count": 60,
    "recent_activity": [
      {
        "id": "f5195e7c-...",
        "prediction": "AI Generated",
        "confidence": 97.8,
        "timestamp": "2026-07-13T05:58:10Z"
      }
    ]
  }
  ```

---

### 11. Get Analytics Details
* **Endpoint:** `GET /analytics`
* **Headers:** `Authorization: Bearer <JWT_TOKEN>`
* **Success Response (200 OK):**
  ```json
  {
    "accuracy_rate": 96.5,
    "average_processing_time": 0.38,
    "monthly_activity": [
      { "month": "July", "scans": 45 }
    ],
    "distribution": {
      "real": 60.0,
      "ai": 40.0
    }
  }
  ```

---

## 👑 Administration (Admin Role Required)

### 12. Get System Settings & Model Management
* **Endpoint:** `GET /admin`
* **Headers:** `Authorization: Bearer <JWT_TOKEN>`
* **Success Response (200 OK):**
  ```json
  {
    "model_versions": [
      {
        "version": "1.0.0",
        "active": true,
        "accuracy": 96.5,
        "created_at": "2026-06-01T00:00:00Z"
      }
    ],
    "total_users": 820,
    "system_status": "Healthy"
  }
  ```

---

## 🩺 System Health

### 13. Health Check
* **Endpoint:** `GET /health`
* **Success Response (200 OK):**
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-07-13T05:58:10Z",
    "version": "1.0.0"
  }
  ```
