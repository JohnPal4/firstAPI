import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client

# Load environment variables (Render will provide these)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = os.getenv("TABLE_NAME", "items")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="FastAPI Supabase CRUD API")

# Allow frontend / Render / local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Model
# -------------------------
class Item(BaseModel):
    name: str
    description: str | None = None


# -------------------------
# CREATE
# -------------------------
@app.post("/items")
def create_item(item: Item):
    res = supabase.table(TABLE_NAME).insert(item.model_dump()).execute()
    return res.data


# -------------------------
# READ ALL
# -------------------------
@app.get("/items")
def get_items():
    res = supabase.table(TABLE_NAME).select("*").execute()
    return res.data


# -------------------------
# READ ONE
# -------------------------
@app.get("/items/{item_id}")
def get_item(item_id: int):
    res = supabase.table(TABLE_NAME).select("*").eq("id", item_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Item not found")
    return res.data[0]


# -------------------------
# UPDATE
# -------------------------
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    res = supabase.table(TABLE_NAME).update(item.model_dump()).eq("id", item_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Item not found")
    return res.data


# -------------------------
# DELETE
# -------------------------
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    res = supabase.table(TABLE_NAME).delete().eq("id", item_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Deleted successfully"}
