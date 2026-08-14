from typing import Any, Optional
import random


from app.schemas.base_event import BasePensionMemberPayload
from app.schemas.chaos_config import ChaosConfig


CRITICAL_KEYS = {"member_id", "schema_version", "first_name", "last_name"}

def inject_nulls(record_dict: dict, null_rate: float = 0.05) -> dict:
    if random.random() >= null_rate:
        return record_dict
    
    mutated_record = record_dict.copy()

    nullable_candidates = [
        key for key in mutated_record.keys()
        if key not in CRITICAL_KEYS and mutated_record[key] is not None
    ]

    if nullable_candidates:
        num_fields_to_null = random.randint(1, min(2, len(nullable_candidates)))
        
        target_keys = random.sample(nullable_candidates, k=num_fields_to_null)
        for key in target_keys:
            mutated_record[key] = None

    return mutated_record

def inject_schema_drift(record_dict: dict, drift_type: Optional[str] = None) -> dict:
    strategies = {
        "addition": _apply_column_addition,
        "mutation": _apply_type_mutation,
        "rename": _apply_column_rename,
    }

    selected_type = drift_type or random.choice(list(strategies.keys()))
    transform_fn = strategies.get(selected_type, _apply_column_addition)

    return transform_fn(record_dict)

def _apply_column_addition(record_dict: dict[str, Any]) -> dict[str, Any]:
    mutated = record_dict.copy()
    mutated["schema_version"] = "1.1_drift_added_field"

    first = mutated.get("first_name", "member").lower()
    last = mutated.get("last_name", "user").lower()
    mutated["email"] = f"{first}.{last}@example.com"
    return mutated

def _apply_type_mutation(record_dict: dict[str, Any]) -> dict[str, Any]:
    mutated = record_dict.copy()
    mutated["schema_version"] = "1.1_drift_type_mutation"
    
    salary = mutated.get("salary")
    if isinstance(salary, (int, float)):
        mutated["salary"] = f"${salary:,.2f}"
    else:
        mutated["salary"] = "$85,000.00"
        
    return mutated

def _apply_column_rename(record_dict: dict[str, Any]) -> dict[str, Any]:
    mutated = record_dict.copy()
    mutated["schema_version"] = "1.1_drift_column_rename"
    
    if "city" in mutated:
        mutated["work_location"] = mutated.pop("city")

    if "salary" in mutated:
        mutated["earnings"] = mutated.pop("salary")
        
    return mutated

def inject_salary_outlier(record_dict: dict) -> dict:
    mutated = record_dict.copy()

    target_key = "earnings" if "earnings" in mutated else "salary"
    mutated[target_key] = 1000000 * 100
    return mutated

def inject_duplicates(records: list[dict], duplicate_rate: float = 0.02) -> list[dict]:
    mutated_records = records.copy()
    num_duplicates = int(len(records) * duplicate_rate)

    if num_duplicates > 0 and records:
        duplicates = random.choices(records, k=num_duplicates)
        mutated_records.extend(duplicates)

    return mutated_records

def apply_chaos(records: list[BasePensionMemberPayload], config: ChaosConfig) -> list[dict]:
    mutated_batch = []
    
    for record in records:
        current_record = record.dict()
        if random.random() < getattr(config, "drift_rate", 0.0):
            current_record = inject_schema_drift(current_record)

        if random.random() < getattr(config, "null_rate", 0.0):
            current_record = inject_nulls(current_record, null_rate=1.0)

        if random.random() < getattr(config, "outlier_rate", 0.0):
            current_record = inject_salary_outlier(current_record)

        mutated_batch.append(current_record)

    dup_rate = getattr(config, "duplicate_rate", 0.0)
    if dup_rate > 0:
        mutated_batch = inject_duplicates(mutated_batch, duplicate_rate=dup_rate)

    return mutated_batch