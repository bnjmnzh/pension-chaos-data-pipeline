{{ config(materialized='table') }}

SELECT 
    member_id,
    first_name,
    last_name,
    salary,
    status,
    batch_id,
    ingested_at,
    error_reasons
FROM {{ ref('int_members_validated') }}
WHERE is_quarantined