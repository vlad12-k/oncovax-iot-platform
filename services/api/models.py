from typing import Optional

from pydantic import BaseModel, field_validator


class AcknowledgeRequest(BaseModel):
    acknowledged_by: str
    incident_note: Optional[str] = None

    @field_validator("acknowledged_by")
    @classmethod
    def acknowledged_by_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("acknowledged_by must not be empty")
        return v.strip()
