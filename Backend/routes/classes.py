# from fastapi import APIRouter, HTTPException
# import uuid
# from utils.file_handler import load_json, save_json
# from models.schemas import Class

# router = APIRouter(tags=["Classes"])

# @router.post("/classes")
# def create_class(cls: Class):
#     classes = load_json("classes.json")
#     cls.id = str(uuid.uuid4())
#     classes.append(cls.model_dump())
#     save_json("classes.json", classes)
#     return cls

# @router.get("/classes/{class_id}")
# def get_class(class_id: str):
#     classes = load_json("classes.json")
#     for c in classes:
#         if c["id"] == class_id:
#             return c
#     raise HTTPException(404, "Class not found")

# @router.get("/users/{user_id}/classes")
# def get_user_classes(user_id: str):
#     classes = load_json("classes.json")
#     return [c for c in classes if user_id == c["teacher_id"] or user_id in c["students"]]

# @router.post("/classes/{class_id}/join/{user_id}")
# def join_class(class_id: str, user_id: str):
#     classes = load_json("classes.json")
#     for c in classes:
#         if c["id"] == class_id:
#             if user_id not in c["students"]:
#                 c["students"].append(user_id)
#                 save_json("classes.json", classes)
#             return c
#     raise HTTPException(404, "Class not found")

from fastapi import APIRouter, HTTPException
from supabase_client import supabase
import uuid

router = APIRouter(tags=["Classes"])

# Create class
@router.post("/classes")
def create_class(payload: dict):

    name = payload.get("name")
    teacher_id = payload.get("teacher_id")

    if not name or not teacher_id:
        raise HTTPException(status_code=400, detail="name and teacher_id required")

    new_class = {
        "id": str(uuid.uuid4()),
        "name": name,
        "teacher_id": teacher_id
    }

    res = supabase.table("classes").insert(new_class).execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)

    return {"message": "Class created", "class": new_class}


# Get class by ID
@router.get("/classes/{class_id}")
def get_class(class_id: str):
    res = supabase.table("classes").select("*").eq("id", class_id).single().execute()

    if not res.data:
        raise HTTPException(status_code=404, detail="Class not found")

    return res.data


# Get all classes for a user (teacher + student)
@router.get("/users/{user_id}/classes")
def get_user_classes(user_id: str):

    teacher_classes = supabase.table("classes").select("*").eq("teacher_id", user_id).execute().data

    student_rows = supabase.table("class_students").select("*").eq("student_id", user_id).execute().data
    student_class_ids = [row["class_id"] for row in student_rows]

    student_classes = []
    if student_class_ids:
        student_classes = supabase.table("classes").select("*").in_("id", student_class_ids).execute().data

    return teacher_classes + student_classes


# Join class
@router.post("/classes/{class_id}/join/{user_id}")
def join_class(class_id: str, user_id: str):

    cls = supabase.table("classes").select("*").eq("id", class_id).single().execute().data
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    exists = supabase.table("class_students") \
        .select("*") \
        .eq("class_id", class_id) \
        .eq("student_id", user_id) \
        .execute().data

    if exists:
        return {"message": "Already joined", "class": cls}

    entry = {
        "class_id": class_id,
        "student_id": user_id
    }

    res = supabase.table("class_students").insert(entry).execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)

    return {"message": "Joined class", "class": cls}
