# from fastapi import APIRouter
# import uuid
# from utils.file_handler import load_json, save_json
# from models.schemas import Message

# router = APIRouter(prefix="/classes/{class_id}/messages", tags=["Messages"])

# @router.post("")
# def add_message(class_id: str, message: Message):
#     messages = load_json("messages.json")
#     message.id = str(uuid.uuid4())
#     message.class_id = class_id
#     messages.append(message.dict())
#     save_json("messages.json", messages)
#     return message

# @router.get("")
# def get_messages(class_id: str):
#     messages = load_json("messages.json")
#     return [m for m in messages if m["class_id"] == class_id]

from fastapi import APIRouter, HTTPException
from supabase_client import supabase
import uuid

router = APIRouter(prefix="/classes/{class_id}/messages", tags=["Messages"])

@router.post("")
def add_message(class_id: str, payload: dict):

    user_id = payload.get("user_id")
    content = payload.get("content")

    if not user_id or not content:
        raise HTTPException(status_code=400, detail="user_id and content are required")

    new_msg = {
        "id": str(uuid.uuid4()),
        "class_id": class_id,
        "user_id": user_id,
        "content": content
    }

    res = supabase.table("messages").insert(new_msg).execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)

    return {"message": "Message sent", "data": new_msg}


@router.get("")
def get_messages(class_id: str):
    res = supabase.table("messages").select("*").eq("class_id", class_id).order("sent_at", desc=False).execute()

    return res.data
