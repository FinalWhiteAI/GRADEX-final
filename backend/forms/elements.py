from enum import Enum
from typing import List, Union
from pydantic import BaseModel, Field
class ElementType(Enum):
    TEXT ="text"
    RADIO="radio"
    SELECT="select"
    CHECKBOX="checkbox"
    FILEUPLOAD="fileupload"


class Options(BaseModel):
    label:str
    value:str


class Validation(BaseModel):
    minSelections:int
    maxSelections:int

class FileUplaodconfig(BaseModel):
    allowedFileTypes: Union[List[str], str] = Field(default="*")
    maxFiles:int=1