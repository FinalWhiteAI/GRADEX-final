Your repo has many branches
✔ This README belongs to one specific branch only
✔ Others should ignore this README if they are not on this branch

Clean, professional, and ready to use.

📘 Notebook Assistant — README (Branch-Specific)

⚠️ Important:
This repository contains multiple branches with different versions of the project.
This README belongs ONLY to the current branch you are working on.
Other branches may have different implementations, UIs, or backend integrations.

✔ If you are reading this from another branch → please ignore this README.

🧠 Overview

This branch implements a full Document Chat + Code Execution Notebook, built using React + Tailwind CSS, integrated with multiple FastAPI backends.

This version includes:

PDF upload

Firebase/FastAPI notes fetching

Upload document from URL

RAG-based chat with selected documents

Python code execution engine

Output panel with stdout/stderr

Complete chat + code UI layout

🚀 Features in This Branch
✓ Upload PDF

Uploads local PDFs to the main backend at:

POST /upload/

✓ Fetch Notes (Firebase -> FastAPI)

Loads notes using:

GET api/user/{user_id}/section/notes

✓ Upload From URL

Processes Firebase-stored document URLs using:

POST /upload-from-url/

✓ Document History Panel

Shows all processed PDFs for the logged-in user.

✓ Chat Notebook (RAG)

Chat with any selected document using:

POST /query/rag/

✓ Code Editor + Executor

Runs Python code using:

POST /execute


Shows live results:

STDOUT

STDERR

Exit Code

🔧 API Configuration (Branch Specific)

This branch uses three different backend services:

1️⃣ Main Document Backend (RAG Engine + Uploads)
https://760eacb1e388.ngrok-free.app

2️⃣ Firebase Notes Service
https://k5flk5h4-8000.inc1.devtunnels.ms/

3️⃣ Python Code Executor
https://wqlq1078-8000.inc1.devtunnels.ms/execute


⚠️ These URLs may differ in other branches.
This README applies only to this branch’s configuration.

🏗 Project Setup
1. Install dependencies
npm install

2. Run the app
npm start


Runs on:

http://localhost:3000

🗂 Folder Structure (Branch-Specific)
src/
 ├── App.jsx                
 ├── components/
 │     ├── ChatInterface.jsx
 │     └── CodeEditor.jsx
 ├── index.js
 └── styles.css


Only this branch contains this exact layout.

⚠️ Branch Disclaimer

Because your repo has many branches:

✔ This branch = Active Notebook UI + RAG Chat + Code Executor
❌ Other branches ≠ Not guaranteed to have this UI or logic
✔ Only push updates to this branch README
✔ Other branches may contain older experiments, tests, or drafts

You can add this near the top of the README if needed:

# ⚠️ Branch Notice
This README is maintained exclusively for the branch named: <your-branch-name>
Do NOT use this README for other branches.
