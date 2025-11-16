from typing import Optional
from .db import db
from google.cloud import firestore
from langchain.tools import tool

@tool
def createNewForm(uid:Optional[str],title:str,description:Optional[str],type:str)->str:
    """
    Creates a new form document in the Firestore 'Forms' collection.

    This function generates a new document ID, stores the form's metadata 
    (owner, title, description, type, creation timestamp), and initializes 
    an empty 'questions' list.

    Args:
        uid (Optional[str]): The user ID of the form's owner. Can be None.
        title (str): The main title of the form.
        description (Optional[str]): A brief description of the form. Can be None.
        type (str): The category or type of the form (e.g., "survey", "quiz", "registration").

    Returns:
        str: The unique document ID (formId) of the newly created form.
    """
    doc_ref=db.collection("Forms").document()
    new_form_id = doc_ref.id

    form = {
        "formId": new_form_id,            
        "createdAt": firestore.SERVER_TIMESTAMP, 
        "uid": uid,
        "type": type,                
        "title": title,
        "description": description,
        'questions':[]
    }
    doc_ref.set(form)
    return new_form_id