# # # from fastapi import FastAPI, HTTPException
# # # from fastapi.middleware.cors import CORSMiddleware
# # # from pydantic import BaseModel
# # # from typing import List
# # # import json, uuid, os

# # # app = FastAPI()

# # # app.add_middleware(
# # #     CORSMiddleware,
# # #     allow_origins=["*"],
# # #     allow_methods=["*"],
# # #     allow_headers=["*"]
# # # )

# # # DATA_DIR = "./data"

# # # def load_json(file):
# # #     path = os.path.join(DATA_DIR, file)
# # #     if not os.path.exists(path):
# # #         with open(path, "w") as f:
# # #             json.dump([], f)
# # #     with open(path, "r") as f:
# # #         return json.load(f)

# # # def save_json(file, data):
# # #     path = os.path.join(DATA_DIR, file)
# # #     with open(path, "w") as f:
# # #         json.dump(data, f, indent=4)

# # # # -------------------- MODELS --------------------
# # # class User(BaseModel):
# # #     id: str = None
# # #     name: str
# # #     role: str  # "teacher" or "student"

# # # class Class(BaseModel):
# # #     id: str = None
# # #     name: str
# # #     teacher_id: str
# # #     students: List[str] = []

# # # class Note(BaseModel):
# # #     id: str = None
# # #     class_id: str
# # #     title: str
# # #     content: str

# # # class Assignment(BaseModel):
# # #     id: str = None
# # #     class_id: str
# # #     title: str
# # #     description: str

# # # class Submission(BaseModel):
# # #     id: str = None
# # #     assignment_id: str
# # #     student_id: str
# # #     content: str

# # # class Message(BaseModel):
# # #     id: str = None
# # #     class_id: str
# # #     user_id: str
# # #     content: str

# # # # -------------------- USERS --------------------
# # # @app.get("/users")
# # # def get_users():
# # #     return load_json("users.json")

# # # @app.post("/users")
# # # def create_user(user: User):
# # #     users = load_json("users.json")
# # #     user.id = str(uuid.uuid4())
# # #     users.append(user.dict())
# # #     save_json("users.json", users)
# # #     return user

# # # @app.get("/users/{user_id}")
# # # def get_user(user_id: str):
# # #     users = load_json("users.json")
# # #     for u in users:
# # #         if u["id"] == user_id:
# # #             return u
# # #     raise HTTPException(404, "User not found")

# # # # -------------------- CLASSES --------------------
# # # @app.post("/classes")
# # # def create_class(cls: Class):
# # #     classes = load_json("classes.json")
# # #     cls.id = str(uuid.uuid4())
# # #     classes.append(cls.dict())
# # #     save_json("classes.json", classes)
# # #     return cls

# # # @app.get("/classes/{class_id}")
# # # def get_class(class_id: str):
# # #     classes = load_json("classes.json")
# # #     for c in classes:
# # #         if c["id"] == class_id:
# # #             return c
# # #     raise HTTPException(404, "Class not found")

# # # @app.get("/users/{user_id}/classes")
# # # def get_user_classes(user_id: str):
# # #     classes = load_json("classes.json")
# # #     return [c for c in classes if user_id == c["teacher_id"] or user_id in c["students"]]

# # # @app.post("/classes/{class_id}/join/{user_id}")
# # # def join_class(class_id: str, user_id: str):
# # #     classes = load_json("classes.json")
# # #     for c in classes:
# # #         if c["id"] == class_id:
# # #             if user_id not in c["students"]:
# # #                 c["students"].append(user_id)
# # #                 save_json("classes.json", classes)
# # #             return c
# # #     raise HTTPException(404, "Class not found")

# # # # -------------------- NOTES --------------------
# # # @app.post("/classes/{class_id}/notes")
# # # def add_note(class_id: str, note: Note):
# # #     notes = load_json("notes.json")
# # #     note.id = str(uuid.uuid4())
# # #     note.class_id = class_id
# # #     notes.append(note.dict())
# # #     save_json("notes.json", notes)
# # #     return note

# # # @app.get("/classes/{class_id}/notes")
# # # def get_notes(class_id: str):
# # #     notes = load_json("notes.json")
# # #     return [n for n in notes if n["class_id"] == class_id]

# # # # -------------------- ASSIGNMENTS --------------------
# # # @app.post("/classes/{class_id}/assignments")
# # # def add_assignment(class_id: str, assignment: Assignment):
# # #     assignments = load_json("assignments.json")
# # #     assignment.id = str(uuid.uuid4())
# # #     assignment.class_id = class_id
# # #     assignments.append(assignment.dict())
# # #     save_json("assignments.json", assignments)
# # #     return assignment

# # # @app.get("/classes/{class_id}/assignments")
# # # def get_assignments(class_id: str):
# # #     assignments = load_json("assignments.json")
# # #     return [a for a in assignments if a["class_id"] == class_id]

# # # # -------------------- SUBMISSIONS --------------------
# # # @app.post("/assignments/{assignment_id}/submit")
# # # def submit_assignment(assignment_id: str, submission: Submission):
# # #     submissions = load_json("submissions.json")
# # #     submission.id = str(uuid.uuid4())
# # #     submission.assignment_id = assignment_id
# # #     submissions.append(submission.dict())
# # #     save_json("submissions.json", submissions)
# # #     return submission

# # # @app.get("/assignments/{assignment_id}/submissions")
# # # def get_submissions(assignment_id: str):
# # #     submissions = load_json("submissions.json")
# # #     return [s for s in submissions if s["assignment_id"] == assignment_id]

# # # # -------------------- MESSAGES --------------------
# # # @app.post("/classes/{class_id}/messages")
# # # def add_message(class_id: str, message: Message):
# # #     messages = load_json("messages.json")
# # #     message.id = str(uuid.uuid4())
# # #     message.class_id = class_id
# # #     messages.append(message.dict())
# # #     save_json("messages.json", messages)
# # #     return message

# # # @app.get("/classes/{class_id}/messages")
# # # def get_messages(class_id: str):
# # #     messages = load_json("messages.json")
# # #     return [m for m in messages if m["class_id"] == class_id]



# # from fastapi import FastAPI
# # from fastapi.middleware.cors import CORSMiddleware
# # from routes import users, classes, notes, assignments, submissions, messages
# # import os


# # app = FastAPI(
# #     title="Classroom API",
# #     description="Backend with Supabase + FastAPI + SQLAlchemy",
# #     version="1.0.0"
# # )

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #        allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # # Ensure data directory exists
# # # os.makedirs("data", exist_ok=True)

# # # Include routers
# # app.include_router(users.router)
# # app.include_router(classes.router)
# # app.include_router(notes.router)
# # app.include_router(assignments.router)
# # app.include_router(submissions.router)
# # app.include_router(messages.router)



# # # import requests
# # # import json

# # # # Replace with your Supabase project info
# # # SUPABASE_URL = os.getenv("SUPABASE_URL")
# # # SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# # # # Example table: users
# # # table_name = "users"

# # # # Fake user data
# # # user_data = {
    
# # #     "name": "John hshsaadithya Doe",
# # #     "email": "john@example.com",
# # #      "password": "mypassword"
# # # }

# # # # REST API endpoint for the table
# # # url = f"{SUPABASE_URL}/{table_name}"

# # # # Headers
# # # headers = {
# # #     "apikey": SUPABASE_KEY,
# # #     "Authorization": f"Bearer {SUPABASE_KEY}",
# # #     "Content-Type": "application/json",
# # #     "Prefer": "return=representation"  # to get the inserted row back
# # # }

# # # # Make POST request
# # # response = requests.post(url, headers=headers, data=json.dumps(user_data))

# # # # Check result
# # # if response.status_code in [200, 201]:
# # #     print("Inserted successfully:", response.json())
# # # else:
# # #     print("Error:", response.status_code, response.text)





# #new one 

# # app/main.py (single-file preview - secure role hierarchy updated per user's new rules)
# # Run with: SUPABASE_URL, SUPABASE_KEY, OWNER_EMAIL set in env

# from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File
# from pydantic import BaseModel, EmailStr
# from typing import Optional, List
# from supabase import create_client
# import os
# import secrets
# from datetime import datetime
# from functools import wraps
# import json

# # --------------------------
# # Configuration / DB client
# # --------------------------
# # SUPABASE_URL = os.getenv('SUPABASE_URL')
# # SUPABASE_KEY = os.getenv('SUPABASE_KEY')
# # OWNER_EMAIL = os.getenv('OWNER_EMAIL')
# SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFwdXlwdHhsaHlubWx2ZXRlcGFoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTMxNzQwMiwiZXhwIjoyMDc2ODkzNDAyfQ.mXqjdeRRJvZBhwbZNxtp6x-YylykL4Yq7azG9QYP_3c"
# SUPABASE_URL="https://qpuyptxlhynmlvetepah.supabase.co"  
# OWNER_EMAIL="aadithyanayakv07@gmail.com"
# print("SUPABASE_URL:", SUPABASE_URL)
# print("SUPABASE_KEY:", SUPABASE_KEY)
# print("OWNER_EMAIL:", OWNER_EMAIL)

# if not SUPABASE_URL or not SUPABASE_KEY:
#     raise RuntimeError('Set SUPABASE_URL and SUPABASE_KEY env vars')
# if not OWNER_EMAIL:
#     raise RuntimeError('Set OWNER_EMAIL env var (app owner email)')

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# # --------------------------
# # Helper utilities
# # --------------------------
# def get_user_row(user_id: str):
#     r = supabase.table('users').select('*').eq('id', user_id).single().execute()
#     return r.data if getattr(r, 'status_code', None) in (200, 201) else None

# def get_user_row_by_email(email: str):
#     r = supabase.table('users').select('*').eq('email', email).single().execute()
#     return r.data if getattr(r, 'status_code', None) in (200,201) else None

# def has_role(user_row, role: str) -> bool:
#     # roles stored as JSON array in 'roles' column
#     roles = user_row.get('roles') or []
#     return role in roles

# # --------------------------
# # Pydantic models
# # --------------------------
# class LoginReq(BaseModel):
#     email: EmailStr
#     password: str

# class CreateOrg(BaseModel):
#     name: str

# class AddUserReq(BaseModel):
#     email: EmailStr
#     full_name: str

# class CreateClassReq(BaseModel):
#     org_id: str
#     title: str
#     description: Optional[str] = None

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
#     file_path: str

# class FinalMarkReq(BaseModel):
#     org_id: str
#     student_id: str
#     subject_name: str
#     unit_name: str
#     marks: float

# class MessageReq(BaseModel):
#     class_id: str
#     receiver_id: str
#     content: str
#     is_public: Optional[bool] = False 

# # --------------------------
# # Auth dependency (validate Supabase token)
# # --------------------------
# from fastapi import Security

# def get_current_user(authorization: Optional[str] = Header(None)):
#     if not authorization:
#         raise HTTPException(status_code=401, detail='Missing Authorization header')
#     if not authorization.startswith('Bearer '):
#         raise HTTPException(status_code=401, detail='Invalid Authorization header')
#     token = authorization.split(' ',1)[1]
#     try:
#         user_resp = supabase.auth.get_user(token=token)
#     except Exception:
#         raise HTTPException(status_code=401, detail='Invalid token')

#     user_obj = None
#     try:
#         user_obj = user_resp.data.user if hasattr(user_resp, 'data') and user_resp.data else None
#     except Exception:
#         user_obj = None
#     if not user_obj:
#         if isinstance(user_resp, dict) and user_resp.get('user'):
#             user_obj = user_resp['user']
#     if not user_obj:
#         raise HTTPException(status_code=401, detail='Unauthorized')

#     app_user = get_user_row(user_obj.id)
#     if not app_user:
#         # In this design there is NO public signup; owner/admin/class-teacher create users.
#         raise HTTPException(status_code=403, detail='User not registered in app DB')
#     return app_user

# # --------------------------
# # Role guard helpers (supports multiple roles per user)
# # --------------------------
# def require_any_role(*roles):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
#             user_roles = current_user.get('roles') or []
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

# # --------------------------
# # FastAPI app & routes
# # --------------------------
# app = FastAPI(title='Classroom Supabase Backend - Roles as list (owner/admin/class_teacher/sub_teacher/student)')

# # ---------- AUTH (no public register) ----------
# @app.post('/api/auth/login')
# def login(req: LoginReq):
#     # login with email/password (accounts are created by owner/admin/teachers)
#     try:
#         signin = supabase.auth.sign_in_with_password({ 'email': req.email, 'password': req.password })
#     except Exception:
#         raise HTTPException(status_code=401, detail='Invalid credentials')
#     token = None
#     try:
#         token = signin.session.access_token
#     except Exception:
#         token = signin.get('access_token') if isinstance(signin, dict) else None
#     if not token:
#         raise HTTPException(status_code=401, detail='Login failed')
#     return { 'access_token': token }

# # ---------- ORG / OWNER ----------
# @app.post('/api/orgs')
# @require_owner
# def create_org(req: CreateOrg, current_user=Depends(get_current_user)):
#     r = supabase.table('organizations').insert({ 'name': req.name }).execute()
#     if getattr(r, 'status_code', None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to create org')
#     return r.data[0]

# # Owner creates Admin for org
# @app.post('/api/orgs/{org_id}/admin/create')
# @require_owner
# def create_admin(org_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
#     # create auth user and app user with admin role attached to org
#     try:
#         signup = supabase.auth.sign_up({ 'email': payload.email, 'password': secrets.token_urlsafe(12) })
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f'Auth error: {e}')
#     user_id = None
#     try:
#         user_id = signup.data.user.id
#     except Exception:
#         if isinstance(signup, dict) and signup.get('user'):
#             user_id = signup['user']['id']
#     if not user_id:
#         raise HTTPException(status_code=500, detail='Failed to create auth admin user')
#     res = supabase.table('users').insert({
#         'id': user_id,
#         'email': payload.email,
#         'full_name': payload.full_name,
#         'roles': json.dumps(['admin']),
#         'org_id': org_id
#     }).execute()
#     if getattr(res, 'status_code', None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to create admin record')
#     return {'message':'admin created', 'user_id': user_id}

# # ---------- Admin actions (manage class teachers) ----------
# @app.post('/api/orgs/{org_id}/teachers/create')
# @require_any_role('admin')
# def create_class_teacher(org_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
#     if current_user.get('org_id') != org_id:
#         raise HTTPException(status_code=403, detail='Not your org')
#     try:
#         signup = supabase.auth.sign_up({ 'email': payload.email, 'password': secrets.token_urlsafe(10) })
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f'Auth error: {e}')
#     user_id = None
#     try:
#         user_id = signup.data.user.id
#     except Exception:
#         if isinstance(signup, dict) and signup.get('user'):
#             user_id = signup['user']['id']
#     if not user_id:
#         raise HTTPException(status_code=500, detail='Failed to create class teacher')
#     r = supabase.table('users').insert({
#         'id': user_id,
#         'email': payload.email,
#         'full_name': payload.full_name,
#         'roles': json.dumps(['class_teacher']),
#         'org_id': org_id
#     }).execute()
#     if getattr(r, 'status_code', None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to create class teacher record')
#     return {'message':'class teacher created', 'user_id': user_id}

# @app.delete('/api/orgs/{org_id}/teachers/{teacher_id}')
# @require_any_role('admin')
# def delete_class_teacher(org_id: str, teacher_id: str, current_user=Depends(get_current_user)):
#     if current_user.get('org_id') != org_id:
#         raise HTTPException(status_code=403, detail='Not your org')
#     supabase.table('users').delete().eq('id', teacher_id).eq('org_id', org_id).execute()
#     return {'message':'deleted teacher if existed'}

# # ---------- CLASS TEACHER -> add sub teacher (sub_teacher can create assignments/grade)
# @app.post('/api/teachers/add-sub')
# @require_any_role('class_teacher','admin')
# def add_sub_teacher(payload: AddUserReq, current_user=Depends(get_current_user)):
#     org_id = current_user.get('org_id')
#     try:
#         signup = supabase.auth.sign_up({ 'email': payload.email, 'password': secrets.token_urlsafe(10) })
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f'Auth error: {e}')
#     user_id = None
#     try:
#         user_id = signup.data.user.id
#     except Exception:
#         if isinstance(signup, dict) and signup.get('user'):
#             user_id = signup['user']['id']
#     if not user_id:
#         raise HTTPException(status_code=500, detail='Failed to create sub teacher')
#     supabase.table('users').insert({
#         'id': user_id,
#         'email': payload.email,
#         'full_name': payload.full_name,
#         'roles': json.dumps(['sub_teacher']),
#         'org_id': org_id
#     }).execute()
#     supabase.table('teacher_hierarchy').insert({
#         'org_id': org_id,
#         'class_teacher_id': current_user['id'],
#         'sub_teacher_id': user_id
#     }).execute()
#     return {'message':'sub teacher added', 'user_id': user_id}

# # ---------- CLASSES ----------
# @app.post('/api/classes')
# @require_any_role('sub_teacher','class_teacher')
# def create_class(req: CreateClassReq, current_user=Depends(get_current_user)):
#     for _ in range(5):
#         code = secrets.token_urlsafe(4).upper()
#         q = supabase.table('classes').select('id').eq('class_code', code).execute()
#         if getattr(q,'status_code',None) == 200 and not q.data:
#             break
#     ct_id = None
#     if 'sub_teacher' in (current_user.get('roles') or []):
#         h = supabase.table('teacher_hierarchy').select('class_teacher_id').eq('sub_teacher_id', current_user['id']).single().execute()
#         if getattr(h,'data',None):
#             ct_id = h.data.get('class_teacher_id')
#     elif 'class_teacher' in (current_user.get('roles') or []):
#         ct_id = current_user['id']
#     body = {
#         'org_id': req.org_id,
#         'title': req.title,
#         'description': req.description,
#         'created_by': current_user['id'],
#         'class_teacher_id': ct_id,
#         'class_code': code
#     }
#     r = supabase.table('classes').insert(body).execute()
#     if getattr(r,'status_code',None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to create class')
#     try:
#         supabase.table('class_memberships').insert({'class_id': r.data[0]['id'], 'user_id': current_user['id'], 'role': 'teacher'}).execute()
#     except Exception:
#         pass
#     return r.data[0]

# # Students join via code; users are created by owner/admin/class-teacher so no public signup
# @app.post('/api/classes/join')
# @require_any_role('none','student')
# def join_class(req: JoinClassReq, current_user=Depends(get_current_user)):
#     q = supabase.table('classes').select('id, org_id').eq('class_code', req.class_code).single().execute()
#     if not getattr(q,'data',None):
#         raise HTTPException(status_code=404, detail='Class not found')
#     class_id = q.data['id']
#     org_id = q.data['org_id']
#     # if the user has no student role, add it
#     roles = json.loads(current_user.get('roles') or '[]') if isinstance(current_user.get('roles'), str) else (current_user.get('roles') or [])
#     if 'student' not in roles:
#         roles.append('student')
#         supabase.table('users').update({'roles': json.dumps(roles), 'org_id': org_id}).eq('id', current_user['id']).execute()
#     supabase.table('class_memberships').insert({'class_id': class_id, 'user_id': current_user['id'], 'role': 'student'}).execute()
#     return {'message': 'joined'}

# @app.delete('/api/classes/{class_id}')
# @require_any_role('sub_teacher','class_teacher','admin')
# def delete_class(class_id: str, current_user=Depends(get_current_user)):
#     c = supabase.table('classes').select('created_by, class_teacher_id, org_id').eq('id', class_id).single().execute()
#     if not getattr(c,'data',None):
#         raise HTTPException(status_code=404, detail='Class not found')
#     allowed = False
#     # admin of same org can delete
#     if 'admin' in (current_user.get('roles') or []) and current_user.get('org_id') == c.data.get('org_id'):
#         allowed = True
#     if c.data.get('created_by') == current_user['id']:
#         allowed = True
#     if c.data.get('class_teacher_id') == current_user['id']:
#         allowed = True
#     if not allowed:
#         raise HTTPException(status_code=403, detail='Not allowed to delete this class')
#     supabase.table('classes').delete().eq('id', class_id).execute()
#     return {'message':'deleted'}

# # ---------- ASSIGNMENTS (only sub_teacher or any user that has 'sub_teacher' role can create/upload/grade)
# @app.post('/api/assignments')
# @require_any_role('sub_teacher')
# def create_assignment(req: CreateAssignmentReq, current_user=Depends(get_current_user)):
#     cm = supabase.table('class_memberships').select('role').eq('class_id', req.class_id).eq('user_id', current_user['id']).single().execute()
#     if not getattr(cm,'data',None) or cm.data.get('role') != 'teacher':
#         raise HTTPException(status_code=403, detail='Only the subject teacher can create assignments for this class')
#     if req.assignment_type not in ('file','text','mixed'):
#         raise HTTPException(status_code=400, detail='Invalid assignment_type')
#     body = {'class_id': req.class_id, 'created_by': current_user['id'], 'title': req.title, 'description': req.description, 'due_at': req.due_at, 'assignment_type': req.assignment_type}
#     r = supabase.table('assignments').insert(body).execute()
#     if getattr(r,'status_code',None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to create assignment')
#     return r.data[0]

# @app.post('/api/assignments/{assignment_id}/upload-file')
# @require_any_role('sub_teacher')
# def upload_assignment_file(assignment_id: str, file: UploadFile = File(...), current_user=Depends(get_current_user)):
#     a = supabase.table('assignments').select('class_id, created_by').eq('id', assignment_id).single().execute()
#     if not getattr(a,'data',None):
#         raise HTTPException(status_code=404, detail='Assignment not found')
#     cm = supabase.table('class_memberships').select('role').eq('class_id', a.data['class_id']).eq('user_id', current_user['id']).single().execute()
#     if not getattr(cm,'data',None) or cm.data.get('role') != 'teacher':
#         raise HTTPException(status_code=403, detail='Only subject teacher can upload file for this assignment')
#     bucket = 'assignments'
#     filename = f"{assignment_id}/{secrets.token_hex(8)}_{file.filename}"
#     try:
#         content = file.file.read()
#         supabase.storage.from_(bucket).upload(filename, content)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f'Upload failed: {e}')
#     file_path = f"{bucket}/{filename}"
#     supabase.table('assignments').update({'file_path': file_path}).eq('id', assignment_id).execute()
#     return {'message':'file uploaded', 'file_path': file_path}

# @app.get('/api/classes/{class_id}/assignments')
# def list_assignments(class_id: str, current_user=Depends(get_current_user)):
#     m = supabase.table('class_memberships').select('*').eq('class_id', class_id).eq('user_id', current_user['id']).single().execute()
#     if not getattr(m,'data',None):
#         raise HTTPException(status_code=403, detail='Not a member of class')
#     r = supabase.table('assignments').select('*').eq('class_id', class_id).execute()
#     # note: class_teacher role is allowed to view assignments if they are a member too; but per rules class_teacher usually shouldn't create them
#     return r.data

# # ---------- SUBMISSIONS (students only)
# @app.post('/api/submissions')
# @require_any_role('student')
# def submit_assignment(file: Optional[UploadFile] = File(None), payload: Optional[SubmitReq] = None, current_user=Depends(get_current_user)):
#     if payload is None and not file:
#         raise HTTPException(status_code=400, detail='No submission data')
#     assignment_id = payload.assignment_id if payload else None
#     if not assignment_id:
#         raise HTTPException(status_code=400, detail='assignment_id required')
#     a = supabase.table('assignments').select('class_id, assignment_type').eq('id', assignment_id).single().execute()
#     if not getattr(a,'data',None):
#         raise HTTPException(status_code=404, detail='Assignment not found')
#     class_id = a.data['class_id']
#     cm = supabase.table('class_memberships').select('*').eq('class_id', class_id).eq('user_id', current_user['id']).single().execute()
#     if not getattr(cm,'data',None):
#         raise HTTPException(status_code=403, detail='Not a member of class')
#     file_path = None
#     text_content = None
#     if file:
#         bucket = 'submissions'
#         filename = f"{assignment_id}/{current_user['id']}/{secrets.token_hex(8)}_{file.filename}"
#         content = file.file.read()
#         try:
#             supabase.storage.from_(bucket).upload(filename, content)
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f'Upload failed: {e}')
#         file_path = f"{bucket}/{filename}"
#     if payload and payload.text_content:
#         text_content = payload.text_content
#     existing = supabase.table('submissions').select('*').eq('assignment_id', assignment_id).eq('student_id', current_user['id']).single().execute()
#     if getattr(existing,'data',None):
#         supabase.table('submissions').update({'text_content': text_content, 'file_path': file_path, 'submitted_at': datetime.utcnow()}).eq('id', existing.data['id']).execute()
#         return {'message':'updated submission'}
#     r = supabase.table('submissions').insert({'assignment_id': assignment_id, 'student_id': current_user['id'], 'text_content': text_content, 'file_path': file_path}).execute()
#     if getattr(r,'status_code',None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to submit')
#     return r.data[0]

# @app.get('/api/assignments/{assignment_id}/submissions')
# @require_any_role('sub_teacher')
# def get_submissions(assignment_id: str, current_user=Depends(get_current_user)):
#     a = supabase.table('assignments').select('class_id, created_by').eq('id', assignment_id).single().execute()
#     if not getattr(a,'data',None):
#         raise HTTPException(status_code=404, detail='Assignment not found')
#     class_id = a.data['class_id']
#     cm = supabase.table('class_memberships').select('*').eq('class_id', class_id).eq('user_id', current_user['id']).single().execute()
#     is_teacher = getattr(cm,'data',None) and cm.data.get('role') == 'teacher'
#     cls = supabase.table('classes').select('class_teacher_id').eq('id', class_id).single().execute()
#     is_supervisor = getattr(cls,'data',None) and cls.data.get('class_teacher_id') == current_user['id']
#     # Only sub_teacher who is subject teacher or class_teacher who is also marked as teacher can view
#     if not (is_teacher or is_supervisor):
#         raise HTTPException(status_code=403, detail='Not allowed')
#     r = supabase.table('submissions').select('*').eq('assignment_id', assignment_id).execute()
#     return r.data

# @app.post('/api/submissions/{submission_id}/grade')
# @require_any_role('sub_teacher')
# def grade_submission(submission_id: str, grade: float, current_user=Depends(get_current_user)):
#     s = supabase.table('submissions').select('assignment_id, student_id').eq('id', submission_id).single().execute()
#     if not getattr(s,'data',None):
#         raise HTTPException(status_code=404, detail='Submission not found')
#     assignment = supabase.table('assignments').select('class_id').eq('id', s.data['assignment_id']).single().execute()
#     class_id = assignment.data['class_id']
#     cm = supabase.table('class_memberships').select('*').eq('class_id', class_id).eq('user_id', current_user['id']).single().execute()
#     if not (getattr(cm,'data',None) and cm.data.get('role') == 'teacher'):
#         raise HTTPException(status_code=403, detail='Only the subject teacher can grade submissions')
#     supabase.table('submissions').update({'grade': grade, 'graded_by': current_user['id']}).eq('id', submission_id).execute()
#     return {'message':'graded'}

# # ---------- NOTES ----------
# @app.post('/api/notes')
# @require_any_role('sub_teacher')
# def upload_note(req: NoteCreateReq, current_user=Depends(get_current_user)):
#     cm = supabase.table('class_memberships').select('role').eq('class_id', req.class_id).eq('user_id', current_user['id']).single().execute()
#     if not getattr(cm,'data',None) or cm.data.get('role') != 'teacher':
#         raise HTTPException(status_code=403, detail='Only subject teacher can upload notes')
#     r = supabase.table('notes').insert({'class_id': req.class_id, 'uploaded_by': current_user['id'], 'title': req.title, 'file_path': req.file_path}).execute()
#     if getattr(r,'status_code',None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to upload note')
#     return r.data[0]

# @app.get('/api/classes/{class_id}/notes')
# def list_notes(class_id: str, current_user=Depends(get_current_user)):
#     cm = supabase.table('class_memberships').select('*').eq('class_id', class_id).eq('user_id', current_user['id']).single().execute()
#     if not getattr(cm,'data',None):
#         raise HTTPException(status_code=403, detail='Not a member')
#     r = supabase.table('notes').select('*').eq('class_id', class_id).execute()
#     return r.data

# # ---------- FINAL MARKS ----------
# # Only users with role 'sub_teacher' (subject teachers) can add marks. Class teachers can only view grades for classes under them.
# @app.post('/api/finalmarks')
# @require_any_role('sub_teacher')
# def upload_final_marks(req: FinalMarkReq, current_user=Depends(get_current_user)):
#     stu = get_user_row(req.student_id)
#     if not stu:
#         raise HTTPException(status_code=404, detail='Student not found')
#     body = req.dict()
#     body['uploaded_by'] = current_user['id']
#     r = supabase.table('final_marks').insert(body).execute()
#     if getattr(r,'status_code',None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to upload final marks')
#     return {'message':'uploaded'}

# # View grades: class_teacher can view grades of classes under her; admin can view grades if they have org access; sub_teacher can view grades for classes they teach
# @app.get('/api/orgs/{org_id}/grades')
# @require_any_role('class_teacher','admin','sub_teacher')
# def view_all_grades(org_id: str, current_user=Depends(get_current_user)):
#     # if class_teacher, restrict to classes where she is class_teacher
#     roles = current_user.get('roles') or []
#     if 'class_teacher' in roles:
#         # find classes where this user is class_teacher and org matches
#         classes = supabase.table('classes').select('id').eq('class_teacher_id', current_user['id']).eq('org_id', org_id).execute()
#         class_ids = [c['id'] for c in (classes.data or [])]
#         if not class_ids:
#             return []
#         r = supabase.table('final_marks').select('*').in_('class_id', class_ids).execute()
#         return r.data
#     # admin of org can view all grades
#     if 'admin' in roles and current_user.get('org_id') == org_id:
#         r = supabase.table('final_marks').select('*').eq('org_id', org_id).execute()
#         return r.data
#     # sub_teacher: show marks for classes they belong to as teacher
#     if 'sub_teacher' in roles:
#         cm = supabase.table('class_memberships').select('class_id').eq('user_id', current_user['id']).eq('role', 'teacher').execute()
#         class_ids = [c['class_id'] for c in (cm.data or [])]
#         if not class_ids:
#             return []
#         r = supabase.table('final_marks').select('*').in_('class_id', class_ids).execute()
#         return r.data
#     raise HTTPException(status_code=403, detail='Not allowed')

# # ---------- MESSAGES (private student <-> sub teacher) ----------
# @app.post('/api/messages')
# @require_any_role('student','sub_teacher','class_teacher')
# def send_message(req: MessageReq, current_user=Depends(get_current_user)):
#     # Step 1: Check that user belongs to this class
#     cm = supabase.table('class_memberships').select('*')\
#         .eq('class_id', req.class_id).eq('user_id', current_user['id']).single().execute()
#     if not getattr(cm, 'data', None):
#         raise HTTPException(status_code=403, detail='Not a member of this class')

#     # Step 2: Handle private vs public
#     if not req.is_public:
#         # Private message (requires receiver_id)
#         if not req.receiver_id:
#             raise HTTPException(status_code=400, detail='receiver_id required for private message')
#         # Student can only message teachers
#         if 'student' in (current_user.get('roles') or []):
#             check = supabase.table('class_memberships').select('*')\
#                 .eq('class_id', req.class_id).eq('user_id', req.receiver_id).single().execute()
#             if not getattr(check, 'data', None) or check.data.get('role') != 'teacher':
#                 raise HTTPException(status_code=403, detail='Receiver must be a teacher for this class')

#     # Step 3: Insert message
#     supabase.table('messages').insert({
#         'class_id': req.class_id,
#         'sender_id': current_user['id'],
#         'receiver_id': req.receiver_id if not req.is_public else None,
#         'content': req.content,
#         'is_public': req.is_public
#     }).execute()

#     return {'message': 'sent', 'type': 'public' if req.is_public else 'private'}

# @app.get('/api/classes/{class_id}/messages')
# @require_any_role('student','sub_teacher','class_teacher')
# def get_messages(class_id: str, current_user=Depends(get_current_user)):
#     # Must belong to the class
#     cm = supabase.table('class_memberships').select('*')\
#         .eq('class_id', class_id).eq('user_id', current_user['id']).single().execute()
#     if not getattr(cm, 'data', None):
#         raise HTTPException(status_code=403, detail='Not a member')

#     user_id = current_user['id']

#     # Show all public messages + private ones where user is involved
#     r = supabase.table('messages').select('*').eq('class_id', class_id)\
#         .or_(f"(is_public.eq.true),(sender_id.eq.{user_id}),(receiver_id.eq.{user_id})").execute()

#     return r.data

# # ---------- HEALTH ----------
# @app.get('/')
# def root():
#     return {'message':'API up'}

# # --------------------------
# # Notes & next steps
# # --------------------------
# # - Key model change: users now have a 'roles' JSON array instead of a single global_role string.
# # - No public signup: Owner/Admin/ClassTeacher create users by email. When created they get initial roles assigned.
# # - Role semantics:
# #     * owner: app owner (env var) - creates orgs and admins
# #     * admin: org admin - manages class_teachers; does NOT create assignments unless also granted sub_teacher role
# #     * class_teacher: managerial role - can view grades for classes under her and manage sub-teachers
# #     * sub_teacher: operational teacher - can create classes, assignments, upload notes, grade students
# #     * student: can join classes and submit assignments
# # - Roles are additive (a user can be both admin & sub_teacher etc). Endpoints check for required roles explicitly.
# # - You should add DB migrations to change 'global_role' -> 'roles' (JSON) and update existing rows.
# # - Next I can: 1) update the canvas file to include migrations & DDL, 2) split into routers, 3) generate RLS policies, or 4) produce curl/Postman flows demonstrating owner->create admin->create class_teacher->add sub_teacher->create class->student join->assignment->grade. 


# # app/main.py
# """
# Complete single-file FastAPI backend for Classroom app (Supabase).
# Features:
# - Owner / Admin / ClassTeacher / SubTeacher / Student roles (roles stored as JSON array)
# - Optional Departments for every org (school, college, university)
# - Manual flows: create org, create admin, create teachers, create dept, create classes
# - Assignments (create, upload file), Submissions (file/text), grade submissions
# - Notes upload/list
# - Final marks upload / view (with role-based restrictions)
# - Messages: public (to class) + private
# - Bulk import: preview and import Excel/CSV with column mapping (pandas)
# - OpenAPI "Authorize" (Bearer) support for docs
# - Supabase Auth used for login / token validation
# Make sure you created DB tables (DDL provided in prior messages) and storage buckets:
# assignments, submissions, notes
# """
# from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File, Body, Query
# from fastapi.responses import JSONResponse
# from fastapi.openapi.utils import get_openapi
# from pydantic import BaseModel, EmailStr
# from typing import Optional, List, Dict, Any
# from supabase import create_client
# from dotenv import load_dotenv
# import os, secrets, json
# from datetime import datetime
# from functools import wraps
# from io import BytesIO
# import pandas as pd

# # -------------------------
# # Load env
# # -------------------------
# load_dotenv()
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# OWNER_EMAIL = os.getenv("OWNER_EMAIL")
# DEFAULT_ORG_TYPE = os.getenv("DEFAULT_ORG_TYPE", "school")

# if not SUPABASE_URL or not SUPABASE_KEY:
#     raise RuntimeError("Set SUPABASE_URL and SUPABASE_KEY in environment")
# if not OWNER_EMAIL:
#     raise RuntimeError("Set OWNER_EMAIL in environment")

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# # -------------------------
# # Helpers
# # -------------------------
# def _data(resp):
#     return getattr(resp, "data", None)

# def parse_roles_field(roles_field: Any) -> List[str]:
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
#     r = supabase.table('users').select('*').eq('id', user_id).single().execute()
#     return _data(r)

# def get_user_row_by_email(email: str):
#     if not email:
#         return None
#     r = supabase.table('users').select('*').eq('email', email).single().execute()
#     return _data(r)

# def org_has_departments(org_id: str) -> bool:
#     r = supabase.table('organizations').select('org_type').eq('id', org_id).single().execute()
#     d = _data(r)
#     if not d:
#         return False
#     return d.get('org_type') in ('college', 'university')  # treat both as having departments

# # -------------------------
# # Pydantic models
# # -------------------------
# class LoginReq(BaseModel):
#     email: EmailStr
#     password: str

# class CreateOrgReq(BaseModel):
#     name: str
#     org_type: Optional[str] = None  # school / college / university

# class AddUserReq(BaseModel):
#     email: EmailStr
#     full_name: Optional[str] = None
#     roles: Optional[List[str]] = None
#     password: str

# class CreateDeptReq(BaseModel):
#     org_id: str
#     name: str
#     hod_id: Optional[str] = None

# class CreateClassReq(BaseModel):
#     org_id: str
#     title: str
#     description: Optional[str] = None
#     department_id: Optional[str] = None

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
#     file_path: str

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
#     # mapping maps our internal keys to column names in the file
#     # e.g. {"name":"Full Name","email":"Email ID","role":"Role","department":"Dept","class":"Class Title","section":"Section","password":"Pwd"}
#     mapping: Dict[str, str]
#     create_departments: Optional[bool] = True

# # -------------------------
# # Auth dependency + guards
# # -------------------------
# def get_current_user(authorization: Optional[str] = Header(None)):
#     if not authorization:
#         raise HTTPException(status_code=401, detail='Missing Authorization header')
#     if not authorization.startswith('Bearer '):
#         raise HTTPException(status_code=401, detail='Invalid Authorization header')
#     token = authorization.split(' ',1)[1]
#     try:
#         user_resp = supabase.auth.get_user(token=token)
#     except Exception as e:
#         raise HTTPException(status_code=401, detail=f'Invalid token: {e}')
#     # support multiple response shapes
#     user_obj = None
#     try:
#         user_obj = user_resp.user if getattr(user_resp, 'user', None) else None
#     except Exception:
#         user_obj = None
#     try:
#         if not user_obj and getattr(user_resp, 'data', None):
#             user_obj = user_resp.data.user if getattr(user_resp.data, 'user', None) else None
#     except Exception:
#         pass
#     if not user_obj and isinstance(user_resp, dict) and user_resp.get('user'):
#         user_obj = user_resp.get('user')
#     if not user_obj:
#         raise HTTPException(status_code=401, detail='Unauthorized')
#     app_user = get_user_row(user_obj.id)
#     if not app_user:
#         # enforced: no public signup
#         raise HTTPException(status_code=403, detail='User not registered in app DB')
#     return app_user

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
# # App & OpenAPI security
# # -------------------------
# app = FastAPI(title="Classroom Backend (Single-file, Full)")
# from fastapi.middleware.cors import CORSMiddleware

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",   # your React dev server
#         "http://127.0.0.1:5173",   # some browsers use this
#     ],
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
# # AUTH (login only; no public register)
# # -------------------------


# @app.post("/api/users/create")
# @require_any_role("admin", "class_teacher", "sub_teacher")
# def create_user(payload: AddUserReq, current_user=Depends(get_current_user)):
#     """
#     Create a new user (teacher/student/etc.)
#     Automatically creates Supabase Auth account and internal user record.
#     """
#     org_id = current_user.get("org_id")
#     if not org_id:
#         raise HTTPException(status_code=400, detail="You must belong to an organization")

#     # Create Supabase Auth account
#     try:
#         signup = supabase.auth.sign_up({
#             "email": payload.email,
#             "password": payload.password
#         })
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Auth creation failed: {e}")

#     # Get Supabase Auth user ID
#     user_id = None
#     try:
#         user_id = signup.user.id
#     except Exception:
#         try:
#             user_id = signup.data.user.id
#         except Exception:
#             if isinstance(signup, dict) and signup.get("user"):
#                 user_id = signup["user"]["id"]

#     if not user_id:
#         raise HTTPException(status_code=500, detail="Could not get created user ID")

#     # Insert into users table
#     roles = json.dumps(payload.roles or ["student"])
#     res = supabase.table("users").insert({
#         "id": user_id,
#         "email": payload.email,
#         "full_name": payload.full_name,
#         "roles": roles,
#         "org_id": org_id
#     }).execute()

#     if getattr(res, "status_code", None) not in (200, 201):
#         raise HTTPException(status_code=500, detail="Failed to insert user record")

#     return {
#         "message": "User created successfully",
#         "email": payload.email,
#         "roles": json.loads(roles)
#     }



# @app.post('/api/auth/login')
# def login(req: LoginReq):
#     try:
#         signin = supabase.auth.sign_in_with_password({'email': req.email, 'password': req.password})
#     except Exception as e:
#         raise HTTPException(status_code=401, detail=f'Invalid credentials: {e}')
#     # extract token with multiple shape support
#     token = None
#     try:
#         token = signin.session.access_token
#     except Exception:
#         try:
#             token = signin.session.access_token
#         except Exception:
#             token = signin.get('access_token') if isinstance(signin, dict) else None
#     if not token:
#         raise HTTPException(status_code=401, detail='Login failed: no token returned')
#     return {'access_token': token}

# @app.get('/api/users/me')
# def get_me(current_user=Depends(get_current_user)):
#     return current_user

# # -------------------------
# # ORGANIZATIONS (owner)
# # -------------------------
# @app.post('/api/orgs')
# @require_owner
# def create_org(req: CreateOrgReq, current_user=Depends(get_current_user)):
#     org_type = req.org_type or DEFAULT_ORG_TYPE
#     if org_type not in ('school','college','university'):
#         raise HTTPException(status_code=400, detail='org_type must be school|college|university')
#     r = supabase.table('organizations').insert({'name': req.name, 'org_type': org_type}).execute()
#     if getattr(r,'status_code',None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to create org')
#     return _data(r)[0]

# @app.get('/api/orgs')
# @require_owner
# def list_orgs(current_user=Depends(get_current_user)):
#     r = supabase.table('organizations').select('*').execute()
#     return _data(r) or []

# @app.post('/api/orgs/{org_id}/admin/create')
# @require_owner
# def create_admin(org_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
#     password = payload.password or secrets.token_urlsafe(10)
#     try:
#         signup = supabase.auth.sign_up({'email': payload.email, 'password': password})
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f'Auth error: {e}')
#     user_id = None
#     try:
#         user_id = signup.user.id
#     except Exception:
#         try:
#             user_id = signup.data.user.id
#         except Exception:
#             if isinstance(signup, dict) and signup.get('user'):
#                 user_id = signup['user']['id']
#     if not user_id:
#         raise HTTPException(status_code=500, detail='Failed to create auth admin user')
#     res = supabase.table('users').insert({
#         'id': user_id,
#         'email': payload.email,
#         'full_name': payload.full_name,
#         'roles': json.dumps(['admin']),
#         'org_id': org_id
#     }).execute()
#     if getattr(res,'status_code',None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to create admin record')
#     return {'message':'admin created', 'user_id': user_id}

# # -------------------------
# # ADMIN actions
# # -------------------------
# @app.post('/api/orgs/{org_id}/teachers/create')
# @require_any_role('admin')
# def create_class_teacher(org_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
#     if current_user.get('org_id') != org_id:
#         raise HTTPException(status_code=403, detail='Not your org')
#     password = payload.password or secrets.token_urlsafe(8)
#     try:
#         signup = supabase.auth.sign_up({'email': payload.email, 'password': password})
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f'Auth error: {e}')
#     user_id = None
#     try:
#         user_id = signup.user.id
#     except Exception:
#         try:
#             user_id = signup.data.user.id
#         except Exception:
#             if isinstance(signup, dict) and signup.get('user'):
#                 user_id = signup['user']['id']
#     if not user_id:
#         raise HTTPException(status_code=500, detail='Failed to create class teacher')
#     r = supabase.table('users').insert({
#         'id': user_id,
#         'email': payload.email,
#         'full_name': payload.full_name,
#         'roles': json.dumps(['class_teacher']),
#         'org_id': org_id
#     }).execute()
#     if getattr(r,'status_code',None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to create class teacher record')
#     return {'message':'class teacher created', 'user_id': user_id}

# @app.delete('/api/orgs/{org_id}/teachers/{teacher_id}')
# @require_any_role('admin')
# def delete_class_teacher(org_id: str, teacher_id: str, current_user=Depends(get_current_user)):
#     if current_user.get('org_id') != org_id:
#         raise HTTPException(status_code=403, detail='Not your org')
#     supabase.table('users').delete().eq('id', teacher_id).eq('org_id', org_id).execute()
#     return {'message':'deleted teacher if existed'}

# # -------------------------
# # DEPARTMENTS (optional)
# # -------------------------
# @app.post('/api/departments/create')
# @require_any_role('admin')
# def create_department(req: CreateDeptReq, current_user=Depends(get_current_user)):
#     if current_user.get('org_id') != req.org_id:
#         raise HTTPException(status_code=403, detail='Not your org')
#     r = supabase.table('departments').insert({
#         'org_id': req.org_id,
#         'name': req.name,
#         'hod_id': req.hod_id
#     }).execute()
#     if getattr(r,'status_code',None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to create department')
#     return _data(r)[0]

# @app.get('/api/orgs/{org_id}/departments')
# @require_any_role('admin','class_teacher','sub_teacher')
# def list_departments(org_id: str, current_user=Depends(get_current_user)):
#     r = supabase.table('departments').select('*').eq('org_id', org_id).execute()
#     return _data(r) or []

# # -------------------------
# # TEACHER HIERARCHY -> add sub-teacher
# # -------------------------
# @app.post('/api/teachers/add-sub')
# @require_any_role('class_teacher','admin')
# def add_sub_teacher(payload: AddUserReq, current_user=Depends(get_current_user)):
#     org_id = current_user.get('org_id')
#     password = payload.password or secrets.token_urlsafe(10)
#     try:
#         signup = supabase.auth.sign_up({'email': payload.email, 'password': password})
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f'Auth error: {e}')
#     user_id = None
#     try:
#         user_id = signup.user.id
#     except Exception:
#         try:
#             user_id = signup.data.user.id
#         except Exception:
#             if isinstance(signup, dict) and signup.get('user'):
#                 user_id = signup['user']['id']
#     if not user_id:
#         raise HTTPException(status_code=500, detail='Failed to create sub teacher')
#     supabase.table('users').insert({
#         'id': user_id,
#         'email': payload.email,
#         'full_name': payload.full_name,
#         'roles': json.dumps(['sub_teacher']),
#         'org_id': org_id
#     }).execute()
#     supabase.table('teacher_hierarchy').insert({
#         'org_id': org_id,
#         'class_teacher_id': current_user['id'],
#         'sub_teacher_id': user_id
#     }).execute()
#     return {'message':'sub teacher added', 'user_id': user_id}

# # -------------------------
# # CLASSES
# # -------------------------
# @app.post('/api/classes')
# @require_any_role('sub_teacher','class_teacher')
# def create_class(req: CreateClassReq, current_user=Depends(get_current_user)):
#     # if org uses departments, department_id recommended but optional by user's choice
#     if org_has_departments(req.org_id) and not req.department_id:
#         # we allow creation without department if admin/teacher wants; you can enforce if desired
#         pass
#     # unique class code
#     for _ in range(6):
#         code = secrets.token_urlsafe(4).upper()
#         q = supabase.table('classes').select('id').eq('class_code', code).execute()
#         if getattr(q,'data',None) in (None, []) or not q.data:
#             break
#     ct_id = None
#     if 'sub_teacher' in parse_roles_field(current_user.get('roles', [])):
#         h = supabase.table('teacher_hierarchy').select('class_teacher_id').eq('sub_teacher_id', current_user['id']).single().execute()
#         if getattr(h,'data',None):
#             ct_id = h.data.get('class_teacher_id')
#     elif 'class_teacher' in parse_roles_field(current_user.get('roles', [])):
#         ct_id = current_user['id']
#     body = {
#         'org_id': req.org_id,
#         'title': req.title,
#         'description': req.description,
#         'created_by': current_user['id'],
#         'class_teacher_id': ct_id,
#         'class_code': code,
#         'department_id': req.department_id if getattr(req, 'department_id', None) else None
#     }
#     r = supabase.table('classes').insert(body).execute()
#     if getattr(r,'status_code',None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to create class')
#     try:
#         supabase.table('class_memberships').insert({'class_id': r.data[0]['id'], 'user_id': current_user['id'], 'role': 'teacher'}).execute()
#     except Exception:
#         pass
#     return r.data[0]

# @app.post('/api/classes/join')
# @require_any_role('student','none')
# def join_class(req: JoinClassReq, current_user=Depends(get_current_user)):
#     q = supabase.table('classes').select('id, org_id').eq('class_code', req.class_code).single().execute()
#     if not getattr(q,'data',None):
#         raise HTTPException(status_code=404, detail='Class not found')
#     class_id = q.data['id']
#     org_id = q.data['org_id']
#     roles = parse_roles_field(current_user.get('roles') or [])
#     if 'student' not in roles:
#         roles.append('student')
#         supabase.table('users').update({'roles': json.dumps(roles), 'org_id': org_id}).eq('id', current_user['id']).execute()
#     supabase.table('class_memberships').insert({'class_id': class_id, 'user_id': current_user['id'], 'role': 'student'}).execute()
#     return {'message': 'joined'}

# @app.delete('/api/classes/{class_id}')
# @require_any_role('sub_teacher','class_teacher','admin')
# def delete_class(class_id: str, current_user=Depends(get_current_user)):
#     c = supabase.table('classes').select('created_by, class_teacher_id, org_id').eq('id', class_id).single().execute()
#     if not getattr(c,'data',None):
#         raise HTTPException(status_code=404, detail='Class not found')
#     allowed = False
#     if 'admin' in parse_roles_field(current_user.get('roles', [])) and current_user.get('org_id') == c.data.get('org_id'):
#         allowed = True
#     if c.data.get('created_by') == current_user['id']:
#         allowed = True
#     if c.data.get('class_teacher_id') == current_user['id']:
#         allowed = True
#     if not allowed:
#         raise HTTPException(status_code=403, detail='Not allowed to delete this class')
#     supabase.table('classes').delete().eq('id', class_id).execute()
#     return {'message':'deleted'}

# # -------------------------
# # ASSIGNMENTS (create + upload file + list)
# # -------------------------
# @app.post('/api/assignments')
# @require_any_role('sub_teacher')
# def create_assignment(req: CreateAssignmentReq, current_user=Depends(get_current_user)):
#     cm = supabase.table('class_memberships').select('role').eq('class_id', req.class_id).eq('user_id', current_user['id']).single().execute()
#     if not getattr(cm,'data',None) or cm.data.get('role') != 'teacher':
#         raise HTTPException(status_code=403, detail='Only the subject teacher can create assignments for this class')
#     if req.assignment_type not in ('file','text','mixed'):
#         raise HTTPException(status_code=400, detail='Invalid assignment_type')
#     body = {'class_id': req.class_id, 'created_by': current_user['id'], 'title': req.title, 'description': req.description, 'due_at': req.due_at, 'assignment_type': req.assignment_type}
#     r = supabase.table('assignments').insert(body).execute()
#     if getattr(r,'status_code',None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to create assignment')
#     return r.data[0]

# @app.post('/api/assignments/{assignment_id}/upload-file')
# @require_any_role('sub_teacher')
# def upload_assignment_file(assignment_id: str, file: UploadFile = File(...), current_user=Depends(get_current_user)):
#     a = supabase.table('assignments').select('class_id, created_by').eq('id', assignment_id).single().execute()
#     if not getattr(a,'data',None):
#         raise HTTPException(status_code=404, detail='Assignment not found')
#     cm = supabase.table('class_memberships').select('role').eq('class_id', a.data['class_id']).eq('user_id', current_user['id']).single().execute()
#     if not getattr(cm,'data',None) or cm.data.get('role') != 'teacher':
#         raise HTTPException(status_code=403, detail='Only subject teacher can upload file for this assignment')
#     bucket = 'assignments'
#     filename = f"{assignment_id}/{secrets.token_hex(8)}_{file.filename}"
#     try:
#         content = file.file.read()
#         supabase.storage.from_(bucket).upload(filename, content)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f'Upload failed: {e}')
#     file_path = f"{bucket}/{filename}"
#     supabase.table('assignments').update({'file_path': file_path}).eq('id', assignment_id).execute()
#     return {'message':'file uploaded', 'file_path': file_path}

# @app.get('/api/classes/{class_id}/assignments')
# def list_assignments(class_id: str, current_user=Depends(get_current_user)):
#     m = supabase.table('class_memberships').select('*').eq('class_id', class_id).eq('user_id', current_user['id']).single().execute()
#     if not getattr(m,'data',None):
#         raise HTTPException(status_code=403, detail='Not a member of class')
#     r = supabase.table('assignments').select('*').eq('class_id', class_id).execute()
#     return _data(r) or []

# # -------------------------
# # SUBMISSIONS (file/text), list, grade
# # -------------------------
# @app.post('/api/submissions')
# @require_any_role('student')
# def submit_assignment(file: Optional[UploadFile] = File(None), payload: Optional[SubmitReq] = Body(None), current_user=Depends(get_current_user)):
#     # payload must include assignment_id
#     if payload is None and not file:
#         raise HTTPException(status_code=400, detail='No submission data')
#     assignment_id = payload.assignment_id if payload else None
#     if not assignment_id:
#         raise HTTPException(status_code=400, detail='assignment_id required')
#     a = supabase.table('assignments').select('class_id, assignment_type').eq('id', assignment_id).single().execute()
#     if not getattr(a,'data',None):
#         raise HTTPException(status_code=404, detail='Assignment not found')
#     class_id = a.data['class_id']
#     cm = supabase.table('class_memberships').select('*').eq('class_id', class_id).eq('user_id', current_user['id']).single().execute()
#     if not getattr(cm,'data',None):
#         raise HTTPException(status_code=403, detail='Not a member of class')
#     file_path = None
#     text_content = None
#     if file:
#         bucket = 'submissions'
#         filename = f"{assignment_id}/{current_user['id']}/{secrets.token_hex(8)}_{file.filename}"
#         content = file.file.read()
#         try:
#             supabase.storage.from_(bucket).upload(filename, content)
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f'Upload failed: {e}')
#         file_path = f"{bucket}/{filename}"
#     if payload and payload.text_content:
#         text_content = payload.text_content
#     existing = supabase.table('submissions').select('*').eq('assignment_id', assignment_id).eq('student_id', current_user['id']).single().execute()
#     if getattr(existing,'data',None):
#         supabase.table('submissions').update({'text_content': text_content, 'file_path': file_path, 'submitted_at': datetime.utcnow()}).eq('id', existing.data['id']).execute()
#         return {'message':'updated submission'}
#     r = supabase.table('submissions').insert({'assignment_id': assignment_id, 'student_id': current_user['id'], 'text_content': text_content, 'file_path': file_path}).execute()
#     if getattr(r,'status_code',None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to submit')
#     return r.data[0]

# @app.get('/api/assignments/{assignment_id}/submissions')
# @require_any_role('sub_teacher','class_teacher')
# def get_submissions(assignment_id: str, current_user=Depends(get_current_user)):
#     a = supabase.table('assignments').select('class_id, created_by').eq('id', assignment_id).single().execute()
#     if not getattr(a,'data',None):
#         raise HTTPException(status_code=404, detail='Assignment not found')
#     class_id = a.data['class_id']
#     cm = supabase.table('class_memberships').select('*').eq('class_id', class_id).eq('user_id', current_user['id']).single().execute()
#     is_teacher = getattr(cm,'data',None) and cm.data.get('role') == 'teacher'
#     cls = supabase.table('classes').select('class_teacher_id').eq('id', class_id).single().execute()
#     is_supervisor = getattr(cls,'data',None) and cls.data.get('class_teacher_id') == current_user['id']
#     if not (is_teacher or is_supervisor):
#         raise HTTPException(status_code=403, detail='Not allowed')
#     r = supabase.table('submissions').select('*').eq('assignment_id', assignment_id).execute()
#     return _data(r) or []

# @app.post('/api/submissions/{submission_id}/grade')
# @require_any_role('sub_teacher')
# def grade_submission(submission_id: str, grade: float = Body(...), current_user=Depends(get_current_user)):
#     s = supabase.table('submissions').select('assignment_id, student_id').eq('id', submission_id).single().execute()
#     if not getattr(s,'data',None):
#         raise HTTPException(status_code=404, detail='Submission not found')
#     assignment = supabase.table('assignments').select('class_id').eq('id', s.data['assignment_id']).single().execute()
#     class_id = assignment.data['class_id']
#     cm = supabase.table('class_memberships').select('*').eq('class_id', class_id).eq('user_id', current_user['id']).single().execute()
#     if not (getattr(cm,'data',None) and cm.data.get('role') == 'teacher'):
#         raise HTTPException(status_code=403, detail='Only the subject teacher can grade submissions')
#     supabase.table('submissions').update({'grade': grade, 'graded_by': current_user['id']}).eq('id', submission_id).execute()
#     return {'message':'graded'}

# # -------------------------
# # NOTES
# # -------------------------
# @app.post('/api/notes')
# @require_any_role('sub_teacher','class_teacher')
# def upload_note(req: NoteCreateReq, current_user=Depends(get_current_user)):
#     cm = supabase.table('class_memberships').select('role').eq('class_id', req.class_id).eq('user_id', current_user['id']).single().execute()
#     if not getattr(cm,'data',None) or cm.data.get('role') != 'teacher':
#         raise HTTPException(status_code=403, detail='Only subject teacher can upload notes')
#     r = supabase.table('notes').insert({'class_id': req.class_id, 'uploaded_by': current_user['id'], 'title': req.title, 'file_path': req.file_path}).execute()
#     if getattr(r,'status_code',None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to upload note')
#     return r.data[0]

# @app.get('/api/classes/{class_id}/notes')
# def list_notes(class_id: str, current_user=Depends(get_current_user)):
#     cm = supabase.table('class_memberships').select('*').eq('class_id', class_id).eq('user_id', current_user['id']).single().execute()
#     if not getattr(cm,'data',None):
#         raise HTTPException(status_code=403, detail='Not a member')
#     r = supabase.table('notes').select('*').eq('class_id', class_id).execute()
#     return _data(r) or []

# # -------------------------
# # FINAL MARKS
# # -------------------------
# @app.post('/api/finalmarks')
# @require_any_role('sub_teacher')
# def upload_final_marks(req: FinalMarkReq, current_user=Depends(get_current_user)):
#     stu = get_user_row(req.student_id)
#     if not stu:
#         raise HTTPException(status_code=404, detail='Student not found')
#     body = req.dict()
#     body['uploaded_by'] = current_user['id']
#     r = supabase.table('final_marks').insert(body).execute()
#     if getattr(r,'status_code',None) not in (200,201):
#         raise HTTPException(status_code=500, detail='Failed to upload final marks')
#     return {'message':'uploaded'}

# @app.get('/api/orgs/{org_id}/grades')
# @require_any_role('class_teacher','admin','sub_teacher')
# def view_all_grades(org_id: str, current_user=Depends(get_current_user)):
#     roles = parse_roles_field(current_user.get('roles') or [])
#     if 'class_teacher' in roles:
#         classes = supabase.table('classes').select('id').eq('class_teacher_id', current_user['id']).eq('org_id', org_id).execute()
#         class_ids = [c['id'] for c in (classes.data or [])]
#         if not class_ids:
#             return []
#         r = supabase.table('final_marks').select('*').in_('class_id', class_ids).execute()
#         return _data(r) or []
#     if 'admin' in roles and current_user.get('org_id') == org_id:
#         r = supabase.table('final_marks').select('*').eq('org_id', org_id).execute()
#         return _data(r) or []
#     if 'sub_teacher' in roles:
#         cm = supabase.table('class_memberships').select('class_id').eq('user_id', current_user['id']).eq('role', 'teacher').execute()
#         class_ids = [c['class_id'] for c in (cm.data or [])]
#         if not class_ids:
#             return []
#         r = supabase.table('final_marks').select('*').in_('class_id', class_ids).execute()
#         return _data(r) or []
#     raise HTTPException(status_code=403, detail='Not allowed')

# # -------------------------
# # MESSAGES (public + private)
# # -------------------------
# @app.post('/api/messages')
# @require_any_role('student','sub_teacher','class_teacher','admin')
# def send_message(req: MessageReq, current_user=Depends(get_current_user)):
#     # membership check
#     cm = supabase.table('class_memberships').select('*').eq('class_id', req.class_id).eq('user_id', current_user['id']).single().execute()
#     if not getattr(cm,'data',None):
#         raise HTTPException(status_code=403, detail='Not a member of this class')
#     if not req.is_public:
#         if not req.receiver_id:
#             raise HTTPException(status_code=400, detail='receiver_id required for private message')
#         # if sender is student, receiver must be a teacher
#         if 'student' in parse_roles_field(current_user.get('roles', [])):
#             check = supabase.table('class_memberships').select('*').eq('class_id', req.class_id).eq('user_id', req.receiver_id).single().execute()
#             if not getattr(check,'data',None) or check.data.get('role') != 'teacher':
#                 raise HTTPException(status_code=403, detail='Receiver must be a teacher for this class')
#     supabase.table('messages').insert({
#         'class_id': req.class_id,
#         'sender_id': current_user['id'],
#         'receiver_id': req.receiver_id if not req.is_public else None,
#         'content': req.content,
#         'is_public': req.is_public
#     }).execute()
#     return {'message':'sent', 'type': 'public' if req.is_public else 'private'}

# @app.get('/api/classes/{class_id}/messages')
# @require_any_role('student','sub_teacher','class_teacher','admin')
# def get_messages(class_id: str, current_user=Depends(get_current_user)):
#     cm = supabase.table('class_memberships').select('*').eq('class_id', class_id).eq('user_id', current_user['id']).single().execute()
#     if not getattr(cm,'data',None):
#         raise HTTPException(status_code=403, detail='Not a member')
#     user_id = current_user['id']
#     # return public messages + private ones where user is sender or receiver
#     r = supabase.table('messages').select('*').eq('class_id', class_id).execute()
#     msgs = _data(r) or []
#     visible = [m for m in msgs if m.get('is_public') or m.get('sender_id')==user_id or m.get('receiver_id')==user_id]
#     return visible

# # -------------------------
# # BULK IMPORT: preview + import
# # -------------------------
# @app.post('/api/admin/preview-import')
# @require_any_role('admin')
# def preview_import(file: UploadFile = File(...), current_user=Depends(get_current_user)):
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

# @app.post('/api/admin/import-file')
# @require_any_role('admin')
# def import_file(file: UploadFile = File(...), mapping_req: BulkMappingReq = Body(...), current_user=Depends(get_current_user)):
#     org_id = current_user.get('org_id')
#     if not org_id:
#         raise HTTPException(status_code=400, detail='Admin has no org_id assigned')
#     content = file.file.read()
#     try:
#         if file.filename.lower().endswith(('.xls','.xlsx')):
#             df = pd.read_excel(BytesIO(content))
#         else:
#             df = pd.read_csv(BytesIO(content))
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f'Could not parse file: {e}')
#     mapping = mapping_req.mapping or {}
#     created = {'users':0, 'classes':0, 'departments':0, 'memberships':0, 'skipped':0, 'errors':[]}
#     for idx, row in df.iterrows():
#         try:
#             def get_col(key):
#                 col = mapping.get(key) or key
#                 # pandas: access by label or by integer index fallback
#                 if col in row.index:
#                     return row.get(col)
#                 return None
#             name = str(get_col('name') or get_col('Name') or '').strip()
#             email = str(get_col('email') or get_col('Email') or '').strip().lower()
#             role = str(get_col('role') or get_col('Role') or 'student').strip().lower()
#             dept_name = str(get_col('department') or get_col('Department') or '').strip() or None
#             class_title = str(get_col('class') or get_col('Class') or get_col('Class Title') or '').strip() or None
#             section = str(get_col('section') or get_col('Section') or '').strip() or None
#             password = str(get_col('password') or get_col('Password') or secrets.token_urlsafe(8))
#             if not email:
#                 created['skipped'] += 1
#                 continue
#             existing = get_user_row_by_email(email)
#             user_id = None
#             if existing:
#                 user_id = existing['id']
#                 # update roles
#                 roles = parse_roles_field(existing.get('roles'))
#                 if role and role not in roles:
#                     roles.append(role)
#                 supabase.table('users').update({'full_name': name, 'roles': json.dumps(roles), 'org_id': org_id}).eq('id', user_id).execute()
#             else:
#                 # create auth user
#                 try:
#                     signup = supabase.auth.sign_up({'email': email, 'password': password})
#                     user_id = getattr(signup,'user',None).id if getattr(signup,'user',None) else (getattr(signup,'data',None).user.id if getattr(signup,'data',None) else None)
#                 except Exception:
#                     # fallback: try lookup if already exists in auth
#                     try:
#                         eu = supabase.auth.get_user_by_email(email)
#                         user_id = getattr(eu,'user',None).id if getattr(eu,'user',None) else None
#                     except Exception:
#                         user_id = None
#                 if not user_id:
#                     created['errors'].append({'row': idx, 'error': 'Could not create/find auth user', 'email': email})
#                     continue
#                 roles_list = [role] if role else []
#                 supabase.table('users').insert({'id': user_id, 'email': email, 'full_name': name, 'roles': json.dumps(roles_list), 'org_id': org_id}).execute()
#                 created['users'] += 1
#             # department create if provided
#             dept_id = None
#             if dept_name:
#                 q = supabase.table('departments').select('*').eq('org_id', org_id).eq('name', dept_name).single().execute()
#                 if not getattr(q,'data',None):
#                     if mapping_req.create_departments:
#                         nd = supabase.table('departments').insert({'org_id': org_id, 'name': dept_name}).execute()
#                         dept_id = nd.data[0]['id'] if getattr(nd,'data',None) else None
#                         created['departments'] += 1
#                     else:
#                         dept_id = None
#                 else:
#                     dept_id = q.data['id']
#             # class create if provided
#             class_id = None
#             if class_title:
#                 q = supabase.table('classes').select('*').eq('org_id', org_id).eq('title', class_title).eq('department_id', dept_id).single().execute()
#                 if not getattr(q,'data',None):
#                     code = secrets.token_urlsafe(4).upper()
#                     nc = supabase.table('classes').insert({'org_id': org_id, 'title': class_title, 'description': f"Section {section or 'General'}", 'department_id': dept_id, 'class_teacher_id': user_id if role=='class_teacher' else None, 'class_code': code}).execute()
#                     class_id = nc.data[0]['id'] if getattr(nc,'data',None) else None
#                     created['classes'] += 1
#                 else:
#                     class_id = q.data['id']
#             # membership
#             if class_id and role in ('student','sub_teacher','class_teacher'):
#                 mem_role = 'teacher' if role in ('sub_teacher','class_teacher') else 'student'
#                 supabase.table('class_memberships').insert({'class_id': class_id, 'user_id': user_id, 'role': mem_role}).execute()
#                 created['memberships'] += 1
#         except Exception as e:
#             created['errors'].append({'row': idx, 'error': str(e)})
#             continue
#     return created

# # -------------------------
# # HEALTH
# # -------------------------
# @app.get('/')
# def root():
#     return {'message':'API up'}

# # End of file

# app/main.py
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
    db_insert_one("role_assignments", {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "role": role,
        "org_id": org_id,
        "dept_id": dept_id,
        "class_id": class_id
    })


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


@app.post("/api/dept/{dept_id}/add-class-teacher")
@require_role("hod")
def add_class_teacher(dept_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
    user = get_user_row_by_email(payload.email)
    if not user:
        raise HTTPException(404, "User not found")

    assign_role(user["id"], "class_teacher", dept_id=dept_id)
    return {"message": "Class Teacher Added"}

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
@app.post("/api/departments/{dept_id}/add-class-teacher")
@require_any_role("hod")
def add_class_teacher(dept_id: str, payload: AddUserReq, current_user=Depends(get_current_user)):
    # Check if this HOD owns this department
    hod_map = db_find_one("department_hods", hod_id=current_user["id"], dept_id=dept_id)
    if not hod_map:
        raise HTTPException(status_code=403, detail="Not HOD of this department")

    # Create user
    user = get_user_row_by_email(payload.email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    user_id = str(uuid.uuid4())
    hashed_pass = hash_password(payload.password)

    new_user = {
        "id": user_id,
        "email": payload.email,
        "full_name": payload.full_name,
        "roles": json.dumps(["class_teacher"]),
        "org_id": current_user["org_id"],
        "hashed_password": hashed_pass
    }
    db_insert_one("users", new_user)

    # Attach class teacher → department
    db_insert_one("dept_class_teachers", {
        "id": str(uuid.uuid4()),
        "dept_id": dept_id,
        "class_teacher_id": user_id
    })

    return {"message": "Class Teacher added"}

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

    dept = db_find_one("departments", hod_id=hod_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not assigned")

    return dept

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
    
    if get_user_row_by_email(payload.email):
        raise HTTPException(status_code=400, detail="User with this email already exists")

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
@require_any_role('sub_teacher','class_teacher')
def create_class(req: CreateClassReq, current_user=Depends(get_current_user)):
    code = ""
    for _ in range(6):
        code = secrets.token_urlsafe(4).upper()
        if not db_find_one('classes', class_code=code):
            break
    
    ct_id = None
    if 'sub_teacher' in parse_roles_field(current_user.get('roles', [])):
        h = db_find_one('teacher_hierarchy', sub_teacher_id=current_user['id'])
        if not h:
            raise HTTPException(status_code=400, detail="No linked class teacher found for this sub_teacher.")
        ct_id = h.get('class_teacher_id')

    elif 'class_teacher' in parse_roles_field(current_user.get('roles', [])):
        ct_id = current_user['id']
        
    body = {
        'id': str(uuid.uuid4()),
        'org_id': req.org_id,
        'title': req.title,
        'description': req.description,
        'created_by': current_user['id'],
        'class_teacher_id': ct_id,
        'class_code': code,
        'department_id': req.department_id if getattr(req, 'department_id', None) else None
    }
    new_class = db_insert_one('classes', body)
    
    db_insert_one('class_memberships', {
        'id': str(uuid.uuid4()),
        'class_id': new_class['id'], 
        'user_id': current_user['id'], 
        'role': 'teacher'
    })
    return new_class

@app.post('/api/classes/join')
@require_any_role('student','none') # 'none' role won't exist, but we check 'student'
def join_class(req: JoinClassReq, current_user=Depends(get_current_user)):
    cls = db_find_one('classes', class_code=req.class_code)
    if not cls:
        raise HTTPException(status_code=404, detail='Class not found')
    
    class_id = cls['id']
    org_id = cls['org_id']
    
    roles = parse_roles_field(current_user.get('roles') or [])
    if 'student' not in roles:
        roles.append('student')
        db_update_one('users', current_user['id'], {'roles': json.dumps(roles), 'org_id': org_id})
        
    db_insert_one('class_memberships', {
        'id': str(uuid.uuid4()),
        'class_id': class_id, 
        'user_id': current_user['id'], 
        'role': 'student'
    })
    return {'message': 'joined'}

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

# ✅ List all classes for the current teacher (class_teacher or sub_teacher)
# @app.get("/api/classes")
# @require_any_role("sub_teacher", "class_teacher", "admin","student")
# def list_classes(current_user=Depends(get_current_user)):
#     roles = parse_roles_field(current_user.get("roles", []))
#     org_id = current_user.get("org_id")

#     if "admin" in roles:
#         # Admin sees all classes in their org
#         classes = db_find_many("classes", org_id=org_id)
#         return classes or []

#     elif "class_teacher" in roles:
#         # Class teacher sees their own classes
#         classes = db_find_many("classes", class_teacher_id=current_user["id"])
#         return classes or []
#     elif "student" in roles:
#         # Class teacher sees their own classes
#         classes = db_find_many("classes", student_id=current_user["id"])
#         return classes or []

#     elif "sub_teacher" in roles:
#         # Sub teacher sees classes of their linked class teacher
#         link = db_find_one("teacher_hierarchy", sub_teacher_id=current_user["id"])
#         if not link:
#             raise HTTPException(status_code=400, detail="Sub teacher not linked to any class teacher")
        
#         classes = db_find_many("classes", class_teacher_id=link["class_teacher_id"])
#         return classes or []

#     # default fallback
#     raise HTTPException(status_code=403, detail="Not allowed")
@app.get("/api/classes")
@require_any_role("sub_teacher", "class_teacher", "admin", "student")
def list_classes(current_user=Depends(get_current_user)):
    """
    Returns classes visible to the current user:
      - admin: all classes in their org
      - class_teacher: classes where class_teacher_id == current_user.id
      - sub_teacher: classes belonging to their linked class_teacher
      - student: classes where the user has a membership (role=student)
    """
    roles = parse_roles_field(current_user.get("roles", []))
    org_id = current_user.get("org_id")

    if "admin" in roles:
        return db_find_many("classes", org_id=org_id) or []

    if "class_teacher" in roles:
        return db_find_many("classes", class_teacher_id=current_user["id"]) or []

    if "sub_teacher" in roles:
        link = db_find_one("teacher_hierarchy", sub_teacher_id=current_user["id"])
        if not link:
            return []
        return db_find_many("classes", class_teacher_id=link["class_teacher_id"]) or []

    if "student" in roles:
        # list classes where this user has a membership
        mems = db_find_many("class_memberships", user_id=current_user["id"])
        if not mems:
            return []
        class_ids = [m["class_id"] for m in mems]
        all_classes = load_db("classes")
        return [c for c in all_classes if c["id"] in class_ids]

    raise HTTPException(status_code=403, detail="Not allowed")


# @app.post("/api/teachers/add-student")
# @require_any_role("class_teacher", "admin")
# def add_student(
#     class_id: str = Body(...),
#     full_name: str = Body(...),
#     email: EmailStr = Body(...),
#     password: str = Body(...),
#     current_user=Depends(get_current_user)
# ):
#     """Allows class_teacher or admin to manually add a student to a specific class."""
#     org_id = current_user.get("org_id")
#     if not org_id:
#         raise HTTPException(status_code=400, detail="User not linked to any org")

#     # Validate class exists
#     cls = db_find_one("classes", id=class_id)
#     if not cls:
#         raise HTTPException(status_code=404, detail="Class not found")
#     if cls.get("org_id") != org_id:
#         raise HTTPException(status_code=403, detail="Cannot add student to another org's class")

#     # Check if user already exists
#     existing = get_user_row_by_email(email)
#     if existing:
#         user_id = existing["id"]
#         roles = parse_roles_field(existing.get("roles"))
#         if "student" not in roles:
#             roles.append("student")
#             db_update_one("users", user_id, {"roles": json.dumps(roles)})
#     else:
#         # Create new user
#         user_id = str(uuid.uuid4())
#         hashed_pass = hash_password(password)
#         new_student = {
#             "id": user_id,
#             "email": email,
#             "full_name": full_name,
#             "roles": json.dumps(["student"]),
#             "org_id": org_id,
#             "hashed_password": hashed_pass,
#         }
#         db_insert_one("users", new_student)

#     # Add class membership if not already enrolled
#     existing_member = db_find_one("class_memberships", class_id=class_id, user_id=user_id)
#     if not existing_member:
#         db_insert_one(
#             "class_memberships",
#             {
#                 "id": str(uuid.uuid4()),
#                 "class_id": class_id,
#                 "user_id": user_id,
#                 "role": "student",
#             },
#         )

#     return {"message": "Student added successfully", "student_id": user_id}

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
        
    return db_find_many('submissions', assignment_id=assignment_id)

@app.post('/api/submissions/{submission_id}/grade')
@require_any_role('sub_teacher')
def grade_submission(submission_id: str, grade: float = Body(...), current_user=Depends(get_current_user)):
    s = db_find_one('submissions', id=submission_id)
    if not s:
        raise HTTPException(status_code=404, detail='Submission not found')
        
    assignment = db_find_one('assignments', id=s['assignment_id'])
    class_id = assignment['class_id']
    
    cm = db_find_one('class_memberships', class_id=class_id, user_id=current_user['id'])
    if not (cm and cm.get('role') == 'teacher'):
        raise HTTPException(status_code=403, detail='Only the subject teacher can grade submissions')
        
    db_update_one('submissions', submission_id, {'grade': grade, 'graded_by': current_user['id']})
    return {'message':'graded'}

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

# @app.get("/api/classes/{class_id}/grades")
# @require_any_role("class_teacher", "sub_teacher", "admin")
# def get_class_grades(class_id: str, current_user=Depends(get_current_user)):
#     # Check user belongs to that class
#     m = db_find_one("class_memberships", class_id=class_id, user_id=current_user["id"])
#     if not m:
#         raise HTTPException(status_code=403, detail="Not a member of this class")

#     # Load all grades
#     all_marks = load_db("final_marks")

#     # Filter only this class' grades
#     class_grades = [g for g in all_marks if g.get("class_id") == class_id]

#     return class_grades
@app.get("/api/classes/{class_id}/grades")
@require_any_role("admin", "class_teacher", "sub_teacher", "student")
def get_class_grades(class_id: str, current_user=Depends(get_current_user)):

    # Check if user is part of the class
    member = db_find_one("class_memberships", class_id=class_id, user_id=current_user["id"])
    if not member:
        raise HTTPException(status_code=403, detail="Not part of this class")

    roles = parse_roles_field(current_user.get("roles", []))
    org_id = current_user.get("org_id")

    # ADMIN → sees all marks in org for this class
    if "admin" in roles:
        return db_find_many("final_marks", class_id=class_id, org_id=org_id) or []

    # CLASS TEACHER → sees grades only for their classes
    if "class_teacher" in roles:
        cls = db_find_one("classes", id=class_id)
        if cls and cls.get("class_teacher_id") == current_user["id"]:
            return db_find_many("final_marks", class_id=class_id) or []
        raise HTTPException(status_code=403, detail="Not your class")

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
def import_file(file: UploadFile = File(...), mapping_req: BulkMappingReq = Body(...), current_user=Depends(get_current_user)):
    org_id = current_user.get('org_id')
    if not org_id:
        raise HTTPException(status_code=400, detail='Admin has no org_id assigned')
        
    content = file.file.read()
    try:
        if file.filename.lower().endswith(('.xls','.xlsx')):
            df = pd.read_excel(BytesIO(content))
        else:
            df = pd.read_csv(BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Could not parse file: {e}')
        
    mapping = mapping_req.mapping or {}
    created = {'users':0, 'classes':0, 'departments':0, 'memberships':0, 'skipped':0, 'errors':[]}
    
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