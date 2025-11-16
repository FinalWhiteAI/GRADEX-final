from signal import raise_signal
from .db import db
from typing import Dict, Any, List
from .elements import ElementType 
from langchain.tools import tool

@tool
def updateQuestion(formId: str, questionId: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates a single question within a form document in Firestore.

    :param formId: The ID of the form document to update.
    :param questionId: The 'questionId' of the element to find and update.
    :param updates: A dictionary of fields to change (e.g., {"label": "New Label", "required": True}).
    """
    
    doc_ref = db.collection("Forms").document(formId)

    try:
        doc = doc_ref.get()
        if not doc.exists:
            raise ValueError(f"Form with ID {formId} not found.")

        all_questions = doc.to_dict().get("questions", [])
        
        found = False
        updated_questions_list = []
        validation_error_report = None

        for i, original_question in enumerate(all_questions):
            if original_question.get("questionId") == questionId:
                found = True
                
                updated_question = original_question.copy()
                updated_question.update(updates)
                
                validation_result = validateSingleQuestion(updated_question)
                
                if validation_result["status"] == "error":
                    # Stop! The update is invalid.
                    validation_error_report = validation_result["errors"]
                    break  
                
                updated_question['order'] = i 
                updated_questions_list.append(updated_question)
            
            else:
                updated_questions_list.append(original_question)

        if validation_error_report:
            return {
                "status": "error",
                "message": f"Validation failed for update on question {questionId}.",
                "errors": validation_error_report
            }

        if not found:
            raise ValueError(f"Question with ID {questionId} not found in form {formId}.")

        doc_ref.update({"questions": updated_questions_list})
        
        return {
            "status": "success",
            "formId": formId,
            "questionId": questionId,
            "message": f"Successfully updated question."
        }
    
    except Exception as e:
        print(f"Error updating question {questionId} in form {formId}: {e}")
        raise ValueError(f"An unexpected error occurred: {e}") 

def validateSingleQuestion(element_data: dict) -> dict:
    """
    Validates a single question element dictionary.
    Returns a dictionary with 'status' and 'errors'.
    """
    question_id = element_data.get("questionId", "unknown")
    element_type_str = element_data.get("type")

    try:
        element_type = ElementType(element_type_str)
    except ValueError:
        raise ValueError(f"Invalid type: '{element_type_str}'.")

    if not all(k in element_data for k in ["questionId", "label", "required"]):
        raise ValueError("Missing required fields (questionId, label, required).")

    errors = []
    match element_type:
        case ElementType.TEXT:
            pass 

        case ElementType.FILEUPLOAD:
            if "config" in element_data and not isinstance(element_data.get("config"), (dict, type(None))):
                errors.append("'config' must be a dictionary (or null).")
        
        case ElementType.RADIO | ElementType.SELECT | ElementType.CHECKBOX | ElementType.MULTICHOICE:
            if "options" not in element_data:
                errors.append("Missing required field: options.")
            else:
                options = element_data["options"]
                if (not isinstance(options, list) or len(options) < 2):
                    errors.append("'options' must be a list with at least 2 items.")
                else:
                    for opt_idx, opt in enumerate(options):
                        if not (isinstance(opt, dict) and "label" in opt and "value" in opt):
                            errors.append(f"Invalid option structure at option {opt_idx}.")
                            break 
            
            if element_type in (ElementType.CHECKBOX, ElementType.MULTICHOICE) and "validation" in element_data:
                 if not isinstance(element_data.get("validation"), (dict, type(None))):
                    errors.append("'validation' must be a dictionary (or null).")
        case _:
            errors.append(f"No validation logic for unknown type '{element_type.value}'.")
    
    if errors:
        raise Exception(errors)
    
    return {"status": "success"}