from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables (set these in Render)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "items"  # your Supabase table


# Pydantic model
class Item(BaseModel):
    name: str
    description: str


# Root route
@app.get("/")
def read_root():
    return {"message": "FastAPI + Supabase REST API is running 🚀"}


# GET all items
@app.get("/items")
def get_items():
    response = supabase.table(TABLE_NAME).select("*").execute()
    return response.data


# GET single item
@app.get("/items/{item_id}")
def get_item(item_id: int):
    response = supabase.table(TABLE_NAME).select("*").eq("id", item_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Item not found")
    return response.data[0]


# POST create item
@app.post("/items")
def create_item(item: Item):
    response = supabase.table(TABLE_NAME).insert(item.dict()).execute()
    return response.data


# PUT update full item
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    response = supabase.table(TABLE_NAME).update(item.dict()).eq("id", item_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Item not found")
    return response.data


# PATCH partial update
@app.patch("/items/{item_id}")
def patch_item(item_id: int, item: dict):
    response = supabase.table(TABLE_NAME).update(item).eq("id", item_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Item not found")
    return response.data


# DELETE item
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    response = supabase.table(TABLE_NAME).delete().eq("id", item_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}
