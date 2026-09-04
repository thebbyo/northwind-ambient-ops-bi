import csv
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "database.sqlite3"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_schema(conn: sqlite3.Connection):
    cursor = conn.cursor()

    # Drop existing tables and views if reloading
    cursor.executescript("""
    DROP VIEW IF EXISTS v_escalations_full;
    DROP TABLE IF EXISTS escalation;
    DROP TABLE IF EXISTS note_audit;
    DROP TABLE IF EXISTS note;
    DROP TABLE IF EXISTS mds;
    DROP TABLE IF EXISTS clinician;
    DROP TABLE IF EXISTS rubric_weight;
    DROP TABLE IF EXISTS sla_config;

    -- Clinicians
    CREATE TABLE clinician (
        clinician_id TEXT PRIMARY KEY,
        clinician_name TEXT NOT NULL,
        specialty TEXT,
        region TEXT,
        home_timezone TEXT,
        employment_status TEXT,
        record_effective_from TEXT,
        record_effective_to TEXT,
        is_current_record INTEGER
    );

    -- Medical Documentation Specialists
    CREATE TABLE mds (
        mds_id TEXT PRIMARY KEY,
        mds_name TEXT NOT NULL,
        pod TEXT,
        tier TEXT,
        hire_date TEXT,
        status TEXT
    );

    -- Clinical Notes
    CREATE TABLE note (
        note_id TEXT PRIMARY KEY,
        ingestion_id TEXT,
        encounter_id TEXT,
        clinician_id TEXT,
        mds_id TEXT,
        product_line TEXT,
        priority TEXT,
        template_id TEXT,
        source_channel TEXT,
        word_count INTEGER,
        submitted_at_utc TEXT,
        delivered_at_utc TEXT,
        ingested_at_utc TEXT,
        is_void INTEGER,
        void_reason TEXT,
        FOREIGN KEY (clinician_id) REFERENCES clinician(clinician_id),
        FOREIGN KEY (mds_id) REFERENCES mds(mds_id)
    );

    -- Escalations
    CREATE TABLE escalation (
        escalation_id TEXT PRIMARY KEY,
        note_id TEXT,
        created_at_utc TEXT,
        slack_channel TEXT,
        slack_thread_ts REAL,
        status TEXT,
        assignee_mds_id TEXT,
        first_response_at_utc TEXT,
        resolved_at_utc TEXT,
        attempt_count INTEGER,
        last_api_error TEXT,
        FOREIGN KEY (note_id) REFERENCES note(note_id),
        FOREIGN KEY (assignee_mds_id) REFERENCES mds(mds_id)
    );

    -- Note Audits
    CREATE TABLE note_audit (
        audit_id TEXT PRIMARY KEY,
        note_id TEXT,
        auditor_mds_id TEXT,
        audited_at_utc TEXT,
        rubric_version TEXT,
        score_accuracy REAL,
        score_completeness REAL,
        score_formatting REAL,
        score_terminology REAL,
        score_hpi REAL,
        score_ros REAL,
        score_plan REAL,
        composite_score REAL,
        pass_fail TEXT,
        FOREIGN KEY (note_id) REFERENCES note(note_id),
        FOREIGN KEY (auditor_mds_id) REFERENCES mds(mds_id)
    );

    -- Rubric Weights
    CREATE TABLE rubric_weight (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rubric_version TEXT,
        dimension TEXT,
        weight REAL,
        effective_from TEXT,
        pass_threshold REAL
    );

    -- SLA Config
    CREATE TABLE sla_config (
        config_id TEXT PRIMARY KEY,
        product_line TEXT,
        priority TEXT,
        target_minutes INTEGER,
        effective_from TEXT,
        effective_to TEXT
    );

    -- Indexes
    CREATE INDEX idx_escalation_status ON escalation(status);
    CREATE INDEX idx_escalation_note ON escalation(note_id);
    CREATE INDEX idx_escalation_assignee ON escalation(assignee_mds_id);
    CREATE INDEX idx_note_clinician ON note(clinician_id);
    CREATE INDEX idx_note_mds ON note(mds_id);
    CREATE INDEX idx_note_priority ON note(priority);
    CREATE INDEX idx_note_audit_note ON note_audit(note_id);

    -- Enriched Full Escalation View
    CREATE VIEW v_escalations_full AS
    SELECT 
        e.escalation_id,
        e.status,
        e.slack_channel,
        e.created_at_utc,
        e.first_response_at_utc,
        e.resolved_at_utc,
        ROUND((julianday(e.first_response_at_utc) - julianday(e.created_at_utc)) * 24 * 60, 1) AS response_time_minutes,
        ROUND((julianday(e.resolved_at_utc) - julianday(e.created_at_utc)) * 24 * 60, 1) AS resolution_time_minutes,
        e.attempt_count,
        e.last_api_error,
        e.note_id,
        n.encounter_id,
        n.product_line,
        n.priority,
        n.word_count,
        c.clinician_name,
        c.specialty,
        c.region,
        e.assignee_mds_id,
        m.mds_name AS assignee_name,
        m.pod AS assignee_pod,
        m.tier AS assignee_tier
    FROM escalation e
    LEFT JOIN note n ON e.note_id = n.note_id
    LEFT JOIN clinician c ON n.clinician_id = c.clinician_id
    LEFT JOIN mds m ON e.assignee_mds_id = m.mds_id;
    """)
    conn.commit()

def load_csvs(conn: sqlite3.Connection):
    cursor = conn.cursor()

    # 1. Clinicians
    clinician_path = DATA_DIR / "clinician.csv"
    if clinician_path.exists():
        with open(clinician_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [
                (
                    row["clinician_id"],
                    row["clinician_name"],
                    row.get("specialty"),
                    row.get("region"),
                    row.get("home_timezone"),
                    row.get("employment_status"),
                    row.get("record_effective_from"),
                    row.get("record_effective_to") or None,
                    1 if row.get("is_current_record", "").lower() in ("true", "1") else 0
                )
                for row in reader
            ]
            cursor.executemany("""
                INSERT INTO clinician VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
        print(f"Loaded {len(rows)} records into clinician")

    # 2. MDS
    mds_path = DATA_DIR / "mds.csv"
    if mds_path.exists():
        with open(mds_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [
                (
                    row["mds_id"],
                    row["mds_name"],
                    row.get("pod"),
                    row.get("tier"),
                    row.get("hire_date"),
                    row.get("status")
                )
                for row in reader
            ]
            cursor.executemany("""
                INSERT INTO mds VALUES (?, ?, ?, ?, ?, ?)
            """, rows)
        print(f"Loaded {len(rows)} records into mds")

    # 3. Note
    note_path = DATA_DIR / "note.csv"
    if note_path.exists():
        with open(note_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [
                (
                    row["note_id"],
                    row.get("ingestion_id"),
                    row.get("encounter_id"),
                    row.get("clinician_id"),
                    row.get("mds_id"),
                    row.get("product_line"),
                    row.get("priority"),
                    row.get("template_id"),
                    row.get("source_channel"),
                    int(row["word_count"]) if row.get("word_count") else None,
                    row.get("submitted_at_utc"),
                    row.get("delivered_at_utc") or None,
                    row.get("ingested_at_utc") or None,
                    1 if row.get("is_void", "").lower() in ("true", "1") else 0,
                    row.get("void_reason") or None
                )
                for row in reader
            ]
            cursor.executemany("""
                INSERT INTO note VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
        print(f"Loaded {len(rows)} records into note")

    # 4. Escalation
    escalation_path = DATA_DIR / "escalation.csv"
    if escalation_path.exists():
        with open(escalation_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [
                (
                    row["escalation_id"],
                    row.get("note_id"),
                    row.get("created_at_utc"),
                    row.get("slack_channel"),
                    float(row["slack_thread_ts"]) if row.get("slack_thread_ts") else None,
                    row.get("status"),
                    row.get("assignee_mds_id"),
                    row.get("first_response_at_utc") or None,
                    row.get("resolved_at_utc") or None,
                    int(row["attempt_count"]) if row.get("attempt_count") else 1,
                    row.get("last_api_error") or None
                )
                for row in reader
            ]
            cursor.executemany("""
                INSERT INTO escalation VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
        print(f"Loaded {len(rows)} records into escalation")

    # 5. Note Audit
    audit_path = DATA_DIR / "note_audit.csv"
    if audit_path.exists():
        with open(audit_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [
                (
                    row["audit_id"],
                    row.get("note_id"),
                    row.get("auditor_mds_id"),
                    row.get("audited_at_utc"),
                    row.get("rubric_version"),
                    float(row["score_accuracy"]) if row.get("score_accuracy") else None,
                    float(row["score_completeness"]) if row.get("score_completeness") else None,
                    float(row["score_formatting"]) if row.get("score_formatting") else None,
                    float(row["score_terminology"]) if row.get("score_terminology") else None,
                    float(row["score_hpi"]) if row.get("score_hpi") else None,
                    float(row["score_ros"]) if row.get("score_ros") else None,
                    float(row["score_plan"]) if row.get("score_plan") else None,
                    float(row["composite_score"]) if row.get("composite_score") else None,
                    row.get("pass_fail")
                )
                for row in reader
            ]
            cursor.executemany("""
                INSERT INTO note_audit VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
        print(f"Loaded {len(rows)} records into note_audit")

    # 6. Rubric Weight
    rubric_path = DATA_DIR / "rubric_weight.csv"
    if rubric_path.exists():
        with open(rubric_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [
                (
                    row["rubric_version"],
                    row.get("dimension"),
                    float(row["weight"]) if row.get("weight") else None,
                    row.get("effective_from"),
                    float(row["pass_threshold"]) if row.get("pass_threshold") else None
                )
                for row in reader
                if row.get("rubric_version")
            ]
            cursor.executemany("""
                INSERT INTO rubric_weight (rubric_version, dimension, weight, effective_from, pass_threshold)
                VALUES (?, ?, ?, ?, ?)
            """, rows)
        print(f"Loaded {len(rows)} records into rubric_weight")

    # 7. SLA Config
    sla_path = DATA_DIR / "sla_config.csv"
    if sla_path.exists():
        with open(sla_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [
                (
                    row["config_id"],
                    row.get("product_line"),
                    row.get("priority"),
                    int(row["target_minutes"]) if row.get("target_minutes") else None,
                    row.get("effective_from"),
                    row.get("effective_to") or None
                )
                for row in reader
                if row.get("config_id")
            ]
            cursor.executemany("""
                INSERT INTO sla_config VALUES (?, ?, ?, ?, ?, ?)
            """, rows)
        print(f"Loaded {len(rows)} records into sla_config")

    conn.commit()

def verify_counts(conn: sqlite3.Connection):
    cursor = conn.cursor()
    tables = ["escalation", "note", "clinician", "mds", "note_audit", "rubric_weight", "sla_config"]
    print("\nDatabase verification summary:")
    print("=" * 40)
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table.ljust(16)}: {count} rows")
    print("=" * 40)

if __name__ == "__main__":
    print(f"Connecting to SQLite database at {DB_PATH}...")
    conn = get_db()
    init_schema(conn)
    load_csvs(conn)
    verify_counts(conn)
    conn.close()
    print("Database initialization and loading complete!")
