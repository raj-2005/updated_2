# app/tools/scheduler.py

from datetime import datetime


def schedule_task(task_name: str, time_str: str) -> str:
    """
    Schedules a task (prototype version).

    time_str format: 'YYYY-MM-DD HH:MM'
    """

    try:
        scheduled_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValueError("Invalid time format. Use YYYY-MM-DD HH:MM")

    return f"Task '{task_name}' scheduled at {scheduled_time}"