from fastapi import APIRouter,HTTPException
import uuid
from utils.file_handler import load_json, save_json
from models.schemas import Assignment

router = APIRouter(prefix="/classes/{class_id}/assignments", tags=["Assignments"])

@router.post("")
def add_assignment(class_id: str, assignment: Assignment):
    classes = load_json("classes.json")
    cls = next((c for c in classes if c["id"] == class_id), None)
    if not cls:
        raise HTTPException(404, "Class not found")

    # Only teacher can add assignments
    if assignment.user_id != cls["teacher_id"]:
        raise HTTPException(403, "Only the class teacher can add assignments")

    assignments = load_json("assignments.json")
    assignment.id = str(uuid.uuid4())
    assignment.class_id = class_id
    assignments.append(assignment.model_dump())
    save_json("assignments.json", assignments)
    return assignment

@router.get("")
def get_assignments(class_id: str):
    assignments = load_json("assignments.json")
    return [a for a in assignments if a["class_id"] == class_id]
