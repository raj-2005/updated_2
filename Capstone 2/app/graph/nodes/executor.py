# app/graph/nodes/executor.py

import os
from dotenv import load_dotenv

from app.graph.state import WorkflowState
from app.tools.email import send_email
from app.tools.file import read_file, write_file
from app.tools.scheduler import schedule_task

# Load environment variables from .env
load_dotenv()


def executor_node(state: WorkflowState) -> WorkflowState:

    # Stop if already finished
    if state.finished:
        return state

    # Stop if no more steps
    if state.current_step >= len(state.planned_steps):
        state.finished = True
        return state

    step = state.planned_steps[state.current_step]
    action = step.action

    try:
        step.status = "running"

        # =========================================
        # EMAIL ACTION
        # =========================================
        if action == "send_email":

            email_user = os.getenv("EMAIL_USERNAME")
            email_pass = os.getenv("EMAIL_PASSWORD")

            print("DEBUG EMAIL USER:", email_user)
            print("DEBUG EMAIL PASS:", "SET" if email_pass else "NOT SET")

            result = send_email(
                to=step.params.get("to"),
                subject=step.params.get("subject"),
                body=state.context.get("email_body", ""),
                username=email_user,
                password=email_pass
            )

            state.context["email_result"] = result

        elif action == "fetch_email_body":
            body = "Respected Manager,\n\nI would like to request leave for tomorrow due to personal reasons.\n\nKindly approve.\n\nThank you."
            state.context["email_body"] = body
            result = "Email body generated"

        # =========================================
        # FILE ACTIONS
        # =========================================
        elif action == "read_file":
            content = read_file(step.params.get("path"))
            state.context["file_content"] = content
            result = f"File read: {step.params.get('path')}"

        elif action == "write_file":
            result = write_file(
                step.params.get("path"),
                step.params.get("content", "")
            )
            state.context["file_written"] = step.params.get("path")

        # =========================================
        # SCHEDULER ACTION
        # =========================================
        elif action == "schedule_task":
            result = schedule_task(
                task_name=step.params.get("task_name"),
                time_str=step.params.get("time")
            )
            state.context["schedule_result"] = result

        # =========================================
        # UNKNOWN TOOL
        # =========================================
        else:
            raise ValueError(f"No tool implemented for action '{action}'")

        step.status = "done"
        state.execution_logs.append(f"Executed: {action}")

    except Exception as e:
        step.status = "failed"
        state.execution_logs.append(
            f"Execution failed for {action}: {str(e)}"
        )

    # Move to next step
    state.current_step += 1

    # Stop condition (IMPORTANT for avoiding recursion error)
    if state.current_step >= len(state.planned_steps):
        state.finished = True

    return state
 