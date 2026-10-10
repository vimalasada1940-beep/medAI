from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings

# Import API Routers
from app.routes.dashboard import router as dashboard_router
from app.routes.inventory import router as inventory_router
from app.routes.alerts import router as alerts_router
from app.routes.redistribution import router as redistribution_router
from app.routes.indent import router as indent_router
from app.routes.ingestion import router as ingestion_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Medicine Stock-Out Early Warning & Smart Redistribution System for PHCs (Student Decision-Support Prototype)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration for local React Vite development frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "ERROR",
            "message": "An unexpected error occurred on the MediPulse server.",
            "detail": str(exc)
        }
    )

# Health Check Endpoint
@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "prototype_disclaimer": "Student decision-support prototype. Not clinically validated or government deployed."
    }

# Register API Routers under /api/v1 prefix
API_PREFIX = "/api/v1"
app.include_router(dashboard_router, prefix=API_PREFIX)
app.include_router(inventory_router, prefix=API_PREFIX)
app.include_router(alerts_router, prefix=API_PREFIX)
app.include_router(redistribution_router, prefix=API_PREFIX)
app.include_router(indent_router, prefix=API_PREFIX)
app.include_router(ingestion_router, prefix=API_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
