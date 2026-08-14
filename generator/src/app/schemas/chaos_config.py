from pydantic import BaseModel, Field

class ChaosConfig(BaseModel):
    """Configuration rates for injecting synthetic anomalies and schema drift."""

    drift_rate: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="Probability (0.0 to 1.0) of applying schema drift",
    )
    null_rate: float = Field(
        default=0.02,
        ge=0.0,
        le=1.0,
        description="Probability (0.0 to 1.0) of setting some fields to None.",
    )
    outlier_rate: float = Field(
        default=0.01,
        ge=0.0,
        le=1.0,
        description="Probability (0.0 to 1.0) of setting an extreme salary outlier.",
    )
    duplicate_rate: float = Field(
        default=0.01,
        ge=0.0,
        le=1.0,
        description="Percentage (0.0 to 1.0) of extra duplicate records to append to the batch.",
    )