from pydantic import BaseModel, Field
from typing import Optional


class ParkModelArgs(BaseModel):
    park_code: Optional[str] = Field(description="Park code from NPS website")
    state_code: Optional[str] = Field(description="US state where the park is addressed")
    search_term: Optional[str] = Field(description="Term to search in the API output")
