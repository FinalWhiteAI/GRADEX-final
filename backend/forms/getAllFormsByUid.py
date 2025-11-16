import logging
from .db import db
from langchain.tools import tool

@tool
def getAllFormsByUid(uid:str):
    """
    Retrieves all forms from the 'Forms' collection where the 'uid' field matches.

    Queries the 'Forms' collection for documents where the 'uid' field 
    (note: not 'owner') matches the provided uid.

    Args:
        uid (str): The user ID to filter forms by (must match the 'uid' field).

    Returns:
        Optional[List[Dict[str, Any]]]: A list of dictionaries, where each dictionary 
        represents a form document (including its document ID as 'id'). 
        Returns an empty list if no forms are found.
        Returns None if a database error occurs.
    """
    try:
        print(f"DEBUG: {uid}")
        forms= db.collection("Forms").where("uid","==",uid).get()
        forms_list = []
        for doc in forms:
            form_data = doc.to_dict()
            form_data['id'] = doc.id  
            forms_list.append(form_data)
            
        return forms_list
    except Exception as e:
        logging.error(f"Error fetching forms for uid {uid}: {e}")
        return None
@tool    
def getFormById(formId:str):
    """
    Creates a query to find a form by its 'formId' field.

    IMPORTANT: This tool does NOT return the form data. It returns a 
    Firestore Query object. You must call .get() on the result to 
    fetch the actual documents.

    A more common way to get a document by its unique ID is:
    db.collection('Forms').document(formId).get()

    Args:
        formId (str): The value to match against the 'formId' field in the documents.

    Returns:
        Union[Query, str]: 
        - On success: A Firestore Query object (not the form data).
        - On failure: An error message string.
    """
    try:
        forms=db.collection('Forms').where("formId","==",formId)
        return forms
    except Exception as e:
        return f"Error occured : {e}"
        
def getFormByIdALT(formId:str):
    """
    Creates a query to find a form by its 'formId' field.

    IMPORTANT: This tool does NOT return the form data. It returns a 
    Firestore Query object. You must call .get() on the result to 
    fetch the actual documents.

    A more common way to get a document by its unique ID is:
    db.collection('Forms').document(formId).get()

    Args:
        formId (str): The value to match against the 'formId' field in the documents.

    Returns:
        Union[Query, str]: 
        - On success: A Firestore Query object (not the form data).
        - On failure: An error message string.
    """
    try:
        forms=db.collection('Forms').where("formId","==",formId)
        return forms 
    except Exception as e:
        return f"Error occured : {e}"