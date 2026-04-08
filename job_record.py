from pydantic import BaseModel
from typing import Optional


class JobRecord(BaseModel):
    id: str
    title: str
    level: Optional[str] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    tech_stack: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
