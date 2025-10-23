from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json, uuid, os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

DATA_DIR = "./data"

def load_json(file):
    path = os.path.join(DATA_DIR, file)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump([], f)
    with open(path, "r") as f:
        return json.load(f)

def save_json(file, data):
    path = os.path.join(DATA_DIR, file)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# -------------------- MODELS --------------------
class User(BaseModel):
    id: str = None
    name: str
    role: str  # "teacher" or "student"

class Class(BaseModel):
    id: str = None
    name: str
    teacher_id: str
    students: List[str] = []

class Note(BaseModel):
    id: str = None
    class_id: str
    title: str
    content: str

class Assignment(BaseModel):
    id: str = None
    class_id: str
    title: str
    description: str

class Submission(BaseModel):
    id: str = None
    assignment_id: str
    student_id: str
    content: str

class Message(BaseModel):
    id: str = None
    class_id: str
    user_id: str
    content: str

# -------------------- USERS --------------------
@app.get("/users")
def get_users():
    return load_json("users.json")

@app.post("/users")
def create_user(user: User):
    users = load_json("users.json")
    user.id = str(uuid.uuid4())
    users.append(user.dict())
    save_json("users.json", users)
    return user

@app.get("/users/{user_id}")
def get_user(user_id: str):
    users = load_json("users.json")
    for u in users:
        if u["id"] == user_id:
            return u
    raise HTTPException(404, "User not found")

# -------------------- CLASSES --------------------
@app.post("/classes")
def create_class(cls: Class):
    classes = load_json("classes.json")
    cls.id = str(uuid.uuid4())
    classes.append(cls.dict())
    save_json("classes.json", classes)
    return cls

@app.get("/classes/{class_id}")
def get_class(class_id: str):
    classes = load_json("classes.json")
    for c in classes:
        if c["id"] == class_id:
            return c
    raise HTTPException(404, "Class not found")

@app.get("/users/{user_id}/classes")
def get_user_classes(user_id: str):
    classes = load_json("classes.json")
    return [c for c in classes if user_id == c["teacher_id"] or user_id in c["students"]]

@app.post("/classes/{class_id}/join/{user_id}")
def join_class(class_id: str, user_id: str):
    classes = load_json("classes.json")
    for c in classes:
        if c["id"] == class_id:
            if user_id not in c["students"]:
                c["students"].append(user_id)
                save_json("classes.json", classes)
            return c
    raise HTTPException(404, "Class not found")

# -------------------- NOTES --------------------
@app.post("/classes/{class_id}/notes")
def add_note(class_id: str, note: Note):
    notes = load_json("notes.json")
    note.id = str(uuid.uuid4())
    note.class_id = class_id
    notes.append(note.dict())
    save_json("notes.json", notes)
    return note

@app.get("/classes/{class_id}/notes")
def get_notes(class_id: str):
    notes = load_json("notes.json")
    return [n for n in notes if n["class_id"] == class_id]

# -------------------- ASSIGNMENTS --------------------
@app.post("/classes/{class_id}/assignments")
def add_assignment(class_id: str, assignment: Assignment):
    assignments = load_json("assignments.json")
    assignment.id = str(uuid.uuid4())
    assignment.class_id = class_id
    assignments.append(assignment.dict())
    save_json("assignments.json", assignments)
    return assignment

@app.get("/classes/{class_id}/assignments")
def get_assignments(class_id: str):
    assignments = load_json("assignments.json")
    return [a for a in assignments if a["class_id"] == class_id]

# -------------------- SUBMISSIONS --------------------
@app.post("/assignments/{assignment_id}/submit")
def submit_assignment(assignment_id: str, submission: Submission):
    submissions = load_json("submissions.json")
    submission.id = str(uuid.uuid4())
    submission.assignment_id = assignment_id
    submissions.append(submission.dict())
    save_json("submissions.json", submissions)
    return submission

@app.get("/assignments/{assignment_id}/submissions")
def get_submissions(assignment_id: str):
    submissions = load_json("submissions.json")
    return [s for s in submissions if s["assignment_id"] == assignment_id]

# -------------------- MESSAGES --------------------
@app.post("/classes/{class_id}/messages")
def add_message(class_id: str, message: Message):
    messages = load_json("messages.json")
    message.id = str(uuid.uuid4())
    message.class_id = class_id
    messages.append(message.dict())
    save_json("messages.json", messages)
    return message

@app.get("/classes/{class_id}/messages")
def get_messages(class_id: str):
    messages = load_json("messages.json")
    return [m for m in messages if m["class_id"] == class_id]
