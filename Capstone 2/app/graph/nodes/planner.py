from typing import List
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.graph.state import WorkflowState, Action


# -----------------------------------------
# LLM Setup (Groq)
# -----------------------------------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",   # fast + free tier friendly
    temperature=0
)


# -----------------------------------------
# Prompt Template
# -----------------------------------------
PLANNER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert workflow planner.

Convert the user's intent into a minimal list of executable workflow steps.

Return STRICT JSON in this format:

[
  {{
    "action": "string",
    "params": {{}},
    "risk": "low | medium | high"
  }}
]

Rules:
- Do NOT include explanations.
- Only return valid JSON.
- Keep steps minimal but complete.
- Mark destructive or external actions as high risk.
""",
        ),
        ("human", "{intent}"),
    ]
)


# -----------------------------------------
# Helper: Parse LLM JSON safely
# -----------------------------------------
def _parse_steps(json_text: str) -> List[Action]:
    """
    Convert LLM JSON output into Step objects safely.
    """
    try:
        data = json.loads(json_text)
        return [Action(**item) for item in data]
    except Exception as e:
        raise ValueError(f"Planner produced invalid JSON: {e}\nOutput: {json_text}")


# -----------------------------------------
# Planner Node Function (LangGraph Node)
# -----------------------------------------
def planner_node(state: WorkflowState) -> WorkflowState:
    """
    LangGraph planner node.

    Reads:
        - state.user_intent

    Writes:
        - state.planned_steps
        - state.execution_logs
    """

    # Skip planning if already planned (useful for resume)
    if state.planned_steps:
        return state

    # Call LLM
    chain = PLANNER_PROMPT | llm
    response = chain.invoke({"intent": state.user_intent})

    # Extract text safely
    content = response.content.strip()

    # Parse into Step objects
    steps = _parse_steps(content)

    # Update state
    state.planned_steps = steps
    state.execution_logs.append(f"Planner created {len(steps)} steps.")

    return state