from fastapi import FastAPI
from app.routers import listings

app = FastAPI(
    title="PropAI Listings API",
    version="0.1.0"
)

app.include_router(listings.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}