from fastapi import FastAPI
from app.routers import listings
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="PropAI Listings API",
    version="0.1.0"
)

app.include_router(listings.router)

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}