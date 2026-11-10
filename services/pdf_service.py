import json

from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)


def format_value(value, column=None):

    if value is None:
        return ""

    if isinstance(value, (datetime, date)):
        return value.strftime("%d %b %Y, %H:%M") if isinstance(
            value, datetime
        ) else value.strftime("%d %b %Y")

    if column and any(
        column.endswith(suffix)
        for suffix in ("_charges", "_payments", "_net_amount")
    ):
        return f"{float(value):,.2f}"

    if isinstance(value, (int, float, Decimal)):
        return f"{value:,}"

    return str(value)


def get_statistic_label(column):

    labels = {
        "total_users": "Total Users",
        "verified_users": "Verified Users",
        "unverified_users": "Unverified Users",
        "email_alerts_enabled": "Email Alerts Enabled",
        "sms_alerts_enabled": "SMS Alerts Enabled",

        "total_transactions": "Total Transactions",
        "users_with_transactions": "Users With Transactions",
        "first_transaction": "First Transaction",
        "latest_transaction": "Latest Transaction"
    }

    if column in labels:
        return labels[column]

    currency_labels = {
        "usd": "US Dollar (USD)",
        "lt": "Turkish Lira (LT)",
        "unknown": "Unknown Currency"
    }

    suffix_labels = {
        "transactions": "Transactions",
        "users": "Users",
        "charges": "Charges",
        "payments": "Payments",
        "net_amount": "Net Amount"
    }

    for currency, currency_name in currency_labels.items():

        prefix = f"{currency}_"

        if column.startswith(prefix):

            suffix = column[len(prefix):]

            if suffix in suffix_labels:
                return f"{currency_name} - {suffix_labels[suffix]}"

    return column.replace("_", " ").title()


def export_pdf(
    data,
    file_path,
    title,
    columns,
    pdf_layout="records",
    statistics_title=None
):

    document = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1E293B"),
        alignment=0,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=3
    )

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#26374A"),
        spaceBefore=8,
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    label_style = ParagraphStyle(
        "StatLabel",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#475569")
    )

    value_style = ParagraphStyle(
        "StatValue",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        alignment=2,
        textColor=colors.HexColor("#1E293B")
    )

    elements = []

    generated_at = datetime.now().strftime(
        "%d %B %Y, %H:%M"
    )

    elements.append(
        Paragraph(escape(title), title_style)
    )

    elements.append(
        Paragraph(
            f"Generated: {generated_at}",
            subtitle_style
        )
    )

    elements.append(Spacer(1, 5 * mm))

    # Detect reports containing AI commentary.
    summary_report = (
        bool(data)
        and (
            "ai_summary" in data[0]
            or "ai_observations" in data[0]
        )
    )

    if not data:

        elements.append(
            Paragraph("No records found.", body_style)
        )

    # STATISTICAL REPORT
    elif summary_report:

        record = data[0]

        heading = statistics_title or "Statistics"

        elements.append(
            Paragraph(escape(heading), section_style)
        )

        table_data = []

        for column in columns:

            if column in ("ai_summary", "ai_observations"):
                continue

            label = get_statistic_label(column)
            value = format_value(record.get(column), column)

            table_data.append([
                Paragraph(escape(label), label_style),
                Paragraph(escape(value), value_style)
            ])

        statistics_table = Table(
            table_data,
            colWidths=[112 * mm, 48 * mm]
        )

        statistics_table.setStyle(
            TableStyle([
                (
                    "ROWBACKGROUNDS",
                    (0, 0),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F1F5F9")
                    ]
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.35,
                    colors.HexColor("#E2E8F0")
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                )
            ])
        )

        elements.append(statistics_table)

        # AI SUMMARY
        ai_summary = record.get("ai_summary")

        if ai_summary:

            summary_table = Table(
                [[
                    Paragraph(
                        escape(str(ai_summary)),
                        body_style
                    )
                ]],
                colWidths=[160 * mm]
            )

            summary_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor("#EFF6FF")
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.7,
                        colors.HexColor("#BFDBFE")
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    )
                ])
            )

            elements.append(
                KeepTogether([
                    Paragraph("AI Summary", section_style),
                    summary_table
                ])
            )

        # AI OBSERVATIONS
        ai_observations = record.get("ai_observations")

        if ai_observations:

            observation_text = str(ai_observations).strip()

            if observation_text:

                observation_paragraph = Paragraph(
                    f"&bull;&nbsp; {escape(observation_text)}",
                    body_style
                )

                elements.append(
                    KeepTogether([
                        Paragraph(
                            "AI Observations",
                            section_style
                        ),
                        observation_paragraph
                    ])
                )

    # GENERIC RECORD LAYOUT
    elif pdf_layout == "records":

        field_style = ParagraphStyle(
            "Field",
            parent=styles["Normal"],
            fontSize=8,
            leading=11
        )

        for index, record in enumerate(data, start=1):

            elements.append(
                Paragraph(
                    f"Record #{index}",
                    section_style
                )
            )

            table_data = []

            for column in columns:

                value = record.get(column, "")

                if isinstance(value, (dict, list)):

                    value = json.dumps(
                        value,
                        ensure_ascii=False,
                        default=str
                    )

                table_data.append([
                    Paragraph(
                        f"<b>{escape(str(column))}</b>",
                        field_style
                    ),
                    Paragraph(
                        escape(
                            str(value if value is not None else "")
                        ).replace("\n", "<br/>"),
                        body_style
                    )
                ])

            table = Table(
                table_data,
                colWidths=[45 * mm, 115 * mm]
            )

            table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.HexColor("#F1F5F9")
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor("#E2E8F0")
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    )
                ])
            )

            elements.append(table)
            elements.append(Spacer(1, 4 * mm))

    # GENERIC TABLE LAYOUT
    elif pdf_layout == "table":

        table_data = [
            [str(column) for column in columns]
        ]

        for record in data:

            table_data.append([
                str(record.get(column, "") or "")
                for column in columns
            ])

        table = Table(
            table_data,
            repeatRows=1
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#26374A")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F3F5F7")
                    ]
                )
            ])
        )

        elements.append(table)

    else:

        raise ValueError(
            f"Unsupported PDF layout: {pdf_layout}"
        )

    # FOOTER
    def add_page_number(canvas, doc):

        canvas.saveState()

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(
            colors.HexColor("#64748B")
        )

        canvas.drawString(
            20 * mm,
            10 * mm,
            "Generated by MySQL AI Agent"
        )

        canvas.drawRightString(
            A4[0] - 20 * mm,
            10 * mm,
            f"Page {doc.page}"
        )

        canvas.restoreState()

    document.build(
        elements,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    return str(file_path)