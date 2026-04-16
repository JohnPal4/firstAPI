from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import os
from datetime import date
from typing import Optional

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "inventory"


# ✅ Model matches your SQL table
class InventoryItem(BaseModel):
    material_id: int
    material_name: str
    purchase_date: Optional[date] = None
    purchase_quantity: int
    storage_location: Optional[str] = None
    on_hand_quantity: int


# Root
@app.get("/")
def root():
    return {"message": "Inventory API running 🚀"}


# GET all
@app.get("/inventory")
def get_all():
    res = supabase.table(TABLE_NAME).select("*").execute()
    return res.data


# GET one (using material_id)
@app.get("/inventory/{material_id}")
def get_one(material_id: int):
    res = supabase.table(TABLE_NAME).select("*").eq("material_id", material_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Item not found")
    return res.data[0]


# POST
@app.post("/inventory")
def create_item(item: InventoryItem):
    res = supabase.table(TABLE_NAME).insert(item.dict()).execute()
    return res.data


# PUT (full replace)
@app.put("/inventory/{material_id}")
def replace_item(material_id: int, item: InventoryItem):
    res = supabase.table(TABLE_NAME)\
        .update(item.dict())\
        .eq("material_id", material_id)\
        .execute()

    if not res.data:
        raise HTTPException(status_code=404, detail="Item not found")

    return res.data


# PATCH (partial update)
@app.patch("/inventory/{material_id}")
def patch_item(material_id: int, item: dict):
    res = supabase.table(TABLE_NAME)\
        .update(item)\
        .eq("material_id", material_id)\
        .execute()

    if not res.data:
        raise HTTPException(status_code=404, detail="Item not found")

    return res.data


# DELETE
@app.delete("/inventory/{material_id}")
def delete_item(material_id: int):
    res = supabase.table(TABLE_NAME)\
        .delete()\
        .eq("material_id", material_id)\
        .execute()

    if not res.data:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"message": "Deleted successfully"}
