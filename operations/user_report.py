##	Retrieve user records
OPERATION_ID = "user_report"

OPERATION_NAME = "User Report"

OPERATION_DESCRIPTION = (
    "Retrieve user records from the MySQL database."
)


# 1. Database query

SQL_QUERY = """
    SELECT
        COUNT(*) AS total_users,

        COALESCE(SUM(
            CASE WHEN verified = 1 THEN 1 ELSE 0 END
        ), 0) AS verified_users,

        COALESCE(SUM(
            CASE WHEN verified = 0 THEN 1 ELSE 0 END
        ), 0) AS unverified_users,

        COALESCE(SUM(
            CASE WHEN alertemail = 1 THEN 1 ELSE 0 END
        ), 0) AS email_alerts_enabled,

        COALESCE(SUM(
            CASE WHEN alertsms = 1 THEN 1 ELSE 0 END
        ), 0) AS sms_alerts_enabled

    FROM rm_users
"""


# 2. AI configuration

AI_ENABLED = True

AI_OUTPUT_FORMAT = "json"

AI_INSTRUCTIONS = """
You are a database report analyst.

You will receive exact statistics calculated by SQL.

Return a JSON object containing exactly these two fields:

{
    "summary": "A short description of the overall situation.",
    "observations": "Useful observations based only on the supplied statistics."
}

Rules:
- Do not invent facts.
- Do not change or recalculate any statistics.
- Do not include numerical values in your summary or observations.
- Do not claim trends or changes over time.
- If the data does not support an observation, say so.
- Return valid JSON only.
"""

# 3. Output configuration

OUTPUT_FORMAT = "pdf"

OUTPUT_FILENAME = "user_report"

OUTPUT_SHEET_NAME = "Users"

PDF_LAYOUT = "records"

PDF_TITLE = "Users"

PDF_STATISTICS_TITLE = "User Statistics"