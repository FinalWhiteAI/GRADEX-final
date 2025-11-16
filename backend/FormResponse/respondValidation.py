from typing import Any, Dict, List
from fastapi import HTTPException



def validate_response(form_structure: dict, response_data: dict) -> List[str]:
    """
    Checks a response against a form structure and returns a list of errors.
    An empty list means the validation passed.
    """
    errors = []
    questions = form_structure.get("questions", [])

    for question in questions:
        q_id = question.get("questionId")
        q_label = question.get("label")
        q_type = question.get("type")
        q_is_required = question.get("required", False)

        answer_data = response_data.get(q_id)
        answer_value = answer_data.get("Answer") if answer_data else None

        is_empty = (
            answer_value is None or
            (isinstance(answer_value, str) and answer_value.strip() == "") or
            (isinstance(answer_value, list) and len(answer_value) == 0)
        )

        if q_is_required and is_empty:
            errors.append(f"{q_label} ({q_id}) is required but was left empty.")
            continue  

        if not q_is_required and is_empty:
            continue

        if q_type.lower() != answer_data.get("type", "").lower():
            errors.append(f"Type mismatch for {q_label} ({q_id}). Form expects '{q_type}', but response gave '{answer_data.get('type')}'")
            continue
        
        
        if q_type in ("radio", "select"):
            valid_values = [opt['value'] for opt in question.get("options", [])]
            if answer_value not in valid_values:
                errors.append(f"Invalid option '{answer_value}' for {q_label} ({q_id}).")

        elif q_type == "checkbox":
            if not isinstance(answer_value, list):
                errors.append(f"{q_label} ({q_id}) answer must be a list, but got {type(answer_value)}.")
                continue

            valid_values = [opt['value'] for opt in question.get("options", [])]
            for selected_option in answer_value:
                if selected_option not in valid_values:
                    errors.append(f"Invalid option '{selected_option}' for {q_label} ({q_id}).")

            validation_rules = question.get("validation", {})
            min_sel = validation_rules.get("minSelections")
            max_sel = validation_rules.get("maxSelections")
            
            if min_sel is not None and len(answer_value) < min_sel:
                errors.append(f"{q_label} ({q_id}) requires at least {min_sel} selections.")
            if max_sel is not None and len(answer_value) > max_sel:
                errors.append(f"{q_label} ({q_id}) allows at most {max_sel} selections.")

        elif q_type == "fileUpload":
            if not isinstance(answer_value, list):
                errors.append(f"{q_label} ({q_id}) answer must be a list of URLs, but got {type(answer_value)}.")
                continue
            
            config = question.get("config", {})
            max_files = config.get("maxFiles")
            if max_files is not None and len(answer_value) > max_files:
                errors.append(f"{q_label} ({q_id}) allows at most {max_files} file(s).")

    return errors

