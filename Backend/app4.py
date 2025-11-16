# """
# Complete single-file FastAPI backend for Classroom app (FULL CLOUD).
# Features:
# - Replaces local JSON DB with Google Firestore.
# - Replaces self-hosted JWT with Firebase Auth (no passwords).
# - Replaces local file storage with Cloudinary for all uploads.
# """
# from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File, Body, Query
# from fastapi.responses import JSONResponse
# from fastapi.openapi.utils import get_openapi
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, EmailStr
# from fastapi import Form

# from typing import Optional, List, Dict, Any
# from dotenv import load_dotenv
# import os, secrets, json, uuid
# from datetime import datetime
# from functools import wraps
# from io import BytesIO
# import pandas as pd
# from pathlib import Path

# # --- New Imports ---
# import firebase_admin
# from firebase_admin import credentials, auth, firestore
# import cloudinary
# import cloudinary.uploader

# # -------------------------
# # Load env & Setup
# # -------------------------
# load_dotenv()
# OWNER_EMAIL = os.getenv("OWNER_EMAIL")
# DEFAULT_ORG_TYPE = os.getenv("DEFAULT_ORG_TYPE", "school")

# if not OWNER_EMAIL:
#     raise RuntimeError("Set OWNER_EMAIL in environment")

# # --- Firebase Admin SDK Setup ---
# # 1. Download your serviceAccountKey.json from Firebase
# # 2. Update the path below
# try:
#     cred = credentials.Certificate("whiteai-ce125-firebase-adminsdk-fbsvc-5e0c161eeb.json") 
#     firebase_admin.initialize_app(cred)
# except Exception as e:
#     raise RuntimeError(f"Failed to initialize Firebase: {e}\nDid you set the path to your serviceAccountKey.json?")

# db = firestore.client() # This is our new database client

# # --- Cloudinary Setup ---
# cloudinary.config(
#     cloud_name=os.getenv('CLOUD_NAME'),
#     api_key=os.getenv('CLOUDINARY_API_KEY'),
#     api_secret=os.getenv('CLOUDINARY_SECRET_KEY')
# )
# if not os.getenv('CLOUD_NAME'):
#     print("WARNING: Cloudinary environment variables not set. File uploads will fail.")


# # -------------------------
# # Pydantic models (Passwords REMOVED)
# # -------------------------
# # class LoginReq(BaseModel): # DELETED
# #     email: EmailStr
# #     password: str

# class CreateOrgReq(BaseModel):
#     name: str
#     org_type: Optional[str] = None  # school / college / university

# class AddUserReq(BaseModel):
#     email: EmailStr
#     full_name: Optional[str] = None
#     roles: Optional[List[str]] = None
#     # password: str # REMOVED

# class AddStudentReq(BaseModel):
#     class_id: str
#     email: EmailStr
#     full_name: Optional[str] = None
#     # password: Optional[str] = None # REMOVED

# class CreateDeptReq(BaseModel):
#     org_id: str
#     name: str
#     hod_id: Optional[str] = None

# class CreateClassReq(BaseModel):
#     org_id: str
#     title: str
#     description: Optional[str] = None
#     department_id: Optional[str] = None
#     section: Optional[str] = None

# class JoinClassReq(BaseModel):
#     class_code: str

# class CreateAssignmentReq(BaseModel):
#     class_id: str
#     title: str
#     description: Optional[str] = None
#     due_at: Optional[datetime] = None
#     assignment_type: Optional[str] = 'file'  # file, text, mixed

# class SubmitReq(BaseModel):
#     assignment_id: str
#     text_content: Optional[str] = None

# class NoteCreateReq(BaseModel):
#     class_id: str
#     title: str
#     file_path: str # Note: This model is now unused, replaced by /api/notes/upload

# class FinalMarkReq(BaseModel):
#     org_id: str
#     class_id: Optional[str] = None
#     student_id: str
#     subject_name: str
#     unit_name: str
#     marks: float

# class MessageReq(BaseModel):
#     class_id: str
#     receiver_id: Optional[str] = None
#     content: str
#     is_public: Optional[bool] = False

# class BulkMappingReq(BaseModel):
#     mapping: Dict[str, str]
#     create_departments: Optional[bool] = True

# # -------------------------
# # NEW: Firestore DB Helpers
# # -------------------------
# def db_find_one(table_name: str, **kwargs) -> Optional[Dict[str, Any]]:
#     """Finds the first item in a collection matching all kwargs."""
#     try:
#         query = db.collection(table_name)
#         for key, value in kwargs.items():
#             query = query.where(key, "==", value)
        
#         docs = query.limit(1).stream()
#         for doc in docs:
#             data = doc.to_dict()
#             data['id'] = doc.id  # Add the doc ID to the dict
#             return data
#         return None
#     except Exception as e:
#         print(f"Error in db_find_one({table_name}, {kwargs}): {e}")
#         return None

# def db_find_many(table_name: str, **kwargs) -> List[Dict[str, Any]]:
#     """Finds all items in a collection matching all kwargs."""
#     try:
#         query = db.collection(table_name)
#         for key, value in kwargs.items():
#             query = query.where(key, "==", value)
        
#         results = []
#         for doc in query.stream():
#             data = doc.to_dict()
#             data['id'] = doc.id
#             results.append(data)
#         return results
#     except Exception as e:
#         print(f"Error in db_find_many({table_name}, {kwargs}): {e}")
#         return []

# def db_insert_one(table_name: str, item: Dict[str, Any], doc_id: Optional[str] = None) -> Dict[str, Any]:
#     """Inserts a new item into a collection. Uses doc_id if provided."""
#     try:
#         if 'id' in item:
#             # Don't store 'id' field *inside* the Firestore document
#             internal_id = item.pop('id')
#             if not doc_id:
#                 doc_id = internal_id
        
#         if doc_id:
#             doc_ref = db.collection(table_name).document(doc_id)
#         else:
#             doc_ref = db.collection(table_name).document()  # Auto-generate ID
        
#         doc_ref.set(item)
#         item['id'] = doc_ref.id  # Return the full dict with ID
#         return item
#     except Exception as e:
#         print(f"Error in db_insert_one({table_name}): {e}")
#         raise HTTPException(status_code=500, detail=f"Firestore insert error: {e}")


# def db_update_one(table_name: str, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
#     """Finds an item by ID and applies updates."""
#     try:
#         doc_ref = db.collection(table_name).document(item_id)
#         doc = doc_ref.get()
#         if not doc.exists:
#             return None
        
#         doc_ref.update(updates)
#         updated_data = doc_ref.get().to_dict()
#         updated_data['id'] = item_id
#         return updated_data
#     except Exception as e:
#         print(f"Error in db_update_one({table_name}, {item_id}): {e}")
#         return None

# def db_delete_one(table_name: str, item_id: str) -> bool:
#     """Deletes an item by its ID."""
#     try:
#         doc_ref = db.collection(table_name).document(item_id)
#         if not doc_ref.get().exists:
#             return False
#         doc_ref.delete()
#         return True
#     except Exception as e:
#         print(f"Error in db_delete_one({table_name}, {item_id}): {e}")
#         return False

# # -------------------------
# # DELETED: Password & JWT Helpers
# # -------------------------
# # def hash_password(...) -> DELETED
# # def verify_password(...) -> DELETED
# # def create_access_token(...) -> DELETED

# # -------------------------
# # REFACTORED: Core Helpers
# # -------------------------
# def _data(resp):
#     return resp

# def parse_roles_field(roles_field: Any) -> List[str]:
#     # This function is perfect, no changes needed.
#     if roles_field is None:
#         return []
#     if isinstance(roles_field, (list, tuple)):
#         return list(roles_field)
#     if isinstance(roles_field, str):
#         try:
#             parsed = json.loads(roles_field)
#             if isinstance(parsed, list):
#                 return parsed
#         except Exception:
#             # comma separated fallback
#             return [r.strip() for r in roles_field.split(",") if r.strip()]
#     return []

# def get_user_row(user_id: str):
#     """Gets a user document from Firestore by its ID (Firebase UID)."""
#     try:
#         doc = db.collection('users').document(user_id).get()
#         if doc.exists:
#             data = doc.to_dict()
#             data['id'] = doc.id
#             return data
#         return None
#     except Exception as e:
#         print(f"Error in get_user_row({user_id}): {e}")
#         return None


# def get_user_row_by_email(email: str):
#     if not email:
#         return None
#     return db_find_one('users', email=email) # Uses new Firestore helper

# def org_has_departments(org_id: str) -> bool:
#     org = db.collection('organizations').document(org_id).get()
#     if not org.exists:
#         return False
#     return org.to_dict().get('org_type') in ('college', 'university')

# # -------------------------
# # REFACTORED: Auth dependency + guards
# # -------------------------
# def get_current_user(authorization: Optional[str] = Header(None)):
#     """
#     Validates Firebase ID Token and returns user doc from Firestore.
#     """
#     if not authorization:
#         raise HTTPException(status_code=401, detail='Missing Authorization header')
#     if not authorization.startswith('Bearer '):
#         raise HTTPException(status_code=401, detail='Invalid Authorization header')
    
#     token = authorization.split(' ', 1)[1]
    
#     try:
#         # 1. Verify the token with Firebase
#         decoded_token = auth.verify_id_token(token)
#         user_id = decoded_token["uid"] # This is the Firebase UID
    
#     except Exception as e:
#         # Token is invalid, expired, etc.
#         raise HTTPException(status_code=401, detail=f'Invalid Firebase token: {e}')
    
#     # 2. Get the user from *our* Firestore 'users' collection
#     app_user = get_user_row(user_id)
    
#     if not app_user:
#         # This means they are authenticated with Firebase, but not in our app DB
#         raise HTTPException(status_code=403, detail='User not registered in app DB')
    
#     # 3. Return the user document
#     return app_user

# # --- require_any_role and require_owner are UNCHANGED (they use get_current_user) ---
# def require_any_role(*roles):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
#             user_roles = parse_roles_field(current_user.get('roles') or [])
#             if not any(r in user_roles for r in roles):
#                 raise HTTPException(status_code=403, detail='Insufficient role')
#             return func(*args, current_user=current_user, **kwargs)
#         return wrapper
#     return decorator

# def require_owner(func):
#     @wraps(func)
#     def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
#         if current_user.get('email') != OWNER_EMAIL:
#             raise HTTPException(status_code=403, detail='Only app owner can perform this action')
#         return func(*args, current_user=current_user, **kwargs)
#     return wrapper

# # -------------------------
# # App & OpenAPI security (Unchanged)
# # -------------------------
# app = FastAPI(title="Classroom Backend (Firestore, Firebase Auth)")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     openapi_schema = get_openapi(title=app.title, version="1.0.0", routes=app.routes)
#     openapi_schema["components"]["securitySchemes"] = {
#         "BearerAuth": {"type":"http","scheme":"bearer","bearerFormat":"JWT"}
#     }
#     openapi_schema["security"] = [{"BearerAuth": []}]
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

# app.openapi = custom_openapi

# # -------------------------
# # REFACTORED: AUTH
# # -------------------------

# def get_roles(user_id):
#     roles = db_find_many("role_assignments", user_id=user_id)
#     return roles or []

# def has_role(user_id, role):
#     return db_find_one("role_assignments", user_id=user_id, role=role) is not None

# def assign_role(user_id, role, org_id=None, dept_id=None, class_id=None):
#     # Store in role_assignments table
#     db_insert_one("role_assignments", {
#         # "id" will be auto-generated by Firestore
#         "user_id": user_id,
#         "role": role,
#         "org_id": org_id,
#         "dept_id": dept_id,
#         "class_id": class_id
#     })

#     # Update "roles" field INSIDE user table
#     user = get_user_row(user_id) # Uses new helper
#     if user:
#         roles = parse_roles_field(user.get("roles"))
#         if role not in roles:
#             roles.append(role)
#             db_update_one("users", user_id, { "roles": json.dumps(roles) })

    
# @app.get("/api/users/roles/{user_id}")
# def get_user_roles(user_id: str):
#     """Return all roles of a user as a clean list."""
    
#     user = get_user_row(user_id)
#     if not user:
#        raise HTTPException(status_code=404, detail="User not found")

#     roles = parse_roles_field(user.get("roles"))
#     return { "roles": roles }


# @app.post("/api/users/create")
# @require_any_role("admin", "class_teacher", "sub_teacher")
# def create_user(payload: AddUserReq, current_user=Depends(get_current_user)):
#     """
#     Create a new user in Firebase Auth and Firestore DB.
#     NO password needed.
#     """
#     org_id = current_user.get("org_id")
#     if not org_id:
#         raise HTTPException(status_code=400, detail="You must belong to an organization")
    
#     if get_user_row_by_email(payload.email):
#         raise HTTPException(status_code=400, detail="User with this email already exists")

#     roles = payload.roles or ["student"]
#     user_id = None
    
#     try:
#         # 1. Create user in Firebase Auth
#         fb_user = auth.create_user(
#             email=payload.email,
#             full_name=payload.full_name,
#             email_verified=True
#         )
#         user_id = fb_user.uid # Get the new Firebase UID
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Firebase Auth error: {e}")

#     # 2. Create user document in Firestore
#     new_user = {
#         "email": payload.email,
#         "full_name": payload.full_name,
#         "roles": json.dumps(roles), # Store roles as a JSON string for consistency
#         "org_id": org_id,
#         # "hashed_password": REMOVED
#     }
    
#     # Use the Firebase UID as the document ID in Firestore
#     db_insert_one("users", new_user, doc_id=user_id)

#     return {
#         "message": "User created successfully in Firebase Auth and Firestore",
#         "email": payload.email,
#         "user_id": user_id,
#         "roles": roles
#     }

# def require_role(*allowed_roles):
#     def wrapper(fn):
#         def inner(*args, current_user=Depends(get_current_user), **kwargs):
#             user_roles = get_roles(current_user["id"])
#             roles_only = [r["role"] for r in user_roles]

#             if not any(role in roles_only for role in allowed_roles):
#                 raise HTTPException(status_code=403, detail="Role not allowed")

#             return fn(*args, current_user=current_user, **kwargs)
#         return inner
#     return wrapper
# # --- PASTE THIS INTO YOUR BACKEND PYTHON FILE ---
# # --- PASTE THIS INTO YOUR BACKEND PYTHON FILE ---

# from pydantic import BaseModel

# # --- Pydantic model for the new form ---
# class AddStudentReq(BaseModel):
#     full_name: str
#     email: str

# # -----------------------------------------------------------------
# # NEW ENDPOINT: Add a student (THIS IS THE ONE YOU'RE MISSING)
# # -----------------------------------------------------------------
# @app.post("/api/class-teacher/add-student")
# @require_any_role("class_teacher") # Only class teachers
# def add_student_to_section(
#     payload: AddStudentReq, 
#     current_user=Depends(get_current_user)
# ):
    
#     # 1. Find the class teacher's assignment
#     teacher_map = db_find_one("dept_class_teachers", class_teacher_id=current_user["id"])
#     if not teacher_map:
#         raise HTTPException(403, "You are not a class teacher of any section")
        
#     section = teacher_map.get("section")
#     dept_id = teacher_map.get("dept_id")
#     org_id = current_user.get("org_id")

#     # 2. Check if student email already exists
#     if get_user_row_by_email(payload.email):
#         raise HTTPException(400, "User with this email already exists")

#     # 3. Create the user
#     user_id = None
#     try:
#         fb_user = auth.create_user(
#             email=payload.email,
#             display_name=payload.full_name  # <-- FIX: Use display_name
#         )
#         user_id = fb_user.uid
        
#         # 4. Add to 'users' collection
#         db_insert_one("users", {
#             "email": payload.email,
#             "full_name": payload.full_name,
#             "roles": ["student"],  # <-- FIX: Save as list
#             "org_id": org_id,
#         }, doc_id=user_id)
        
#         # 5. Add to 'students' collection (mapping)
#         db_insert_one("students", {
#             "user_id": user_id,
#             "full_name": payload.full_name,
#             "email": payload.email,
#             "org_id": org_id,
#             "dept_id": dept_id,
#             "section": section,
#         })
        
#     except Exception as e:
#         if user_id:
#             auth.delete_user(user_id)
#         raise HTTPException(500, f"Error creating student: {e}")

#     return {"message": "Student added successfully", "user_id": user_id}
# from pydantic import BaseModel

# class AssignSubjectTeacherReq(BaseModel):
#     subject_name: str
#     teacher_email: str

# @app.post("/api/class-teacher/assign-subject-teacher")
# @require_any_role("class_teacher") # Only class teachers can call this
# def assign_subject_teacher(
#     payload: AssignSubjectTeacherReq, 
#     current_user=Depends(get_current_user)
# ):
    
#     # 1. Find the class teacher's section (e.g., "5A")
#     teacher_map = db_find_one("dept_class_teachers", class_teacher_id=current_user["id"])
#     if not teacher_map:
#         raise HTTPException(403, "You are not assigned to a section")
    
#     section_name = teacher_map.get("section")
#     dept_id = teacher_map.get("dept_id")

#     # 2. Find the user being assigned (by email)
#     user = get_user_row_by_email(payload.teacher_email)
#     user_id = None
    
#     if not user:
#         # 3a. If user doesn't exist, create them
#         try:
#             fb_user = auth.create_user(
#                 email=payload.teacher_email,
#                 display_name=payload.teacher_email 
#             )
#             user_id = fb_user.uid
            
#             db_insert_one("users", {
#                 "email": payload.teacher_email,
#                 "full_name": "New Teacher", # Placeholder
#                 "roles": ["teacher"], # Start with just 'teacher'
#                 "org_id": current_user["org_id"],
#             }, doc_id=user_id)
            
#         except Exception as e:
#             raise HTTPException(500, f"Firebase Auth error: {e}")
#     else:
#         # 3b. User *does* exist (this is the case you asked about)
#         user_id = user["id"]
        
#         roles = parse_roles_field(user.get("roles") or [])
        
#         if "teacher" not in roles:
#             roles.append("teacher")
#             db_update_one("users", user_id, {"roles": roles})

#     # 4. Map this teacher to the subject and section
#     db_insert_one("subject_teachers", {
#         "dept_id": dept_id,
#         "section": section_name,
#         "subject_name": payload.subject_name,
#         "teacher_id": user_id
#     })

#     return {"message": "Subject teacher assigned successfully", "user_id": user_id}
# @app.post("/api/dept/{dept_id}/assign-hod")
# @require_role("admin")
# def assign_hod(dept_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
#     user = get_user_row_by_email(payload.email)
#     if not user:
#         raise HTTPException(404, "User not found (must be created first)")

#     assign_role(user["id"], "hod", org_id=current_user["org_id"], dept_id=dept_id)
#     return {"message": "HOD Assigned"}

# @app.post("/api/admin/assign-hod")
# @require_any_role("admin")
# def assign_hod(req: dict, current_user=Depends(get_current_user)):
#     dept_id = req.get("dept_id")
#     hod_id = req.get("hod_id") # This is now a Firebase UID

#     dept = db_find_one("departments", id=dept_id)
#     if not dept:
#         raise HTTPException(status_code=404, detail="Department not exists")

#     # Assign HOD to department
#     db_update_one("departments", dept_id, { "hod_id": hod_id })

#     # Add HOD role to user
#     user = get_user_row(hod_id)
#     # roles = parse_roles_field(user["roles"])
#     roles = parse_roles_field(user.get("roles") or [])
#     if "hod" not in roles:
#         roles.append("hod")
#         # db_update_one("users", hod_id, { "roles": json.dumps(roles) })
#         db_update_one("users", hod_id, { "roles": roles })
#     return {"message": "HOD assigned"}

# @app.post("/api/departments/{dept_id}/add-class-teacher")
# @require_any_role("hod")
# def add_class_teacher(
#     dept_id: str,
#     full_name: str = Form(...),
#     email: str = Form(...),
#     section: str = Form(...),
#     current_user=Depends(get_current_user)
# ):

#     hod_map = db_find_one("department_hods", hod_id=current_user["id"], dept_id=dept_id)
#     if not hod_map:
#         raise HTTPException(403, "Not HOD of this department")

#     if get_user_row_by_email(email):
#         raise HTTPException(400, "User already exists")

#     user_id = None
#     try:
#         # 1. Create in Firebase Auth
#         fb_user = auth.create_user(
#             email=email,
#             display_name=full_name  # <--- FIX 1
#         )
#         user_id = fb_user.uid
#     except Exception as e:
#         raise HTTPException(500, f"Firebase Auth error: {e}")

#     # 2. Create in Firestore
#     db_insert_one("users", {
#         "email": email,
#         "full_name": full_name,
#         "roles": ["class_teacher"],  # <--- FIX 2
#         "org_id": current_user["org_id"],
#     }, doc_id=user_id)

#     # 3. Save mapping
#     db_insert_one("dept_class_teachers", {
#         "dept_id": dept_id,
#         "class_teacher_id": user_id,
#         "section": section
#     })

#     return {"message": "Class teacher added", "user_id": user_id, "section": section}
# @app.post("/api/departments/{dept_id}/sections")
# @require_any_role("hod")
# def create_section(dept_id: str, name: str = Form(...), current_user=Depends(get_current_user)):
#     hod_map = db_find_one("department_hods", hod_id=current_user["id"], dept_id=dept_id)
#     if not hod_map:
#         raise HTTPException(403, "Not HOD of this department")

#     section = {
#         # "id" auto-generated
#         "dept_id": dept_id,
#         "name": name,  # Example: "5A"
#         "class_teacher_id": None
#     }
#     new_section = db_insert_one("sections", section)
#     return new_section

# @app.post("/api/sections/{section_id}/assign-teacher")
# @require_any_role("hod")
# def assign_class_teacher(
#     section_id: str,
#     full_name: str = Form(...),
#     email: str = Form(...),
#     # password: str = Form(...), # REMOVED
#     current_user=Depends(get_current_user)
# ):
#     section = db.collection("sections").document(section_id).get()
#     if not section.exists:
#         raise HTTPException(404, "Section not found")

#     hod_map = db_find_one("department_hods", hod_id=current_user["id"], dept_id=section.to_dict()["dept_id"])
#     if not hod_map:
#         raise HTTPException(403, "Not HOD for this department")

#     if get_user_row_by_email(email):
#         raise HTTPException(400, "Teacher already exists")

#     user_id = None
#     try:
#         # 1. Create in Firebase Auth
#         fb_user = auth.create_user(
#             email=email,
#             full_name=full_name
#         )
#         user_id = fb_user.uid
#     except Exception as e:
#         raise HTTPException(500, f"Firebase Auth error: {e}")

#     # 2. Create in Firestore
#     db_insert_one("users", {
#         "email": email,
#         "full_name": full_name,
#         # "roles": json.dumps(["class_teacher"]),
#         "roles":roles,
#         "org_id": current_user["org_id"],
#         # "hashed_password": REMOVED
#     }, doc_id=user_id)

#     # 3. Assign to section
#     db_update_one("sections", section_id, {"class_teacher_id": user_id})

#     return {"message": "Teacher assigned to section", "user_id": user_id}

# @app.post("/api/orgs/{org_id}/departments/{dept_id}/assign-hod")
# @require_any_role("admin")
# def assign_hod(org_id: str, dept_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
#     if current_user.get("org_id") != org_id:
#         raise HTTPException(status_code=403, detail="Not your org")

#     user = get_user_row_by_email(payload.email)
#     user_id = None

#     if not user:
#         try:
#             # 1. Create in Firebase Auth
#             fb_user = auth.create_user(
#                 email=payload.email,
#                 display_name=payload.full_name  # <--- FIX 1
#             )
#             user_id = fb_user.uid
#         except Exception as e:
#             raise HTTPException(500, f"Firebase Auth error: {e}")
        
#         # 2. Create in Firestore
#         user = {
#             "email": payload.email,
#             "full_name": payload.full_name,
#             "roles": ["hod"],  # <--- FIX 2
#             "org_id": org_id,
#         }
#         db_insert_one("users", user, doc_id=user_id)
#         user['id'] = user_id # for consistency
#     else:
#         # 3. Update existing user
#         user_id = user["id"]
#         roles = parse_roles_field(user.get("roles"))
#         if "hod" not in roles:
#             roles.append("hod")
#         db_update_one("users", user["id"], {"roles": roles}) # <--- FIX 3

#     # 4. Store HOD–Department mapping
#     db_insert_one("department_hods", {
#         # "id" auto-generated
#         "org_id": org_id,
#         "dept_id": dept_id,
#         "hod_id": user_id
#     })

#     return {"message": "HOD assigned successfully", "user_id": user_id}

# @app.get("/api/departments/{dept_id}/classes")
# @require_any_role("hod")
# def get_dept_classes(dept_id: str, current_user=Depends(get_current_user)):
#     hod_map = db_find_one("department_hods", hod_id=current_user["id"], dept_id=dept_id)
#     if not hod_map:
#         raise HTTPException(status_code=403, detail="Not HOD of this department")

#     classes = db_find_many("classes", department_id=dept_id)
#     return classes

# @app.get("/api/departments/{dept_id}/class-teachers")
# @require_any_role("hod")
# def list_class_teachers(dept_id: str, current_user=Depends(get_current_user)):
#     hod_map = db_find_one("department_hods", hod_id=current_user["id"], dept_id=dept_id)
#     if not hod_map:
#         raise HTTPException(status_code=403, detail="Not your department")

#     entries = db_find_many("dept_class_teachers", dept_id=dept_id)

#     teachers = []
#     for e in entries:
#         u = get_user_row(e["class_teacher_id"])
#         if u:
#             teachers.append(u)
#     return teachers

# @app.post('/api/departments/create')
# @require_any_role('admin')
# def create_department(req: CreateDeptReq, current_user=Depends(get_current_user)):
#     new_dept = {
#         # "id" auto-generated
#         "org_id": req.org_id,
#         "name": req.name,
#         "hod_id": None
#     }
#     new_doc = db_insert_one('departments', new_dept)
#     return new_doc

# @app.get("/api/hod/department")
# @require_any_role("hod")
# def get_hod_department(current_user=Depends(get_current_user)):
#     hod_id = current_user["id"]
#     mapping = db_find_one("department_hods", hod_id=hod_id)
#     if not mapping:
#         raise HTTPException(404, "Department not assigned")
#     dept_id = mapping["dept_id"]
    
#     dept = db.collection("departments").document(dept_id).get()
#     if not dept.exists:
#         raise HTTPException(404, "Department missing in DB")
    
#     dept_data = dept.to_dict()
#     dept_data['id'] = dept.id
#     return dept_data

# def find_user_section(user_id: str):
#     memberships = db_find_many("class_memberships", user_id=user_id)
#     for m in memberships:
#         cls_doc = db.collection("classes").document(m["class_id"]).get()
#         if cls_doc.exists:
#             cls = cls_doc.to_dict()
#             if cls and cls.get("section"):
#                 return cls["section"]
#     return None

# @app.get("/api/user/{user_id}/section/students")
# def get_students_from_user_section(user_id: str):
#     section = find_user_section(user_id)
#     if not section:
#         raise HTTPException(404, detail="User has no section assigned")

#     classes = db_find_many("classes", section=section)
#     class_ids = [c["id"] for c in classes]

#     students = {}
#     for cid in class_ids:
#         members = db_find_many("class_memberships", class_id=cid, role="student")
#         for m in members:
#             u = get_user_row(m["user_id"])
#             if u:
#                 students[u["id"]] = {
#                     "id": u["id"],
#                     "name": u["full_name"],
#                     "email": u["email"]
#                 }
#     return list(students.values())

# @app.get("/api/user/{user_id}/section/notes")
# def get_notes_from_user_section(user_id: str):
#     section = find_user_section(user_id)
#     if not section:
#         raise HTTPException(404, detail="User has no section assigned")
#     classes = db_find_many("classes", section=section)
#     class_ids = [c["id"] for c in classes]
#     notes = []
#     for cid in class_ids:
#         notes += db_find_many("notes", class_id=cid)
#     return notes

# @app.get("/api/user/{user_id}/section/grades")
# def get_grades_from_user_section(user_id: str):
#     section = find_user_section(user_id)
#     if not section:
#         raise HTTPException(404, detail="User has no section assigned")
#     classes = db_find_many("classes", section=section)
#     class_ids = [c["id"] for c in classes]
#     grades = []
#     for cid in class_ids:
#         grades += db_find_many("final_marks", class_id=cid)
#     return grades


# @app.get("/api/user/{user_id}/grades")
# def get_user_grades(user_id: str):
#     section = find_user_section(user_id)
#     if not section:
#         raise HTTPException(404, detail="User has no section assigned")

#     classes = db_find_many("classes", section=section)
#     class_ids = [c["id"] for c in classes]

#     all_marks = []
#     for cid in class_ids:
#         all_marks += db_find_many("final_marks", class_id=cid, student_id=user_id)

#     grouped = {}
#     for m in all_marks:
#         subject = m["subject_name"]
#         unit = m["unit_name"]
#         marks = m["marks"]
#         if subject not in grouped:
#             grouped[subject] = []
#         grouped[subject].append({
#             "unit": unit,
#             "marks": marks,
#             "class_id": m["class_id"]
#         })

#     return {
#         "user_id": user_id,
#         "section": section,
#         "subjects": grouped
#     }


# # @app.post('/api/auth/login') # DELETED
# # def login(req: LoginReq):
# #     ...

# @app.get('/api/users/me')
# def get_me(current_user=Depends(get_current_user)):
#     # This works perfectly with the new get_current_user
#     return current_user

# # -------------------------
# # REFACTORED: ORGANIZATIONS
# # -------------------------
# @app.post('/api/orgs')
# @require_owner
# def create_org(req: CreateOrgReq, current_user=Depends(get_current_user)):
#     org_type = req.org_type or DEFAULT_ORG_TYPE
#     if org_type not in ('school','college','university'):
#         raise HTTPException(status_code=400, detail='org_type must be school|college|university')
    
#     new_org = {
#         # "id" auto-generated
#         "name": req.name,
#         "org_type": org_type
#     }
#     new_doc = db_insert_one('organizations', new_org)
#     return new_doc

# # In your main.py or wherever /api/orgs is
# @app.get("/api/orgs")
# def get_all_organizations(current_user=Depends(get_current_user)):
    
#     # --- THIS IS THE FIX ---
#     # Check if the user is the OWNER
#     if "owner" in current_user.get("roles", []):
#         # If they are the owner, they get to see ALL orgs
#         all_orgs = db_find_many("organizations") 
#         return all_orgs
#     # --- END OF FIX ---
    
#     # If not an owner, run the old logic for admins/teachers
#     user_org_id = current_user.get("org_id")
    
#     if not user_org_id:
#         # Not an owner and no org_id, so they see nothing
#         return []

#     # This is an admin/teacher, so only show their org
#     org = db_find_one("organizations", id=user_org_id)
#     return [org] if org else []# This just works

# @app.post('/api/orgs/{org_id}/admin/create')
# @require_owner
# def create_admin(org_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
#     org_doc = db.collection("organizations").document(org_id).get()
#     if not org_doc.exists:
#         raise HTTPException(status_code=404, detail='Organization not found')
        
#     if get_user_row_by_email(payload.email):
#         raise HTTPException(status_code=400, detail="User with this email already exists")

#     user_id = None
#     try:
#         # 1. Create in Firebase Auth
#         fb_user = auth.create_user(
#             email=payload.email,
#             display_name=payload.full_name
#         )
#         user_id = fb_user.uid
#     except Exception as e:
#         raise HTTPException(500, f"Firebase Auth error: {e}")

#     # 2. Create in Firestore
#     new_admin = {
#         'email': payload.email,
#         'full_name': payload.full_name,
#         'roles': ['admin'],
#         'org_id': org_id,
#     }
#     db_insert_one('users', new_admin, doc_id=user_id)
#     return {'message':'admin created', 'user_id': user_id}

# # -------------------------
# # REFACTORED: ADMIN actions
# # -------------------------
# @app.post('/api/orgs/{org_id}/teachers/create')
# @require_any_role('admin')
# def create_class_teacher(org_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
#     if current_user.get('org_id') != org_id:
#         raise HTTPException(status_code=403, detail='Not your org')
        
#     if get_user_row_by_email(payload.email):
#         raise HTTPException(status_code=400, detail="User with this email already exists")

#     user_id = None
#     try:
#         # 1. Create in Firebase Auth
#         fb_user = auth.create_user(
#             email=payload.email,
#             full_name=payload.full_name
#         )
#         user_id = fb_user.uid
#     except Exception as e:
#         raise HTTPException(500, f"Firebase Auth error: {e}")

#     # 2. Create in Firestore
#     new_teacher = {
#         'email': payload.email,
#         'full_name': payload.full_name,
#         'roles': json.dumps(['class_teacher']),
#         'org_id': org_id,
#     }
#     db_insert_one('users', new_teacher, doc_id=user_id)
#     return {'message':'class teacher created', 'user_id': user_id}

# @app.delete('/api/orgs/{org_id}/teachers/{teacher_id}')
# @require_any_role('admin')
# def delete_class_teacher(org_id: str, teacher_id: str, current_user=Depends(get_current_user)):
#     if current_user.get('org_id') != org_id:
#         raise HTTPException(status_code=403, detail='Not your org')
    
#     # 1. Check if user is in org
#     teacher = get_user_row(teacher_id)
#     if not teacher or teacher.get('org_id') != org_id:
#          raise HTTPException(status_code=404, detail='Teacher not found in this org')

#     try:
#         # 2. Delete from Firebase Auth
#         auth.delete_user(teacher_id)
#     except Exception as e:
#         raise HTTPException(500, f"Firebase Auth deletion error: {e}")
    
#     # 3. Delete from Firestore
#     db_delete_one('users', teacher_id)
#     # Note: You might want to clean up other references (classes, etc.)
        
#     return {'message': 'deleted teacher from Auth and Firestore'}

# # -------------------------
# # REFACTORED: DEPARTMENTS
# # -------------------------
# # This duplicate endpoint is in your code, keeping it
# @app.post('/api/departments/create') 
# @require_any_role('admin')
# def create_department(req: CreateDeptReq, current_user=Depends(get_current_user)):
#     if current_user.get('org_id') != req.org_id:
#         raise HTTPException(status_code=403, detail='Not your org')
    
#     new_dept = {
#         # "id" auto-generated
#         'org_id': req.org_id,
#         'name': req.name,
#         'hod_id': req.hod_id
#     }
#     new_doc = db_insert_one('departments', new_dept)
#     return new_doc

# @app.get('/api/orgs/{org_id}/departments')
# @require_any_role('admin','class_teacher','sub_teacher')
# def list_departments(org_id: str, current_user=Depends(get_current_user)):
#     return db_find_many('departments', org_id=org_id) # This just works

# # -------------------------
# # REFACTORED: TEACHER HIERARCHY
# # -------------------------
# @app.post('/api/teachers/add-sub')
# @require_any_role('class_teacher','admin')
# def add_sub_teacher(payload: AddUserReq, current_user=Depends(get_current_user)):
#     org_id = current_user.get('org_id')
    
#     if get_user_row_by_email(payload.email):
#         raise HTTPException(status_code=400, detail="User with this email already exists")

#     user_id = None
#     try:
#         # 1. Create in Firebase Auth
#         fb_user = auth.create_user(
#             email=payload.email,
#             full_name=payload.full_name
#         )
#         user_id = fb_user.uid
#     except Exception as e:
#         raise HTTPException(500, f"Firebase Auth error: {e}")

#     # 2. Create in Firestore
#     new_sub_teacher = {
#         'email': payload.email,
#         'full_name': payload.full_name,
#         'roles': json.dumps(['sub_teacher']),
#         'org_id': org_id,
#     }
#     db_insert_one('users', new_sub_teacher, doc_id=user_id)
    
#     # 3. Create mapping
#     db_insert_one('teacher_hierarchy', {
#         # "id" auto-generated
#         'org_id': org_id,
#         'class_teacher_id': current_user['id'],
#         'sub_teacher_id': user_id
#     })
#     return {'message':'sub teacher added', 'user_id': user_id}

# # -------------------------
# # REFACTORED: CLASSES
# # -------------------------

# @app.post('/api/classes')
# @require_any_role('sub_teacher', 'class_teacher')
# def create_class(req: CreateClassReq, current_user=Depends(get_current_user)):
#     # ... (code for generating class_code is fine) ...
#     code = ""
#     for _ in range(6):
#         code = secrets.token_urlsafe(4).upper()
#         if not db_find_one('classes', class_code=code):
#             break

#     # ... (code for finding ct_id is fine) ...
#     ct_id = None
#     if 'sub_teacher' in parse_roles_field(current_user.get('roles', [])):
#         h = db_find_one("teacher_hierarchy", sub_teacher_id=current_user["id"])
#         if not h:
#             raise HTTPException(status_code=400, detail="No linked class teacher found for this sub_teacher.")
#         ct_id = h["class_teacher_id"]
#     elif 'class_teacher' in parse_roles_field(current_user.get('roles', [])):
#         ct_id = current_user["id"]
#     else:
#         raise HTTPException(status_code=403, detail="Not allowed")

#     # ... (code for auto-detecting dept/section is fine) ...
#     mapping = db_find_one("dept_class_teachers", class_teacher_id=ct_id)
#     dept_id = mapping["dept_id"] if mapping else None
#     section = mapping["section"] if mapping else None

#     # Create new class
#     body = {
#         # "id" auto-generated
#         "org_id": req.org_id,
#         "title": req.title,
#         "description": req.description,
#         "created_by": current_user["id"],
#         "class_teacher_id": ct_id,
#         "class_code": code,
#         "department_id": dept_id,
#         "section": section
#     }
#     new_class = db_insert_one("classes", body)

#     # Add teacher membership
#     db_insert_one("class_memberships", {
#         # "id" auto-generated
#         "class_id": new_class["id"],
#         "user_id": current_user["id"],
#         "role": "teacher"
#     })

#     return new_class


# @app.get("/api/classes/{class_id}")
# def get_class_info(class_id: str):
#     cls_doc = db.collection("classes").document(class_id).get()
#     if not cls_doc.exists:
#         raise HTTPException(404, "Class not found")
#     cls = cls_doc.to_dict()
#     cls['id'] = cls_doc.id
#     return cls


# @app.delete('/api/classes/{class_id}')
# @require_any_role('sub_teacher','class_teacher','admin')
# def delete_class(class_id: str, current_user=Depends(get_current_user)):
#     c = db.collection("classes").document(class_id).get()
#     if not c.exists:
#         raise HTTPException(status_code=404, detail='Class not found')
    
#     c_data = c.to_dict()
#     allowed = False
#     if 'admin' in parse_roles_field(current_user.get('roles', [])) and current_user.get('org_id') == c_data.get('org_id'):
#         allowed = True
#     if c_data.get('created_by') == current_user['id']:
#         allowed = True
#     if c_data.get('class_teacher_id') == current_user['id']:
#         allowed = True
    
#     if not allowed:
#         raise HTTPException(status_code=403, detail='Not allowed to delete this class')
    
#     db_delete_one('classes', class_id)
#     # Note: You should also delete memberships, assignments, etc. (cascading delete)
#     return {'message':'deleted'}

# @app.get("/api/classes/{class_id}/students")
# @require_any_role("class_teacher", "sub_teacher", "admin","student")
# def get_class_students(class_id: str, current_user=Depends(get_current_user)):
#     m = db_find_one("class_memberships", class_id=class_id, user_id=current_user["id"])
#     if not m:
#         raise HTTPException(status_code=403, detail="Not part of this class")

#     members = db_find_many("class_memberships", class_id=class_id)
#     students = []
#     for mem in members:
#         if mem.get("role") == "student":
#             u = get_user_row(mem["user_id"])
#             if u:
#                 students.append({
#                     "id": u["id"],
#                     "full_name": u.get("full_name"),
#                     "email": u.get("email")
#                 })
#     return students

# @app.get("/api/classes")
# @require_any_role("sub_teacher", "class_teacher", "admin", "student")
# def list_classes(current_user=Depends(get_current_user)):
#     roles = parse_roles_field(current_user.get("roles", []))
#     org_id = current_user.get("org_id")

#     if "admin" in roles:
#         return db_find_many("classes", org_id=org_id) or []
#     if "class_teacher" in roles:
#         return db_find_many("classes", class_teacher_id=current_user["id"]) or []

#     # For students and sub-teachers, we must query memberships first
#     # This logic is correct and will use the new Firestore helpers
#     if "sub_teacher" in roles:
#         memberships = db_find_many("class_memberships", user_id=current_user["id"], role="teacher")
#     elif "student" in roles:
#         memberships = db_find_many("class_memberships", user_id=current_user["id"], role="student")
#     else:
#         raise HTTPException(status_code=403, detail="Not allowed")

#     class_ids = [m["class_id"] for m in memberships]
#     if not class_ids:
#         return []
        
#     # Firestore 'in' query is limited to 10 items.
#     # For a real app, you'd fetch docs one-by-one or restructure data.
#     # For this project, we'll fetch one-by-one.
#     all_classes = []
#     for cid in class_ids:
#         c_doc = db.collection("classes").document(cid).get()
#         if c_doc.exists:
#             c_data = c_doc.to_dict()
#             c_data['id'] = c_doc.id
#             all_classes.append(c_data)
#     return all_classes

# @app.post("/api/teachers/add-student")
# @require_any_role("class_teacher", "admin", "sub_teacher")
# def add_student(payload: AddStudentReq, current_user=Depends(get_current_user)):
#     """
#     Create or update a student in Firebase/Firestore and add them to the class.
#     """
#     class_id = payload.class_id
#     email = payload.email.strip().lower()
#     full_name = (payload.full_name or "").strip()
#     # password = REMOVED

#     cls_doc = db.collection("classes").document(class_id).get()
#     if not cls_doc.exists:
#         raise HTTPException(status_code=404, detail="Class not found")
#     cls = cls_doc.to_dict()

#     # ... (Permission checks are fine) ...
#     roles = parse_roles_field(current_user.get("roles") or [])
#     allowed = False
#     if "admin" in roles and current_user.get("org_id") == cls.get("org_id"):
#         allowed = True
#     if "class_teacher" in roles and cls.get("class_teacher_id") == current_user["id"]:
#         allowed = True
#     if "sub_teacher" in roles:
#         cm = db_find_one("class_memberships", class_id=class_id, user_id=current_user["id"])
#         if cm and cm.get("role") == "teacher":
#             allowed = True
#     if not allowed:
#         raise HTTPException(status_code=403, detail="Not allowed to add students to this class")

#     if not email:
#         raise HTTPException(status_code=400, detail="Email required")

#     existing = get_user_row_by_email(email)
#     user_id = None

#     if existing:
#         user_id = existing["id"]
#         # ensure 'student' role present
#         roles_list = parse_roles_field(existing.get("roles") or [])
#         if "student" not in roles_list:
#             roles_list.append("student")
#             db_update_one("users", user_id, {"roles": json.dumps(roles_list)})
#         # ensure org matches class org
#         if existing.get("org_id") != cls.get("org_id"):
#             db_update_one("users", user_id, {"org_id": cls.get("org_id")})
#     else:
#         try:
#             # 1. Create in Firebase Auth
#             fb_user = auth.create_user(
#                 email=email,
#                 full_name=full_name
#             )
#             user_id = fb_user.uid
#         except Exception as e:
#             raise HTTPException(500, f"Firebase Auth error: {e}")
        
#         # 2. Create in Firestore
#         # 2. Create user document in Firestore
#         new_user = {
#     "email": payload.email,
#     "full_name": payload.full_name,
#     "roles": roles, # <--- GOOD
#     "org_id": org_id
#   }
#         db_insert_one("users", new_user, doc_id=user_id)

#     # create membership if not exists
#     existing_mem = db_find_one("class_memberships", class_id=class_id, user_id=user_id)
#     if not existing_mem:
#         db_insert_one("class_memberships", {
#             # "id" auto-generated
#             "class_id": class_id,
#             "user_id": user_id,
#             "role": "student"
#         })

#     return {"message": "student added/updated", "user_id": user_id}

# # -------------------------
# # REFACTORED: ASSIGNMENTS
# # -------------------------
# @app.post('/api/assignments')
# @require_any_role('sub_teacher')
# def create_assignment(req: CreateAssignmentReq, current_user=Depends(get_current_user)):
#     cm = db_find_one('class_memberships', class_id=req.class_id, user_id=current_user['id'])
#     if not cm or cm.get('role') != 'teacher':
#         raise HTTPException(status_code=403, detail='Only the subject teacher can create assignments for this class')
#     if req.assignment_type not in ('file','text','mixed'):
#         raise HTTPException(status_code=400, detail='Invalid assignment_type')
        
#     body = {
#         # "id" auto-generated
#         'class_id': req.class_id, 
#         'created_by': current_user['id'], 
#         'title': req.title, 
#         'description': req.description, 
#         'due_at': req.due_at, 
#         'assignment_type': req.assignment_type,
#         'file_url': None, # New field
#         'public_id': None # New field
#     }
#     new_assignment = db_insert_one('assignments', body)
#     return new_assignment

# @app.post('/api/assignments/{assignment_id}/upload-file')
# @require_any_role('sub_teacher')
# def upload_assignment_file(assignment_id: str, file: UploadFile = File(...), current_user=Depends(get_current_user)):
#     a = db.collection('assignments').document(assignment_id).get()
#     if not a.exists:
#         raise HTTPException(status_code=404, detail='Assignment not found')
        
#     cm = db_find_one('class_memberships', class_id=a.to_dict()['class_id'], user_id=current_user['id'])
#     if not cm or cm.get('role') != 'teacher':
#         raise HTTPException(status_code=403, detail='Only subject teacher can upload file for this assignment')

#     # Upload to cloudinary
#     try:
#         upload_result = cloudinary.uploader.upload(
#             file.file,
#             folder=f"assignments/{assignment_id}", 
#             resource_type="auto"
#         )
#     except Exception as e:
#         raise HTTPException(500, f"Cloudinary upload failed: {e}")
    
#     # Store URL in Firestore
#     db_update_one('assignments', assignment_id, {
#         'file_url': upload_result["secure_url"],
#         'public_id': upload_result["public_id"]
#     })
    
#     return {'message':'file uploaded', 'file_url': upload_result["secure_url"]}

# @app.get('/api/classes/{class_id}/assignments')
# def list_assignments(class_id: str, current_user=Depends(get_current_user)):
#     m = db_find_one('class_memberships', class_id=class_id, user_id=current_user['id'])
#     if not m:
#         raise HTTPException(status_code=403, detail='Not a member of class')
    
#     return db_find_many('assignments', class_id=class_id)

# # -------------------------
# # REFACTORED: SUBMISSIONS
# # -------------------------
# @app.post('/api/submissions')
# @require_any_role('student')
# def submit_assignment(
#     assignment_id: str = Form(...),
#     text_content: Optional[str] = Form(None),
#     file: Optional[UploadFile] = File(None),
#     current_user=Depends(get_current_user)
# ):
#     assignment = db.collection('assignments').document(assignment_id).get()
#     if not assignment.exists:
#         raise HTTPException(status_code=404, detail='Assignment not found')

#     class_id = assignment.to_dict()['class_id']
#     cm = db_find_one('class_memberships', class_id=class_id, user_id=current_user["id"])
#     if not cm:
#         raise HTTPException(status_code=403, detail="Not in class")

#     file_url = None
#     public_id = None

#     if file:
#         try:
#             upload_result = cloudinary.uploader.upload(
#                 file.file,
#                 folder=f"submissions/{assignment_id}/{current_user['id']}", 
#                 resource_type="auto"
#             )
#             file_url = upload_result["secure_url"]
#             public_id = upload_result["public_id"]
#         except Exception as e:
#             raise HTTPException(500, f"Cloudinary upload failed: {e}")

#     # Check if exists
#     existing = db_find_one("submissions", assignment_id=assignment_id, student_id=current_user["id"])
    
#     update_data = {
#         "text_content": text_content,
#         "submitted_at": datetime.utcnow()
#     }
#     if file_url:
#         update_data["file_url"] = file_url
#         update_data["public_id"] = public_id

#     if existing:
#         db_update_one("submissions", existing["id"], update_data)
#         return {"message": "updated submission"}

#     new_sub = {
#         # "id" auto-generated
#         "assignment_id": assignment_id,
#         "student_id": current_user["id"],
#         "text_content": text_content,
#         "file_url": file_url,
#         "public_id": public_id,
#         "submitted_at": datetime.utcnow()
#     }

#     new_doc = db_insert_one("submissions", new_sub)
#     return {"message": "submitted", "id": new_doc["id"]}


# @app.get('/api/assignments/{assignment_id}/submissions')
# @require_any_role('sub_teacher','class_teacher')
# def get_submissions(assignment_id: str, current_user=Depends(get_current_user)):
#     a = db.collection('assignments').document(assignment_id).get()
#     if not a.exists:
#         raise HTTPException(status_code=404, detail='Assignment not found')
    
#     a_data = a.to_dict()
#     class_id = a_data['class_id']
#     cm = db_find_one('class_memberships', class_id=class_id, user_id=current_user['id'])
#     is_teacher = cm and cm.get('role') == 'teacher'
    
#     cls_doc = db.collection('classes').document(class_id).get()
#     is_supervisor = cls_doc.exists and cls_doc.to_dict().get('class_teacher_id') == current_user['id']
    
#     if not (is_teacher or is_supervisor):
#         raise HTTPException(status_code=403, detail='Not allowed')
        
#     return db_find_many('submissions', assignment_id=assignment_id)

# @app.post('/api/submissions/{submission_id}/grade')
# @require_any_role('sub_teacher')
# def grade_submission(submission_id: str, grade: float = Body(...), current_user=Depends(get_current_user)):
#     s = db.collection('submissions').document(submission_id).get()
#     if not s.exists:
#         raise HTTPException(status_code=404, detail='Submission not found')
        
#     assignment = db.collection('assignments').document(s.to_dict()['assignment_id']).get()
#     class_id = assignment.to_dict()['class_id']
    
#     cm = db_find_one('class_memberships', class_id=class_id, user_id=current_user['id'])
#     if not (cm and cm.get('role') == 'teacher'):
#         raise HTTPException(status_code=403, detail='Only the subject teacher can grade submissions')
        
#     db_update_one('submissions', submission_id, {'grade': grade, 'graded_by': current_user['id']})
#     return {'message':'graded'}

# # -------------------------
# # REFACTORED: NOTES (Already uses Cloudinary)
# # -------------------------
# # @app.post('/api/notes') # DELETED - This endpoint was flawed
# # def upload_note(req: NoteCreateReq, ...):
# #     ...
    
# @app.get('/api/classes/{class_id}/notes')
# def list_notes(class_id: str, current_user=Depends(get_current_user)):
#     cm = db_find_one('class_memberships', class_id=class_id, user_id=current_user['id'])
#     if not cm:
#         raise HTTPException(status_code=403, detail='Not a member')
    
#     return db_find_many('notes', class_id=class_id)

# @app.post("/api/notes/upload")
# @require_any_role("class_teacher", "sub_teacher")
# def upload_note(
#     class_id: str = Form(...),
#     title: str = Form(...),
#     file: UploadFile = File(...),
#     current_user=Depends(get_current_user)
# ):
#     # This endpoint is already perfect and uses Cloudinary. No changes needed.
#     cm = db_find_one("class_memberships", class_id=class_id, user_id=current_user["id"])
#     if not cm or cm.get("role") != "teacher":
#         raise HTTPException(status_code=403, detail="Not allowed")

#     try:
#         upload_result = cloudinary.uploader.upload(
#             file.file,
#             folder=f"class_notes/{class_id}", 
#             resource_type="auto"
#         )
#     except Exception as e:
#         raise HTTPException(500, f"Cloudinary upload failed: {e}")

#     note = {
#         # "id" auto-generated
#         "class_id": class_id,
#         "uploaded_by": current_user["id"],
#         "title": title,
#         "file_url": upload_result["secure_url"],
#         "public_id": upload_result["public_id"],
#         "uploaded_at": str(datetime.utcnow())
#     }

#     new_note = db_insert_one("notes", note)
#     return {"message": "Uploaded", "note": new_note}

# # -------------------------
# # REFACTORED: FINAL MARKS
# # -------------------------
# @app.post('/api/finalmarks')
# @require_any_role('sub_teacher')
# def upload_final_marks(req: FinalMarkReq, current_user=Depends(get_current_user)):
#     stu = get_user_row(req.student_id)
#     if not stu:
#         raise HTTPException(status_code=404, detail='Student not found')
        
#     body = req.dict()
#     # "id" auto-generated
#     body['uploaded_by'] = current_user['id']
    
#     db_insert_one('final_marks', body)
#     return {'message':'uploaded'}


# @app.get("/api/classes/{class_id}/grades")
# @require_any_role("admin", "class_teacher", "sub_teacher", "student")
# def get_class_grades(class_id: str, current_user=Depends(get_current_user)):
#     # This logic is fine and will use the new DB helpers
#     member = db_find_one("class_memberships", class_id=class_id, user_id=current_user["id"])
#     if not member:
#         raise HTTPException(status_code=403, detail="Not part of this class")

#     roles = parse_roles_field(current_user.get("roles", []))
#     org_id = current_user.get("org_id")

#     if "admin" in roles:
#         return db_find_many("final_marks", class_id=class_id, org_id=org_id) or []

#     if "class_teacher" in roles:
#         cls_doc = db.collection("classes").document(class_id).get()
#         if cls_doc.exists and cls_doc.to_dict().get("class_teacher_id") == current_user["id"]:
#             return db_find_many("final_marks", class_id=class_id) or []
#         raise HTTPException(status_code=403, detail="Not your class")

#     if "sub_teacher" in roles:
#         return db_find_many("final_marks", class_id=class_id) or []

#     if "student" in roles:
#         return db_find_many("final_marks", class_id=class_id, student_id=current_user["id"]) or []

#     raise HTTPException(status_code=403, detail="Not allowed")


# @app.get('/api/orgs/{org_id}/grades')
# @require_any_role('class_teacher','admin','sub_teacher')
# def view_all_grades(org_id: str, current_user=Depends(get_current_user)):
#     # This logic is complex but should work with the new DB helpers
#     roles = parse_roles_field(current_user.get('roles') or [])
    
#     if 'class_teacher' in roles:
#         classes = db_find_many('classes', class_teacher_id=current_user['id'], org_id=org_id)
#         class_ids = [c['id'] for c in classes]
#         if not class_ids: return []
#         # Firestore 'in' query limit is 10. This is a potential bug.
#         # A better query would be needed for > 10 classes.
#         # For now, we assume < 10 classes per teacher
#         return db.collection('final_marks').where('class_id', 'in', class_ids).stream()
        
#     if 'admin' in roles and current_user.get('org_id') == org_id:
#         return db_find_many('final_marks', org_id=org_id)
        
#     if 'sub_teacher' in roles:
#         cm = db_find_many('class_memberships', user_id=current_user['id'], role='teacher')
#         class_ids = [c['class_id'] for c in cm]
#         if not class_ids: return []
#         # Same 'in' query limitation
#         return db.collection('final_marks').where('class_id', 'in', class_ids).stream()
        
#     raise HTTPException(status_code=403, detail='Not allowed')

# # -------------------------
# # REFACTORED: MESSAGES
# # -------------------------
# @app.post('/api/messages')
# @require_any_role('student','sub_teacher','class_teacher','admin')
# def send_message(req: MessageReq, current_user=Depends(get_current_user)):
#     # This logic is fine and will use the new DB helpers
#     cm = db_find_one('class_memberships', class_id=req.class_id, user_id=current_user['id'])
#     if not cm:
#         raise HTTPException(status_code=403, detail='Not a member of this class')
        
#     if not req.is_public:
#         if not req.receiver_id:
#             raise HTTPException(status_code=400, detail='receiver_id required for private message')
#         if 'student' in parse_roles_field(current_user.get('roles', [])):
#             check = db_find_one('class_memberships', class_id=req.class_id, user_id=req.receiver_id)
#             if not check or check.get('role') != 'teacher':
#                 raise HTTPException(status_code=403, detail='Receiver must be a teacher for this class')
                
#     db_insert_one('messages', {
#         # "id" auto-generated
#         'class_id': req.class_id,
#         'sender_id': current_user['id'],
#         'receiver_id': req.receiver_id if not req.is_public else None,
#         'content': req.content,
#         'is_public': req.is_public,
#         'sent_at': datetime.utcnow()
#     })
#     return {'message':'sent', 'type': 'public' if req.is_public else 'private'}

# @app.get('/api/classes/{class_id}/messages')
# @require_any_role('student','sub_teacher','class_teacher','admin')
# def get_messages(class_id: str, current_user=Depends(get_current_user)):
#     cm = db_find_one('class_memberships', class_id=class_id, user_id=current_user['id'])
#     if not cm:
#         raise HTTPException(status_code=403, detail='Not a member')
    
#     user_id = current_user['id']
#     msgs = db_find_many('messages', class_id=class_id)
    
#     visible = [m for m in msgs if m.get('is_public') or m.get('sender_id')==user_id or m.get('receiver_id')==user_id]
#     return visible

# # -------------------------
# # REFACTORED: BULK IMPORT
# # -------------------------
# @app.post('/api/admin/preview-import')
# @require_any_role('admin')
# def preview_import(file: UploadFile = File(...), current_user=Depends(get_current_user)):
#     # This endpoint doesn't touch the DB, so it's fine.
#     content = file.file.read()
#     try:
#         if file.filename.lower().endswith(('.xls','.xlsx')):
#             df = pd.read_excel(BytesIO(content))
#         else:
#             df = pd.read_csv(BytesIO(content))
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f'Could not parse file: {e}')
#     preview = df.head(10).fillna('').to_dict(orient='records')
#     columns = list(df.columns)
#     return {'columns': columns, 'preview': preview}

# @app.post("/api/teachers/import-students")
# @require_any_role("class_teacher")
# def import_students_for_class(
#     file: UploadFile = File(...),
#     class_id: str = Query(..., description="Class ID to which students will be added"),
#     current_user=Depends(get_current_user)
# ):
#     """
#     Import students from Excel/CSV.
#     Creates them in Firebase Auth and Firestore.
#     Format: name, email (password column is ignored)
#     """
#     org_id = current_user.get("org_id")
#     if not org_id:
#         raise HTTPException(status_code=400, detail="User not linked to any organization")

#     cls_doc = db.collection("classes").document(class_id).get()
#     if not cls_doc.exists:
#         raise HTTPException(status_code=404, detail="Class not found")
#     if cls_doc.to_dict().get("class_teacher_id") != current_user["id"]:
#         raise HTTPException(status_code=403, detail="Not allowed to import for this class")

#     content = file.file.read()
#     try:
#         if file.filename.lower().endswith((".xls", ".xlsx")):
#             df = pd.read_excel(BytesIO(content))
#         else:
#             df = pd.read_csv(BytesIO(content))
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Could not parse file: {e}")

#     required_columns = {"name", "email"}
#     df_cols_lower = set(df.columns.str.lower())
#     if not required_columns.issubset(df_cols_lower):
#         missing = required_columns - df_cols_lower
#         raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing)}")

#     created = {"new_students": 0, "existing_students": 0, "memberships_added": 0, "errors": []}

#     for _, row in df.iterrows():
#         try:
#             name = str(row.get("name") or row.get("Name") or "").strip()
#             email = str(row.get("email") or row.get("Email") or "").strip().lower()
#             # password = str(row.get("password") or row.get("Password") or "").strip() # IGNORED

#             if not email:
#                 continue

#             existing = get_user_row_by_email(email)
#             user_id = None
#             if existing:
#                 user_id = existing["id"]
#                 roles = parse_roles_field(existing.get("roles"))
#                 if "student" not in roles:
#                     roles.append("student")
#                     db_update_one("users", user_id, {"roles": json.dumps(roles)})
#                 created["existing_students"] += 1
#             else:
#                 try:
#                     fb_user = auth.create_user(email=email, full_name=name)
#                     user_id = fb_user.uid
#                 except Exception as e:
#                     created["errors"].append(f"{email}: Firebase Auth error: {e}")
#                     continue
                
#                 new_student = {
#                     "email": email,
#                     "full_name": name,
#                     "roles": json.dumps(["student"]),
#                     "org_id": org_id,
#                 }
#                 db_insert_one("users", new_student, doc_id=user_id)
#                 created["new_students"] += 1

#             # Add class membership
#             if not db_find_one("class_memberships", class_id=class_id, user_id=user_id):
#                 db_insert_one("class_memberships", {
#                     "class_id": class_id,
#                     "user_id": user_id,
#                     "role": "student",
#                 })
#                 created["memberships_added"] += 1
#         except Exception as e:
#             created["errors"].append(f"{email}: {e}")
#             continue

#     return {"message": "Import completed", "summary": created}

# @app.post('/api/admin/import-file')
# @require_any_role('admin')
# def import_file(
#     file: UploadFile = File(...),
#     mapping_req: str = Form(...),
#     current_user=Depends(get_current_user)
# ):
#     # This is a very complex function. I have adapted it to the new auth/db.
#     try:
#         mapping_data = json.loads(mapping_req)
#     except:
#         raise HTTPException(400, "mapping_req must be JSON")

#     mapping = mapping_data.get("mapping", {})
#     create_departments = mapping_data.get("create_departments", True)
#     org_id = current_user.get('org_id')
#     if not org_id:
#         raise HTTPException(400, "Admin has no org_id assigned")

#     content = file.file.read()
#     try:
#         if file.filename.lower().endswith(('.xls','.xlsx')):
#             df = pd.read_excel(BytesIO(content))
#         else:
#             df = pd.read_csv(BytesIO(content))
#     except Exception as e:
#         raise HTTPException(400, f"Could not parse file: {e}")

#     created = {
#         "users": 0, "classes": 0, "departments": 0,
#         "memberships": 0, "skipped": 0, "errors": []
#     }

#     # Batch writing for efficiency
#     batch = db.batch()
#     all_new_user_mappings = {} # email -> uid
    
#     # We can't cache locally anymore easily, so we query per row.
#     # This will be SLOW but correct.
#     for idx, row in df.iterrows():
#         try:
#             def get_col(key):
#                 col = mapping.get(key) or key
#                 if col in row.index:
#                     return row.get(col)
#                 return None

#             name = str(get_col('name') or '').strip()
#             email = str(get_col('email') or '').strip().lower()
#             role = str(get_col('role') or 'student').strip().lower()
#             dept_name = str(get_col('department') or '').strip() or None
#             class_title = str(get_col('class') or '').strip() or None
#             section = str(get_col('section') or '').strip() or None
#             # password = IGNORED
            
#             if not email:
#                 created['skipped'] += 1
#                 continue
                
#             existing = get_user_row_by_email(email)
#             user_id = None
#             if existing:
#                 user_id = existing['id']
#                 roles = parse_roles_field(existing.get('roles'))
#                 if role and role not in roles:
#                     roles.append(role)
#                     batch.update(db.collection('users').document(user_id), {
#                         'full_name': name, 
#                         'roles': json.dumps(roles), 
#                         'org_id': org_id
#                     })
#             else:
#                 if email in all_new_user_mappings:
#                     user_id = all_new_user_mappings[email]
#                 else:
#                     try:
#                         fb_user = auth.create_user(email=email, full_name=name)
#                         user_id = fb_user.uid
#                         all_new_user_mappings[email] = user_id
#                     except Exception as e:
#                         raise Exception(f"Firebase Auth create error: {e}")
                    
#                     roles_list = [role] if role else []
#                     user_doc_ref = db.collection('users').document(user_id)
#                     batch.set(user_doc_ref, {
#                         'email': email, 'full_name': name,
#                         'roles': json.dumps(roles_list), 'org_id': org_id
#                     })
#                     created['users'] += 1
            
#             # Department
#             dept_id = None
#             if dept_name:
#                 dept = db_find_one('departments', name=dept_name, org_id=org_id)
#                 if not dept:
#                     if create_departments:
#                         dept_doc_ref = db.collection('departments').document()
#                         dept_id = dept_doc_ref.id
#                         batch.set(dept_doc_ref, {'org_id': org_id, 'name': dept_name})
#                         created['departments'] += 1
#                 else:
#                     dept_id = dept['id']
            
#             # Class
#             class_id = None
#             if class_title:
#                 cls = db_find_one('classes', title=class_title, org_id=org_id, department_id=dept_id)
#                 if not cls:
#                     class_doc_ref = db.collection('classes').document()
#                     class_id = class_doc_ref.id
#                     code = secrets.token_urlsafe(4).upper()
#                     batch.set(class_doc_ref, {
#                         'org_id': org_id, 'title': class_title,
#                         'description': f"Section {section or 'General'}",
#                         'department_id': dept_id,
#                         'class_teacher_id': user_id if role=='class_teacher' else None,
#                         'class_code': code
#                     })
#                     created['classes'] += 1
#                 else:
#                     class_id = cls['id']
            
#             # Membership
#             if class_id and role in ('student','sub_teacher','class_teacher'):
#                 mem_role = 'teacher' if role in ('sub_teacher','class_teacher') else 'student'
#                 if not db_find_one('class_memberships', class_id=class_id, user_id=user_id):
#                     mem_doc_ref = db.collection('class_memberships').document()
#                     batch.set(mem_doc_ref, {
#                         'class_id': class_id, 'user_id': user_id, 'role': mem_role
#                     })
#                     created['memberships'] += 1
#         except Exception as e:
#             created['errors'].append({'row': idx, 'error': str(e)})
#             continue
            
#     # --- Commit all changes at the end ---
#     try:
#         batch.commit()
#     except Exception as e:
#         raise HTTPException(500, f"Firestore batch commit error: {e}")
    
#     return created

# # -------------------------
# # HEALTH (Unchanged)
# # -------------------------
# @app.get('/')
# def root():
#     return {'message': 'API up and running with Firestore & Firebase Auth'}

# # End of file

"""
Complete single-file FastAPI backend for Classroom app (FULL CLOUD).
Features:
- Replaces local JSON DB with Google Firestore.
- Replaces self-hosted JWT with Firebase Auth (no passwords).
- Replaces local file storage with Cloudinary for all uploads.
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
from datetime import datetime
from functools import wraps
from io import BytesIO
import pandas as pd
from pathlib import Path

# --- New Imports ---
import firebase_admin
from firebase_admin import credentials, auth, firestore
import cloudinary
import cloudinary.uploader

# -------------------------
# Load env & Setup
# -------------------------
load_dotenv()
OWNER_EMAIL = os.getenv("OWNER_EMAIL")
DEFAULT_ORG_TYPE = os.getenv("DEFAULT_ORG_TYPE", "school")

if not OWNER_EMAIL:
    raise RuntimeError("Set OWNER_EMAIL in environment")

# --- Firebase Admin SDK Setup ---
# 1. Download your serviceAccountKey.json from Firebase
# 2. Update the path below
try:
    cred = credentials.Certificate("whiteai-ce125-firebase-adminsdk-fbsvc-5e0c161eeb.json") 
    firebase_admin.initialize_app(cred)
except Exception as e:
    raise RuntimeError(f"Failed to initialize Firebase: {e}\nDid you set the path to your serviceAccountKey.json?")

db = firestore.client() # This is our new database client

# --- Cloudinary Setup ---
cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_SECRET_KEY')
)
if not os.getenv('CLOUD_NAME'):
    print("WARNING: Cloudinary environment variables not set. File uploads will fail.")


# -------------------------
# Pydantic models (Passwords REMOVED)
# -------------------------
# class LoginReq(BaseModel): # DELETED
#     email: EmailStr
#     password: str

class CreateOrgReq(BaseModel):
    name: str
    org_type: Optional[str] = None  # school / college / university

class AddUserReq(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    roles: Optional[List[str]] = None
    # password: str # REMOVED

class AddStudentReq(BaseModel):
    class_id: str
    email: EmailStr
    full_name: Optional[str] = None
    # password: Optional[str] = None # REMOVED

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
    file_path: str # Note: This model is now unused, replaced by /api/notes/upload

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
# NEW: Firestore DB Helpers
# -------------------------
def db_find_one(table_name: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Finds the first item in a collection matching all kwargs."""
    try:
        query = db.collection(table_name)
        for key, value in kwargs.items():
            query = query.where(key, "==", value)
        
        docs = query.limit(1).stream()
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id  # Add the doc ID to the dict
            return data
        return None
    except Exception as e:
        print(f"Error in db_find_one({table_name}, {kwargs}): {e}")
        return None

def db_find_many(table_name: str, **kwargs) -> List[Dict[str, Any]]:
    """Finds all items in a collection matching all kwargs."""
    try:
        query = db.collection(table_name)
        for key, value in kwargs.items():
            query = query.where(key, "==", value)
        
        results = []
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            results.append(data)
        return results
    except Exception as e:
        print(f"Error in db_find_many({table_name}, {kwargs}): {e}")
        return []

def db_insert_one(table_name: str, item: Dict[str, Any], doc_id: Optional[str] = None) -> Dict[str, Any]:
    """Inserts a new item into a collection. Uses doc_id if provided."""
    try:
        if 'id' in item:
            # Don't store 'id' field *inside* the Firestore document
            internal_id = item.pop('id')
            if not doc_id:
                doc_id = internal_id
        
        if doc_id:
            doc_ref = db.collection(table_name).document(doc_id)
        else:
            doc_ref = db.collection(table_name).document()  # Auto-generate ID
        
        doc_ref.set(item)
        item['id'] = doc_ref.id  # Return the full dict with ID
        return item
    except Exception as e:
        print(f"Error in db_insert_one({table_name}): {e}")
        raise HTTPException(status_code=500, detail=f"Firestore insert error: {e}")


def db_update_one(table_name: str, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Finds an item by ID and applies updates."""
    try:
        doc_ref = db.collection(table_name).document(item_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        
        doc_ref.update(updates)
        updated_data = doc_ref.get().to_dict()
        updated_data['id'] = item_id
        return updated_data
    except Exception as e:
        print(f"Error in db_update_one({table_name}, {item_id}): {e}")
        return None

def db_delete_one(table_name: str, item_id: str) -> bool:
    """Deletes an item by its ID."""
    try:
        doc_ref = db.collection(table_name).document(item_id)
        if not doc_ref.get().exists:
            return False
        doc_ref.delete()
        return True
    except Exception as e:
        print(f"Error in db_delete_one({table_name}, {item_id}): {e}")
        return False

# -------------------------
# DELETED: Password & JWT Helpers
# -------------------------
# def hash_password(...) -> DELETED
# def verify_password(...) -> DELETED
# def create_access_token(...) -> DELETED

# -------------------------
# REFACTORED: Core Helpers
# -------------------------
def _data(resp):
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
    """Gets a user document from Firestore by its ID (Firebase UID)."""
    try:
        doc = db.collection('users').document(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    except Exception as e:
        print(f"Error in get_user_row({user_id}): {e}")
        return None


def get_user_row_by_email(email: str):
    if not email:
        return None
    return db_find_one('users', email=email) # Uses new Firestore helper

def org_has_departments(org_id: str) -> bool:
    org = db.collection('organizations').document(org_id).get()
    if not org.exists:
        return False
    return org.to_dict().get('org_type') in ('college', 'university')

# -------------------------
# REFACTORED: Auth dependency + guards
# -------------------------
def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Validates Firebase ID Token and returns user doc from Firestore.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail='Missing Authorization header')
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Invalid Authorization header')
    
    token = authorization.split(' ', 1)[1]
    
    try:
        # 1. Verify the token with Firebase
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"] # This is the Firebase UID
    
    except Exception as e:
        # Token is invalid, expired, etc.
        raise HTTPException(status_code=401, detail=f'Invalid Firebase token: {e}')
    
    # 2. Get the user from *our* Firestore 'users' collection
    app_user = get_user_row(user_id)
    
    if not app_user:
        # This means they are authenticated with Firebase, but not in our app DB
        raise HTTPException(status_code=403, detail='User not registered in app DB')
    
    # 3. Return the user document
    return app_user

# --- require_any_role and require_owner are UNCHANGED (they use get_current_user) ---
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
app = FastAPI(title="Classroom Backend (Firestore, Firebase Auth)")

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
        # "id" will be auto-generated by Firestore
        "user_id": user_id,
        "role": role,
        "org_id": org_id,
        "dept_id": dept_id,
        "class_id": class_id
    })

    # Update "roles" field INSIDE user table
    user = get_user_row(user_id) # Uses new helper
    if user:
        roles = parse_roles_field(user.get("roles"))
        if role not in roles:
            roles.append(role)
            # --- FIX 1: Removed json.dumps ---
            db_update_one("users", user_id, { "roles": roles })

    
@app.get("/api/users/roles/{user_id}")
def get_user_roles(user_id: str):
    """Return all roles of a user as a clean list."""
    
    user = get_user_row(user_id)
    if not user:
       raise HTTPException(status_code=404, detail="User not found")

    roles = parse_roles_field(user.get("roles"))
    return { "roles": roles }


@app.post("/api/users/create")
@require_any_role("admin", "class_teacher", "sub_teacher")
def create_user(payload: AddUserReq, current_user=Depends(get_current_user)):
    """
    Create a new user in Firebase Auth and Firestore DB.
    NO password needed.
    """
    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="You must belong to an organization")
    
    if get_user_row_by_email(payload.email):
        raise HTTPException(status_code=400, detail="User with this email already exists")

    roles = payload.roles or ["student"]
    user_id = None
    
    try:
        # 1. Create user in Firebase Auth
        # --- FIX 2: Changed full_name to display_name ---
        fb_user = auth.create_user(
            email=payload.email,
            display_name=payload.full_name,
            email_verified=True
        )
        user_id = fb_user.uid # Get the new Firebase UID
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firebase Auth error: {e}")

    # 2. Create user document in Firestore
    new_user = {
        "email": payload.email,
        "full_name": payload.full_name,
        "roles": roles, # --- FIX 1: Removed json.dumps ---
        "org_id": org_id,
        # "hashed_password": REMOVED
    }
    
    # Use the Firebase UID as the document ID in Firestore
    db_insert_one("users", new_user, doc_id=user_id)

    return {
        "message": "User created successfully in Firebase Auth and Firestore",
        "email": payload.email,
        "user_id": user_id,
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

# --- All your new endpoints are here ---

from pydantic import BaseModel

# --- Pydantic model for the new form ---
# class AddStudentReq(BaseModel): # Already defined above
#     full_name: str
#     email: str

# -----------------------------------------------------------------
# NEW ENDPOINT: Add a student (THIS IS THE ONE YOU'RE MISSING)
# -----------------------------------------------------------------
@app.post("/api/class-teacher/add-student")
@require_any_role("class_teacher") # Only class teachers
def add_student_to_section(
    payload: AddStudentReq, 
    current_user=Depends(get_current_user)
):
    
    # 1. Find the class teacher's assignment
    teacher_map = db_find_one("dept_class_teachers", class_teacher_id=current_user["id"])
    if not teacher_map:
        raise HTTPException(403, "You are not a class teacher of any section")
        
    section = teacher_map.get("section")
    dept_id = teacher_map.get("dept_id")
    org_id = current_user.get("org_id")

    # 2. Check if student email already exists
    if get_user_row_by_email(payload.email):
        raise HTTPException(400, "User with this email already exists")

    # 3. Create the user
    user_id = None
    try:
        fb_user = auth.create_user(
            email=payload.email,
            display_name=payload.full_name  # <-- FIX 2 (was already correct in your paste)
        )
        user_id = fb_user.uid
        
        # 4. Add to 'users' collection
        db_insert_one("users", {
            "email": payload.email,
            "full_name": payload.full_name,
            "roles": ["student"],  # <-- FIX 1 (was already correct in your paste)
            "org_id": org_id,
        }, doc_id=user_id)
        
        # 5. Add to 'students' collection (mapping)
        db_insert_one("students", {
            "user_id": user_id,
            "full_name": payload.full_name,
            "email": payload.email,
            "org_id": org_id,
            "dept_id": dept_id,
            "section": section,
        })
        
    except Exception as e:
        if user_id:
            auth.delete_user(user_id)
        raise HTTPException(500, f"Error creating student: {e}")

    return {"message": "Student added successfully", "user_id": user_id}

# from pydantic import BaseModel # Already imported

class AssignSubjectTeacherReq(BaseModel):
    subject_name: str
    teacher_email: str

@app.post("/api/class-teacher/assign-subject-teacher")
@require_any_role("class_teacher") # Only class teachers can call this
def assign_subject_teacher(
    payload: AssignSubjectTeacherReq, 
    current_user=Depends(get_current_user)
):
    
    # 1. Find the class teacher's section (e.g., "5A")
    teacher_map = db_find_one("dept_class_teachers", class_teacher_id=current_user["id"])
    if not teacher_map:
        raise HTTPException(403, "You are not assigned to a section")
    
    section_name = teacher_map.get("section")
    dept_id = teacher_map.get("dept_id")

    # 2. Find the user being assigned (by email)
    user = get_user_row_by_email(payload.teacher_email)
    user_id = None
    
    if not user:
        # 3a. If user doesn't exist, create them
        try:
            fb_user = auth.create_user(
                email=payload.teacher_email,
                display_name=payload.teacher_email 
            )
            user_id = fb_user.uid
            
            db_insert_one("users", {
                "email": payload.teacher_email,
                "full_name": "New Teacher", # Placeholder
                "roles": ["teacher"], # Start with just 'teacher'
                "org_id": current_user["org_id"],
            }, doc_id=user_id)
            
        except Exception as e:
            raise HTTPException(500, f"Firebase Auth error: {e}")
    else:
        # 3b. User *does* exist (this is the case you asked about)
        user_id = user["id"]
        
        roles = parse_roles_field(user.get("roles") or [])
        
        if "teacher" not in roles:
            roles.append("teacher")
            db_update_one("users", user_id, {"roles": roles}) # <-- FIX 1 (was already correct)

    # 4. Map this teacher to the subject and section
    db_insert_one("subject_teachers", {
        "dept_id": dept_id,
        "section": section_name,
        "subject_name": payload.subject_name,
        "teacher_id": user_id
    })

    return {"message": "Subject teacher assigned successfully", "user_id": user_id}

# -----------------------------------------------------------------
# NEW HELPER ENDPOINTS FOR TEACHER DASHBOARD
# -----------------------------------------------------------------

@app.get("/api/class-teacher/my-section")
@require_any_role("class_teacher")
def get_my_section(current_user=Depends(get_current_user)):
    teacher_map = db_find_one("dept_class_teachers", class_teacher_id=current_user["id"])
    if not teacher_map:
        raise HTTPException(404, "You are not assigned to a section")
    return teacher_map

@app.get("/api/class-teacher/students")
@require_any_role("class_teacher")
def get_students_in_section(current_user=Depends(get_current_user)):
    teacher_map = db_find_one("dept_class_teachers", class_teacher_id=current_user["id"])
    if not teacher_map:
        raise HTTPException(404, "You are not assigned to a section")
    
    students = db_find_many("students", section=teacher_map.get("section"))
    return students

@app.get("/api/teacher/my-subjects")
@require_any_role("teacher", "class_teacher") # Allow both roles
def get_my_assigned_subjects(current_user=Depends(get_current_user)):
    subjects = db_find_many("subject_teachers", teacher_id=current_user["id"])
    return subjects

# -------------------------
# END OF NEW ENDPOINTS
# -------------------------


@app.post("/api/dept/{dept_id}/assign-hod")
@require_role("admin")
def assign_hod_to_dept(dept_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
    user = get_user_row_by_email(payload.email)
    if not user:
        raise HTTPException(404, "User not found (must be created first)")

    # This helper function handles appending the role
    assign_role(user["id"], "hod", org_id=current_user["org_id"], dept_id=dept_id)
    return {"message": "HOD Assigned"}

@app.post("/api/admin/assign-hod")
@require_any_role("admin")
def assign_hod_role(req: dict, current_user=Depends(get_current_user)):
    dept_id = req.get("dept_id")
    hod_id = req.get("hod_id") # This is now a Firebase UID

    dept = db_find_one("departments", id=dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not exists")

    # Assign HOD to department
    db_update_one("departments", dept_id, { "hod_id": hod_id })

    # Add HOD role to user
    user = get_user_row(hod_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    roles = parse_roles_field(user.get("roles") or [])
    if "hod" not in roles:
        roles.append("hod")
        db_update_one("users", hod_id, { "roles": roles }) # <-- FIX 1 (was already correct)
    return {"message": "HOD assigned"}

@app.post("/api/departments/{dept_id}/add-class-teacher")
@require_any_role("hod")
def add_class_teacher(
    dept_id: str,
    full_name: str = Form(...),
    email: str = Form(...),
    section: str = Form(...),
    current_user=Depends(get_current_user)
):

    hod_map = db_find_one("department_hods", hod_id=current_user["id"], dept_id=dept_id)
    if not hod_map:
        raise HTTPException(403, "Not HOD of this department")

    if get_user_row_by_email(email):
        raise HTTPException(400, "User already exists")

    user_id = None
    try:
        # 1. Create in Firebase Auth
        fb_user = auth.create_user(
            email=email,
            display_name=full_name  # <-- FIX 2 (was already correct)
        )
        user_id = fb_user.uid
    except Exception as e:
        raise HTTPException(500, f"Firebase Auth error: {e}")

    # 2. Create in Firestore
    db_insert_one("users", {
        "email": email,
        "full_name": full_name,
        "roles": ["class_teacher"],  # <-- FIX 1 (was already correct)
        "org_id": current_user["org_id"],
    }, doc_id=user_id)

    # 3. Save mapping
    db_insert_one("dept_class_teachers", {
        "dept_id": dept_id,
        "class_teacher_id": user_id,
        "section": section
    })

    return {"message": "Class teacher added", "user_id": user_id, "section": section}

@app.post("/api/departments/{dept_id}/sections")
@require_any_role("hod")
def create_section(dept_id: str, name: str = Form(...), current_user=Depends(get_current_user)):
    hod_map = db_find_one("department_hods", hod_id=current_user["id"], dept_id=dept_id)
    if not hod_map:
        raise HTTPException(403, "Not HOD of this department")

    section = {
        # "id" auto-generated
        "dept_id": dept_id,
        "name": name,  # Example: "5A"
        "class_teacher_id": None
    }
    new_section = db_insert_one("sections", section)
    return new_section

@app.post("/api/sections/{section_id}/assign-teacher")
@require_any_role("hod")
def assign_class_teacher(
    section_id: str,
    full_name: str = Form(...),
    email: str = Form(...),
    # password: str = Form(...), # REMOVED
    current_user=Depends(get_current_user)
):
    section_doc = db.collection("sections").document(section_id).get()
    if not section_doc.exists:
        raise HTTPException(404, "Section not found")

    hod_map = db_find_one("department_hods", hod_id=current_user["id"], dept_id=section_doc.to_dict()["dept_id"])
    if not hod_map:
        raise HTTPException(403, "Not HOD for this department")

    # --- FIX 3: LOGIC CHANGE ---
    # We must check if user exists first to handle multiple roles
    user = get_user_row_by_email(email)
    user_id = None
    
    if user:
        # User already exists
        user_id = user["id"]
        roles = parse_roles_field(user.get("roles") or [])
        if "class_teacher" not in roles:
            roles.append("class_teacher")
            db_update_one("users", user_id, {"roles": roles}) # <-- FIX 1
    
    else:
        # User does not exist, create them
        try:
            # 1. Create in Firebase Auth
            # --- FIX 2: Changed full_name to display_name ---
            fb_user = auth.create_user(
                email=email,
                display_name=full_name 
            )
            user_id = fb_user.uid
        except Exception as e:
            raise HTTPException(500, f"Firebase Auth error: {e}")

        # 2. Create in Firestore
        db_insert_one("users", {
            "email": email,
            "full_name": full_name,
            "roles": ["class_teacher"], # <-- FIX 1
            "org_id": current_user["org_id"],
        }, doc_id=user_id)

    # 3. Assign to section
    db_update_one("sections", section_id, {"class_teacher_id": user_id})

    return {"message": "Teacher assigned to section", "user_id": user_id}

@app.post("/api/orgs/{org_id}/departments/{dept_id}/assign-hod")
@require_any_role("admin")
def assign_hod_to_dept_and_create_user(org_id: str, dept_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
    if current_user.get("org_id") != org_id:
        raise HTTPException(status_code=403, detail="Not your org")

    user = get_user_row_by_email(payload.email)
    user_id = None

    if not user:
        try:
            # 1. Create in Firebase Auth
            fb_user = auth.create_user(
                email=payload.email,
                display_name=payload.full_name  # <-- FIX 2 (was already correct)
            )
            user_id = fb_user.uid
        except Exception as e:
            raise HTTPException(500, f"Firebase Auth error: {e}")
        
        # 2. Create in Firestore
        user = {
            "email": payload.email,
            "full_name": payload.full_name,
            "roles": ["hod"],  # <-- FIX 1 (was already correct)
            "org_id": org_id,
        }
        db_insert_one("users", user, doc_id=user_id)
        user['id'] = user_id # for consistency
    else:
        # 3. Update existing user
        user_id = user["id"]
        roles = parse_roles_field(user.get("roles"))
        if "hod" not in roles:
            roles.append("hod")
        db_update_one("users", user["id"], {"roles": roles}) # <-- FIX 1 & 3 (was already correct)

    # 4. Store HOD–Department mapping
    # Check if mapping already exists to avoid duplicates
    existing_map = db_find_one("department_hods", org_id=org_id, dept_id=dept_id)
    if existing_map:
        db_update_one("department_hods", existing_map["id"], {"hod_id": user_id})
    else:
        db_insert_one("department_hods", {
            "org_id": org_id,
            "dept_id": dept_id,
            "hod_id": user_id
        })

    return {"message": "HOD assigned successfully", "user_id": user_id}

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
            # Add the section to the user object for the frontend
            u['section'] = e.get('section') 
            teachers.append(u)
    return teachers

@app.post('/api/departments/create')
@require_any_role('admin')
def create_department_endpoint(req: CreateDeptReq, current_user=Depends(get_current_user)):
    # This is a duplicate endpoint from your file, fixed it.
    if current_user.get('org_id') != req.org_id:
        raise HTTPException(status_code=403, detail='Not your org')
    
    new_dept = {
        # "id" auto-generated
        "org_id": req.org_id,
        "name": req.name,
        "hod_id": req.hod_id or None
    }
    new_doc = db_insert_one('departments', new_dept)
    return new_doc

@app.get("/api/hod/department")
@require_any_role("hod")
def get_hod_department(current_user=Depends(get_current_user)):
    hod_id = current_user["id"]
    mapping = db_find_one("department_hods", hod_id=hod_id)
    if not mapping:
        raise HTTPException(404, "Department not assigned")
    dept_id = mapping["dept_id"]
    
    dept_doc = db.collection("departments").document(dept_id).get()
    if not dept_doc.exists:
        raise HTTPException(404, "Department missing in DB")
    
    dept_data = dept_doc.to_dict()
    dept_data['id'] = dept_doc.id
    return dept_data

def find_user_section(user_id: str):
    # This is a complex way to find a section. 
    # A student should probably have a 'section' field directly.
    # But keeping your logic:
    memberships = db_find_many("class_memberships", user_id=user_id)
    for m in memberships:
        cls_doc = db.collection("classes").document(m["class_id"]).get()
        if cls_doc.exists:
            cls = cls_doc.to_dict()
            if cls and cls.get("section"):
                return cls["section"]
    
    # Fallback for class teachers
    teacher_map = db_find_one("dept_class_teachers", class_teacher_id=user_id)
    if teacher_map:
        return teacher_map.get("section")
        
    return None

@app.get("/api/user/{user_id}/section/students")
def get_students_from_user_section(user_id: str):
    section = find_user_section(user_id)
    if not section:
        raise HTTPException(404, detail="User has no section assigned")

    # This logic is flawed. It should find students in the same section.
    # Fixed logic:
    students = db_find_many("students", section=section)
    return students

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
    # This logic assumes a student.
    student = get_user_row(user_id)
    if not student or "student" not in parse_roles_field(student.get("roles")):
        raise HTTPException(404, detail="Not a student")

    all_marks = db_find_many("final_marks", student_id=user_id)

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
            "class_id": m.get("class_id") # Use .get for safety
        })

    return {
        "user_id": user_id,
        "section": db_find_one("students", user_id=user_id).get("section"), # More direct
        "subjects": grouped
    }


# @app.post('/api/auth/login') # DELETED
# def login(req: LoginReq):
#     ...

@app.get('/api/users/me')
def get_me(current_user=Depends(get_current_user)):
    # This works perfectly with the new get_current_user
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
        # "id" auto-generated
        "name": req.name,
        "org_type": org_type
    }
    new_doc = db_insert_one('organizations', new_org)
    return new_doc

# In your main.py or wherever /api/orgs is
@app.get("/api/orgs")
def get_all_organizations(current_user=Depends(get_current_user)):
    
    # --- THIS IS THE FIX ---
    # Check if the user is the OWNER
    if "owner" in current_user.get("roles", []):
        # If they are the owner, they get to see ALL orgs
        all_orgs = db_find_many("organizations") 
        return all_orgs
    # --- END OF FIX ---
    
    # If not an owner, run the old logic for admins/teachers
    user_org_id = current_user.get("org_id")
    
    if not user_org_id:
        # Not an owner and no org_id, so they see nothing
        return []

    # This is an admin/teacher, so only show their org
    org_doc = db.collection("organizations").document(user_org_id).get()
    if not org_doc.exists:
        return []
    org = org_doc.to_dict()
    org['id'] = org_doc.id
    return [org] # This just works
@app.post('/api/orgs/{org_id}/admin/create')
@require_owner
def create_admin(org_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
    org_doc = db.collection("organizations").document(org_id).get()
    if not org_doc.exists:
        raise HTTPException(status_code=404, detail='Organization not found')
        
    # --- START OF NEW LOGIC ---
    
    user = get_user_row_by_email(payload.email)
    user_id = None

    if user:
        # --- CASE 1: USER ALREADY EXISTS ---
        user_id = user["id"]
        
        # 1. Get their old roles
        roles = parse_roles_field(user.get("roles") or [])
        
        # 2. Add the 'admin' role if they don't have it
        if "admin" not in roles:
            roles.append("admin")
        
        # 3. Update the user with new roles and correct org_id
        db_update_one("users", user_id, {
            "roles": roles, # Save the updated list
            "org_id": org_id, # Ensure they are assigned to this org
            "full_name": payload.full_name or user.get("full_name") # Update name if provided
        })
        
        return {'message':'Admin role added to existing user', 'user_id': user_id, "roles": roles}
        
    else:
        # --- CASE 2: USER IS NEW ---
        try:
            # 1. Create in Firebase Auth
            fb_user = auth.create_user(
                email=payload.email,
                display_name=payload.full_name # Fixed: display_name
            )
            user_id = fb_user.uid
        except Exception as e:
            raise HTTPException(500, f"Firebase Auth error: {e}")

        # 2. Create in Firestore
        new_admin = {
            'email': payload.email,
            'full_name': payload.full_name,
            'roles': ['admin'], # Fixed: native list
            'org_id': org_id,
        }
        db_insert_one('users', new_admin, doc_id=user_id)
        return {'message':'New admin user created', 'user_id': user_id}

    # --- END OF NEW LOGIC ---
# -------------------------
# REFACTORED: ADMIN actions
# -------------------------
@app.post('/api/orgs/{org_id}/teachers/create')
@require_any_role('admin')
def create_class_teacher_admin(org_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
    if current_user.get('org_id') != org_id:
        raise HTTPException(status_code=403, detail='Not your org')
        
    if get_user_row_by_email(payload.email):
        raise HTTPException(status_code=400, detail="User with this email already exists")

    user_id = None
    try:
        # 1. Create in Firebase Auth
        # --- FIX 2: Changed full_name to display_name ---
        fb_user = auth.create_user(
            email=payload.email,
            display_name=payload.full_name
        )
        user_id = fb_user.uid
    except Exception as e:
        raise HTTPException(500, f"Firebase Auth error: {e}")

    # 2. Create in Firestore
    new_teacher = {
        'email': payload.email,
        'full_name': payload.full_name,
        'roles': ['class_teacher'], # --- FIX 1: Removed json.dumps ---
        'org_id': org_id,
    }
    db_insert_one('users', new_teacher, doc_id=user_id)
    return {'message':'class teacher created', 'user_id': user_id}

@app.delete('/api/orgs/{org_id}/teachers/{teacher_id}')
@require_any_role('admin')
def delete_class_teacher(org_id: str, teacher_id: str, current_user=Depends(get_current_user)):
    if current_user.get('org_id') != org_id:
        raise HTTPException(status_code=403, detail='Not your org')
    
    # 1. Check if user is in org
    teacher = get_user_row(teacher_id)
    if not teacher or teacher.get('org_id') != org_id:
         raise HTTPException(status_code=404, detail='Teacher not found in this org')

    try:
        # 2. Delete from Firebase Auth
        auth.delete_user(teacher_id)
    except Exception as e:
        raise HTTPException(500, f"Firebase Auth deletion error: {e}")
    
    # 3. Delete from Firestore
    db_delete_one('users', teacher_id)
    # Note: You might want to clean up other references (classes, etc.)
        
    return {'message': 'deleted teacher from Auth and Firestore'}

# -------------------------
# REFACTORED: DEPARTMENTS
# -------------------------
# This duplicate endpoint is in your code, keeping it
@app.post('/api/departments/create') 
@require_any_role('admin')
def create_department_admin(req: CreateDeptReq, current_user=Depends(get_current_user)):
    if current_user.get('org_id') != req.org_id:
        raise HTTPException(status_code=403, detail='Not your org')
    
    new_dept = {
        # "id" auto-generated
        'org_id': req.org_id,
        'name': req.name,
        'hod_id': req.hod_id
    }
    new_doc = db_insert_one('departments', new_dept)
    return new_doc

@app.get('/api/orgs/{org_id}/departments')
@require_any_role('admin','class_teacher','sub_teacher', 'hod') # Added HOD
def list_departments(org_id: str, current_user=Depends(get_current_user)):
    return db_find_many('departments', org_id=org_id) # This just works

# -------------------------
# REFACTORED: TEACHER HIERARCHY
# -------------------------
@app.post('/api/teachers/add-sub')
@require_any_role('class_teacher','admin')
def add_sub_teacher(payload: AddUserReq, current_user=Depends(get_current_user)):
    org_id = current_user.get('org_id')
    
    # --- FIX 3: LOGIC CHANGE ---
    # Check if user exists to append roles
    user = get_user_row_by_email(payload.email)
    user_id = None
    
    if user:
        user_id = user["id"]
        roles = parse_roles_field(user.get("roles") or [])
        if "sub_teacher" not in roles:
            roles.append("sub_teacher")
            db_update_one("users", user_id, {"roles": roles}) # <-- FIX 1
    else:
        # User does not exist, create them
        try:
            # 1. Create in Firebase Auth
            # --- FIX 2: Changed full_name to display_name ---
            fb_user = auth.create_user(
                email=payload.email,
                display_name=payload.full_name
            )
            user_id = fb_user.uid
        except Exception as e:
            raise HTTPException(500, f"Firebase Auth error: {e}")

        # 2. Create in Firestore
        new_sub_teacher = {
            'email': payload.email,
            'full_name': payload.full_name,
            'roles': ['sub_teacher'], # --- FIX 1: Removed json.dumps ---
            'org_id': org_id,
        }
        db_insert_one('users', new_sub_teacher, doc_id=user_id)
    
    # 3. Create mapping
    # Avoid duplicate mappings
    existing_map = db_find_one('teacher_hierarchy', 
                                org_id=org_id, 
                                class_teacher_id=current_user['id'], 
                                sub_teacher_id=user_id)
    if not existing_map:
        db_insert_one('teacher_hierarchy', {
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
    # ... (code for generating class_code is fine) ...
    code = ""
    for _ in range(6):
        code = secrets.token_urlsafe(4).upper()
        if not db_find_one('classes', class_code=code):
            break

    # ... (code for finding ct_id is fine) ...
    ct_id = None
    roles = parse_roles_field(current_user.get('roles', []))
    
    if 'sub_teacher' in roles:
        h = db_find_one("teacher_hierarchy", sub_teacher_id=current_user["id"])
        if not h:
            raise HTTPException(status_code=400, detail="No linked class teacher found for this sub_teacher.")
        ct_id = h["class_teacher_id"]
    elif 'class_teacher' in roles:
        ct_id = current_user["id"]
    else:
        raise HTTPException(status_code=403, detail="Not allowed")

    # ... (code for auto-detecting dept/section is fine) ...
    mapping = db_find_one("dept_class_teachers", class_teacher_id=ct_id)
    dept_id = mapping["dept_id"] if mapping else None
    section = mapping["section"] if mapping else None

    # Create new class
    body = {
        # "id" auto-generated
        "org_id": req.org_id,
        "title": req.title,
        "description": req.description,
        "created_by": current_user["id"],
        "class_teacher_id": ct_id,
        "class_code": code,
        "department_id": req.department_id or dept_id, # Allow override
        "section": req.section or section # Allow override
    }
    new_class = db_insert_one("classes", body)

    # Add teacher membership
    db_insert_one("class_memberships", {
        # "id" auto-generated
        "class_id": new_class["id"],
        "user_id": current_user["id"],
        "role": "teacher"
    })

    return new_class


@app.get("/api/classes/{class_id}")
def get_class_info(class_id: str):
    cls_doc = db.collection("classes").document(class_id).get()
    if not cls_doc.exists:
        raise HTTPException(404, "Class not found")
    cls = cls_doc.to_dict()
    cls['id'] = cls_doc.id
    return cls


@app.delete('/api/classes/{class_id}')
@require_any_role('sub_teacher','class_teacher','admin')
def delete_class(class_id: str, current_user=Depends(get_current_user)):
    c = db.collection("classes").document(class_id).get()
    if not c.exists:
        raise HTTPException(status_code=404, detail='Class not found')
    
    c_data = c.to_dict()
    allowed = False
    if 'admin' in parse_roles_field(current_user.get('roles', [])) and current_user.get('org_id') == c_data.get('org_id'):
        allowed = True
    if c_data.get('created_by') == current_user['id']:
        allowed = True
    if c_data.get('class_teacher_id') == current_user['id']:
        allowed = True
    
    if not allowed:
        raise HTTPException(status_code=403, detail='Not allowed to delete this class')
    
    db_delete_one('classes', class_id)
    # Note: You should also delete memberships, assignments, etc. (cascading delete)
    return {'message':'deleted'}

@app.get("/api/classes/{class_id}/students")
@require_any_role("class_teacher", "sub_teacher", "admin","student", "hod")
def get_class_students(class_id: str, current_user=Depends(get_current_user)):
    # Simpler check: are they in the org?
    cls_doc = db.collection("classes").document(class_id).get()
    if not cls_doc.exists:
        raise HTTPException(status_code=404, detail="Class not found")
        
    if current_user.get("org_id") != cls_doc.to_dict().get("org_id"):
        raise HTTPException(status_code=403, detail="Not in your organization")

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
@require_any_role("sub_teacher", "class_teacher", "admin", "student", "hod")
def list_classes(current_user=Depends(get_current_user)):
    roles = parse_roles_field(current_user.get("roles", []))
    org_id = current_user.get("org_id")
    user_id = current_user["id"]

    if "admin" in roles:
        return db_find_many("classes", org_id=org_id) or []
        
    if "hod" in roles:
        hod_map = db_find_one("department_hods", hod_id=user_id)
        if hod_map:
            return db_find_many("classes", department_id=hod_map["dept_id"]) or []
        return []
        
    if "class_teacher" in roles:
        return db_find_many("classes", class_teacher_id=user_id) or []

    # For students and sub-teachers, query memberships
    memberships = []
    if "sub_teacher" in roles:
        memberships = db_find_many("class_memberships", user_id=user_id, role="teacher")
    elif "student" in roles:
        memberships = db_find_many("class_memberships", user_id=user_id, role="student")
    else:
        # This case should be impossible due to @require_any_role
        return [] 

    class_ids = [m["class_id"] for m in memberships]
    if not class_ids:
        return []
        
    # Firestore 'in' query is limited to 10 items.
    # For a real app, you'd fetch docs one-by-one or restructure data.
    # For this project, we'll fetch one-by-one.
    all_classes = []
    # Use set to avoid duplicates if member of same class twice
    for cid in set(class_ids): 
        c_doc = db.collection("classes").document(cid).get()
        if c_doc.exists:
            c_data = c_doc.to_dict()
            c_data['id'] = c_doc.id
            all_classes.append(c_data)
    return all_classes

@app.post("/api/teachers/add-student")
@require_any_role("class_teacher", "admin", "sub_teacher")
def add_student(payload: AddStudentReq, current_user=Depends(get_current_user)):
    """
    Create or update a student in Firebase/Firestore and add them to the class.
    """
    class_id = payload.class_id
    email = payload.email.strip().lower()
    full_name = (payload.full_name or "").strip()

    cls_doc = db.collection("classes").document(class_id).get()
    if not cls_doc.exists:
        raise HTTPException(status_code=404, detail="Class not found")
    cls = cls_doc.to_dict()

    # ... (Permission checks are fine) ...
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

    if not email:
        raise HTTPException(status_code=400, detail="Email required")

    existing = get_user_row_by_email(email)
    user_id = None
    org_id = cls.get("org_id") # Get org from class

    if existing:
        user_id = existing["id"]
        # ensure 'student' role present
        roles_list = parse_roles_field(existing.get("roles") or [])
        if "student" not in roles_list:
            roles_list.append("student")
            # --- FIX 1: Removed json.dumps ---
            db_update_one("users", user_id, {"roles": roles_list}) 
        # ensure org matches class org
        if existing.get("org_id") != org_id:
            db_update_one("users", user_id, {"org_id": org_id})
    else:
        try:
            # 1. Create in Firebase Auth
            # --- FIX 2: Changed full_name to display_name ---
            fb_user = auth.create_user(
                email=email,
                display_name=full_name
            )
            user_id = fb_user.uid
        except Exception as e:
            raise HTTPException(500, f"Firebase Auth error: {e}")
        
        # 2. Create in Firestore
        new_user = {
            "email": email,
            "full_name": full_name,
            "roles": ["student"], # --- FIX 3 (Typo): Was 'roles', changed to ["student"] ---
            "org_id": org_id
        }
        db_insert_one("users", new_user, doc_id=user_id)

    # create membership if not exists
    existing_mem = db_find_one("class_memberships", class_id=class_id, user_id=user_id)
    if not existing_mem:
        db_insert_one("class_memberships", {
            # "id" auto-generated
            "class_id": class_id,
            "user_id": user_id,
            "role": "student"
        })

    return {"message": "student added/updated", "user_id": user_id}

# -------------------------
# REFACTORED: ASSIGNMENTS
# -------------------------
@app.post('/api/assignments')
@require_any_role('sub_teacher', 'teacher') # 'teacher' is the role
def create_assignment(req: CreateAssignmentReq, current_user=Depends(get_current_user)):
    cm = db_find_one('class_memberships', class_id=req.class_id, user_id=current_user['id'])
    if not cm or cm.get('role') != 'teacher':
        raise HTTPException(status_code=403, detail='Only the subject teacher can create assignments for this class')
    if req.assignment_type not in ('file','text','mixed'):
        raise HTTPException(status_code=400, detail='Invalid assignment_type')
        
    body = {
        # "id" auto-generated
        'class_id': req.class_id, 
        'created_by': current_user['id'], 
        'title': req.title, 
        'description': req.description, 
        'due_at': req.due_at, 
        'assignment_type': req.assignment_type,
        'file_url': None, # New field
        'public_id': None # New field
    }
    new_assignment = db_insert_one('assignments', body)
    return new_assignment

@app.post('/api/assignments/{assignment_id}/upload-file')
@require_any_role('sub_teacher', 'teacher') # 'teacher' is the role
def upload_assignment_file(assignment_id: str, file: UploadFile = File(...), current_user=Depends(get_current_user)):
    a = db.collection('assignments').document(assignment_id).get()
    if not a.exists:
        raise HTTPException(status_code=404, detail='Assignment not found')
        
    cm = db_find_one('class_memberships', class_id=a.to_dict()['class_id'], user_id=current_user['id'])
    if not cm or cm.get('role') != 'teacher':
        raise HTTPException(status_code=403, detail='Only subject teacher can upload file for this assignment')

    # Upload to cloudinary
    try:
        upload_result = cloudinary.uploader.upload(
            file.file,
            folder=f"assignments/{assignment_id}", 
            resource_type="auto"
        )
    except Exception as e:
        raise HTTPException(500, f"Cloudinary upload failed: {e}")
    
    # Store URL in Firestore
    db_update_one('assignments', assignment_id, {
        'file_url': upload_result["secure_url"],
        'public_id': upload_result["public_id"]
    })
    
    return {'message':'file uploaded', 'file_url': upload_result["secure_url"]}

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
    assignment_doc = db.collection('assignments').document(assignment_id).get()
    if not assignment_doc.exists:
        raise HTTPException(status_code=404, detail='Assignment not found')

    class_id = assignment_doc.to_dict()['class_id']
    cm = db_find_one('class_memberships', class_id=class_id, user_id=current_user["id"])
    if not cm:
        raise HTTPException(status_code=403, detail="Not in class")

    file_url = None
    public_id = None

    if file:
        try:
            upload_result = cloudinary.uploader.upload(
                file.file,
                folder=f"submissions/{assignment_id}/{current_user['id']}", 
                resource_type="auto"
            )
            file_url = upload_result["secure_url"]
            public_id = upload_result["public_id"]
        except Exception as e:
            raise HTTPException(500, f"Cloudinary upload failed: {e}")

    # Check if exists
    existing = db_find_one("submissions", assignment_id=assignment_id, student_id=current_user["id"])
    
    update_data = {
        "text_content": text_content,
        "submitted_at": datetime.utcnow()
    }
    if file_url:
        update_data["file_url"] = file_url
        update_data["public_id"] = public_id

    if existing:
        db_update_one("submissions", existing["id"], update_data)
        return {"message": "updated submission"}

    new_sub = {
        # "id" auto-generated
        "assignment_id": assignment_id,
        "student_id": current_user["id"],
        "text_content": text_content,
        "file_url": file_url,
        "public_id": public_id,
        "submitted_at": datetime.utcnow()
    }

    new_doc = db_insert_one("submissions", new_sub)
    return {"message": "submitted", "id": new_doc["id"]}


@app.get('/api/assignments/{assignment_id}/submissions')
@require_any_role('sub_teacher','class_teacher', 'teacher', 'hod')
def get_submissions(assignment_id: str, current_user=Depends(get_current_user)):
    a = db.collection('assignments').document(assignment_id).get()
    if not a.exists:
        raise HTTPException(status_code=404, detail='Assignment not found')
    
    a_data = a.to_dict()
    class_id = a_data['class_id']
    
    # Check permissions
    roles = parse_roles_field(current_user.get("roles", []))
    allowed = False
    
    # Is subject teacher?
    cm = db_find_one('class_memberships', class_id=class_id, user_id=current_user['id'])
    if cm and cm.get('role') == 'teacher':
        allowed = True
        
    # Is class teacher (supervisor)?
    cls_doc = db.collection('classes').document(class_id).get()
    if cls_doc.exists and cls_doc.to_dict().get('class_teacher_id') == current_user['id']:
        allowed = True
        
    # Is HOD of the department?
    if "hod" in roles and cls_doc.exists:
        hod_map = db_find_one("department_hods", hod_id=current_user["id"])
        if hod_map and hod_map.get("dept_id") == cls_doc.to_dict().get("department_id"):
            allowed = True
            
    if not allowed:
        raise HTTPException(status_code=403, detail='Not allowed')
        
    return db_find_many('submissions', assignment_id=assignment_id)

@app.post('/api/submissions/{submission_id}/grade')
@require_any_role('sub_teacher', 'teacher') # 'teacher' is the role
def grade_submission(submission_id: str, grade: float = Body(...), current_user=Depends(get_current_user)):
    s = db.collection('submissions').document(submission_id).get()
    if not s.exists:
        raise HTTPException(status_code=404, detail='Submission not found')
        
    assignment = db.collection('assignments').document(s.to_dict()['assignment_id']).get()
    class_id = assignment.to_dict()['class_id']
    
    cm = db_find_one('class_memberships', class_id=class_id, user_id=current_user['id'])
    if not (cm and cm.get('role') == 'teacher'):
        raise HTTPException(status_code=403, detail='Only the subject teacher can grade submissions')
        
    db_update_one('submissions', submission_id, {'grade': grade, 'graded_by': current_user['id']})
    return {'message':'graded'}

# -------------------------
# REFACTORED: NOTES (Already uses Cloudinary)
# -------------------------
# @app.post('/api/notes') # DELETED - This endpoint was flawed
# def upload_note(req: NoteCreateReq, ...):
#     ...
    
@app.get('/api/classes/{class_id}/notes')
def list_notes(class_id: str, current_user=Depends(get_current_user)):
    cm = db_find_one('class_memberships', class_id=class_id, user_id=current_user['id'])
    if not cm:
        raise HTTPException(status_code=403, detail='Not a member')
    
    return db_find_many('notes', class_id=class_id)

@app.post("/api/notes/upload")
@require_any_role("class_teacher", "sub_teacher", "teacher") # 'teacher' is the role
def upload_note(
    class_id: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    # This endpoint is already perfect and uses Cloudinary. No changes needed.
    cm = db_find_one("class_memberships", class_id=class_id, user_id=current_user["id"])
    if not cm or cm.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Not allowed")

    try:
        upload_result = cloudinary.uploader.upload(
            file.file,
            folder=f"class_notes/{class_id}", 
            resource_type="auto"
        )
    except Exception as e:
        raise HTTPException(500, f"Cloudinary upload failed: {e}")

    note = {
        # "id" auto-generated
        "class_id": class_id,
        "uploaded_by": current_user["id"],
        "title": title,
        "file_url": upload_result["secure_url"],
        "public_id": upload_result["public_id"],
        "uploaded_at": str(datetime.utcnow())
    }

    new_note = db_insert_one("notes", note)
    return {"message": "Uploaded", "note": new_note}

# -------------------------
# REFACTORED: FINAL MARKS
# -------------------------
@app.post('/api/finalmarks')
@require_any_role('sub_teacher', 'teacher') # 'teacher' is the role
def upload_final_marks(req: FinalMarkReq, current_user=Depends(get_current_user)):
    stu = get_user_row(req.student_id)
    if not stu:
        raise HTTPException(status_code=404, detail='Student not found')
        
    body = req.dict()
    # "id" auto-generated
    body['uploaded_by'] = current_user['id']
    
    db_insert_one('final_marks', body)
    return {'message':'uploaded'}


@app.get("/api/classes/{class_id}/grades")
@require_any_role("admin", "class_teacher", "sub_teacher", "student", "teacher", "hod")
def get_class_grades(class_id: str, current_user=Depends(get_current_user)):
    # This logic is fine and will use the new DB helpers
    member = db_find_one("class_memberships", class_id=class_id, user_id=current_user["id"])
    roles = parse_roles_field(current_user.get("roles", []))
    org_id = current_user.get("org_id")
    
    # Student can only see their own grades
    if "student" in roles:
        if not member:
             raise HTTPException(status_code=403, detail="Not part of this class")
        return db_find_many("final_marks", class_id=class_id, student_id=current_user["id"]) or []

    # All other roles (admin, teachers, hod) must be in the org
    cls_doc = db.collection("classes").document(class_id).get()
    if not cls_doc.exists or cls_doc.to_dict().get("org_id") != org_id:
        raise HTTPException(status_code=403, detail="Not in your org")

    if "admin" in roles:
        return db_find_many("final_marks", class_id=class_id, org_id=org_id) or []

    if "class_teacher" in roles:
        if cls_doc.to_dict().get("class_teacher_id") == current_user["id"]:
            return db_find_many("final_marks", class_id=class_id) or []
        # else, they might be a subject teacher, so don't raise error yet
            
    if "hod" in roles:
        hod_map = db_find_one("department_hods", hod_id=current_user["id"])
        if hod_map and hod_map.get("dept_id") == cls_doc.to_dict().get("department_id"):
            return db_find_many("final_marks", class_id=class_id) or []
        # else, they might be a subject teacher, so don't raise error yet

    if "sub_teacher" in roles or "teacher" in roles:
        if member and member.get("role") == "teacher":
            return db_find_many("final_marks", class_id=class_id) or []

    raise HTTPException(status_code=403, detail="Not allowed")


@app.get('/api/orgs/{org_id}/grades')
@require_any_role('class_teacher','admin','sub_teacher', 'teacher', 'hod')
def view_all_grades(org_id: str, current_user=Depends(get_current_user)):
    # This logic is complex but should work with the new DB helpers
    roles = parse_roles_field(current_user.get('roles') or [])
    
    if 'admin' in roles and current_user.get('org_id') == org_id:
        return db_find_many('final_marks', org_id=org_id)
        
    if 'hod' in roles:
        hod_map = db_find_one("department_hods", hod_id=current_user["id"])
        if not hod_map: return []
        dept_id = hod_map["dept_id"]
        classes = db_find_many('classes', department_id=dept_id)
        class_ids = [c['id'] for c in classes]
    
    elif 'class_teacher' in roles:
        classes = db_find_many('classes', class_teacher_id=current_user['id'], org_id=org_id)
        class_ids = [c['id'] for c in classes]
            
    elif 'sub_teacher' in roles or 'teacher' in roles:
        cm = db_find_many('class_memberships', user_id=current_user['id'], role='teacher')
        class_ids = [c['class_id'] for c in cm]
        
    else:
        raise HTTPException(status_code=403, detail='Not allowed')

    if not class_ids: return []
        
    # Firestore 'in' query limit is 10. This is a potential bug.
    # For a real app, you'd fetch docs one-by-one or restructure data.
    # For now, we assume < 10 classes per teacher
    # We must fetch one by one to overcome 10-item limit
    all_marks = []
    for cid in set(class_ids):
        all_marks.extend(db_find_many('final_marks', class_id=cid))
    return all_marks

# -------------------------
# REFACTORED: MESSAGES
# -------------------------
@app.post('/api/messages')
@require_any_role('student','sub_teacher','class_teacher','admin', 'teacher', 'hod')
def send_message(req: MessageReq, current_user=Depends(get_current_user)):
    # This logic is fine and will use the new DB helpers
    cm = db_find_one('class_memberships', class_id=req.class_id, user_id=current_user['id'])
    
    # Allow admin or HOD to send messages even if not a "member"
    roles = parse_roles_field(current_user.get("roles", []))
    is_admin_or_hod = "admin" in roles or "hod" in roles
    
    if not cm and not is_admin_or_hod:
        raise HTTPException(status_code=403, detail='Not a member of this class')
        
    if not req.is_public:
        if not req.receiver_id:
            raise HTTPException(status_code=400, detail='receiver_id required for private message')
        if 'student' in roles:
            check = db_find_one('class_memberships', class_id=req.class_id, user_id=req.receiver_id)
            if not check or check.get('role') != 'teacher':
                raise HTTPException(status_code=403, detail='Receiver must be a teacher for this class')
                
    db_insert_one('messages', {
        # "id" auto-generated
        'class_id': req.class_id,
        'sender_id': current_user['id'],
        'receiver_id': req.receiver_id if not req.is_public else None,
        'content': req.content,
        'is_public': req.is_public,
        'sent_at': datetime.utcnow()
    })
    return {'message':'sent', 'type': 'public' if req.is_public else 'private'}

@app.get('/api/classes/{class_id}/messages')
@require_any_role('student','sub_teacher','class_teacher','admin', 'teacher', 'hod')
def get_messages(class_id: str, current_user=Depends(get_current_user)):
    cm = db_find_one('class_memberships', class_id=class_id, user_id=current_user['id'])
    
    # Allow admin or HOD to read messages even if not a "member"
    roles = parse_roles_field(current_user.get("roles", []))
    is_admin_or_hod = "admin" in roles or "hod" in roles
    
    if not cm and not is_admin_or_hod:
        raise HTTPException(status_code=403, detail='Not a member')
    
    user_id = current_user['id']
    msgs = db_find_many('messages', class_id=class_id)
    
    # Admins/HODs see all messages
    if is_admin_or_hod:
        return msgs
        
    visible = [m for m in msgs if m.get('is_public') or m.get('sender_id')==user_id or m.get('receiver_id')==user_id]
    return visible

# -------------------------
# REFACTORED: BULK IMPORT
# -------------------------
@app.post('/api/admin/preview-import')
@require_any_role('admin')
def preview_import(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    # This endpoint doesn't touch the DB, so it's fine.
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
    Import students from Excel/CSV.
    Creates them in Firebase Auth and Firestore.
    Format: name, email (password column is ignored)
    """
    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="User not linked to any organization")

    cls_doc = db.collection("classes").document(class_id).get()
    if not cls_doc.exists:
        raise HTTPException(status_code=404, detail="Class not found")
    if cls_doc.to_dict().get("class_teacher_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not allowed to import for this class")

    content = file.file.read()
    try:
        if file.filename.lower().endswith((".xls", ".xlsx")):
            df = pd.read_excel(BytesIO(content))
        else:
            df = pd.read_csv(BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse file: {e}")

    required_columns = {"name", "email"}
    df_cols_lower = set([str(c).lower() for c in df.columns])
    if not required_columns.issubset(df_cols_lower):
        missing = required_columns - df_cols_lower
        raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing)}")

    created = {"new_students": 0, "existing_students": 0, "memberships_added": 0, "errors": []}

    for _, row in df.iterrows():
        try:
            name = str(row.get("name") or row.get("Name") or "").strip()
            email = str(row.get("email") or row.get("Email") or "").strip().lower()
            # password = str(row.get("password") or row.get("Password") or "").strip() # IGNORED

            if not email:
                continue

            existing = get_user_row_by_email(email)
            user_id = None
            if existing:
                user_id = existing["id"]
                roles = parse_roles_field(existing.get("roles"))
                if "student" not in roles:
                    roles.append("student")
                    # --- FIX 1: Removed json.dumps ---
                    db_update_one("users", user_id, {"roles": roles}) 
                created["existing_students"] += 1
            else:
                try:
                    # --- FIX 2: Changed full_name to display_name ---
                    fb_user = auth.create_user(email=email, display_name=name)
                    user_id = fb_user.uid
                except Exception as e:
                    created["errors"].append(f"{email}: Firebase Auth error: {e}")
                    continue
                
                new_student = {
                    "email": email,
                    "full_name": name,
                    "roles": ["student"], # --- FIX 1: Removed json.dumps ---
                    "org_id": org_id,
                }
                db_insert_one("users", new_student, doc_id=user_id)
                created["new_students"] += 1

            # Add class membership
            if not db_find_one("class_memberships", class_id=class_id, user_id=user_id):
                db_insert_one("class_memberships", {
                    "class_id": class_id,
                    "user_id": user_id,
                    "role": "student",
                })
                created["memberships_added"] += 1
        except Exception as e:
            created["errors"].append(f"{email}: {e}")
            continue

    return {"message": "Import completed", "summary": created}

@app.post('/api/admin/import-file')
@require_any_role('admin')
def import_file(
    file: UploadFile = File(...),
    mapping_req: str = Form(...),
    current_user=Depends(get_current_user)
):
    # This is a very complex function. I have adapted it to the new auth/db.
    try:
        mapping_data = json.loads(mapping_req)
    except:
        raise HTTPException(400, "mapping_req must be JSON")

    mapping = mapping_data.get("mapping", {})
    create_departments = mapping_data.get("create_departments", True)
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

    created = {
        "users": 0, "classes": 0, "departments": 0,
        "memberships": 0, "skipped": 0, "errors": []
    }

    # Batch writing for efficiency
    batch = db.batch()
    all_new_user_mappings = {} # email -> uid
    
    # We can't cache locally anymore easily, so we query per row.
    # This will be SLOW but correct.
    for idx, row in df.iterrows():
        try:
            def get_col(key):
                col = mapping.get(key) or key
                if col in row.index:
                    return row.get(col)
                return None

            name = str(get_col('name') or '').strip()
            email = str(get_col('email') or '').strip().lower()
            role = str(get_col('role') or 'student').strip().lower()
            dept_name = str(get_col('department') or '').strip() or None
            class_title = str(get_col('class') or '').strip() or None
            section = str(get_col('section') or '').strip() or None
            # password = IGNORED
            
            if not email:
                created['skipped'] += 1
                continue
                
            existing = get_user_row_by_email(email)
            user_id = None
            if existing:
                user_id = existing['id']
                roles = parse_roles_field(existing.get('roles'))
                if role and role not in roles:
                    roles.append(role)
                    batch.update(db.collection('users').document(user_id), {
                        'full_name': name, 
                        'roles': roles, # --- FIX 1: Removed json.dumps ---
                        'org_id': org_id
                    })
            else:
                if email in all_new_user_mappings:
                    user_id = all_new_user_mappings[email]
                else:
                    try:
                        # --- FIX 2: Changed full_name to display_name ---
                        fb_user = auth.create_user(email=email, display_name=name)
                        user_id = fb_user.uid
                        all_new_user_mappings[email] = user_id
                    except Exception as e:
                        raise Exception(f"Firebase Auth create error: {e}")
                    
                    roles_list = [role] if role else []
                    user_doc_ref = db.collection('users').document(user_id)
                    batch.set(user_doc_ref, {
                        'email': email, 'full_name': name,
                        'roles': roles_list, 'org_id': org_id # --- FIX 1: Removed json.dumps ---
                    })
                    created['users'] += 1
            
            # Department
            dept_id = None
            if dept_name:
                dept = db_find_one('departments', name=dept_name, org_id=org_id)
                if not dept:
                    if create_departments:
                        dept_doc_ref = db.collection('departments').document()
                        dept_id = dept_doc_ref.id
                        batch.set(dept_doc_ref, {'org_id': org_id, 'name': dept_name, 'hod_id': None})
                        created['departments'] += 1
                else:
                    dept_id = dept['id']
            
            # Class
            class_id = None
            if class_title:
                cls = db_find_one('classes', title=class_title, org_id=org_id, department_id=dept_id)
                if not cls:
                    class_doc_ref = db.collection('classes').document()
                    class_id = class_doc_ref.id
                    code = secrets.token_urlsafe(4).upper()
                    batch.set(class_doc_ref, {
                        'org_id': org_id, 'title': class_title,
                        'description': f"Section {section or 'General'}",
                        'department_id': dept_id,
                        'class_teacher_id': user_id if role=='class_teacher' else None,
                        'class_code': code,
                        'section': section
                    })
                    created['classes'] += 1
                else:
                    class_id = cls['id']
            
            # Membership
            if class_id and role in ('student','sub_teacher','class_teacher'):
                mem_role = 'teacher' if role in ('sub_teacher','class_teacher') else 'student'
                if not db_find_one('class_memberships', class_id=class_id, user_id=user_id):
                    mem_doc_ref = db.collection('class_memberships').document()
                    batch.set(mem_doc_ref, {
                        'class_id': class_id, 'user_id': user_id, 'role': mem_role
                    })
                    created['memberships'] += 1
        except Exception as e:
            created['errors'].append({'row': idx, 'error': str(e)})
            continue
            
    # --- Commit all changes at the end ---
    try:
        batch.commit()
    except Exception as e:
        raise HTTPException(500, f"Firestore batch commit error: {e}")
    
    return created

# -------------------------
# HEALTH (Unchanged)
# -------------------------
@app.get('/')
def root():
    return {'message': 'API up and running with Firestore & Firebase Auth'}

# End of file