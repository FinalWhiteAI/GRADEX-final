# from fastapi import APIRouter, HTTPException
# import uuid
# from utils.file_handler import load_json, save_json
# from models.schemas import User

# router = APIRouter(prefix="/users", tags=["Users"])

# @router.get("")
# def get_users():
#     return load_json("users.json")

# @router.post("")
# def create_user(user: User):
#     users = load_json("users.json")
#     user.id = str(uuid.uuid4())
#     users.append(user.dict())
#     save_json("users.json", users)
#     return user

# @router.get("/{user_id}")
# def get_user(user_id: str):
#     users = load_json("users.json")
#     for u in users:
#         if u["id"] == user_id:
#             return u
#     raise HTTPException(404, "User not found")

from fastapi import APIRouter, HTTPException
from supabase_client import supabase
import uuid

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("")
def get_users():
    res = supabase.table("users").select("*").execute()
    return res.data


@router.post("")
def create_user(payload: dict):
    # Required fields
    name = payload.get("name")
    email = payload.get("email")
    password = payload.get("password")  # you will hash later

    if not name or not email or not password:
        raise HTTPException(status_code=400, detail="name, email, password required")

    new_user = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "password": password
    }

    res = supabase.table("users").insert(new_user).execute()

    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)

    return {"message": "User created", "data": new_user}


@router.get("/{user_id}")
def get_user(user_id: str):
    res = supabase.table("users").select("*").eq("id", user_id).single().execute()

    if not res.data:
        raise HTTPException(status_code=404, detail="User not found")

    return res.data
