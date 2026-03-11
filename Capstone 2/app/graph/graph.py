from langgraph.graph import StateGraph, END

from app.graph.state import WorkflowState
from app.graph.nodes.planner import planner_node
from app.graph.nodes.subtask import subtask_node
from app.graph.nodes.risk import risk_node
from app.graph.nodes.approval import approval_node
from app.graph.nodes.executor import executor_node


# -----------------------------------------
# Graph Builder
# -----------------------------------------

def build_graph():

    graph = StateGraph(WorkflowState)

    # Register Nodes
    graph.add_node("planner", planner_node)
    graph.add_node("subtask", subtask_node) # novelty 
    graph.add_node("risk", risk_node)
    graph.add_node("approval", approval_node)
    graph.add_node("executor", executor_node)

    # -----------------------------------------
    # Define Flow
    # -----------------------------------------

    # Entry
    graph.set_entry_point("planner")

    # Planner → Subtask
    graph.add_edge("planner", "subtask")

    # Subtask → Risk
    graph.add_edge("subtask", "risk")

    # Risk → Conditional Routing
    graph.add_conditional_edges(
        "risk",
        route_after_risk,
        {
            "approval": "approval",
            "executor": "executor",
        },
    )

    # Approval → Executor (after approval)
    graph.add_edge("approval", "executor")

    # Executor → Conditional Loop
    graph.add_conditional_edges(
        "executor",
        route_after_execution,
        {
            "continue": "subtask",
            "end": END,
        },
    )

    return graph.compile()


# -----------------------------------------
# Routing Functions
# -----------------------------------------

def route_after_risk(state: WorkflowState) -> str:
    """
    Decide whether to go to approval or executor.
    """
    if state.approval_status == "pending":
        return "approval"
    return "executor"


def route_after_execution(state: WorkflowState) -> str:
    """
    Decide whether workflow should continue or end.
    """
    if state.finished:
        return "end"
    return "continue"