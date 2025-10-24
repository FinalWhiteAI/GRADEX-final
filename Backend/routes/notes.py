from fastapi import APIRouter,HTTPException
import uuid
from utils.file_handler import load_json, save_json
from models.schemas import Note

router = APIRouter(prefix="/classes/{class_id}/notes", tags=["Notes"])

@router.post("")
def add_note(class_id: str, note: Note):
    classes = load_json("classes.json")
    # Find the class
    cls = next((c for c in classes if c["id"] == class_id), None)
    if not cls:
        raise HTTPException(404, "Class not found")
    
    # Only teacher can add notes
    if note.user_id != cls["teacher_id"]:
        raise HTTPException(403, "Only the class creator can add notes")

    notes = load_json("notes.json")
    note.id = str(uuid.uuid4())
    note.class_id = class_id
    notes.append(note.model_dump())
    save_json("notes.json", notes)
    return note

@router.get("")
def get_notes(class_id: str):
    notes = load_json("notes.json")
    return [n for n in notes if n["class_id"] == class_id]
