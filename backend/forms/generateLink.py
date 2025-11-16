import os
from dotenv import load_dotenv
from langchain.tools import tool


load_dotenv()

@tool
def generateFormLink(formId:str):
    """
    Generates a shareable link for a specific form ID.
    """
    base_url = os.environ.get("BACKEND_URL") 

    if not base_url:
        return "Error: BACKEND_URL environment variable is not set."
    link=base_url+"/form/"+formId
    return link