SET client_encoding = 'UTF8';

-- results_record_db DDL for PostgreSQL 18.3
--
-- This DDL is for a seminar-oriented local PostgreSQL sample.
-- It intentionally favors clarity and traceability over production-grade generalization.

CREATE TABLE work_log (
    work_log_id BIGSERIAL PRIMARY KEY,

    order_no VARCHAR(30) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    process_name VARCHAR(30) NOT NULL,
    worker_name VARCHAR(50) NOT NULL,

    -- NOTE:
    -- This seminar sample treats all timestamps as local factory time in Japan.
    -- TIMESTAMP is used intentionally to keep the example simple.
    -- For production systems with multiple time zones, UTC-based operations,
    -- or daylight saving time concerns, consider TIMESTAMPTZ instead.
    start_ts TIMESTAMP NOT NULL,
    end_ts TIMESTAMP NOT NULL,

    elapsed_sec INTEGER NOT NULL,
    work_sec INTEGER NOT NULL,

    result_cd VARCHAR(10) NOT NULL,
    source_system VARCHAR(50) NOT NULL,
    source_file_name VARCHAR(255) NOT NULL,
    source_row_no INTEGER NOT NULL,
    ingest_batch_id VARCHAR(30) NOT NULL,

    -- NOTE:
    -- created_at is also treated as local seminar execution time.
    -- This is acceptable for the local demo database used in this seminar.
    -- Production systems should consider TIMESTAMPTZ and explicit timezone policy.
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- NOTE:
    -- This UNIQUE constraint intentionally models the seminar assumption:
    -- "one order passes through each process once".
    --
    -- Rework / reprocessing records are out of scope for this sample.
    -- If production use requires rework history, replace this with a model such as:
    --   UNIQUE (order_no, process_name, attempt_no)
    -- or introduce a separate rework/history table.
    UNIQUE (order_no, process_name),

    CHECK (process_name IN ('内装組立', '外装組立', '出荷検査')),
    CHECK (result_cd IN ('OK', 'NG')),
    CHECK (
        source_system IN (
            'internal_assembly_tool',
            'external_assembly_tool',
            'shipping_inspection_tool'
        )
    ),
    CHECK (end_ts >= start_ts),
    CHECK (elapsed_sec >= 0),
    CHECK (work_sec >= 0 AND work_sec <= elapsed_sec)
);

CREATE TABLE work_log_reject (
    reject_id BIGSERIAL PRIMARY KEY,

    source_system VARCHAR(50),
    source_file_name VARCHAR(255),
    source_row_no INTEGER,
    reject_reason_cd VARCHAR(50),
    reject_reason_detail TEXT,
    raw_payload_json TEXT,
    ingest_batch_id VARCHAR(30),

    -- NOTE:
    -- Same timestamp policy as work_log.created_at.
    -- Local seminar execution time is sufficient for this sample.
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_work_log_process_end_ts
    ON work_log (process_name, end_ts);

CREATE INDEX idx_work_log_worker_end_ts
    ON work_log (worker_name, end_ts);

-- NOTE:
-- PostgreSQL automatically creates an equivalent B-tree index for:
--   UNIQUE (order_no, process_name)
--
-- Therefore, this explicit index is redundant in production.
-- It is intentionally kept in this seminar sample to make the intended
-- lookup axis visible in the DDL and to match the README's stated index list.
--
-- In production, remove this index unless there is a specific query-plan reason.
CREATE INDEX idx_work_log_order_process
    ON work_log (order_no, process_name);
