# from fastapi import APIRouter
# import uuid
# from utils.file_handler import load_json, save_json
# from models.schemas import Submission

# router = APIRouter(prefix="/assignments", tags=["Submissions"])

# @router.post("/{assignment_id}/submit")
# def submit_assignment(assignment_id: str, submission: Submission):
#     submissions = load_json("submissions.json")
#     submission.id = str(uuid.uuid4())
#     submission.assignment_id = assignment_id
#     submissions.append(submission.model_dump())
#     save_json("submissions.json", submissions)
#     return submission

# @router.get("/{assignment_id}/submissions")
# def get_submissions(assignment_id: str):
#     submissions = load_json("submissions.json")
#     return [s for s in submissions if s["assignment_id"] == assignment_id]

from fastapi import APIRouter, HTTPException
from supabase_client import supabase
import uuid

router = APIRouter(prefix="/assignments", tags=["Submissions"])

@router.post("/{assignment_id}/submit")
def submit_assignment(assignment_id: str, payload: dict):
    student_id = payload.get("student_id")
    content = payload.get("content")

    if not student_id or not content:
        raise HTTPException(status_code=400, detail="student_id and content required")

    # Check assignment exists
    assignment = supabase.table("assignments").select("*").eq("id", assignment_id).single().execute().data
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Check student exists
    user = supabase.table("users").select("*").eq("id", student_id).single().execute().data
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    new_submission = {
        "id": str(uuid.uuid4()),
        "assignment_id": assignment_id,
        "student_id": student_id,
        "content": content
    }

    res = supabase.table("submissions").insert(new_submission).execute()

    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)

    return {"message": "Submitted", "data": new_submission}


@router.get("/{assignment_id}/submissions")
def get_submissions(assignment_id: str):
    # Check assignment exists
    assignment = supabase.table("assignments").select("*").eq("id", assignment_id).single().execute().data
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    res = supabase.table("submissions").select("*").eq("assignment_id", assignment_id).execute()
    return res.data
