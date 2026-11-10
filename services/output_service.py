import json
import csv

from pathlib import Path
from datetime import datetime

import pandas as pd

from docx import Document

from services.pdf_service import export_pdf


def export_data(
    data,
    filename,
    output_format,
    sheet_name="Report",
    columns=None,
    pdf_layout="records",
    pdf_title=None,
    pdf_statistics_title=None
):

    reports_directory = Path("/app/reports")
    reports_directory.mkdir(parents=True, exist_ok=True)

    output_format = output_format.lower()

    supported_formats = [
        "xlsx",
        "json",
        "txt",
        "csv",
        "docx",
        "pdf"
    ]

    if output_format not in supported_formats:
        raise ValueError(
            f"Unsupported output format: {output_format}"
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{filename}_{timestamp}.{output_format}"
    file_path = reports_directory / filename

    if columns is None:
        columns = list(data[0].keys()) if data else []

    # EXCEL
    if output_format == "xlsx":

        dataframe = pd.DataFrame(data, columns=columns or None)

        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:

            dataframe.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False
            )

            worksheet = writer.sheets[sheet_name]
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions

    # JSON
    elif output_format == "json":

        with open(file_path, "w", encoding="utf-8") as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
                default=str
            )

    # TXT
    elif output_format == "txt":

        with open(file_path, "w", encoding="utf-8") as file:

            for record in data:
                file.write(str(record) + "\n")

    # CSV
    elif output_format == "csv":

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            if columns:

                writer = csv.DictWriter(
                    file,
                    fieldnames=columns
                )

                writer.writeheader()
                writer.writerows(data)

    # WORD
    elif output_format == "docx":

        document = Document()

        document.add_heading(sheet_name, level=1)

        document.add_paragraph(
            f"Generated: {datetime.now():%d %B %Y, %H:%M}"
        )

        document.add_paragraph(
            f"Total records: {len(data)}"
        )

        for index, record in enumerate(data, start=1):

            document.add_heading(
                f"Record #{index}",
                level=2
            )

            table = document.add_table(
                rows=0,
                cols=2
            )

            table.style = "Table Grid"

            for column in columns:

                cells = table.add_row().cells

                cells[0].text = str(column)
                cells[1].text = str(
                    record.get(column, "") or ""
                )

        if not data:
            document.add_paragraph("No records found.")

        document.save(file_path)

    # PDF
    elif output_format == "pdf":

        return export_pdf(
            data=data,
            file_path=file_path,
            title=pdf_title or sheet_name,
            columns=columns,
            pdf_layout=pdf_layout,
            statistics_title=pdf_statistics_title
        )

    return str(file_path)