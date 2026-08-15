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
        (payload->>'member_id')::INT as member_id,
        payload->>'first_name' as first_name,
        payload->>'last_name' as last_name,
        REGEXP_REPLACE(COALESCE(
            payload->>'salary',
            payload->>'earnings'), '[,$]', '', 'g')::NUMERIC(10, 2) as salary,
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
    PARTITION BY payload->>'member_id'
    ORDER BY ingested_at DESC, raw_id DESC
) AS row_num
    FROM raw_source
),

deduped AS (
    SELECT * FROM extracted
    WHERE row_num = 1
)

SELECT * FROM deduped