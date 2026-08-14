from datetime import date
from enum import Enum
from pydantic import BaseModel, Field

class MemberStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEFERRED = "DEFERRED"
    RETIRED = "RETIRED"

class BasePensionMemberPayload(BaseModel):
    member_id: str = Field(
        description="Unique id for the pension plan member."
    )
    first_name: str
    last_name: str
    date_of_birth: date
    hire_date: date
    status: MemberStatus = Field(
        default=MemberStatus.ACTIVE,
        description="Current status of the member in the pension plan."
    )
    salary: int = Field(
        description="Annual pensionable earnings (stored as integer cents)."
    )
    service_years: float = Field(
        ge=0.0,
        description="Accrued pension service credit in years."
    )
    contribution_rate: float = Field(
        default=0.09,
        description="Member contribution rate percentage (e.g. 0.09 for 9%)."
    )
    city: str
    province: str = Field(default="ON")
    schema_version: str = Field(
        default="1.0",
        description="Version marker to test schema evolution."
    )