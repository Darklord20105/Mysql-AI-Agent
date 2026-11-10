OPERATION_ID = "debt_report"

OPERATION_NAME = "Debt Report"

OPERATION_DESCRIPTION = (
    "Analyze debt transaction activity by currency."
)


SQL_QUERY = """
    SELECT

        COUNT(*) AS total_transactions,

        COUNT(DISTINCT username) AS users_with_transactions,

        MIN(date) AS first_transaction,

        MAX(date) AS latest_transaction,

        -- USD statistics
        SUM(CASE
            WHEN UPPER(TRIM(currency)) = 'USD'
            THEN 1 ELSE 0
        END) AS usd_transactions,

        COUNT(DISTINCT CASE
            WHEN UPPER(TRIM(currency)) = 'USD'
            THEN username
        END) AS usd_users,

        SUM(CASE
            WHEN UPPER(TRIM(currency)) = 'USD'
                 AND amount > 0
            THEN amount ELSE 0
        END) AS usd_charges,

        SUM(CASE
            WHEN UPPER(TRIM(currency)) = 'USD'
                 AND amount < 0
            THEN ABS(amount) ELSE 0
        END) AS usd_payments,

        SUM(CASE
            WHEN UPPER(TRIM(currency)) = 'USD'
            THEN amount ELSE 0
        END) AS usd_net_amount,

        -- LT statistics
        SUM(CASE
            WHEN UPPER(TRIM(currency)) = 'LT'
            THEN 1 ELSE 0
        END) AS lt_transactions,

        COUNT(DISTINCT CASE
            WHEN UPPER(TRIM(currency)) = 'LT'
            THEN username
        END) AS lt_users,

        SUM(CASE
            WHEN UPPER(TRIM(currency)) = 'LT'
                 AND amount > 0
            THEN amount ELSE 0
        END) AS lt_charges,

        SUM(CASE
            WHEN UPPER(TRIM(currency)) = 'LT'
                 AND amount < 0
            THEN ABS(amount) ELSE 0
        END) AS lt_payments,

        SUM(CASE
            WHEN UPPER(TRIM(currency)) = 'LT'
            THEN amount ELSE 0
        END) AS lt_net_amount,

        -- Unknown currency statistics
        SUM(CASE
            WHEN UPPER(TRIM(COALESCE(currency, '')))
                 NOT IN ('USD', 'LT')
            THEN 1 ELSE 0
        END) AS unknown_transactions,

        COUNT(DISTINCT CASE
            WHEN UPPER(TRIM(COALESCE(currency, '')))
                 NOT IN ('USD', 'LT')
            THEN username
        END) AS unknown_users,

        SUM(CASE
            WHEN UPPER(TRIM(COALESCE(currency, '')))
                 NOT IN ('USD', 'LT')
                 AND amount > 0
            THEN amount ELSE 0
        END) AS unknown_charges,

        SUM(CASE
            WHEN UPPER(TRIM(COALESCE(currency, '')))
                 NOT IN ('USD', 'LT')
                 AND amount < 0
            THEN ABS(amount) ELSE 0
        END) AS unknown_payments,

        SUM(CASE
            WHEN UPPER(TRIM(COALESCE(currency, '')))
                 NOT IN ('USD', 'LT')
            THEN amount ELSE 0
        END) AS unknown_net_amount

    FROM rm_users_debt
"""


AI_ENABLED = True

AI_OUTPUT_FORMAT = "json"


AI_INSTRUCTIONS = """
You are a database transaction report analyst.

You will receive pre-calculated database statistics.

Return a JSON object containing exactly two fields:

{
    "summary": "A brief description of the dataset.",
    "observations": "One or two useful observations."
}

Strict rules:

- Do not repeat any numerical values, dates, counts, or monetary amounts.
- Do not calculate percentages, ratios, totals, or additional statistics.
- Do not compare monetary amounts between different currencies.
- Do not compare net amounts across currencies.
- Do not describe net amounts as inflows, outflows, or outstanding balances.
- Do not assume anything about currency conversion.
- LT means Turkish Lira.
- Unknown currency means empty or unrecognized currency.
- Do not invent explanations, trends, or business conclusions.
- Avoid repeating the same information in both fields.
- If no meaningful observation can be made, write:
  "No additional observations can be established from these statistics."
- Return valid JSON only.
"""


OUTPUT_FORMAT = "pdf"

OUTPUT_FILENAME = "debt_report"

OUTPUT_SHEET_NAME = "Debt Report"

PDF_LAYOUT = "records"

PDF_TITLE = "Debt Report"

PDF_STATISTICS_TITLE = "Debt Statistics"