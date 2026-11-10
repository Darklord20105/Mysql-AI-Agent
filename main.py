from config import EXECUTION_MODE

from agent.worker import run_operation
from operations import user_report
from scheduler.scheduler import start_scheduler


def main():

    if EXECUTION_MODE == "manual":

        print("Execution mode: Manual")
        run_operation(user_report)

    elif EXECUTION_MODE == "scheduled":

        print("Execution mode: Scheduled")
        start_scheduler()

    else:

        raise ValueError(
            f"Invalid execution mode: {EXECUTION_MODE}"
        )


if __name__ == "__main__":
    main()