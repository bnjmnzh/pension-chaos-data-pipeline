from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.chaos_config import ChaosConfig

class GeneratorRequest(BaseModel):
    """Payload to trigger member data generation."""

    num_records: int = Field(
        default=100,
        gt=1,
        le=10000,
        description="Number of records to generate."
    )
    seed: Optional[int] = Field(
        default=None,
        description="Optional seed for reproducible outputs."
    )
    chaos: ChaosConfig = Field(
        default_factory=ChaosConfig,
        description="Anomaly and schema drift injection configuration.",
    )
