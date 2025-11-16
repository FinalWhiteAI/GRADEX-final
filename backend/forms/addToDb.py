from .db import db
from typing import List, Dict, Any
from .elements import ElementType
from langchain.tools import tool

def validateQuestionsList(form_elements: List[dict]) -> dict:
    """
    Validates a list of question elements based on your sample JSON.
    It collects *all* errors, not just the first one.
    Returns a dictionary with 'status' and 'errors' or 'elements'.
    """
    validation_errors = []
    validated_elements_with_order = []

    if not form_elements:
        return {"status": "error", "errors": [{"index": 0, "id": "general", "error": "Form must have at least one question."}]}

    for i, element_data in enumerate(form_elements):
        has_error = False  
        element_type_str = element_data.get("type")
        question_id = element_data.get("questionId", f"unknown_at_index_{i}")

        try:
            element_type = ElementType(element_type_str)
        except ValueError:
            validation_errors.append(
                {"index": i, "id": question_id, "error": f"Invalid type: '{element_type_str}'."}
            )
            continue

        if not all(k in element_data for k in ["questionId", "label", "required"]):
            validation_errors.append({
                "index": i, "id": question_id,
                "error": "Missing required fields (questionId, label, required)."
            })
            has_error = True

        match element_type:
            case ElementType.TEXT:
                pass

            case ElementType.FILEUPLOAD:
                if "config" in element_data and not isinstance(element_data["config"], dict):
                    validation_errors.append({"index": i, "id": question_id, "error": "'config' must be a dictionary (or null)."})
                    has_error = True
            
            case ElementType.RADIO | ElementType.SELECT | ElementType.CHECKBOX:
                if "options" not in element_data:
                    validation_errors.append({"index": i, "id": question_id, "error": "Missing required field: options."})
                    has_error = True
                else:
                    options = element_data["options"]
                    if (not isinstance(options, list) or len(options) < 2):
                        validation_errors.append({"index": i, "id": question_id, "error": "'options' must be a list with at least 2 items."})
                        has_error = True
                    else:
                        for opt_idx, opt in enumerate(options):
                            if not (isinstance(opt, dict) and "label" in opt and "value" in opt):
                                validation_errors.append({"index": i, "id": question_id, "error": f"Invalid option structure at option {opt_idx}. Must be {{'label': ..., 'value': ...}}."})
                                has_error = True 
                                break 
                
                if element_type in (ElementType.CHECKBOX, ElementType.CHECKBOX) and "validation" in element_data:
                     if not isinstance(element_data["validation"], dict):
                        validation_errors.append({"index": i, "id": question_id, "error": "'validation' must be a dictionary (or null)."})
                        has_error = True

            case _:
                validation_errors.append({
                    "index": i, "id": question_id,
                    "error": f"No validation logic for unknown type '{element_type.value}'."
                })
                has_error = True
        
        if not has_error:
            element_data_with_order = element_data.copy()
            element_data_with_order["order"] = i
            validated_elements_with_order.append(element_data_with_order)
    
    if validation_errors:
        return {"status": "error", "errors": validation_errors}

    return {"status": "success", "elements": validated_elements_with_order}


@tool
def updateForm(formId: str, formData: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates specific fields of an existing form document in Firestore after validating its questions.

    This tool attempts to update a form specified by 'formId'. It extracts 'title', 
    'description', 'formType', and 'questions' from the 'formData' dictionary.
    
    The 'questions' list undergoes validation using the 'validateQuestionsList' helper 
    function. If validation fails, the update is aborted, and an error dictionary 
    is returned.
    
    If validation succeeds, the form document is updated with the validated questions 
    and the other provided metadata.

    Args:
        formId (str): The unique document ID of the form to update.
        formData (Dict[str, Any]): A dictionary containing the data to update.
            Expected keys:
            - "title" (Optional[str]): The new title for the form.
            - "description" (Optional[str]): The new description for the form.
            - "formType" (Optional[str]): The new type for the form (e.g., "survey").
            - "questions" (List[Dict]): A list of question element dictionaries 
                                        to be validated and set as the new questions.

    Returns:
        Dict[str, Any]: A dictionary indicating the result.
        - On success: {"status": "success", "formId": str, "message": str}
        - On validation failure: {"status": "error", "errors": ...} (from validateQuestionsList)
        - On unexpected exception: {"status": "error", "error": str}
    """
    try:
        doc_ref = db.collection("Forms").document(formId)

        questions_list = formData.get("questions", [])
        
        validation_result = validateQuestionsList(questions_list) 
        
        if validation_result["status"] == "error":
            print(f"Validation failed for form {formId}: {validation_result['errors']}")
            return validation_result

        validated_questions = validation_result["elements"]

        update_payload = {
            "title": formData.get("title", "Untitled Form"),
            "description": formData.get("description", ""),
            "formType": formData.get("formType", "survey"), 
            "questions": validated_questions  
        }
        
        doc_ref.update(update_payload)
        
        return {
            "status": "success",
            "formId": formId,
            "message": f"Successfully updated form with {len(validated_questions)} elements."
        }
    
    except Exception as e:
        print(f"Error updating form {formId}: {e}")
        return {"status": "error", "error": f"An unexpected error occurred: {e}"}