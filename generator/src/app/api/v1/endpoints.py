from app.core.chaos import apply_chaos
from app.core.generator import generate_member_batch
from app.schemas.base_event import BasePensionMemberPayload
from fastapi import APIRouter, HTTPException
from app.schemas.generator_request import GeneratorRequest
from app.schemas.generator_response import GeneratorResponse
from http import HTTPStatus

router = APIRouter(prefix="/members", tags=["Member Data Generation"])

@router.post("/generate",
    response_model=GeneratorResponse,
    status_code=HTTPStatus.OK,
    summary="Generate batch of member records",)
def generate_events(request: GeneratorRequest) -> GeneratorResponse:
    # 1. Generate clean synthetic records
    clean_records: list[BasePensionMemberPayload] = generate_member_batch(
        num_records=request.num_records,
        seed=request.seed,
    )

    # 2. Apply chaos transformations
    chaos_active = any(
        [
            request.chaos.drift_rate > 0,
            request.chaos.null_rate > 0,
            request.chaos.outlier_rate > 0,
            request.chaos.duplicate_rate > 0,
        ]
    )

    final_data = apply_chaos(clean_records, request.chaos)
    return GeneratorResponse(
        total_records=len(final_data),
        chaos_enabled=chaos_active,
        data=final_data,
    )