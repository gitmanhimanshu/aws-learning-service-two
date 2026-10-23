# AWS Learning - Service Two (Processing Service)

FastAPI microservice demonstrating asynchronous data processing and service-to-service internal communication.

## Features
- Endpoints:
  - `GET /` & `GET /service2`: Welcome message.
  - `GET /health` & `GET /service2/health`: Health check (used by ALB Target Group).
  - `GET /info` & `GET /service2/info`: Service metadata, version, and active environment.
  - `GET /process` & `GET /service2/process`: Simulates business logic/processing.
  - `GET /service-one` & `GET /service2/service-one`: Queries Service 1 internally.
- Structured logging with timestamps and duration.

## Local Setup (Without Docker)

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux / macOS:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run service:**
   ```bash
   python main.py
   # Or using uvicorn directly:
   uvicorn main:app --host 0.0.0.0 --port 8002
   ```

4. **Verify:**
   - Health check: `http://localhost:8002/health`
   - Process endpoint: `http://localhost:8002/process`
   - Inter-service call: `http://localhost:8002/service-one` (Ensure Service 1 is running on port 8001).

## Sample Responses

### `GET /process`
```json
{
  "service": "aws-learning-service-two",
  "environment": "dev",
  "result": "processing successful",
  "processed_at": "2026-10-23T08:00:00Z",
  "batch_id": "batch-1774252800"
}
```

### `GET /service-one`
```json
{
  "service": "aws-learning-service-two",
  "status": "success",
  "message": "Successfully communicated with Service 1",
  "service_one_response": {
    "service": "aws-learning-service-one",
    "version": "1.0.0",
    "environment": "dev",
    "status": "running"
  }
}
```

