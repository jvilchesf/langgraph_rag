from __future__ import annotations

from dataclasses import dataclass, fields, field
from typing import Optional, TypeVar, Type, Annotated

from langchain_core.runnables import RunnableConfig, ensure_config

@dataclass(kw_only=True)
class DatabaseConfiguration:
    """Class containing agent project variables"""

    db_path : str = field(
        default= 'src/agent_retriever/data/augmented_data.sqlite',
        metadata= (
            {"description": "Path folder is where the retrieved data is saved"}
        )
    )

    response_model: Annotated[
        str,
        {"__template_metadata__": {"kind":"llm"}}
    ] = field(
        default="openai/gpt-3.5-turbo",
        metadata = {
            "description": "Model used by the agent"
            },
    )

    @classmethod
    def from_runnable_config(
        cls: Type[T],
        config: Optional[RunnableConfig] = None
    ) -> T: 
        
        config = ensure_config(config)
        configurable_data = config.get("configurable_data") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable_data.items() if k in _fields})

T = TypeVar("T", bound=DatabaseConfiguration)