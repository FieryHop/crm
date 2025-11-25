from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class OperatorBase(BaseModel):
    name: str
    is_active: bool = True
    max_load: int = 10


class OperatorCreate(OperatorBase):
    pass


class Operator(OperatorBase):
    id: int
    current_load: int = 0

    class Config:
        orm_mode = True


class LeadBase(BaseModel):
    external_id: str


class LeadCreate(LeadBase):
    pass


class Lead(LeadBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class SourceBase(BaseModel):
    name: str


class SourceCreate(SourceBase):
    pass


class Source(SourceBase):
    id: int

    class Config:
        orm_mode = True


class AssignmentBase(BaseModel):
    operator_id: int
    source_id: int
    weight: int = 1


class AssignmentCreate(AssignmentBase):
    pass


class Assignment(AssignmentBase):
    id: int

    class Config:
        orm_mode = True


class ContactResponse(BaseModel):
    id: int
    lead_id: int
    source_id: int
    operator_id: Optional[int] = None
    created_at: datetime
    lead_external_id: str

    class Config:
        orm_mode = True


class ContactCreate(BaseModel):
    lead_external_id: str
    source_id: int