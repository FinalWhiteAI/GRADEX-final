# from pydantic import BaseModel
# from typing import List

# class User(BaseModel):
#     id: str | None = None
#     name: str
#     role: str 

# class Class(BaseModel):
#     id: str | None = None
#     name: str
#     teacher_id: str
#     students: List[str] = []

# class Note(BaseModel):
#     id: str | None = None
#     class_id: str
#     title: str
#     content: str
#     user_id: str

# class Assignment(BaseModel):
#     id: str | None = None
#     class_id: str
#     title: str
#     description: str
#     user_id: str

# class Submission(BaseModel):
#     id: str | None = None
#     assignment_id: str
#     student_id: str
#     content: str

# class Message(BaseModel):
#     id: str | None = None
#     class_id: str
#     user_id: str
#     content: str


# # models.py
# from sqlalchemy import Column, String, Text, ForeignKey, Table, DateTime
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import relationship, declarative_base
# import uuid
# from datetime import datetime

# Base = declarative_base()

# # Many-to-Many: Students <-> Classes
# class_students = Table(
#     "class_students",
#     Base.metadata,
#     Column("class_id", UUID(as_uuid=True), ForeignKey("classes.id"), primary_key=True),
#     Column("student_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
# )

# class User(Base):
#     __tablename__ = "users"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     name = Column(String, nullable=False)
#     email = Column(String, unique=True, nullable=False)
#     password = Column(String, nullable=False)  # hashed password
#     created_at = Column(DateTime, default=datetime.utcnow)

#     # Relations
#     classes_created = relationship("Class", back_populates="teacher")
#     notes = relationship("Note", back_populates="creator")
#     assignments = relationship("Assignment", back_populates="creator")
#     submissions = relationship("Submission", back_populates="student")
#     messages = relationship("Message", back_populates="user")
#     enrolled_classes = relationship("Class", secondary=class_students, back_populates="students")

# class Class(Base):
#     __tablename__ = "classes"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     name = Column(String, nullable=False)
#     teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

#     # Relations
#     teacher = relationship("User", back_populates="classes_created")
#     students = relationship("User", secondary=class_students, back_populates="enrolled_classes")
#     notes = relationship("Note", back_populates="cls")
#     assignments = relationship("Assignment", back_populates="cls")
#     messages = relationship("Message", back_populates="cls")

# class Note(Base):
#     __tablename__ = "notes"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
#     title = Column(String, nullable=False)
#     content = Column(Text, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     # Relations
#     cls = relationship("Class", back_populates="notes")
#     creator = relationship("User", back_populates="notes")

# class Assignment(Base):
#     __tablename__ = "assignments"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
#     title = Column(String, nullable=False)
#     description = Column(Text, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     # Relations
#     cls = relationship("Class", back_populates="assignments")
#     creator = relationship("User", back_populates="assignments")
#     submissions = relationship("Submission", back_populates="assignment")

# class Submission(Base):
#     __tablename__ = "submissions"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     assignment_id = Column(UUID(as_uuid=True), ForeignKey("assignments.id"), nullable=False)
#     student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
#     content = Column(Text, nullable=False)
#     submitted_at = Column(DateTime, default=datetime.utcnow)

#     # Relations
#     assignment = relationship("Assignment", back_populates="submissions")
#     student = relationship("User", back_populates="submissions")

# class Message(Base):
#     __tablename__ = "messages"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
#     content = Column(Text, nullable=False)
#     sent_at = Column(DateTime, default=datetime.utcnow)

#     # Relations
#     cls = relationship("Class", back_populates="messages")
#     user = relationship("User", back_populates="messages")
