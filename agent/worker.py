import json

from services.execution_history import (
    start_execution,
    finish_execution
)
from database.connection import get_db_connection
from services.output_service import export_data
from services.llm_service import generate_response


def run_operation(operation):

    connection = None
    execution_id = None

    try:
        print(f"\nStarting operation: {operation.OPERATION_NAME}")

        # Start execution history.
        try:
            execution_id = start_execution(
                operation.OPERATION_NAME
            )
        except Exception as history_error:
            print(
                f"Warning: Could not start execution history: "
                f"{history_error}"
            )

        # Connect to MySQL
        connection = get_db_connection()

        print("Database connection successful.")

        # Execute SQL
        cursor = connection.cursor(dictionary=True)

        try:
            print("Executing database query...")

            cursor.execute(operation.SQL_QUERY)

            results = cursor.fetchall()

            print(f"Retrieved {len(results)} result row(s).")

        finally:
            cursor.close()

        # Keep the original SQL result safe.
        report = results[0] if results else {}

        # Run AI only when enabled.
        if operation.AI_ENABLED:

            print("\nSending statistics to local AI...")

            prompt = f"""
            Analyze these exact database statistics.

            Do not calculate or change any numbers.
            Do not invent additional statistics.

            Statistics:
            {json.dumps(report, ensure_ascii=False, default=str)}

            Return the requested JSON summary and observations.
            """

            ai_response = generate_response(
                prompt=prompt,
                system_prompt=operation.AI_INSTRUCTIONS,
                model=getattr(operation, "AI_MODEL", None),
                output_format=getattr(
                    operation,
                    "AI_OUTPUT_FORMAT",
                    "json"
                )
            )

            print("AI processing completed.")

            # Validate AI response.
            try:
                ai_result = json.loads(ai_response)

            except json.JSONDecodeError:
                raise RuntimeError(
                    "AI returned invalid JSON."
                )

            if not isinstance(ai_result, dict):
                raise RuntimeError(
                    "AI response must be a JSON object."
                )

            required_fields = ["summary", "observations"]

            if not all(
                isinstance(ai_result.get(field), str)
                for field in required_fields
            ):
                raise RuntimeError(
                    "AI response is missing valid summary or observations."
                )

            # Add AI commentary without replacing SQL statistics.
            report["ai_summary"] = ai_result["summary"]
            report["ai_observations"] = ai_result["observations"]

        # Export the combined report.
        columns = list(report.keys())

        print(
            f"\nGenerating {operation.OUTPUT_FORMAT.upper()} report..."
        )

        file_path = export_data(
            data=[report],
            filename=operation.OUTPUT_FILENAME,
            output_format=operation.OUTPUT_FORMAT,
            sheet_name=operation.OUTPUT_SHEET_NAME,
            columns=columns,
            pdf_layout=getattr(
                operation,
                "PDF_LAYOUT",
                "records"
            ),
            pdf_title=getattr(
                operation,
                "PDF_TITLE",
                operation.OUTPUT_SHEET_NAME
            ),
            pdf_statistics_title=getattr(
                operation,
                "PDF_STATISTICS_TITLE",
                None
            )
        )

        print(f"\nReport generated: {file_path}")
        print("\nOperation completed successfully.")

        # Mark execution as successful.
        if execution_id:

            try:
                finish_execution(
                    execution_id=execution_id,
                    status="SUCCESS",
                    output=file_path
                )

                print("Execution history updated: SUCCESS")

            except Exception as history_error:
                print(
                    f"Warning: Could not update execution history: "
                    f"{history_error}"
                )

        return file_path

    except Exception as error:

        print(f"\nOperation failed: {error}")

        # Mark execution as failed.
        if execution_id:

            try:
                finish_execution(
                    execution_id=execution_id,
                    status="FAILED",
                    error=str(error)
                )

                print("Execution history updated: FAILED")

            except Exception as history_error:
                print(
                    f"Warning: Could not update execution history: "
                    f"{history_error}"
                )

        return None

    finally:

        if connection and connection.is_connected():
            connection.close()

            print("Database connection closed.")