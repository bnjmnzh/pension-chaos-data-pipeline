"""tests/test_generator.py

Unit tests for the synthetic data generator core module.
"""

from datetime import date
from src.app.schemas.base_event import BasePensionMemberPayload, MemberStatus
from src.app.core.generator import (
    calculate_service_years,
    generate_birth_hire_dates,
    generate_member_batch,
    generate_member_id,
    generate_single_member,
)


def test_generate_member_id_format():
    """Verify generated member ID returns a non-empty string."""
    member_id = generate_member_id()
    assert isinstance(member_id, str)
    assert len(member_id) > 0


def test_generate_birth_hire_dates_logic():
    """Verify that hire date is strictly after birth date and member is at least 18 years old at hire."""
    birth_date, hire_date = generate_birth_hire_dates()

    assert isinstance(birth_date, date)
    assert isinstance(hire_date, date)
    assert hire_date > birth_date

    # Member must be at least 18 years old at hire
    age_at_hire = (hire_date - birth_date).days / 365.25
    assert age_at_hire >= 18.0


def test_calculate_service_years():
    """Verify service years calculation returns non-negative rounded float."""
    past_hire_date = date(2020, 1, 1)
    service_years = calculate_service_years(past_hire_date)

    assert isinstance(service_years, float)
    assert service_years > 0.0


def test_generate_single_member_schema_validity():
    """Verify generate_single_member produces a valid BasePensionMemberPayload."""
    member = generate_single_member()

    assert isinstance(member, BasePensionMemberPayload)
    assert isinstance(member.status, MemberStatus)
    assert member.salary >= 50000
    assert member.contribution_rate == 0.09
    assert member.province == "ON"
    assert member.schema_version == "1.0"


def test_generate_member_batch_length():
    """Verify generated batch contains requested number of items."""
    count = 10
    batch = generate_member_batch(num_records=count)

    assert len(batch) == count
    assert all(isinstance(m, BasePensionMemberPayload) for m in batch)


def test_generate_member_batch_seed_reproducibility():
    """Verify that passing the same seed produces identical results."""
    seed_value = 42

    batch_1 = generate_member_batch(num_records=5, seed=seed_value)
    batch_2 = generate_member_batch(num_records=5, seed=seed_value)

    # Convert Pydantic models to dicts for direct comparison
    data_1 = [m.model_dump() for m in batch_1]
    data_2 = [m.model_dump() for m in batch_2]

    assert data_1 == data_2