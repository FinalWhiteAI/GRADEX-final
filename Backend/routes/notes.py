# from fastapi import APIRouter,HTTPException
# import uuid
# from utils.file_handler import load_json, save_json
# from models.schemas import Note

# router = APIRouter(prefix="/classes/{class_id}/notes", tags=["Notes"])

# @router.post("")
# def add_note(class_id: str, note: Note):
#     classes = load_json("classes.json")
#     # Find the class
#     cls = next((c for c in classes if c["id"] == class_id), None)
#     if not cls:
#         raise HTTPException(404, "Class not found")
    
#     # Only teacher can add notes
#     if note.user_id != cls["teacher_id"]:
#         raise HTTPException(403, "Only the class creator can add notes")

#     notes = load_json("notes.json")
#     note.id = str(uuid.uuid4())
#     note.class_id = class_id
#     notes.append(note.model_dump())
#     save_json("notes.json", notes)
#     return note

# @router.get("")
# def get_notes(class_id: str):
#     notes = load_json("notes.json")
#     return [n for n in notes if n["class_id"] == class_id]
from fastapi import APIRouter, HTTPException
from supabase_client import supabase
import uuid

router = APIRouter(prefix="/classes/{class_id}/notes", tags=["Notes"])

@router.post("")
def add_note(class_id: str, payload: dict):

    user_id = payload.get("user_id")
    content = payload.get("content")

    if not user_id or not content:
        raise HTTPException(status_code=400, detail="user_id and content are required")

    # Check class exists
    cls = supabase.table("classes").select("*").eq("id", class_id).single().execute().data
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    # Only teacher can add notes
    if user_id != cls["teacher_id"]:
        raise HTTPException(status_code=403, detail="Only the class teacher can add notes")

    new_note = {
        "id": str(uuid.uuid4()),
        "class_id": class_id,
        "user_id": user_id,
        "content": content
    }

    res = supabase.table("notes").insert(new_note).execute()

    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)

    return {"message": "Note created", "data": new_note}


@router.get("")
def get_notes(class_id: str):
    res = supabase.table("notes").select("*").eq("class_id", class_id).order("created_at", desc=False).execute()
    return res.data
