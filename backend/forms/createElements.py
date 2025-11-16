from typing import List
from .elements import ElementType, FileUplaodconfig,Options, Validation
from .db import db
import uuid
from langchain.tools import tool




# def validateAndAddElements(formId: str, form: List[dict]):
#     """
#     Validates each element in the form list and adds it to the database.

#     NOTE: This adds elements one by one. If one fails, others might
#     already be added. A safer approach is to validate all first,
#     then add all in a single DB transaction.
#     """
#     validation_errors = []

#     for i, element_data in enumerate(form):
#         element_type_str = element_data.get("type")

#         try:
#             element_type = ElementType(element_type_str)
#         except ValueError:
#             print(
#                 f"Error: Element {i} has invalid type '{element_type_str}'. Skipping."
#             )
#             validation_errors.append(
#                 {"index": i, "error": f"Invalid type: {element_type_str}"}
#             )
#             continue
#         match element_type:
#             case ElementType.TEXT:
#                 if not all(
#                     k in element_data for k in ["questionId", "label", "required"]
#                 ):
#                     print(
#                         f"Error: TEXT element {i} ('{element_data.get('questionId')}') is missing required fields. Skipping."
#                     )
#                     validation_errors.append(
#                         {
#                             "index": i,
#                             "id": element_data.get("questionId"),
#                             "error": "Missing required fields (questionId, label, required).",
#                         }
#                     )
#                     continue

#                 db.add_element_to_form(formId, element_data, order=i)

#             case ElementType.RADIO | ElementType.SELECT | ElementType.CHECKBOX:
#                 if not all(
#                     k in element_data
#                     for k in ["questionId", "label", "required", "options"]
#                 ):
#                     print(
#                         f"Error: {element_type.value} element {i} ('{element_data.get('questionId')}') is missing required fields. Skipping."
#                     )
#                     validation_errors.append(
#                         {
#                             "index": i,
#                             "id": element_data.get("questionId"),
#                             "error": "Missing required fields (questionId, label, required, options).",
#                         }
#                     )
#                     continue

#                 if (
#                     not isinstance(element_data["options"], list)
#                     or not element_data["options"]
#                 ):
#                     print(
#                         f"Error: {element_type.value} element {i} ('{element_data.get('questionId')}') 'options' must be a non-empty list. Skipping."
#                     )
#                     validation_errors.append(
#                         {
#                             "index": i,
#                             "id": element_data.get("questionId"),
#                             "error": "'options' must be a non-empty list.",
#                         }
#                     )
#                     continue

#                 valid_options = True
#                 for opt in element_data["options"]:
#                     if not isinstance(opt, dict) or not all(
#                         k in opt for k in ["label", "value"]
#                     ):
#                         print(
#                             f"Error: {element_type.value} element {i} ('{element_data.get('questionId')}') has an invalid option structure. Skipping."
#                         )
#                         validation_errors.append(
#                             {
#                                 "index": i,
#                                 "id": element_data.get("questionId"),
#                                 "error": "Invalid option structure. Must be {'label': ..., 'value': ...}.",
#                             }
#                         )
#                         valid_options = False
#                         break
#                 if not valid_options:
#                     continue

#                 db.add_element_to_form(formId, element_data, order=i)

#             case ElementType.FILE_UPLOAD:
#                 if not all(
#                     k in element_data for k in ["questionId", "label", "required"]
#                 ):
#                     print(
#                         f"Error: FILE_UPLOAD element {i} ('{element_data.get('questionId')}') is missing required fields. Skipping."
#                     )
#                     validation_errors.append(
#                         {
#                             "index": i,
#                             "id": element_data.get("questionId"),
#                             "error": "Missing required fields (questionId, label, required).",
#                         }
#                     )
#                     continue

#                 db.add_element_to_form(formId, element_data, order=i)

#             case _:
#                 print(
#                     f"Warning: No validation logic defined for type '{element_type.value}'. Skipping."
#                 )
#                 validation_errors.append(
#                     {
#                         "index": i,
#                         "id": element_data.get("questionId"),
#                         "error": f"No validation logic for type '{element_type.value}'.",
#                     }
#                 )
#                 pass

#     if validation_errors:
#         print(f"\nCompleted with {len(validation_errors)} errors.")
#         return {"status": "error", "errors": validation_errors}

#     print(
#         f"\nSuccessfully validated and added {len(form)} elements to form '{formId}'."
#     )
#     return {"status": "success"}


@tool
def addTextElement(label: str, required: bool):
    """
    Adds a text input element to the form.

    Args:
        label (str): The question or label displayed for the text input.
        required (bool): Whether this field must be filled out by the user.

    Returns:
        Dict[str, Any]: A dictionary representing the text element configuration.
    """
    return {
        "questionId": f"{str(uuid.uuid4())}",
        "label": label,
        "type": ElementType.TEXT,
        "required": required,
    }

@tool
def addRadioElement(label: str, required: bool,options:List[Options]):
    """
    Adds a radio button group element (single choice) to the form.

    Requires at least two options to be provided.

    Args:
        label (str): The question or label displayed for the radio group.
        required (bool): Whether one option must be selected.
        options (List[Options]): A list of option dictionaries (e.g., [{"value": "val1", "label": "Label 1"}, {"value": "val2", "label": "Label 2"}]).
                                 Must contain at least 2 options.

    Returns:
        Dict[str, Any]: A dictionary representing the radio element configuration.
    
    Raises:
        ValueError: If the 'options' list contains fewer than 2 items.
    """
    count = 0
    for i in options :                  
        count +=1
    if count < 2:
        raise ValueError ("Error occured: options need to be atleast 2. got less than 2.")
    return {
        "questionId": f"{str(uuid.uuid4())}",
        "label": label,
        "type": ElementType.RADIO,
        "required": required,
        "options": options 
    }

@tool
def addSelectElement(label: str, required: bool,options:List[Options]):
    """
    Adds a dropdown select element (single choice) to the form.

    Requires at least two options to be provided.

    Args:
        label (str): The question or label displayed for the select dropdown.
        required (bool): Whether one option must be selected.
        options (List[Options]): A list of option dictionaries (e.g., [{"value": "val1", "label": "Label 1"}, {"value": "val2", "label": "Label 2"}]).
                                 Must contain at least 2 options.

    Returns:
        Union[Dict[str, Any], str]: A dictionary representing the select element configuration,
                                    or an error string if fewer than 2 options are provided.
    """
    count = 0
    for i in options :                  
        count +=1
    if count < 2:
        return "Error occured: options need to be atleast 2. got less than 2."
    return {
        "questionId": f"{str(uuid.uuid4())}",
        "label": label,
        "type": ElementType.SELECT,
        "required": required,
        "options": options 
    }

@tool
def addMultiChoiceElement(label: str, required: bool,options:List[Options],validation:Validation):
    """
    Adds a checkbox group element (multiple choices allowed) to the form.

    Requires at least two options to be provided.

    Args:
        label (str): The question or label displayed for the checkbox group.
        required (bool): Whether at least one option must be selected (if not overridden by validation).
        options (List[Options]): A list of option dictionaries (e.g., [{"value": "val1", "label": "Label 1"}, {"value": "val2", "label": "Label 2"}]).
                                 Must contain at least 2 options.
        validation (Validation): A dictionary specifying selection rules 
                                 (e.g., {"min_select": 1, "max_select": 3}).

    Returns:
        Union[Dict[str, Any], str]: A dictionary representing the multichoice element configuration,
                                    or an error string if fewer than 2 options are provided.
    """
    count = 0
    for i in options :                  
        count +=1
    if count < 2:
        return "Error occured: options need to be atleast 2. got less than 2."
    return {
        "questionId": f"{str(uuid.uuid4())}",
        "label": label,
        "type": ElementType.CHECKBOX,
        "required": required,
        "options": options,
        "validation":validation
    }

@tool
def addFileUploadElement(label: str, required: bool,fileUploadConfig:FileUplaodconfig):
    """
    Adds a file upload element to the form.

    Args:
        label (str): The question or label displayed for the file upload.
        required (bool): Whether a file must be uploaded.
        fileUploadConfig (FileUplaodconfig): A dictionary specifying upload constraints 
                                             (e.g., {"allowed_types": ["pdf"], "max_size_mb": 5}).

    Returns:
        Dict[str, Any]: A dictionary representing the file upload element configuration.
    """
    return {
        "questionId": f"{str(uuid.uuid4())}",
        "label": label,
        "type": ElementType.FILEUPLOAD,
        "required": required,
        "config":fileUploadConfig
    }

# def createElements()
# @tool