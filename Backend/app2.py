
# app.py
"""
Complete single-file FastAPI backend for Classroom app (LOCAL JSON DB).
Features:
- Replaces Supabase with local JSON files in ./data/
- Replaces Supabase Auth with self-hosted JWT (python-jose)
- Replaces Supabase Storage with local file storage in ./uploads/
- Maintains 100% API compatibility with the frontend.
"""
from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File, Body, Query
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from fastapi import Form

from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import os, secrets, json, uuid
from datetime import datetime, timedelta
from functools import wraps
from io import BytesIO
import pandas as pd
from pathlib import Path

# --- New Imports ---
import bcrypt
from jose import JWTError, jwt

# -------------------------
# Load env & Setup
# -------------------------
load_dotenv()
OWNER_EMAIL = os.getenv("OWNER_EMAIL")
DEFAULT_ORG_TYPE = os.getenv("DEFAULT_ORG_TYPE", "school")

# --- New JWT & File Setup ---
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

if not JWT_SECRET_KEY:
    raise RuntimeError("Set JWT_SECRET_KEY in environment")
if not OWNER_EMAIL:
    raise RuntimeError("Set OWNER_EMAIL in environment")

# --- Create local DB and Upload directories ---
DATA_DIR = Path("data")
UPLOAD_DIR = Path("uploads")
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
(UPLOAD_DIR / "assignments").mkdir(exist_ok=True)
(UPLOAD_DIR / "submissions").mkdir(exist_ok=True)
(UPLOAD_DIR / "notes").mkdir(exist_ok=True)


import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="drtoaiaxq",
    api_key="819392728915415",
    api_secret="z3G53swRGVGDL7NMrzO-p0h-oO0"
)


# -------------------------
# Pydantic models (Unchanged)
# -------------------------
# ... (All your Pydantic models are identical, so I'll skip them for brevity, 
# but they are in the final code block) ...
class LoginReq(BaseModel):
    email: EmailStr
    password: str

class CreateOrgReq(BaseModel):
    name: str
    org_type: Optional[str] = None  # school / college / university

class AddUserReq(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    roles: Optional[List[str]] = None
    password: str
from pydantic import BaseModel

class AddStudentReq(BaseModel):
    class_id: str
    email: EmailStr
    full_name: Optional[str] = None
    password: Optional[str] = None


class CreateDeptReq(BaseModel):
    org_id: str
    name: str
    hod_id: Optional[str] = None

class CreateClassReq(BaseModel):
    org_id: str
    title: str
    description: Optional[str] = None
    department_id: Optional[str] = None
    section: Optional[str] = None 

class JoinClassReq(BaseModel):
    class_code: str

class CreateAssignmentReq(BaseModel):
    class_id: str
    title: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    assignment_type: Optional[str] = 'file'  # file, text, mixed

class SubmitReq(BaseModel):
    assignment_id: str
    text_content: Optional[str] = None

class NoteCreateReq(BaseModel):
    class_id: str
    title: str
    file_path: str # Note: We'll have to adjust how file uploads work

class FinalMarkReq(BaseModel):
    org_id: str
    class_id: Optional[str] = None
    student_id: str
    subject_name: str
    unit_name: str
    marks: float

class MessageReq(BaseModel):
    class_id: str
    receiver_id: Optional[str] = None
    content: str
    is_public: Optional[bool] = False

class BulkMappingReq(BaseModel):
    mapping: Dict[str, str]
    create_departments: Optional[bool] = True

# -------------------------
# NEW: Local JSON DB Helpers
# -------------------------
def load_db(table_name: str) -> List[Dict[str, Any]]:
    """Loads a 'table' (JSON file) from the data directory."""
    db_file = DATA_DIR / f"{table_name}.json"
    if not db_file.exists():
        return []  # Return empty list if file doesn't exist
    try:
        with open(db_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_db(table_name: str, data: List[Dict[str, Any]]):
    """Saves a 'table' (JSON file) to the data directory."""
    db_file = DATA_DIR / f"{table_name}.json"
    with open(db_file, 'w') as f:
        json.dump(data, f, indent=2, default=str) # Use default=str for datetimes

def db_find_one(table_name: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Finds the first item in a table matching all kwargs."""
    data = load_db(table_name)
    for item in data:
        if all(item.get(key) == value for key, value in kwargs.items()):
            return item
    return None

def db_find_many(table_name: str, **kwargs) -> List[Dict[str, Any]]:
    """Finds all items in a table matching all kwargs."""
    data = load_db(table_name)
    results = []
    for item in data:
        if all(item.get(key) == value for key, value in kwargs.items()):
            results.append(item)
    return results

def db_insert_one(table_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
    """Inserts a new item into a table, adding a UUID 'id' if not present."""
    data = load_db(table_name)
    if 'id' not in item:
        item['id'] = str(uuid.uuid4())
    data.append(item)
    save_db(table_name, data)
    return item

def db_update_one(table_name: str, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Finds an item by ID and applies updates."""
    data = load_db(table_name)
    updated_item = None
    for i, item in enumerate(data):
        if item.get('id') == item_id:
            item.update(updates)
            data[i] = item
            updated_item = item
            break
    if updated_item:
        save_db(table_name, data)
    return updated_item

def db_delete_one(table_name: str, item_id: str) -> bool:
    """Deletes an item by its ID."""
    data = load_db(table_name)
    original_len = len(data)
    data = [item for item in data if item.get('id') != item_id]
    if len(data) < original_len:
        save_db(table_name, data)
        return True
    return False

# -------------------------
# NEW: Password & JWT Helpers
# -------------------------
def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """Creates a new JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

# -------------------------
# REFACTORED: Core Helpers
# -------------------------
def _data(resp):
    # This helper is no longer needed, but we'll keep it for compatibility
    # in case it was used somewhere I missed.
    return resp

def parse_roles_field(roles_field: Any) -> List[str]:
    # This function is perfect, no changes needed.
    if roles_field is None:
        return []
    if isinstance(roles_field, (list, tuple)):
        return list(roles_field)
    if isinstance(roles_field, str):
        try:
            parsed = json.loads(roles_field)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            # comma separated fallback
            return [r.strip() for r in roles_field.split(",") if r.strip()]
    return []

def get_user_row(user_id: str):
    return db_find_one('users', id=user_id)

def get_user_row_by_email(email: str):
    if not email:
        return None
    return db_find_one('users', email=email)

def org_has_departments(org_id: str) -> bool:
    org = db_find_one('organizations', id=org_id)
    if not org:
        return False
    return org.get('org_type') in ('college', 'university')

# -------------------------
# REFACTORED: Auth dependency + guards
# -------------------------
def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail='Missing Authorization header')
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Invalid Authorization header')
    
    token = authorization.split(' ',1)[1]
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub") # We'll store the user ID in the 'sub' claim
        if user_id is None:
            raise HTTPException(status_code=401, detail='Invalid token: No user ID')
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f'Invalid token: {e}')
    
    app_user = get_user_row(user_id)
    
    if not app_user:
        # This logic is the same as yours, which is great!
        raise HTTPException(status_code=403, detail='User not registered in app DB')
    
    return app_user

# --- require_any_role and require_owner are UNCHANGED ---
def require_any_role(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            user_roles = parse_roles_field(current_user.get('roles') or [])
            if not any(r in user_roles for r in roles):
                raise HTTPException(status_code=403, detail='Insufficient role')
            return func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def require_owner(func):
    @wraps(func)
    def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
        if current_user.get('email') != OWNER_EMAIL:
            raise HTTPException(status_code=403, detail='Only app owner can perform this action')
        return func(*args, current_user=current_user, **kwargs)
    return wrapper

# -------------------------
# App & OpenAPI security (Unchanged)
# -------------------------
app = FastAPI(title="Classroom Backend (LOCAL JSON DB, Full)")

app.add_middleware(
    CORSMiddleware,
      allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(title=app.title, version="1.0.0", routes=app.routes)
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type":"http","scheme":"bearer","bearerFormat":"JWT"}
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# -------------------------
# REFACTORED: AUTH
# -------------------------

def get_roles(user_id):
    roles = db_find_many("role_assignments", user_id=user_id)
    return roles or []

def has_role(user_id, role):
    return db_find_one("role_assignments", user_id=user_id, role=role) is not None

def assign_role(user_id, role, org_id=None, dept_id=None, class_id=None):
    # Store in role_assignments table
    db_insert_one("role_assignments", {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "role": role,
        "org_id": org_id,
        "dept_id": dept_id,
        "class_id": class_id
    })

    # Update "roles" field INSIDE user table
    user = db_find_one("users", id=user_id)
    if user:
        roles = parse_roles_field(user.get("roles"))
        if role not in roles:
            roles.append(role)
            db_update_one("users", user_id, { "roles": json.dumps(roles) })

    
@app.get("/api/users/roles/{user_id}")
def get_user_roles(user_id: str):
    """Return all roles of a user as a clean list."""
    
    user = db_find_one("users", id=user_id)
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")

    roles = parse_roles_field(user.get("roles"))

    return {
        
        "roles": roles
    }


@app.post("/api/users/create")
@require_any_role("admin", "class_teacher", "sub_teacher")
def create_user(payload: AddUserReq, current_user=Depends(get_current_user)):
    """
    Create a new user (teacher/student/etc.)
    Saves to local users.json with a hashed password.
    """
    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="You must belong to an organization")
    
    if get_user_row_by_email(payload.email):
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Create local app user
    user_id = str(uuid.uuid4())
    hashed_pass = hash_password(payload.password)
    roles = payload.roles or ["student"]
    
    new_user = {
        "id": user_id,
        "email": payload.email,
        "full_name": payload.full_name,
        "roles": json.dumps(roles), # Store roles as a JSON string for consistency
        "org_id": org_id,
        "hashed_password": hashed_pass
    }
    
    db_insert_one("users", new_user)

    return {
        "message": "User created successfully",
        "email": payload.email,
        "roles": roles
    }

def require_role(*allowed_roles):
    def wrapper(fn):
        def inner(*args, current_user=Depends(get_current_user), **kwargs):
            user_roles = get_roles(current_user["id"])
            roles_only = [r["role"] for r in user_roles]

            if not any(role in roles_only for role in allowed_roles):
                raise HTTPException(status_code=403, detail="Role not allowed")

            return fn(*args, current_user=current_user, **kwargs)
        return inner
    return wrapper

@app.post("/api/dept/{dept_id}/assign-hod")
@require_role("admin")
def assign_hod(dept_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
    user = get_user_row_by_email(payload.email)
    if not user:
        raise HTTPException(404, "User not found")

    assign_role(user["id"], "hod", org_id=current_user["org_id"], dept_id=dept_id)
    return {"message": "HOD Assigned"}
@app.post("/api/admin/assign-hod")
@require_any_role("admin")
def assign_hod(req: dict, current_user=Depends(get_current_user)):
    dept_id = req.get("dept_id")
    hod_id = req.get("hod_id")

    dept = db_find_one("departments", id=dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not exists")

    # Assign HOD to department
    db_update_one("departments", dept_id, { "hod_id": hod_id })

    # Add HOD role to user
    user = db_find_one("users", id=hod_id)
    roles = parse_roles_field(user["roles"])
    if "hod" not in roles:
        roles.append("hod")
        db_update_one("users", hod_id, { "roles": json.dumps(roles) })

    return {"message": "HOD assigned"}


@app.post("/api/departments/{dept_id}/add-class-teacher")
@require_any_role("hod")
def add_class_teacher(
    dept_id: str,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    section: str = Form(...),
    current_user=Depends(get_current_user)
):

    # Check HOD owns department
    hod_map = db_find_one("department_hods", hod_id=current_user["id"], dept_id=dept_id)
    if not hod_map:
        raise HTTPException(403, "Not HOD of this department")

    # Check if user exists
    if get_user_row_by_email(email):
        raise HTTPException(400, "User already exists")

    user_id = str(uuid.uuid4())
    hashed_pass = hash_password(password)

    # Create user
    db_insert_one("users", {
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "roles": json.dumps(["class_teacher"]),
        "org_id": current_user["org_id"],
        "hashed_password": hashed_pass
    })

    # Save teacher → dept mapping along with section
    db_insert_one("dept_class_teachers", {
        "id": str(uuid.uuid4()),
        "dept_id": dept_id,
        "class_teacher_id": user_id,
        "section": section
    })

    return {"message": "Class teacher added", "section": section}

@app.post("/api/departments/{dept_id}/sections")
@require_any_role("hod")
def create_section(dept_id: str, name: str = Form(...), current_user=Depends(get_current_user)):

    # Check if HOD valid
    hod_map = db_find_one("department_hods", hod_id=current_user["id"], dept_id=dept_id)
    if not hod_map:
        raise HTTPException(403, "Not HOD of this department")

    section = {
        "id": str(uuid.uuid4()),
        "dept_id": dept_id,
        "name": name,      # Example: "5A"
        "class_teacher_id": None
    }

    db_insert_one("sections", section)
    return section
@app.post("/api/sections/{section_id}/assign-teacher")
@require_any_role("hod")
def assign_class_teacher(
    section_id: str,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    current_user=Depends(get_current_user)
):
    # Validate section
    section = db_find_one("sections", id=section_id)
    if not section:
        raise HTTPException(404, "Section not found")

    # Check if HOD owns dept
    hod_map = db_find_one("department_hods", hod_id=current_user["id"], dept_id=section["dept_id"])
    if not hod_map:
        raise HTTPException(403, "Not HOD for this department")

    # Check if teacher already exists
    if get_user_row_by_email(email):
        raise HTTPException(400, "Teacher already exists")

    # Create user
    user_id = str(uuid.uuid4())
    hashed_pass = hash_password(password)

    db_insert_one("users", {
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "roles": json.dumps(["class_teacher"]),
        "org_id": current_user["org_id"],
        "hashed_password": hashed_pass
    })

    # Assign to section
    db_update_one("sections", section_id, {"class_teacher_id": user_id})

    return {"message": "Teacher assigned to section"}

@app.post("/api/orgs/{org_id}/departments/{dept_id}/assign-hod")
@require_any_role("admin")
def assign_hod(org_id: str, dept_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
    if current_user.get("org_id") != org_id:
        raise HTTPException(status_code=403, detail="Not your org")

    user = get_user_row_by_email(payload.email)

    if not user:
        # create user if not exist
        user_id = str(uuid.uuid4())
        hashed_pass = hash_password(payload.password)
        user = {
            "id": user_id,
            "email": payload.email,
            "full_name": payload.full_name,
            "roles": json.dumps(["hod"]),
            "org_id": org_id,
            "hashed_password": hashed_pass
        }
        db_insert_one("users", user)
    else:
        # update role if existing user
        roles = parse_roles_field(user.get("roles"))
        if "hod" not in roles:
            roles.append("hod")
        db_update_one("users", user["id"], {"roles": json.dumps(roles)})

    # Store HOD–Department mapping
    db_insert_one("department_hods", {
        "id": str(uuid.uuid4()),
        "org_id": org_id,
        "dept_id": dept_id,
        "hod_id": user["id"]
    })

    return {"message": "HOD assigned successfully"}


@app.get("/api/departments/{dept_id}/classes")
@require_any_role("hod")
def get_dept_classes(dept_id: str, current_user=Depends(get_current_user)):
    hod_map = db_find_one("department_hods", hod_id=current_user["id"], dept_id=dept_id)
    if not hod_map:
        raise HTTPException(status_code=403, detail="Not HOD of this department")

    classes = db_find_many("classes", department_id=dept_id)
    return classes

@app.get("/api/departments/{dept_id}/class-teachers")
@require_any_role("hod")
def list_class_teachers(dept_id: str, current_user=Depends(get_current_user)):
    hod_map = db_find_one("department_hods", hod_id=current_user["id"], dept_id=dept_id)
    if not hod_map:
        raise HTTPException(status_code=403, detail="Not your department")

    entries = db_find_many("dept_class_teachers", dept_id=dept_id)

    teachers = []
    for e in entries:
        u = get_user_row(e["class_teacher_id"])
        if u:
            teachers.append(u)

    return teachers

@app.post('/api/departments/create')
@require_any_role('admin')
def create_department(req: CreateDeptReq, current_user=Depends(get_current_user)):
    new_dept = {
        "id": str(uuid.uuid4()),
        "org_id": req.org_id,
        "name": req.name,
        "hod_id": None
    }
    db_insert_one('departments', new_dept)
    return new_dept
@app.get("/api/hod/department")
@require_any_role("hod")
def get_hod_department(current_user=Depends(get_current_user)):
    hod_id = current_user["id"]

    # 1️⃣ Get mapping entry
    mapping = db_find_one("department_hods", hod_id=hod_id)
    if not mapping:
        raise HTTPException(404, "Department not assigned")

    dept_id = mapping["dept_id"]

    # 2️⃣ Get real department row
    dept = db_find_one("departments", id=dept_id)
    if not dept:
        raise HTTPException(404, "Department missing in DB")

    return dept
def find_user_section(user_id: str):
    # user must be in class_memberships
    memberships = db_find_many("class_memberships", user_id=user_id)

    for m in memberships:
        cls = db_find_one("classes", id=m["class_id"])
        if cls and cls.get("section"):
            return cls["section"]
    
    return None  # not assigned
@app.get("/api/user/{user_id}/section/students")
def get_students_from_user_section(user_id: str):
    section = find_user_section(user_id)
    if not section:
        raise HTTPException(404, detail="User has no section assigned")

    classes = db_find_many("classes", section=section)
    class_ids = [c["id"] for c in classes]

    students = {}
    for cid in class_ids:
        members = db_find_many("class_memberships", class_id=cid, role="student")
        for m in members:
            u = db_find_one("users", id=m["user_id"])
            if u:
                students[u["id"]] = {
                    "id": u["id"],
                    "name": u["full_name"],
                    "email": u["email"]
                }

    return list(students.values())
@app.get("/api/user/{user_id}/section/notes")
def get_notes_from_user_section(user_id: str):
    section = find_user_section(user_id)
    if not section:
        raise HTTPException(404, detail="User has no section assigned")

    classes = db_find_many("classes", section=section)
    class_ids = [c["id"] for c in classes]

    notes = []
    for cid in class_ids:
        notes += db_find_many("notes", class_id=cid)

    return notes
@app.get("/api/user/{user_id}/section/grades")
def get_grades_from_user_section(user_id: str):
    section = find_user_section(user_id)
    if not section:
        raise HTTPException(404, detail="User has no section assigned")

    classes = db_find_many("classes", section=section)
    class_ids = [c["id"] for c in classes]

    grades = []
    for cid in class_ids:
        grades += db_find_many("final_marks", class_id=cid)

    return grades


@app.get("/api/user/{user_id}/grades")
def get_user_grades(user_id: str):
    # 1. find student’s section
    section = find_user_section(user_id)
    if not section:
        raise HTTPException(404, detail="User has no section assigned")

    # 2. find all classes in that section
    classes = db_find_many("classes", section=section)
    class_ids = [c["id"] for c in classes]

    # 3. fetch all grades for this student from all section classes
    all_marks = []
    for cid in class_ids:
        all_marks += db_find_many("final_marks", class_id=cid, student_id=user_id)

    # 4. group subject → unit → marks
    grouped = {}

    for m in all_marks:
        subject = m["subject_name"]
        unit = m["unit_name"]
        marks = m["marks"]

        if subject not in grouped:
            grouped[subject] = []

        grouped[subject].append({
            "unit": unit,
            "marks": marks,
            "class_id": m["class_id"]
        })

    return {
        "user_id": user_id,
        "section": section,
        "subjects": grouped
    }


@app.post('/api/auth/login')
def login(req: LoginReq):
    user = get_user_row_by_email(req.email)
    
    if not user:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    
    if not verify_password(req.password, user.get('hashed_password', '')):
        raise HTTPException(status_code=401, detail='Invalid credentials')
        
    # Create token
    token = create_access_token(data={"sub": user['id']})
    
    return {'access_token': token}

@app.get('/api/users/me')
def get_me(current_user=Depends(get_current_user)):
    # This works perfectly now!
    return current_user

# -------------------------
# REFACTORED: ORGANIZATIONS
# -------------------------
@app.post('/api/orgs')
@require_owner
def create_org(req: CreateOrgReq, current_user=Depends(get_current_user)):
    org_type = req.org_type or DEFAULT_ORG_TYPE
    if org_type not in ('school','college','university'):
        raise HTTPException(status_code=400, detail='org_type must be school|college|university')
    
    new_org = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "org_type": org_type
    }
    db_insert_one('organizations', new_org)
    return new_org

@app.get('/api/orgs')
@require_owner
def list_orgs(current_user=Depends(get_current_user)):
    return load_db('organizations')

@app.post('/api/orgs/{org_id}/admin/create')
@require_owner
def create_admin(org_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
    if not db_find_one('organizations', id=org_id):
        raise HTTPException(status_code=404, detail='Organization not found')
        
    if get_user_row_by_email(payload.email):
        raise HTTPException(status_code=400, detail="User with this email already exists")

    password = payload.password or secrets.token_urlsafe(10)
    user_id = str(uuid.uuid4())
    hashed_pass = hash_password(password)

    new_admin = {
        'id': user_id,
        'email': payload.email,
        'full_name': payload.full_name,
        'roles': json.dumps(['admin']),
        'org_id': org_id,
        'hashed_password': hashed_pass
    }
    
    db_insert_one('users', new_admin)
    return {'message':'admin created', 'user_id': user_id}

# -------------------------
# REFACTORED: ADMIN actions
# -------------------------
@app.post('/api/orgs/{org_id}/teachers/create')
@require_any_role('admin')
def create_class_teacher(org_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
    if current_user.get('org_id') != org_id:
        raise HTTPException(status_code=403, detail='Not your org')
        
    if get_user_row_by_email(payload.email):
        raise HTTPException(status_code=400, detail="User with this email already exists")

    password = payload.password or secrets.token_urlsafe(8)
    user_id = str(uuid.uuid4())
    hashed_pass = hash_password(password)

    new_teacher = {
        'id': user_id,
        'email': payload.email,
        'full_name': payload.full_name,
        'roles': json.dumps(['class_teacher']),
        'org_id': org_id,
        'hashed_password': hashed_pass
    }
    
    db_insert_one('users', new_teacher)
    return {'message':'class teacher created', 'user_id': user_id}

@app.delete('/api/orgs/{org_id}/teachers/{teacher_id}')
@require_any_role('admin')
def delete_class_teacher(org_id: str, teacher_id: str, current_user=Depends(get_current_user)):
    if current_user.get('org_id') != org_id:
        raise HTTPException(status_code=403, detail='Not your org')
    
    # We can't filter by org_id in db_delete_one, so we check first
    teacher = db_find_one('users', id=teacher_id, org_id=org_id)
    if teacher:
        db_delete_one('users', teacher_id)
        
    return {'message':'deleted teacher if existed'}

# -------------------------
# REFACTORED: DEPARTMENTS
# -------------------------
@app.post('/api/departments/create')
@require_any_role('admin')
def create_department(req: CreateDeptReq, current_user=Depends(get_current_user)):
    if current_user.get('org_id') != req.org_id:
        raise HTTPException(status_code=403, detail='Not your org')
    
    new_dept = {
        "id": str(uuid.uuid4()),
        'org_id': req.org_id,
        'name': req.name,
        'hod_id': req.hod_id
    }
    db_insert_one('departments', new_dept)
    return new_dept

@app.get('/api/orgs/{org_id}/departments')
@require_any_role('admin','class_teacher','sub_teacher')
def list_departments(org_id: str, current_user=Depends(get_current_user)):
    return db_find_many('departments', org_id=org_id)

# -------------------------
# REFACTORED: TEACHER HIERARCHY
# -------------------------
@app.post('/api/teachers/add-sub')
@require_any_role('class_teacher','admin')
def add_sub_teacher(payload: AddUserReq, current_user=Depends(get_current_user)):
    org_id = current_user.get('org_id')
    
    # if get_user_row_by_email(payload.email):
    #     raise HTTPException(status_code=400, detail="User with this email already exists")

    password = payload.password or secrets.token_urlsafe(10)
    user_id = str(uuid.uuid4())
    hashed_pass = hash_password(password)

    new_sub_teacher = {
        'id': user_id,
        'email': payload.email,
        'full_name': payload.full_name,
        'roles': json.dumps(['sub_teacher']),
        'org_id': org_id,
        'hashed_password': hashed_pass
    }
    db_insert_one('users', new_sub_teacher)
    
    db_insert_one('teacher_hierarchy', {
        'id': str(uuid.uuid4()),
        'org_id': org_id,
        'class_teacher_id': current_user['id'],
        'sub_teacher_id': user_id
    })
    return {'message':'sub teacher added', 'user_id': user_id}

# -------------------------
# REFACTORED: CLASSES
# -------------------------

@app.post('/api/classes')
@require_any_role('sub_teacher', 'class_teacher')
def create_class(req: CreateClassReq, current_user=Depends(get_current_user)):

    # Generate unique class code
    code = ""
    for _ in range(6):
        code = secrets.token_urlsafe(4).upper()
        if not db_find_one('classes', class_code=code):
            break

    # Determine class_teacher_id
    ct_id = None
    if 'sub_teacher' in parse_roles_field(current_user.get('roles', [])):
        # Get linked class teacher
        h = db_find_one("teacher_hierarchy", sub_teacher_id=current_user["id"])
        if not h:
            raise HTTPException(status_code=400, detail="No linked class teacher found for this sub_teacher.")
        ct_id = h["class_teacher_id"]

    elif 'class_teacher' in parse_roles_field(current_user.get('roles', [])):
        ct_id = current_user["id"]

    else:
        raise HTTPException(status_code=403, detail="Not allowed")

    # ----------------------------------------
    # 🔥 AUTO-DETECT DEPARTMENT + SECTION
    # ----------------------------------------
    mapping = db_find_one("dept_class_teachers", class_teacher_id=ct_id)

    dept_id = mapping["dept_id"] if mapping else None
    section = mapping["section"] if mapping else None

    # ----------------------------------------
    # Create new class
    # ----------------------------------------
    body = {
        "id": str(uuid.uuid4()),
        "org_id": req.org_id,
        "title": req.title,
        "description": req.description,
        "created_by": current_user["id"],
        "class_teacher_id": ct_id,
        "class_code": code,
        "department_id": dept_id,
        "section": section    # 🔥 NOW ALWAYS SAVED
    }

    new_class = db_insert_one("classes", body)

    # Add teacher membership
    db_insert_one("class_memberships", {
        "id": str(uuid.uuid4()),
        "class_id": new_class["id"],
        "user_id": current_user["id"],
        "role": "teacher"
    })

    return new_class



@app.get("/api/classes/{class_id}")
def get_class_info(class_id: str):
    cls = db_find_one("classes", id=class_id)
    if not cls:
        raise HTTPException(404, "Class not found")
    return cls


@app.delete('/api/classes/{class_id}')
@require_any_role('sub_teacher','class_teacher','admin')
def delete_class(class_id: str, current_user=Depends(get_current_user)):
    c = db_find_one('classes', id=class_id)
    if not c:
        raise HTTPException(status_code=404, detail='Class not found')
    
    allowed = False
    if 'admin' in parse_roles_field(current_user.get('roles', [])) and current_user.get('org_id') == c.get('org_id'):
        allowed = True
    if c.get('created_by') == current_user['id']:
        allowed = True
    if c.get('class_teacher_id') == current_user['id']:
        allowed = True
    
    if not allowed:
        raise HTTPException(status_code=403, detail='Not allowed to delete this class')
    
    db_delete_one('classes', class_id)
    return {'message':'deleted'}

@app.get("/api/classes/{class_id}/students")
@require_any_role("class_teacher", "sub_teacher", "admin","student")
def get_class_students(class_id: str, current_user=Depends(get_current_user)):
    # Check member
    m = db_find_one("class_memberships", class_id=class_id, user_id=current_user["id"])
    if not m:
        raise HTTPException(status_code=403, detail="Not part of this class")

    # Fetch all memberships STUDENTS
    members = db_find_many("class_memberships", class_id=class_id)

    students = []
    for mem in members:
        if mem.get("role") == "student":
            u = get_user_row(mem["user_id"])
            if u:
                students.append({
                    "id": u["id"],
                    "full_name": u.get("full_name"),
                    "email": u.get("email")
                })

    return students

@app.get("/api/classes")
@require_any_role("sub_teacher", "class_teacher", "admin", "student")
def list_classes(current_user=Depends(get_current_user)):
    roles = parse_roles_field(current_user.get("roles", []))
    org_id = current_user.get("org_id")

    # ADMIN → sees all classes of org
    if "admin" in roles:
        return db_find_many("classes", org_id=org_id) or []

    # CLASS TEACHER → sees classes where she is class_teacher
    if "class_teacher" in roles:
        return db_find_many("classes", class_teacher_id=current_user["id"]) or []

    # SUB TEACHER → sees classes where she is added as 'teacher'
    if "sub_teacher" in roles:
        memberships = db_find_many("class_memberships", user_id=current_user["id"], role="teacher")
        class_ids = [m["class_id"] for m in memberships]
        all_classes = load_db("classes")
        return [c for c in all_classes if c["id"] in class_ids]

    # STUDENT → sees classes where they are member
    if "student" in roles:
        memberships = db_find_many("class_memberships", user_id=current_user["id"], role="student")
        class_ids = [m["class_id"] for m in memberships]
        all_classes = load_db("classes")
        return [c for c in all_classes if c["id"] in class_ids]

    raise HTTPException(status_code=403, detail="Not allowed")

@app.post("/api/teachers/add-student")
@require_any_role("class_teacher", "admin", "sub_teacher")
def add_student(payload: AddStudentReq, current_user=Depends(get_current_user)):
    """
    Create or update a student and add them to the given class.
    Accepts JSON body: { class_id, email, full_name, password }
    """
    class_id = payload.class_id
    email = payload.email.strip().lower()
    full_name = (payload.full_name or "").strip()
    password = payload.password or secrets.token_urlsafe(8)

    # Validate class exists
    cls = db_find_one("classes", id=class_id)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    # Permission checks: admin in same org OR class_teacher owning class OR sub_teacher who is teacher member
    roles = parse_roles_field(current_user.get("roles") or [])
    allowed = False
    if "admin" in roles and current_user.get("org_id") == cls.get("org_id"):
        allowed = True
    if "class_teacher" in roles and cls.get("class_teacher_id") == current_user["id"]:
        allowed = True
    if "sub_teacher" in roles:
        cm = db_find_one("class_memberships", class_id=class_id, user_id=current_user["id"])
        if cm and cm.get("role") == "teacher":
            allowed = True
    if not allowed:
        raise HTTPException(status_code=403, detail="Not allowed to add students to this class")

    # Ensure email provided
    if not email:
        raise HTTPException(status_code=400, detail="Email required")

    existing = db_find_one("users", email=email)
    if existing:
        user_id = existing["id"]
        # ensure 'student' role present
        roles_list = parse_roles_field(existing.get("roles") or [])
        if "student" not in roles_list:
            roles_list.append("student")
            db_update_one("users", user_id, {"roles": json.dumps(roles_list)})
        # ensure org matches class org
        if existing.get("org_id") != cls.get("org_id"):
            db_update_one("users", user_id, {"org_id": cls.get("org_id")})
    else:
        # create new user with hashed password
        user_id = str(uuid.uuid4())
        hashed_pass = hash_password(password)
        new_user = {
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "roles": json.dumps(["student"]),
            "org_id": cls.get("org_id"),
            "hashed_password": hashed_pass
        }
        db_insert_one("users", new_user)

    # create membership if not exists
    existing_mem = db_find_one("class_memberships", class_id=class_id, user_id=user_id)
    if not existing_mem:
        db_insert_one("class_memberships", {
            "id": str(uuid.uuid4()),
            "class_id": class_id,
            "user_id": user_id,
            "role": "student"
        })

    return {"message": "student added/updated", "user_id": user_id}

# -------------------------
# REFACTORED: ASSIGNMENTS
# -------------------------
@app.post('/api/assignments')
@require_any_role('sub_teacher')
def create_assignment(req: CreateAssignmentReq, current_user=Depends(get_current_user)):
    cm = db_find_one('class_memberships', class_id=req.class_id, user_id=current_user['id'])
    if not cm or cm.get('role') != 'teacher':
        raise HTTPException(status_code=403, detail='Only the subject teacher can create assignments for this class')
    if req.assignment_type not in ('file','text','mixed'):
        raise HTTPException(status_code=400, detail='Invalid assignment_type')
        
    body = {
        'id': str(uuid.uuid4()),
        'class_id': req.class_id, 
        'created_by': current_user['id'], 
        'title': req.title, 
        'description': req.description, 
        'due_at': req.due_at, 
        'assignment_type': req.assignment_type
    }
    new_assignment = db_insert_one('assignments', body)
    return new_assignment

@app.post('/api/assignments/{assignment_id}/upload-file')
@require_any_role('sub_teacher')
def upload_assignment_file(assignment_id: str, file: UploadFile = File(...), current_user=Depends(get_current_user)):
    a = db_find_one('assignments', id=assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail='Assignment not found')
        
    cm = db_find_one('class_memberships', class_id=a['class_id'], user_id=current_user['id'])
    if not cm or cm.get('role') != 'teacher':
        raise HTTPException(status_code=403, detail='Only subject teacher can upload file for this assignment')

    bucket_path = UPLOAD_DIR / "assignments" / assignment_id
    bucket_path.mkdir(parents=True, exist_ok=True)
    
    filename = f"{secrets.token_hex(8)}_{file.filename}"
    file_path = bucket_path / filename
    
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Upload failed: {e}')
    
    # Store relative path
    relative_path = os.path.join("uploads", "assignments", assignment_id, filename)
    db_update_one('assignments', assignment_id, {'file_path': relative_path})
    
    return {'message':'file uploaded', 'file_path': relative_path}

@app.get('/api/classes/{class_id}/assignments')
def list_assignments(class_id: str, current_user=Depends(get_current_user)):
    m = db_find_one('class_memberships', class_id=class_id, user_id=current_user['id'])
    if not m:
        raise HTTPException(status_code=403, detail='Not a member of class')
    
    return db_find_many('assignments', class_id=class_id)

# -------------------------
# REFACTORED: SUBMISSIONS
# -------------------------
@app.post('/api/submissions')
@require_any_role('student')
def submit_assignment(
    assignment_id: str = Form(...),
    text_content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user=Depends(get_current_user)
):
    # Validate assignment
    assignment = db_find_one('assignments', id=assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail='Assignment not found')

    class_id = assignment['class_id']
    cm = db_find_one('class_memberships', class_id=class_id, user_id=current_user["id"])
    if not cm:
        raise HTTPException(status_code=403, detail="Not in class")

    file_path = None
    if file:
        bucket_path = UPLOAD_DIR / "submissions" / assignment_id / current_user["id"]
        bucket_path.mkdir(parents=True, exist_ok=True)

        filename = f"{secrets.token_hex(8)}_{file.filename}"
        full_path = bucket_path / filename

        with open(full_path, "wb") as f:
            f.write(file.file.read())

        file_path = f"uploads/submissions/{assignment_id}/{current_user['id']}/{filename}"

    # Check if exists
    existing = db_find_one("submissions", assignment_id=assignment_id, student_id=current_user["id"])

    if existing:
        db_update_one("submissions", existing["id"], {
            "text_content": text_content,
            "file_path": file_path,
            "submitted_at": datetime.utcnow()
        })
        return {"message": "updated submission"}

    new_sub = {
        "id": str(uuid.uuid4()),
        "assignment_id": assignment_id,
        "student_id": current_user["id"],
        "text_content": text_content,
        "file_path": file_path,
        "submitted_at": datetime.utcnow()
    }

    db_insert_one("submissions", new_sub)
    return {"message": "submitted", "id": new_sub["id"]}



@app.get('/api/assignments/{assignment_id}/submissions')
@require_any_role('sub_teacher','class_teacher')
def get_submissions(assignment_id: str, current_user=Depends(get_current_user)):
    a = db_find_one('assignments', id=assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail='Assignment not found')
    
    class_id = a['class_id']
    cm = db_find_one('class_memberships', class_id=class_id, user_id=current_user['id'])
    is_teacher = cm and cm.get('role') == 'teacher'
    
    cls = db_find_one('classes', id=class_id)
    is_supervisor = cls and cls.get('class_teacher_id') == current_user['id']
    
    if not (is_teacher or is_supervisor):
        raise HTTPException(status_code=403, detail='Not allowed')
        
    subs = db_find_many('submissions', assignment_id=assignment_id)

    # ---- ADD STUDENT DETAILS ----
    enriched = []
    for s in subs:
        user = db_find_one('users', id=s['student_id'])
        enriched.append({
            **s,
            "student_name": user.get("full_name") if user else None,
            "student_email": user.get("email") if user else None
        })
    
    return enriched
from pydantic import BaseModel

class GradeRequest(BaseModel):
    grade: float
@app.post("/api/submissions/{submission_id}/grade")
@require_any_role("sub_teacher")
def grade_submission(submission_id: str, body: GradeRequest, current_user=Depends(get_current_user)):
    grade = body.grade

    submission = db_find_one("submissions", id=submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    assignment = db_find_one("assignments", id=submission["assignment_id"])
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    class_id = assignment["class_id"]

    membership = db_find_one("class_memberships", class_id=class_id, user_id=current_user["id"])
    if not membership:
        raise HTTPException(status_code=403, detail="You are not part of this class")

    # 💡 removed strict subject teacher authorization check

    db_update_one("submissions", submission_id, {
        "grade": grade,
        "graded_by": current_user["id"]
    })

    return {"message": "Grade submitted successfully"}


# -------------------------
# REFACTORED: NOTES
# -------------------------
@app.post('/api/notes')
@require_any_role('sub_teacher','class_teacher')
def upload_note(req: NoteCreateReq, current_user=Depends(get_current_user)):
    # Note: This implies the file is *already* uploaded, e.g., by a separate endpoint.
    # We will just save the record.
    # A real solution would use an upload endpoint like assignments.
    cm = db_find_one('class_memberships', class_id=req.class_id, user_id=current_user['id'])
    if not cm or cm.get('role') != 'teacher':
        raise HTTPException(status_code=403, detail='Only subject teacher can upload notes')
        
    new_note = {
        'id': str(uuid.uuid4()),
        'class_id': req.class_id, 
        'uploaded_by': current_user['id'], 
        'title': req.title, 
        'file_path': req.file_path
    }
    db_insert_one('notes', new_note)
    return new_note

@app.get('/api/classes/{class_id}/notes')
def list_notes(class_id: str, current_user=Depends(get_current_user)):
    cm = db_find_one('class_memberships', class_id=class_id, user_id=current_user['id'])
    if not cm:
        raise HTTPException(status_code=403, detail='Not a member')
    
    return db_find_many('notes', class_id=class_id)

@app.post("/api/notes/upload")
@require_any_role("class_teacher", "sub_teacher")
def upload_note(
    class_id: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    # Check membership
    cm = db_find_one("class_memberships", class_id=class_id, user_id=current_user["id"])
    if not cm or cm.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Not allowed")

    # Upload to cloudinary
    try:
        upload_result = cloudinary.uploader.upload(
            file.file,
            folder=f"class_notes/{class_id}",  
            resource_type="auto"
        )
    except Exception as e:
        raise HTTPException(500, f"Cloudinary upload failed: {e}")

    note_id = str(uuid.uuid4())

    note = {
        "id": note_id,
        "class_id": class_id,
        "uploaded_by": current_user["id"],
        "title": title,
        "file_url": upload_result["secure_url"],   # ⭐ main download URL
        "public_id": upload_result["public_id"],   # ⭐ useful for deleting later
        "uploaded_at": str(datetime.utcnow())
    }

    db_insert_one("notes", note)

    return {"message": "Uploaded", "note": note}

# -------------------------
# REFACTORED: FINAL MARKS
# -------------------------
@app.post('/api/finalmarks')
@require_any_role('sub_teacher')
def upload_final_marks(req: FinalMarkReq, current_user=Depends(get_current_user)):
    stu = get_user_row(req.student_id)
    if not stu:
        raise HTTPException(status_code=404, detail='Student not found')
        
    body = req.dict()
    body['id'] = str(uuid.uuid4())
    body['uploaded_by'] = current_user['id']
    
    db_insert_one('final_marks', body)
    return {'message':'uploaded'}


@app.get("/api/classes/{class_id}/grades")
@require_any_role("admin", "class_teacher", "sub_teacher", "student","hod")
def get_class_grades(class_id: str, current_user=Depends(get_current_user)):

    # # Check if user is part of the class
    # member = db_find_one("class_memberships", class_id=class_id, user_id=current_user["id"])
    # if not member:
    #     raise HTTPException(status_code=403, detail="Not part of this class")

    roles = parse_roles_field(current_user.get("roles", []))
    org_id = current_user.get("org_id")

    # ADMIN → sees all marks in org for this class
    if "admin" in roles:
        return db_find_many("final_marks", class_id=class_id, org_id=org_id) or []
    if "hod" in roles:
        return db_find_many("final_marks", class_id=class_id) or []
    # CLASS TEACHER → sees grades only for their classes
    if "class_teacher" in roles:
        return db_find_many("final_marks", class_id=class_id) or []
        # cls = db_find_one("classes", id=class_id)
        # if cls and cls.get("class_teacher_id") == current_user["id"]:
        #     return db_find_many("final_marks", class_id=class_id) or []
        # raise HTTPException(status_code=403, detail="Not your class")

    # SUB TEACHER → can view all marks in class
    if "sub_teacher" in roles:
        return db_find_many("final_marks", class_id=class_id) or []

    # STUDENT → only their own grades
    if "student" in roles:
        return db_find_many("final_marks", class_id=class_id, student_id=current_user["id"]) or []

    raise HTTPException(status_code=403, detail="Not allowed")


@app.get('/api/orgs/{org_id}/grades')
@require_any_role('class_teacher','admin','sub_teacher')
def view_all_grades(org_id: str, current_user=Depends(get_current_user)):
    roles = parse_roles_field(current_user.get('roles') or [])
    all_marks = load_db('final_marks')
    
    if 'class_teacher' in roles:
        classes = db_find_many('classes', class_teacher_id=current_user['id'], org_id=org_id)
        class_ids = [c['id'] for c in classes]
        return [m for m in all_marks if m.get('class_id') in class_ids]
        
    if 'admin' in roles and current_user.get('org_id') == org_id:
        return [m for m in all_marks if m.get('org_id') == org_id]
        
    if 'sub_teacher' in roles:
        cm = db_find_many('class_memberships', user_id=current_user['id'], role='teacher')
        class_ids = [c['class_id'] for c in cm]
        return [m for m in all_marks if m.get('class_id') in class_ids]
        
    raise HTTPException(status_code=403, detail='Not allowed')

# -------------------------
# REFACTORED: MESSAGES
# -------------------------
@app.post('/api/messages')
@require_any_role('student','sub_teacher','class_teacher','admin')
def send_message(req: MessageReq, current_user=Depends(get_current_user)):
    cm = db_find_one('class_memberships', class_id=req.class_id, user_id=current_user['id'])
    if not cm:
        raise HTTPException(status_code=403, detail='Not a member of this class')
        
    if not req.is_public:
        if not req.receiver_id:
            raise HTTPException(status_code=400, detail='receiver_id required for private message')
        if 'student' in parse_roles_field(current_user.get('roles', [])):
            check = db_find_one('class_memberships', class_id=req.class_id, user_id=req.receiver_id)
            if not check or check.get('role') != 'teacher':
                raise HTTPException(status_code=403, detail='Receiver must be a teacher for this class')
                
    db_insert_one('messages', {
        'id': str(uuid.uuid4()),
        'class_id': req.class_id,
        'sender_id': current_user['id'],
        'receiver_id': req.receiver_id if not req.is_public else None,
        'content': req.content,
        'is_public': req.is_public,
        'sent_at': datetime.utcnow()
    })
    return {'message':'sent', 'type': 'public' if req.is_public else 'private'}

@app.get('/api/classes/{class_id}/messages')
@require_any_role('student','sub_teacher','class_teacher','admin')
def get_messages(class_id: str, current_user=Depends(get_current_user)):
    cm = db_find_one('class_memberships', class_id=class_id, user_id=current_user['id'])
    if not cm:
        raise HTTPException(status_code=403, detail='Not a member')
    
    user_id = current_user['id']
    msgs = db_find_many('messages', class_id=class_id)
    
    visible = [m for m in msgs if m.get('is_public') or m.get('sender_id')==user_id or m.get('receiver_id')==user_id]
    return visible

# -------------------------
# REFACTORED: BULK IMPORT
# -------------------------
@app.post('/api/admin/preview-import')
@require_any_role('admin')
def preview_import(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    content = file.file.read()
    try:
        if file.filename.lower().endswith(('.xls','.xlsx')):
            df = pd.read_excel(BytesIO(content))
        else:
            df = pd.read_csv(BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Could not parse file: {e}')
    preview = df.head(10).fillna('').to_dict(orient='records')
    columns = list(df.columns)
    return {'columns': columns, 'preview': preview}

@app.post("/api/teachers/import-students")
@require_any_role("class_teacher")
def import_students_for_class(
    file: UploadFile = File(...),
    class_id: str = Query(..., description="Class ID to which students will be added"),
    current_user=Depends(get_current_user)
):
    """
    Allows class teachers to upload an Excel/CSV of students for their class.
    Format: name, email, password
    """
    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="User not linked to any organization")

    # ✅ Validate class ownership
    cls = db_find_one("classes", id=class_id)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    if cls.get("class_teacher_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not allowed to import students for another teacher's class")

    # ✅ Parse Excel or CSV
    content = file.file.read()
    try:
        if file.filename.lower().endswith((".xls", ".xlsx")):
            df = pd.read_excel(BytesIO(content))
        else:
            df = pd.read_csv(BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse file: {e}")

    # ✅ Expected columns
    required_columns = {"name", "email", "password"}
    missing_cols = required_columns - set(df.columns.str.lower())
    if missing_cols:
        raise HTTPException(
            status_code=400,
            detail=f"Missing columns: {', '.join(missing_cols)} (Expected: name, email, password)"
        )

    created = {"new_students": 0, "existing_students": 0, "memberships_added": 0, "errors": []}

    for _, row in df.iterrows():
        try:
            name = str(row.get("name") or row.get("Name") or "").strip()
            email = str(row.get("email") or row.get("Email") or "").strip().lower()
            password = str(row.get("password") or row.get("Password") or "").strip()

            if not email:
                continue

            # ✅ Check if student exists
            existing = get_user_row_by_email(email)
            if existing:
                user_id = existing["id"]
                roles = parse_roles_field(existing.get("roles"))
                if "student" not in roles:
                    roles.append("student")
                    db_update_one("users", user_id, {"roles": json.dumps(roles)})
                created["existing_students"] += 1
            else:
                # ✅ Create new student
                user_id = str(uuid.uuid4())
                hashed_pass = hash_password(password or secrets.token_urlsafe(8))
                new_student = {
                    "id": user_id,
                    "email": email,
                    "full_name": name,
                    "roles": json.dumps(["student"]),
                    "org_id": org_id,
                    "hashed_password": hashed_pass,
                }
                db_insert_one("users", new_student)
                created["new_students"] += 1

            # ✅ Add class membership
            if not db_find_one("class_memberships", class_id=class_id, user_id=user_id):
                db_insert_one(
                    "class_memberships",
                    {
                        "id": str(uuid.uuid4()),
                        "class_id": class_id,
                        "user_id": user_id,
                        "role": "student",
                    },
                )
                created["memberships_added"] += 1
        except Exception as e:
            created["errors"].append(str(e))
            continue

    return {
        "message": "Import completed",
        "summary": created
    }

@app.post('/api/admin/import-file')
@require_any_role('admin')
def import_file(
    file: UploadFile = File(...),
    mapping_req: str = Form(...),   # <── FIXED
    current_user=Depends(get_current_user)
):
    # parse JSON string
    try:
        mapping_req = json.loads(mapping_req)
    except:
        raise HTTPException(400, "mapping_req must be JSON")

    mapping = mapping_req.get("mapping", {})
    create_departments = mapping_req.get("create_departments", True)

    org_id = current_user.get('org_id')
    if not org_id:
        raise HTTPException(400, "Admin has no org_id assigned")

    content = file.file.read()
    try:
        if file.filename.lower().endswith(('.xls','.xlsx')):
            df = pd.read_excel(BytesIO(content))
        else:
            df = pd.read_csv(BytesIO(content))
    except Exception as e:
        raise HTTPException(400, f"Could not parse file: {e}")

    # continue your logic EXACTLY as before...

    created = {
    "users": 0,
    "classes": 0,
    "departments": 0,
    "memberships": 0,
    "skipped": 0,
    "errors": []
}

    mapping = mapping_req.get("mapping", {})
    create_departments = mapping_req.get("create_departments", True)

    # --- Load all data into memory once to avoid repeated file I/O ---
    all_users = load_db('users')
    all_depts = load_db('departments')
    all_classes = load_db('classes')
    all_memberships = load_db('class_memberships')

    def find_user_by_email_local(email):
        return next((u for u in all_users if u['email'] == email), None)
    def find_dept_local(name, org_id):
        return next((d for d in all_depts if d['name'] == name and d['org_id'] == org_id), None)
    def find_class_local(title, org_id, dept_id):
        return next((c for c in all_classes if c['title'] == title and c['org_id'] == org_id and c['department_id'] == dept_id), None)

    for idx, row in df.iterrows():
        try:
            def get_col(key):
                col = mapping.get(key) or key
                if col in row.index:
                    return row.get(col)
                return None

            name = str(get_col('name') or get_col('Name') or '').strip()
            email = str(get_col('email') or get_col('Email') or '').strip().lower()
            role = str(get_col('role') or get_col('Role') or 'student').strip().lower()
            dept_name = str(get_col('department') or get_col('Department') or '').strip() or None
            class_title = str(get_col('class') or get_col('Class') or get_col('Class Title') or '').strip() or None
            section = str(get_col('section') or get_col('Section') or '').strip() or None
            password = str(get_col('password') or get_col('Password') or secrets.token_urlsafe(8))
            
            if not email:
                created['skipped'] += 1
                continue
                
            existing = find_user_by_email_local(email)
            user_id = None
            if existing:
                user_id = existing['id']
                roles = parse_roles_field(existing.get('roles'))
                if role and role not in roles:
                    roles.append(role)
                existing.update({'full_name': name, 'roles': json.dumps(roles), 'org_id': org_id})
            else:
                user_id = str(uuid.uuid4())
                hashed_pass = hash_password(password)
                roles_list = [role] if role else []
                all_users.append({
                    'id': user_id, 
                    'email': email, 
                    'full_name': name, 
                    'roles': json.dumps(roles_list), 
                    'org_id': org_id,
                    'hashed_password': hashed_pass
                })
                created['users'] += 1
            
            # department
            dept_id = None
            if dept_name:
                dept = find_dept_local(dept_name, org_id)
                if not dept:
                    if mapping_req.create_departments:
                        dept_id = str(uuid.uuid4())
                        all_depts.append({'id': dept_id, 'org_id': org_id, 'name': dept_name})
                        created['departments'] += 1
                    else:
                        dept_id = None
                else:
                    dept_id = dept['id']
            
            # class
            class_id = None
            if class_title:
                cls = find_class_local(class_title, org_id, dept_id)
                if not cls:
                    class_id = str(uuid.uuid4())
                    code = secrets.token_urlsafe(4).upper()
                    all_classes.append({
                        'id': class_id,
                        'org_id': org_id, 
                        'title': class_title, 
                        'description': f"Section {section or 'General'}", 
                        'department_id': dept_id, 
                        'class_teacher_id': user_id if role=='class_teacher' else None, 
                        'class_code': code
                    })
                    created['classes'] += 1
                else:
                    class_id = cls['id']
            
            # membership
            if class_id and role in ('student','sub_teacher','class_teacher'):
                mem_role = 'teacher' if role in ('sub_teacher','class_teacher') else 'student'
                all_memberships.append({
                    'id': str(uuid.uuid4()),
                    'class_id': class_id, 
                    'user_id': user_id, 
                    'role': mem_role
                })
                created['memberships'] += 1
        except Exception as e:
            created['errors'].append({'row': idx, 'error': str(e)})
            continue
            
    # --- Save all changes to disk at the very end ---
    save_db('users', all_users)
    save_db('departments', all_depts)
    save_db('classes', all_classes)
    save_db('class_memberships', all_memberships)
    
    return created

# -------------------------
# HEALTH (Unchanged)
# -------------------------
@app.get('/')
def root():
    return {'message':'API up'}

# End of file