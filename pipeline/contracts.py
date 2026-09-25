"""Data contracts for the raw organizer tables.

Derived from the LATAM Bank Complete Data Dictionary v1.0.0 (Sept 2026). These describe what
the organizers *promise*; `dq_checks.py` measures how far the raw data is from each promise.
The silver layer enforces them (see docs/data-issues.md for the cleaning rule per violation).
"""

# rows promised by the dictionary
EXPECTED_ROWS = {
    "customers": 150_000, "products": 400_000, "branches": 350, "service_agents": 1_200,
    "marketing_campaigns": 200, "transactions": 5_000_000, "call_center_interactions": 800_000,
    "call_transcripts": 200_000, "satisfaction_surveys": 250_000, "complaints": 80_000,
    "campaign_sends": 2_000_000, "daily_exchange_rates": 3_000,
}

PRIMARY_KEYS = {
    "customers": "customer_id", "products": "product_id", "branches": "branch_id",
    "service_agents": "agent_id", "marketing_campaigns": "campaign_id",
    "transactions": "transaction_id", "call_center_interactions": "interaction_id",
    "call_transcripts": "transcript_id", "satisfaction_surveys": "survey_id",
    "complaints": "complaint_id", "campaign_sends": "send_id",
}

NOT_NULL = {
    "customers": ["customer_id", "document_number", "document_type", "first_name", "last_name",
                  "date_of_birth", "city", "state", "country", "segment", "registration_date",
                  "registration_branch_id", "customer_status", "last_updated", "accepts_marketing"],
    "call_center_interactions": ["interaction_id", "interaction_date", "process_date", "customer_id",
                                 "interaction_type", "channel", "contact_reason", "reason_category",
                                 "requires_followup", "was_escalated", "has_transcript", "has_recording"],
    "call_transcripts": ["transcript_id", "interaction_id", "process_date", "customer_id", "agent_id",
                         "full_text", "detected_language", "transcription_model", "duration_seconds"],
    "satisfaction_surveys": ["survey_id", "survey_date", "process_date", "customer_id", "survey_type",
                             "send_channel", "main_score"],
    "complaints": ["complaint_id", "creation_date", "process_date", "customer_id", "case_type", "category",
                   "reception_channel", "description", "priority", "status", "sla_breached",
                   "is_repeat_complainer"],
}

# allowed values as documented (English); raw data often uses Spanish equivalents
DOMAINS = {
    ("customers", "country"): ["Mexico", "Colombia", "Argentina"],
    ("customers", "document_type"): ["DNI", "CURP", "CC", "CE", "Passport"],
    ("customers", "segment"): ["Premium", "Plus", "Basic", "Student"],
    ("customers", "customer_status"): ["Active", "Inactive", "Suspended", "Closed"],
    ("call_center_interactions", "reason_category"): ["Transactional", "Product", "Technical", "Commercial", "Complaint"],
    ("call_center_interactions", "detected_sentiment"): ["Positive", "Neutral", "Negative", "Very Negative"],
    ("call_center_interactions", "channel"): ["Phone", "Web Chat", "WhatsApp", "Email", "App"],
    ("transactions", "currency"): ["MXN", "COP", "ARS", "USD"],
    ("complaints", "status"): ["Open", "In Process", "Escalated", "Resolved", "Closed", "Rejected"],
    ("satisfaction_surveys", "nps_category"): ["Promoter", "Passive", "Detractor"],
}

FOREIGN_KEYS = [
    ("call_center_interactions", "customer_id", "customers", "customer_id"),
    ("call_center_interactions", "agent_id", "service_agents", "agent_id"),
    ("call_transcripts", "interaction_id", "call_center_interactions", "interaction_id"),
    ("satisfaction_surveys", "interaction_id", "call_center_interactions", "interaction_id"),
    ("complaints", "customer_id", "customers", "customer_id"),
    ("complaints", "affected_product_id", "products", "product_id"),
    ("complaints", "assigned_agent_id", "service_agents", "agent_id"),
    ("complaints", "related_branch_id", "branches", "branch_id"),
    ("complaints", "origin_interaction_id", "call_center_interactions", "interaction_id"),
    ("transactions", "customer_id", "customers", "customer_id"),
    ("transactions", "product_id", "products", "product_id"),
    ("products", "customer_id", "customers", "customer_id"),
    ("customers", "registration_branch_id", "branches", "branch_id"),
]
