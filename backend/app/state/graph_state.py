from dataclasses import dataclass,field
from typing import Dict,List,Optional

from app.models.chat_models import ChatMessage,SearchResult

"""
dataclass is  used to reduce boilerplate when creating classes that 
primarily store data. It automatically generates special 
methods like __init__, __repr__, and __eq__ based on 
type-annotated fields, making classes cleaner and easier to maintain 
"""

"""
the decorater @dataclass AUTOGENERATES the 
__init__()constructor,
__repr__()readable string representation
__eq__()equality comparison
"""

"""
contains SERIALIZATION HELPERS :

dataclasses.asdict() → convert instance to dictionary.
dataclasses.astuple() → convert instance to tuple.

"""
@dataclass
class GraphState:
    conversation_id :str
    user_message:str
    history : List[ChatMessage]
    conversation_context :List[Dict[str,str]]=field(default_factory=list)
    route :str ="summary"
    summary_output : str = ""
    search_output : str = ""
    search_results : List[SearchResult]=field(default_factory=list)
    final_answer : str =""
