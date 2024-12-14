from __future__ import annotations
import os

from dataclasses import dataclass, field, fields
from typing import Type, Optional, TypeVar,Annotated

from langchain_core.runnables import RunnableConfig, ensure_config

@dataclass(kw_only=True)
class RetrieverConfiguration:

    #Path
    path_folder : str = field(
        default= os.path.join(os.path.dirname(__file__), 'files'),
        metadata= (
            {"description": "Path folder is where the retrieved data is saved"}
        )
    )

    response_model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
    default="openai/gpt-4o",
    metadata={
        "description": "The language model used for generating responses. Should be in the form: provider/model-name."
            },
    )

    @classmethod
    def from_runnable_config(
        cls: Type[T], config: Optional[RunnableConfig] = None
    ) -> T:
        """Create an IndexConfiguration instance from a RunnableConfig object.

        Args:
            cls (Type[T]): The class itself.
            config (Optional[RunnableConfig]): The configuration object to use.

        Returns:
            T: An instance of IndexConfiguration with the specified configuration.
        """
        config = ensure_config(config)
        configurable_data = config.get("configurable_data") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable_data.items() if k in _fields})


T = TypeVar("T", bound=RetrieverConfiguration)