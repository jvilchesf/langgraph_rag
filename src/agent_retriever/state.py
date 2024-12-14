from dataclasses import dataclass, field
from typing import Optional, Sequence, Annotated, List, Any

def string_reducer(
        existing: Optional[Sequence[str]],
        new: str
) -> Sequence[str]:
    """
    Reducers help to add new messages in the state and not overwrite them
    """
    if existing is None:
        existing = []
    if isinstance(new, str):
        existing.append(new)
    return existing


@dataclass(kw_only=True)
class ShareState:
    """
    State to transport the content result among the nodes
    """
    Content: Optional[
        List[Any]
        #Annotated[Sequence[str], string_reducer]
        ] = field(default_factory=list)   
    #Content: Annotated[Sequence[str], string_reducer]  
    ProcessStatus: Optional[
        Annotated[Sequence[str], string_reducer]
        ]

