import json
import uuid

from pathlib import Path
from datetime import datetime


HISTORY_FILE = (
    Path(__file__).resolve().parent.parent
    / "reports"
    / "execution_history.json"
)


def get_current_time():
    return datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


def load_history():

    if not HISTORY_FILE.exists():
        return []

    try:

        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError) as error:

        print(f"Warning: Could not read execution history: {error}")

        return []


def save_history(history):

    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temp_file = HISTORY_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as file:

        json.dump(
            history,
            file,
            indent=4,
            ensure_ascii=False
        )

    temp_file.replace(HISTORY_FILE)


def start_execution(operation_name):

    execution_id = str(uuid.uuid4())

    history = load_history()

    history.append({
        "id": execution_id,
        "operation": operation_name,
        "started_at": get_current_time(),
        "finished_at": None,
        "status": "RUNNING",
        "duration_seconds": None,
        "output": None,
        "error": None
    })

    save_history(history)

    return execution_id


def finish_execution(
    execution_id,
    status,
    output=None,
    error=None
):

    history = load_history()

    for execution in reversed(history):

        if execution["id"] == execution_id:

            finished_at = datetime.now().astimezone()

            started_at = datetime.fromisoformat(
                execution["started_at"]
            )

            execution["finished_at"] = finished_at.isoformat(
                timespec="seconds"
            )

            execution["status"] = status

            execution["duration_seconds"] = round(
                (finished_at - started_at).total_seconds(),
                2
            )

            execution["output"] = (
                str(output) if output else None
            )

            execution["error"] = error

            break

    save_history(history)