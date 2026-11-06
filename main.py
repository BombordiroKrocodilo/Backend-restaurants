from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time

from app.db import Base, engine
from app.routers import restaurants, reviews


app = FastAPI(title="Restaurants API", version="2.0")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    print(f"{request.method} {request.url.path} {response.status_code} {elapsed:.1f}ms")
    return response

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    err = exc.errors()[0]
    field = err["loc"][-1] if err["loc"] else "body"
    return JSONResponse(status_code=400, content={"error": err["msg"], "field": str(field)})

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(restaurants.router)
app.include_router(reviews.router)