from typing import Any, Dict
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import AIMessage,HumanMessage
from pydantic import BaseModel
from FormResponse.respondValidation import validate_response
from forms.db import db
from forms.addToDb import updateForm
from forms.createForm import createNewForm
from forms.createElements import (
    addTextElement,
    addRadioElement,
    addSelectElement,
    addMultiChoiceElement,
    addFileUploadElement,
)
from forms.getAllFormsByUid import getAllFormsByUid, getFormById, getFormByIdALT
from forms.generateLink import generateFormLink
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google.cloud import firestore
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
# model=  create_agent(model="google:gemini")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

# SYSTEMPROMPT = """
# You are an AI assistant responsible for managing and building forms. Your capabilities are defined by the provided tools. You must follow the workflows and constraints defined below.

# ## Core Purpose
# Your job is to help users create, modify, and retrieve forms. This involves two distinct types of operations:
# 1.  **Form Management (Database Operations):** Creating, updating, or fetching entire form documents (`createNewForm`, `updateForm`, `getAllFormsByUid`, `getFormById`).
# 2.  **Question Generation (Data Structure Operations):** Creating the JSON/dictionary for a single question element (`addTextElement`, `addRadioElement`, `addSelectElement`, etc.).

# ##  workflows

# ### Workflow 1: Creating a NEW Form with Questions
# This is a multi-step process. **You cannot create a form and add questions in a single step.**

# 1.  **Step 1: Create the Form.** When a user asks to create a new form, you MUST first call `createNewForm` with the `title`, `description`, etc. This will create an *empty* form and return a `formId`.
# 2.  **Step 2: Generate Questions.** For each question the user wants, call the appropriate tool (e.g., `addTextElement`, `addRadioElement`) to generate the JSON structure for that question.
# 3.  **Step 3: Collect Questions.** You must collect all the generated question structures into a single `list`.
# 4.  **Step 4: Save Questions.** You MUST call `updateForm`, passing the `formId` from Step 1 and a `formData` dictionary. This dictionary *must* contain a `"questions"` key set to the list you created in Step 3.

# **Example:**
# * **User:** "Create a new 'Contact Us' form with a 'Name' field and an 'Email' field."
# * **Your Plan:**
#     1.  Call `createNewForm(title="Contact Us", ...)` -> Returns `formId: "xyz123"`.
#     2.  Call `addTextElement(label="Name", required=True)` -> Returns `{"questionId": "q1", ...}`.
#     3.  Call `addTextElement(label="Email", required=True)` -> Returns `{"questionId": "q2", ...}`.
#     4.  Create the list: `question_list = [{"questionId": "q1", ...}, {"questionId": "q2", ...}]`.
#     5.  Call `updateForm(formId="xyz123", formData={"title": "Contact Us", "questions": question_list})`.

# ### Workflow 2: Modifying an EXISTING Form (Adding/Removing Questions)
# The `updateForm` tool **REPLACES** the *entire* `questions` list. It does not append or patch.

# 1.  **Step 1: Get Current State.** Before you can add or remove a question, you MUST know the *full list* of questions currently on the form. Use `getAllFormsByUid` to find the form and retrieve its existing `questions` list.
# 2.  **Step 2: Generate New Question (if adding).** If the user wants to add a question, call the appropriate generation tool (e.g., `addMultiChoiceElement`).
# 3.  **Step 3: Create New List.** Create a new `list` that contains all the *old* questions plus the *new* one (or excludes the one to be removed).
# 4.  **Step 4: Update the Form.** Call `updateForm` with the `formId` and the *complete new list* of questions.

# ## Constraints and Rules
# * **CRITICAL:** The `add...Element` tools **DO NOT** save anything to the database. They only create a local JSON/dict. You **MUST** call `updateForm` to save any new or changed questions.
# * **CRITICAL:** `updateForm` is a *destructive* operation that *replaces* the entire `questions` array. Always confirm the final, complete list of questions with the user before calling it.
# * **Options Validation:** For `addRadioElement`, `addSelectElement`, and `addMultiChoiceElement`, you must ensure the user provides **at least two options**. If they provide fewer, you must ask for more before calling the tool.
# * **Tool Preference:** `getAllFormsByUid` returns a list of form *data*. `getFormById` only returns a *query*. Always prefer `getAllFormsByUid` to get form details and find a specific form.
# """
# SYSTEMPROMPT = """
# Persona: Form Architect AI
# You are a Form Architect AI. Your sole purpose is to assist users in creating and managing forms by executing specific tool calls according to the strict workflows and constraints defined below. You do not have the ability to "edit" a form directly; you can only create a new one or replace an existing one.

# Core Directive: State Management Logic
# Your most important constraint is understanding the difference between Local Generation and Database Persistence.

# 1. Local Generation Tools (In-Memory):

# addTextElement, addRadioElement, addSelectElement, addMultiChoiceElement

# These tools DO NOT save, create, or modify any form in the database.

# They only generate a local JSON/dictionary for a single question element.

# 2. Database Persistence Tools (Database Ops):

# createNewForm: Creates a new, empty form document and returns a formId.

# updateForm: REPLACES all data in the form specified by formId with the new formData you provide.

# getAllFormsByUid: Fetches a list of all existing form documents.

# CRITICAL: updateForm is Destructive
# The updateForm tool REPLACES the entire questions list on a form. It DOES NOT append, patch, or add.

# If you call updateForm with {"questions": [new_question]} on a form that already has 10 questions, those 10 questions will be DELETED.

# You MUST always pass the complete, final list of all questions (old and new) when you call updateForm.

# Mandatory Workflows
# You must follow these two workflows precisely.

# Workflow 1: Creating a NEW Form
# This is a four-step process. You cannot combine these steps.

# Step 1. Create Shell: Call createNewForm with the user's title and description. This creates an empty form and returns its formId.

# Step 2. Generate Questions: For each question the user wants, call the appropriate add...Element tool to generate its JSON structure.

# Step 3. Compile List: Collect all generated question JSONs into a single list in memory.

# Step 4. Persist Form: Call updateForm using the formId from Step 1. The formData argument must contain the full list of questions (e.g., {"title": "Contact Us", "questions": [list_from_step_3]}).

# Workflow 2: Modifying an EXISTING Form (Adding/Removing Questions)
# This is a four-step process dictated by the destructive nature of updateForm.

# Step 1. Fetch Current State: Call getAllFormsByUid to find the correct form and, most importantly, retrieve its entire current questions list.

# Step 2. Generate New Elements: If the user is adding questions, call the appropriate add...Element tool to generate the JSON for only the new questions.

# Step 3. Construct New State: Create a new, complete list in memory. This list must contain all the old questions from Step 1 (that are being kept) plus any new questions from Step 2 (or minus any questions to be removed).

# Step 4. Persist New State: Call updateForm with the formId and the complete new list from Step 3.

# Validation Rules
# Options Validation: You must not call addRadioElement, addSelectElement, or addMultiChoiceElement unless the user has provided at least two options. If they provide one or zero, you must ask for more options before calling the tool.

# Retrieval Tool: Always use getAllFormsByUid to find and retrieve form data. getFormById is not for data retrieval.

# User Confirmation: Before executing Workflow 2 (Modifying), which is destructive, you should confirm the final state with the user.

# Example: "Okay, I'm adding a 'Phone Number' field. The form will then have 3 questions: 'Name', 'Email', and 'Phone Number'. Is that correct?"
# """
SYSTEMPROMPT = """
<persona>
You are Form Architect AI. Your ONLY purpose is to assist users by executing tool calls.
You MUST follow the strict workflows defined below. You CANNOT respond to the user with "Done" or "Okay" until a full workflow is complete.
</persona>

<state_management_rules>
1.  **Local Generation Tools (In-Memory ONLY):**
    * `addTextElement`, `addRadioElement`, `addSelectElement`, `addMultiChoiceElement`, `addFileUploadElement`
    * These tools DO NOT save to the database. They ONLY return a JSON object.

2.  **Database Persistence Tools (Permanent Storage):**
    * `createNewForm`: Creates an EMPTY form with an empty 'questions' list.
    * `updateForm`: OVERWRITES the *entire* form, including the 'questions' list.
    * `getAllFormsByUid`: Fetches form data.
</state_management_rules>

<critical_rule_updateForm_is_destructive>
⚠️ The `updateForm` tool REPLACES the entire 'questions' list.
If you call `updateForm` with only one new question, you will DELETE all existing questions.
You MUST always provide the *complete, final list* of ALL questions (old and new) when calling `updateForm`.
</critical_rule_updateForm_is_destructive>

<mandatory_workflows>
You MUST follow these workflows precisely. You cannot stop mid-workflow.

<workflow name="Create New Form">
This is a multi-step process. You may not stop until Step 5 is complete.

1.  **Step 1: Create Shell**
    * **Action:** Call `createNewForm` with the user's `title`, `description`, etc.
    * **Output:** Get the `formId`.

2.  **Step 2: Generate ALL Questions**
    * **Action:** For *every* question the user wants, call the appropriate `add...Element` tool (e.g., `addTextElement`).
    * **Output:** Collect all the generated question JSON objects into a *local list variable* in memory.

3.  **Step 3: Compile Full Form Data**
    * **Action:** Create a single `formData` dictionary. This dictionary MUST contain the `title` and the *full list* of questions from Step 2.
    * **Example:** `{"title": "User's Title", "questions": [list_from_step_2]}`

4.  **Step 4: Confirm with User (MANDATORY)**
    * **Action:** Before saving, you MUST confirm the final state with the user.
    * **Your Response:** "Okay, I am ready to create the form 'User's Title' with the following X questions: [List of question labels]. Should I proceed?"

5.  **Step 5: Persist to Database (If Confirmed)**
    * **Action:** ONLY after the user says yes, call `updateForm` with the `formId` from Step 1 and the complete `formData` dictionary from Step 3.
</workflow>

<workflow name="Modify Existing Form">
This is also a multi-step process.

1.  **Step 1: Fetch Current State**
    * **Action:** Call `getAllFormsByUid` to find the form and retrieve its *entire* existing `questions` list. Let's call this `old_questions`.

2.  **Step 2: Generate New Elements (if adding)**
    * **Action:** If adding questions, call the appropriate `add...Element` tools.

3.  **Step 3: Construct New State**
    * **Action:** Create a *new* complete list (`new_questions`) in memory that contains all the `old_questions` (minus any removals) plus any new questions from Step 2.

4.  **Step 4: Confirm with User (MANDATORY)**
    * **Action:** You MUST confirm the final state.
    * **Your Response:** "Okay, I am about to update the form. It will now have X total questions: [List of all question labels in the new list]. This will overwrite the old version. Should I proceed?"

5.  **Step 5: Persist New State (If Confirmed)**
    * **Action:** ONLY after the user says yes, call `updateForm` with the `formId` and the complete `new_questions` list from Step 3.
</workflow>
</mandatory_workflows>

<validation_rules>
* **Options Rule:** Do NOT call `addRadioElement`, `addSelectElement`, or `addMultiChoiceElement` unless the user provides at least 2 options. If they don't, ask for more options first.
* **Retrieval Rule:** ALWAYS use `getAllFormsByUid` to find and retrieve form data.
</validation_rules>
"""

model = create_agent(
    model=llm,
    tools=[
        updateForm,
        createNewForm,
        addTextElement,
        addRadioElement,
        addSelectElement,
        addMultiChoiceElement,
        addFileUploadElement,
        getAllFormsByUid,
        getFormById,
        generateFormLink
    ],
    system_prompt=SYSTEMPROMPT,
)

chatHistory=[]

app=FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, PUT, DELETE, OPTIONS...
    allow_headers=["*"],            # e.g. Authorization, Content-Type
)

@app.get('/')
def getHome():
    return {'Status:':'200','Message':'server is working properly!'}

@app.get('/form/{formid}')
def getForm(formid:str):
    query = getFormByIdALT(formid)
    
    if isinstance(query, str):
        return {"error": query}

    try:
        results = query.get()

        if not results:
            return {"error": "Form not found", "formId": formid}
        
        doc = results[0]
        
        return doc.to_dict()

    except Exception as e:
        return {"error": f"An error occurred while fetching the document: {e}"}

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def handle_chat(request: ChatRequest):
    """
    This new endpoint handles chatting with the agent.
    """
    global chatHistory # Using the global history for this example
    
    # 1. Add the user's new message
    chatHistory.append(HumanMessage(content=request.message))
    
    graph_input = {"messages": chatHistory}
    
    try:
        # 2. Invoke the agent asynchronously
        response_state = await model.ainvoke(graph_input)
        
        # 3. Get the full, updated message list
        final_messages_list = response_state["messages"]
        
        # 4. Get the latest AI reply
        new_ai_message = final_messages_list[-1]
        
        # 5. Update the global history for the next turn
        chatHistory = final_messages_list
        
        if hasattr(new_ai_message, 'content'):
            return {"response": new_ai_message.content}
        else:
            # This happens if the agent ends on a tool call
            return {"response": "AI is processing (tool call)..."}

    except Exception as e:
        return {"error": f"An error occurred: {e}"}
    

@app.post("/forms/{form_id}/submit")
async def submit_form_response(
    form_id: str ,
    response_data: Dict[str, Any]
):
    """
    Submits a new response for a specific form.
    This will first VALIDATE the response, and if successful,
    save it to the 'responses' collection in Firebase.
    """
    if db is None:
        raise HTTPException(status_code=500, detail="Firebase connection not established.")

    # --- Step 1: Get the Form Structure ---
    # We use our mock DB. In a real app, you'd fetch from Firebase.
    # e.g., form_doc = db.collection('forms').document(form_id).get()
    # NEW, CORRECT LINES:
    form_doc_snapshot = db.collection('Forms').document(form_id).get()

    if not form_doc_snapshot.exists:
        raise HTTPException(status_code=404, detail=f"Form with ID '{form_id}' not found.")

    # Get the data from the document
    form_structure = form_doc_snapshot.to_dict()
    if not form_structure:
        raise HTTPException(status_code=404, detail=f"Form with ID '{form_id}' not found.")

    # --- Step 2: Validate the Response ---
    print(f"Validating response for form: {form_id}...")
    validation_errors = validate_response(form_structure, response_data)

    if validation_errors:
        print(f"Validation failed with {len(validation_errors)} errors.")
        # If there are errors, return a 400 Bad Request
        raise HTTPException(
            status_code=400,
            detail={
                "status": "validation_failed",
                "errors": validation_errors
            }
        )

    # --- Step 3: Save to Firebase (if validation passes) ---
    print("Validation passed! Saving to Firebase...")
    try:
        # We add the formId and a submission timestamp to the data
        data_to_save = response_data.copy()
        data_to_save["formId"] = form_id
        data_to_save["submittedAt"] = firestore.SERVER_TIMESTAMP

        # Add the data to the 'responses' collection.
        # .add() automatically generates a new document ID.
        _timestamp, doc_ref = db.collection("responses").add(data_to_save)

        print(f"Successfully saved response with ID: {doc_ref.id}")
        return {
            "status": "success",
            "message": "Response submitted successfully.",
            "formId": form_id,
            "responseId": doc_ref.id
        }
    except Exception as e:
        print(f"Error saving to Firebase: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save response: {e}")