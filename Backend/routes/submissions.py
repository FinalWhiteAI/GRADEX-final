from fastapi import APIRouter
import uuid
from utils.file_handler import load_json, save_json
from models.schemas import Submission

router = APIRouter(prefix="/assignments", tags=["Submissions"])

@router.post("/{assignment_id}/submit")
def submit_assignment(assignment_id: str, submission: Submission):
    submissions = load_json("submissions.json")
    submission.id = str(uuid.uuid4())
    submission.assignment_id = assignment_id
    submissions.append(submission.model_dump())
    save_json("submissions.json", submissions)
    return submission

@router.get("/{assignment_id}/submissions")
def get_submissions(assignment_id: str):
    submissions = load_json("submissions.json")
    return [s for s in submissions if s["assignment_id"] == assignment_id]
