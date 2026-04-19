from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from app.routers import listings, auth

app = FastAPI(
    title="PropAI Listings API",
    version="0.2.0"
)

app.include_router(auth.router)
app.include_router(listings.router)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": _status_code_label(exc.status_code)},
        headers=getattr(exc, "headers", None),
    )


def _status_code_label(status_code: int) -> str:
    labels = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
    }
    return labels.get(status_code, f"HTTP_{status_code}")


@app.get("/")
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.2.0"}
