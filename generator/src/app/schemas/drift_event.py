from pydantic import BaseModel

from app.schemas.base_event import BasePensionMemberPayload

class DriftColumnAddition(BasePensionMemberPayload):
    schema_version: str = "1.1_drift_added_field"
    email: str # New field added to the schema

class DriftTypeMutation(BasePensionMemberPayload):
    schema_version: str = "1.1_drift_type_mutation"
    salary: str  # Changed from int to str

class DriftColumnRename(BaseModel):
    schema_version: str = "1.1_drift_column_rename"
    member_id: str
    first_name: str
    last_name: str
    date_of_birth: date
    hire_date: date
    status: MemberStatus
    earnings: int  # Renamed from salary
    service_years: float
    contribution_rate: float
    work_location: str  # Renamed from city
    province: str