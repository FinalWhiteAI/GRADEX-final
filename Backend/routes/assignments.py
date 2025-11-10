# from fastapi import APIRouter,HTTPException
# import uuid
# from utils.file_handler import load_json, save_json
# from models.schemas import Assignment

# router = APIRouter(prefix="/classes/{class_id}/assignments", tags=["Assignments"])

# @router.post("")
# def add_assignment(class_id: str, assignment: Assignment):
#     classes = load_json("classes.json")
#     cls = next((c for c in classes if c["id"] == class_id), None)
#     if not cls:
#         raise HTTPException(404, "Class not found")

#     # Only teacher can add assignments
#     if assignment.user_id != cls["teacher_id"]:
#         raise HTTPException(403, "Only the class teacher can add assignments")

#     assignments = load_json("assignments.json")
#     assignment.id = str(uuid.uuid4())
#     assignment.class_id = class_id
#     assignments.append(assignment.model_dump())
#     save_json("assignments.json", assignments)
#     return assignment

# @router.get("")
# def get_assignments(class_id: str):
#     assignments = load_json("assignments.json")
#     return [a for a in assignments if a["class_id"] == class_id]
from fastapi import APIRouter, HTTPException
from supabase_client import supabase
import uuid

router = APIRouter(prefix="/classes/{class_id}/assignments", tags=["Assignments"])

@router.post("")
def add_assignment(class_id: str, payload: dict):

    # Check class exists
    cls = supabase.table("classes").select("*").eq("id", class_id).single().execute()
    cls_data = cls.data
    if not cls_data:
        raise HTTPException(status_code=404, detail="Class not found")

    user_id = payload.get("user_id")
    title = payload.get("title")
    description = payload.get("description")
    due_date = payload.get("due_date")  # optional

    # Teacher check
    if user_id != cls_data["teacher_id"]:
        raise HTTPException(status_code=403, detail="Only teacher can add assignments")

    new_assignment = {
        "id": str(uuid.uuid4()),
        "class_id": class_id,
        "user_id": user_id,
        "title": title,
        "description": description,
        "due_date": due_date
    }

    res = supabase.table("assignments").insert(new_assignment).execute()

    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)

    return {"status": "Assignment created", "data": new_assignment}


@router.get("")
def get_assignments(class_id: str):
    res = supabase.table("assignments").select("*").eq("class_id", class_id).execute()

    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)

    return {"assignments": res.data}
