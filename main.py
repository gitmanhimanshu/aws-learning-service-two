import time
import logging
import datetime
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from config import settings

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] service=%(name)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ"
)
logger = logging.getLogger(settings.SERVICE_NAME)

app = FastAPI(
    title="AWS Learning - Service Two (Processing Service)",
    version=settings.VERSION,
    description="Microservice 2: Performs processing and interacts with Service 1."
)

@app.middleware("http")
async def structured_log_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    
    logger.info(
        "environment=%s method=%s path=%s status=%d duration_ms=%.2f client=%s",
        settings.ENVIRONMENT,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request.client.host if request.client else "unknown"
    )
    return response

def get_welcome_data():
    return {
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT,
        "message": "Welcome to AWS Learning Processing Service",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }

def get_health_data():
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }

def get_info_data():
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running"
    }

def get_process_data():
    return {
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT,
        "result": "processing successful",
        "processed_at": datetime.datetime.utcnow().isoformat() + "Z",
        "batch_id": "batch-" + str(int(time.time()))
    }

async def call_service_one():
    target_url = f"{settings.SERVICE_ONE_URL.rstrip('/')}/info"
    logger.info("Initiating service-to-service call to Service 1: %s", target_url)
    try:
        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
            resp = await client.get(target_url)
            resp.raise_for_status()
            service_one_data = resp.json()
            return {
                "service": settings.SERVICE_NAME,
                "status": "success",
                "message": "Successfully communicated with Service 1",
                "service_one_response": service_one_data
            }
    except httpx.RequestError as exc:
        logger.error("Failed to reach Service 1 at %s: %s", target_url, str(exc))
        return JSONResponse(
            status_code=503,
            content={
                "service": settings.SERVICE_NAME,
                "status": "error",
                "message": f"Could not reach Service 1 at {target_url}",
                "error": str(exc)
            }
        )

# Standard endpoints
@app.get("/")
def read_root():
    return get_welcome_data()

@app.get("/health")
def read_health():
    return get_health_data()

@app.get("/info")
def read_info():
    return get_info_data()

@app.get("/process")
def read_process():
    return get_process_data()

@app.get("/service-one")
async def read_service_one():
    return await call_service_one()

# ALB path-based routing compatibility endpoints (/service2/*)
@app.get("/service2")
@app.get("/service2/")
def read_root_prefixed():
    return get_welcome_data()

@app.get("/service2/health")
def read_health_prefixed():
    return get_health_data()

@app.get("/service2/info")
def read_info_prefixed():
    return get_info_data()

@app.get("/service2/process")
def read_process_prefixed():
    return get_process_data()

@app.get("/service2/service-one")
async def read_service_one_prefixed():
    return await call_service_one()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)

