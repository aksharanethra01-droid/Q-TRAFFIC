from fastapi import FastAPI
from api.routes import router


app = FastAPI(
    title="Q-TRAFFIC API",
    description="Quantum-Enhanced Adaptive Urban Traffic Optimization API",
    version="1.0.0"
)


app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Q-TRAFFIC API is running",
        "status": "online"
    }