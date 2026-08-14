import pytest
from src.app.schemas.base_event import BasePensionMemberPayload
from src.app.schemas.chaos_config import ChaosConfig
from src.app.core.chaos import (
    CRITICAL_KEYS,
    apply_chaos,
    inject_duplicates,
    inject_nulls,
    inject_salary_outlier,
    inject_schema_drift,
)


@pytest.fixture
def sample_clean_record_dict():
    return {
        "member_id": "123456789",
        "first_name": "Arthur",
        "last_name": "Pendragon",
        "date_of_birth": "1988-04-12",
        "hire_date": "2015-09-01",
        "status": "ACTIVE",
        "salary": 9500000,
        "service_years": 8.5,
        "contribution_rate": 0.09,
        "city": "Toronto",
        "province": "ON",
        "schema_version": "1.0",
    }


@pytest.fixture
def sample_member_payload():
    return BasePensionMemberPayload(
        member_id="123456789",
        first_name="Arthur",
        last_name="Pendragon",
        date_of_birth="1988-04-12",
        hire_date="2015-09-01",
        status="ACTIVE",
        salary=9500000,
        service_years=8.5,
        contribution_rate=0.09,
        city="Toronto",
        province="ON",
        schema_version="1.0",
    )


def test_inject_nulls_bypasses_when_rate_zero(sample_clean_record_dict):
    """Verify that null rate of 0.0 leaves the record unchanged."""
    result = inject_nulls(sample_clean_record_dict, null_rate=0.0)
    assert result == sample_clean_record_dict


def test_inject_nulls_preserves_critical_keys(sample_clean_record_dict):
    """Verify critical identity keys are never set to None even when null rate is 100%."""
    # Force null injection by setting rate to 1.0
    result = inject_nulls(sample_clean_record_dict, null_rate=1.0)

    # Check critical keys remain non-None
    for key in CRITICAL_KEYS:
        assert result[key] is not None

    # Check that at least one non-critical key became None
    null_keys = [k for k, v in result.items() if v is None]
    assert len(null_keys) >= 1
    assert all(k not in CRITICAL_KEYS for k in null_keys)


def test_inject_schema_drift_addition(sample_clean_record_dict):
    """Verify Type A drift appends email and updates schema version."""
    result = inject_schema_drift(sample_clean_record_dict, drift_type="addition")

    assert result["schema_version"] == "1.1_drift_added_field"
    assert "email" in result
    assert result["email"] == "arthur.pendragon@example.com"


def test_inject_schema_drift_mutation(sample_clean_record_dict):
    """Verify Type B drift converts numeric salary to formatted string."""
    result = inject_schema_drift(sample_clean_record_dict, drift_type="mutation")

    assert result["schema_version"] == "1.1_drift_type_mutation"
    assert isinstance(result["salary"], str)
    assert result["salary"].startswith("$")


def test_inject_schema_drift_rename(sample_clean_record_dict):
    """Verify Type C drift renames city -> work_location and salary -> earnings."""
    result = inject_schema_drift(sample_clean_record_dict, drift_type="rename")

    assert result["schema_version"] == "1.1_drift_column_rename"
    assert "city" not in result
    assert "salary" not in result
    assert "work_location" in result
    assert "earnings" in result
    assert result["work_location"] == "Toronto"


def test_inject_salary_outlier(sample_clean_record_dict):
    """Verify salary outlier mutates salary to 1,000,000 dollars in cents."""
    result = inject_salary_outlier(sample_clean_record_dict)
    assert result["salary"] == 100_000_000


def test_inject_duplicates():
    """Verify duplicates expand the batch size according to the rate."""
    batch = [{"member_id": f"M1000{i}"} for i in range(10)]
    duplicated_batch = inject_duplicates(batch, duplicate_rate=0.2)

    assert len(duplicated_batch) == 12


def test_apply_chaos_zero_rates(sample_member_payload):
    """Verify zero anomaly rates return pure dict conversion without mutation."""
    records = [sample_member_payload]
    config = ChaosConfig(
        drift_rate=0.0,
        null_rate=0.0,
        outlier_rate=0.0,
        duplicate_rate=0.0,
    )

    result = apply_chaos(records, config)

    assert len(result) == 1
    assert result[0] == sample_member_payload.model_dump()


def test_apply_chaos_full_mutation(sample_member_payload):
    """Verify 100% drift rate mutates all records in the batch."""
    records = [sample_member_payload for _ in range(5)]
    config = ChaosConfig(
        drift_rate=1.0,
        null_rate=0.0,
        outlier_rate=0.0,
        duplicate_rate=0.0,
    )

    result = apply_chaos(records, config)

    assert len(result) == 5
    for item in result:
        assert item["schema_version"].startswith("1.1_drift")