"""
Service Mesh Observatory - Main FastAPI Application
Provides REST API and WebSocket endpoints for service mesh observability
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from contextlib import asynccontextmanager
import structlog
import uvicorn

from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.websocket import connection_manager
from app.services.metrics_collector import metrics_collector
from app.db.session import init_db

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'observatory_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'observatory_api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Service Mesh Observatory API")

    # Initialize database
    await init_db()

    # Start metrics collector background task
    await metrics_collector.start()

    yield

    # Cleanup
    logger.info("Shutting down Service Mesh Observatory API")
    await metrics_collector.stop()

app = FastAPI(
    title="Service Mesh Observatory API",
    description="Observability and security platform for service mesh deployments",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness probe"""
    return {"status": "healthy", "service": "service-mesh-observatory"}

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Kubernetes readiness probe"""
    # Check database connection
    try:
        from app.db.session import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "connected"
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "database": "disconnected"}
        )

    return {
        "status": "ready",
        "database": db_status,
        "metrics_collector": "running" if metrics_collector.is_running else "stopped"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from starlette.responses import Response
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time service mesh updates
    Pushes metrics, topology changes, and alerts to connected clients
    """
    await connection_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            logger.debug("WebSocket message received", message=data)

            # Echo back for testing
            await websocket.send_json({"type": "ack", "message": "received"})

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        connection_manager.disconnect(websocket)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Service Mesh Observatory API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health",
        "ready": "/ready",
        "metrics": "/metrics"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
