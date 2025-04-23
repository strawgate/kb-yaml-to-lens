from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Optional, Union

class Grid(BaseModel):
    x: int
    y: int
    w: int
    h: int
    i: Optional[str] = None

    def set_i(self, i: str) -> 'Grid':
        """Set the unique identifier for the grid."""
        self.i = i
        return self
