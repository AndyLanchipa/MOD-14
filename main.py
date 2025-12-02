from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.models import calculation_model, user_model
from app.routers import calculation_routes, user_routes

# Create tables if they don't exist (for Docker/local dev)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Calculation API",
    description="FastAPI app for calculations and user management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_routes.router)
app.include_router(calculation_routes.router)


@app.get("/")
async def root():
    return {"message": "Calculation API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
