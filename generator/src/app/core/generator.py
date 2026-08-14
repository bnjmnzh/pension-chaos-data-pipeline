from datetime import date, timedelta
from random import choices, randint, randbytes, seed as set_random_seed
from typing import Optional

import uuid

from faker import Faker

from src.app.schemas.base_event import MemberStatus, BasePensionMemberPayload


fake = Faker("en_CA")


def generate_member_id() -> str:
    return str(uuid.UUID(bytes=randbytes(16)))

def generate_birth_hire_dates() -> tuple[date, date]:
    birth_date = fake.date_of_birth(minimum_age=22, maximum_age=65)
    min_hire_date = birth_date + timedelta(days=18 * 365)
    hire_date = fake.date_between(start_date=min_hire_date, end_date="today")
    return birth_date, hire_date

def calculate_service_years(hire_date: date) -> float:
    today = date.today()
    service_years = (today - hire_date).days / 365.25
    return round(service_years, 2)

def generate_single_member() -> BasePensionMemberPayload:
    member_id = generate_member_id()
    first_name = fake.first_name()
    last_name = fake.last_name()
    date_of_birth, hire_date = generate_birth_hire_dates()
    status = choices(
        [MemberStatus.ACTIVE, MemberStatus.DEFERRED, MemberStatus.RETIRED],
        weights=[70, 20, 10],
        k=1,
    )[0]
    salary = randint(50000, 100000) * 100  # Salary in cents
    service_years = calculate_service_years(hire_date)
    contribution_rate = 0.09
    city = fake.city()
    province = "ON"
    schema_version = "1.0"

    return BasePensionMemberPayload(
        member_id=member_id,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        hire_date=hire_date,
        status=status,
        salary=salary,
        service_years=service_years,
        contribution_rate=contribution_rate,
        city=city,
        province=province,
        schema_version=schema_version
    )

def generate_member_batch(num_records: int, seed: Optional[int] = None) -> list[BasePensionMemberPayload]:
    if seed is not None:
        Faker.seed(seed)
        fake.seed_instance(seed)
        set_random_seed(seed)
    return [generate_single_member() for _ in range(num_records)]