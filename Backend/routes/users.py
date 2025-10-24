from fastapi import APIRouter, HTTPException
import uuid
from utils.file_handler import load_json, save_json
from models.schemas import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("")
def get_users():
    return load_json("users.json")

@router.post("")
def create_user(user: User):
    users = load_json("users.json")
    user.id = str(uuid.uuid4())
    users.append(user.dict())
    save_json("users.json", users)
    return user

@router.get("/{user_id}")
def get_user(user_id: str):
    users = load_json("users.json")
    for u in users:
        if u["id"] == user_id:
            return u
    raise HTTPException(404, "User not found")
