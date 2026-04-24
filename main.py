from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import os
from datetime import date
from typing import Optional
from fastapi.responses import HTMLResponse
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
@app.get("/", response_class=HTMLResponse)
def serve_home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

#SEARCH FOR FRONTEND
@app.get("/inventory/search")
def search_inventory(q: str = Query(..., min_length=1)):
    try:
        results = []

        # Try numeric search
        if q.isdigit():
            res_id = supabase.table(TABLE_NAME)\
                .select("*")\
                .eq("material_id", int(q))\
                .execute()
            results.extend(res_id.data)

        # Text search
        res_text = supabase.table(TABLE_NAME)\
            .select("*")\
            .or_(
                f"material_name.ilike.%{q}%,storage_location.ilike.%{q}%"
            )\
            .execute()

        results.extend(res_text.data)

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    data = item.dict()

    if data.get("purchase_date"):
        data["purchase_date"] = data["purchase_date"].isoformat()

    res = supabase.table(TABLE_NAME).insert(data).execute()
    return res.data


# PUT (full replace)
@app.put("/inventory/{material_id}")
def replace_item(material_id: int, item: InventoryItem):
    data = item.model_dump(mode="json")

    res = supabase.table(TABLE_NAME)\
        .update(data)\
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
