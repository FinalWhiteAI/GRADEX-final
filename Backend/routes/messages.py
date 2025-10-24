from fastapi import APIRouter
import uuid
from utils.file_handler import load_json, save_json
from models.schemas import Message

router = APIRouter(prefix="/classes/{class_id}/messages", tags=["Messages"])

@router.post("")
def add_message(class_id: str, message: Message):
    messages = load_json("messages.json")
    message.id = str(uuid.uuid4())
    message.class_id = class_id
    messages.append(message.dict())
    save_json("messages.json", messages)
    return message

@router.get("")
def get_messages(class_id: str):
    messages = load_json("messages.json")
    return [m for m in messages if m["class_id"] == class_id]
