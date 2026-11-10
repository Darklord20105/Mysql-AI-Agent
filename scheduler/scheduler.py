import os
import json

from pathlib import Path
from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler

from agent.worker import run_operation
from operations import user_report, debt_report


TIMEZONE = os.getenv(
    "SCHEDULE_TIMEZONE",
    "Europe/Istanbul"
)

STATE_FILE = Path("/app/reports/scheduler_state.json")

scheduler = BlockingScheduler(timezone=TIMEZONE)


def is_enabled(name):
    return os.getenv(name, "true").lower() == "true"


def load_state():

    if not STATE_FILE.exists():
        return {}

    try:
        return json.loads(
            STATE_FILE.read_text(encoding="utf-8")
        )

    except (json.JSONDecodeError, OSError) as error:
        print(f"Warning: Could not read scheduler state: {error}")
        return {}


def save_success(operation_id):

    state = load_state()

    state[operation_id] = datetime.now(
        scheduler.timezone
    ).isoformat()

    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temp_file = STATE_FILE.with_suffix(".tmp")

    temp_file.write_text(
        json.dumps(state, indent=4),
        encoding="utf-8"
    )

    temp_file.replace(STATE_FILE)


def run_scheduled_operation(operation):

    start_time = datetime.now(scheduler.timezone)

    print("\n" + "=" * 50)
    print(f"Scheduled operation: {operation.OPERATION_NAME}")
    print(f"Started at: {start_time:%d %b %Y, %H:%M:%S}")
    print("=" * 50)

    try:

        result = run_operation(operation)

        if result:

            save_success(operation.OPERATION_ID)

            print("Status: SUCCESS")
            print(f"Generated file: {result}")

        else:
            print("Status: FAILED")

    except Exception as error:

        print("Status: FAILED")
        print(f"Error: {error}")

    finally:

        end_time = datetime.now(scheduler.timezone)

        print(f"Finished at: {end_time:%d %b %Y, %H:%M:%S}")
        print("=" * 50 + "\n")


def check_missed_job(operation, hour, minute):

    state = load_state()

    last_success_value = state.get(
        operation.OPERATION_ID
    )

    now = datetime.now(scheduler.timezone)

    today_schedule = now.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )

    if last_success_value:

        last_success = datetime.fromisoformat(
            last_success_value
        )

        latest_due = today_schedule

        if now < today_schedule:
            latest_due -= timedelta(days=1)

        missed = last_success < latest_due

    else:

        # On the first installation, only catch up
        # if today's scheduled time has already passed.
        missed = now >= today_schedule

    if missed:

        print(
            f"\nMissed execution detected: "
            f"{operation.OPERATION_NAME}"
        )

        run_scheduled_operation(operation)


def add_report_job(operation, enabled, hour, minute):

    if not enabled:
        print(f"{operation.OPERATION_NAME}: Disabled")
        return

    hour = int(hour)
    minute = int(minute)

    scheduler.add_job(
        run_scheduled_operation,
        trigger="cron",
        hour=hour,
        minute=minute,
        args=[operation],
        id=operation.OPERATION_ID,
        max_instances=1,
        coalesce=True
    )

    print(
        f"{operation.OPERATION_NAME}: "
        f"Every day at {hour:02d}:{minute:02d}"
    )

    check_missed_job(
        operation,
        hour,
        minute
    )


def show_scheduled_jobs():

    jobs = scheduler.get_jobs()

    print("\nScheduled Jobs")
    print("-" * 50)

    if not jobs:
        print("No active scheduled jobs.")
        return

    now = datetime.now(scheduler.timezone)

    for job in jobs:

        next_run = job.trigger.get_next_fire_time(
            None,
            now
        )

        print(f"Operation: {job.id}")

        if next_run:
            print(
                f"Next execution: "
                f"{next_run.strftime('%d %b %Y, %H:%M:%S %Z')}"
            )
        else:
            print("Next execution: Not available")

        print("-" * 50)


def start_scheduler():

    add_report_job(
        operation=user_report,
        enabled=is_enabled("USER_REPORT_ENABLED"),
        hour=os.getenv("USER_REPORT_HOUR", "8"),
        minute=os.getenv("USER_REPORT_MINUTE", "0")
    )

    add_report_job(
        operation=debt_report,
        enabled=is_enabled("DEBT_REPORT_ENABLED"),
        hour=os.getenv("DEBT_REPORT_HOUR", "20"),
        minute=os.getenv("DEBT_REPORT_MINUTE", "0")
    )

    print(f"\nScheduler started. Timezone: {TIMEZONE}")

    show_scheduled_jobs()

    print("\nWaiting for scheduled jobs...\n")

    try:
        scheduler.start()

    except (KeyboardInterrupt, SystemExit):
        print("\nScheduler stopped.")