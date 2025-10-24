from fastapi import APIRouter, HTTPException
import uuid
from utils.file_handler import load_json, save_json
from models.schemas import Class

router = APIRouter(tags=["Classes"])

@router.post("/classes")
def create_class(cls: Class):
    classes = load_json("classes.json")
    cls.id = str(uuid.uuid4())
    classes.append(cls.model_dump())
    save_json("classes.json", classes)
    return cls

@router.get("/classes/{class_id}")
def get_class(class_id: str):
    classes = load_json("classes.json")
    for c in classes:
        if c["id"] == class_id:
            return c
    raise HTTPException(404, "Class not found")

@router.get("/users/{user_id}/classes")
def get_user_classes(user_id: str):
    classes = load_json("classes.json")
    return [c for c in classes if user_id == c["teacher_id"] or user_id in c["students"]]

@router.post("/classes/{class_id}/join/{user_id}")
def join_class(class_id: str, user_id: str):
    classes = load_json("classes.json")
    for c in classes:
        if c["id"] == class_id:
            if user_id not in c["students"]:
                c["students"].append(user_id)
                save_json("classes.json", classes)
            return c
    raise HTTPException(404, "Class not found")
