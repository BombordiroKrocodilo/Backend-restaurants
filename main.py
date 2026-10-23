from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import time

app = FastAPI(title="Restaurants API", version="1.0")

restaurants: dict[int, dict] = {}
next_id = 1

class RestaurantCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1, max_length=200)
    cuisine: str = Field(..., min_length=1, max_length=100)

    @field_validator("title", "address", "cuisine")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("поле не может быть пустым")
        return v

class RestaurantUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = Field(None, min_length=1, max_length=200)
    cuisine: Optional[str] = Field(None, min_length=1, max_length=100)

    @field_validator("title", "address", "cuisine")
    @classmethod
    def not_blank(cls, v):
        if v is not None and not v.strip():
            raise ValueError("поле не может быть пустым")
        return v

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

@app.post("/api/restaurants", status_code=201)
def create_restaurant(payload: RestaurantCreate):
    global next_id
    item = {"id": next_id, **payload.model_dump()}
    restaurants[next_id] = item
    next_id += 1
    return item

@app.get("/api/restaurants")
def list_restaurants(limit: Optional[int] = None, offset: int = 0, cuisine: Optional[str] = None):
    items = list(restaurants.values())
    if cuisine is not None:
        items = [r for r in items if r["cuisine"] == cuisine]
    if offset:
        items = items[offset:]
    if limit is not None:
        items = items[:limit]
    return items

@app.get("/api/restaurants/{rid}")
def get_restaurant(rid: int):
    if rid not in restaurants:
        return JSONResponse(status_code=404, content={"error": "not found"})
    return restaurants[rid]

@app.patch("/api/restaurants/{rid}")
def update_restaurant(rid: int, payload: RestaurantUpdate):
    if rid not in restaurants:
        return JSONResponse(status_code=404, content={"error": "not found"})
    restaurants[rid].update(payload.model_dump(exclude_unset=True))
    return restaurants[rid]

@app.put("/api/restaurants/{rid}")
def replace_restaurant(rid: int, payload: RestaurantCreate):
    if rid not in restaurants:
        return JSONResponse(status_code=404, content={"error": "not found"})
    restaurants[rid] = {"id": rid, **payload.model_dump()}
    return restaurants[rid]

@app.delete("/api/restaurants/{rid}", status_code=204)
def delete_restaurant(rid: int):
    if rid not in restaurants:
        return JSONResponse(status_code=404, content={"error": "not found"})
    del restaurants[rid]
    return Response(status_code=204)