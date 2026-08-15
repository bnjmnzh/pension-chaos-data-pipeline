{{ config(materialized='ephemeral') }}

WITH raw_source AS (
    SELECT 
        id AS raw_id,
        batch_id,
        payload,
        ingested_at
    FROM {{ source('raw_data', 'members') }}
),

extracted AS (
    SELECT
        payload->>'member_id' as member_id,
        payload->>'first_name' as first_name,
        payload->>'last_name' as last_name,
        REGEXP_REPLACE(COALESCE(
            payload->>'salary',
            payload->>'earnings'), '[,$]|\.\d+', '', 'g')::INT as salary,
        (payload->>'date_of_birth')::DATE as date_of_birth,
        (payload->>'hire_date')::DATE as hire_date,
        payload->>'status' as status,
        (payload->>'service_years')::NUMERIC(5, 2) as service_years,
        (payload->>'contribution_rate')::NUMERIC(5, 2) as contribution_rate,
        COALESCE(
            payload->>'city',
            payload->>'work_location'
        ) as city,
        payload->>'province' as province,
        payload->>'schema_version' as schema_version,
        batch_id,
        ingested_at,
        ROW_NUMBER() OVER (
            PARTITION BY COALESCE(payload->>'member_id', raw_id::text)
            ORDER BY ingested_at DESC, raw_id DESC
        ) AS row_num
    FROM raw_source
),

deduped AS (
    SELECT * FROM extracted
    WHERE row_num = 1
),

validated AS (
    SELECT 
        member_id,
        first_name,
        last_name,
        salary,
        date_of_birth,
        hire_date,
        status,
        service_years,
        contribution_rate,
        city,
        province,
        schema_version,
        batch_id,
        ingested_at,
        ARRAY_REMOVE(
            ARRAY[
                CASE WHEN member_id IS NULL THEN 'MISSING_MEMBER_ID' END,
                CASE WHEN status IS NULL THEN 'MISSING_STATUS' END,
                CASE WHEN status IS NOT NULL AND UPPER(status) NOT IN ('ACTIVE', 'DEFERRED', 'RETIRED') THEN 'INVALID_STATUS' END,
                CASE WHEN UPPER(status) = 'ACTIVE' AND salary IS NULL THEN 'MISSING_SALARY_FOR_ACTIVE' END,
                CASE WHEN salary IS NOT NULL AND salary < 0 THEN 'NEGATIVE_SALARY' END,
                CASE WHEN date_of_birth IS NULL THEN 'INVALID_DATE_OF_BIRTH' END,
                CASE WHEN hire_date IS NULL THEN 'INVALID_HIRE_DATE' END
            ],
            NULL
        ) AS error_reasons
    FROM deduped
)

SELECT 
    *,
    CASE 
        WHEN cardinality(error_reasons) > 0 THEN TRUE 
        ELSE FALSE 
    END AS is_quarantined
FROM validated