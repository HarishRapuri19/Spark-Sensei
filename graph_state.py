import re
from typing import TypedDict, List, Any, Callable
from langgraph import StateGraph, END

# typed execution state for LangGraph
class AgentState(TypedDict, total=False):
    messages: List[str]
    sql_query: str
    error_message: str
    retry_count: int
    results_preview: Any
    schema_info: str

_llm_call: Callable[[str], str] | None = None


def set_llm_call(fn: Callable[[str], str]):
    """Register a pluggable LLM function used by planner/healer nodes."""
    global _llm_call
    _llm_call = fn


def _extract_sql_from_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"```sql\s*([\s\S]*?)```", r"\1", text, flags=re.IGNORECASE)
    text = re.sub(r"```[\s\S]*?```", lambda m: m.group(0).strip('`'), text, flags=re.IGNORECASE)
    text = text.replace("`", "")

    match = re.search(r"(SELECT[\s\S]*?);?$", text.strip(), flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text.strip()


def generate_sql(state: AgentState) -> AgentState:
    if _llm_call is None:
        raise RuntimeError("LLM callback is not set. Call set_llm_call() first.")

    user_prompt = "\n".join(state.get("messages", [])) if state.get("messages") else ""
    schema_info = state.get("schema_info", "")
    planner_prompt = (
        "Given the user intent and table schema, produce the exact Spark SQL query. "
        f"Schema Info: {schema_info}\n\nUser Request: {user_prompt}\n\n"
        "Return only the SQL query without explanation."
    )

    llm_output = _llm_call(planner_prompt)
    cleaned_sql = _extract_sql_from_text(llm_output)

    state["sql_query"] = cleaned_sql
    state["error_message"] = ""
    return state


def run_sql(state: AgentState) -> AgentState:
    query = state.get("sql_query", "").strip()
    if not query:
        state["error_message"] = "No SQL query available for execution"
        return state

    try:
        df = spark.sql(query)
        limited_df = df.limit(20)
        rows = limited_df.collect()
        state["results_preview"] = [row.asDict() for row in rows]
        state["error_message"] = ""
    except Exception as e:
        state["error_message"] = str(e)
        state["results_preview"] = []
    return state


def heal_sql(state: AgentState) -> AgentState:
    if _llm_call is None:
        raise RuntimeError("LLM callback is not set. Call set_llm_call() first.")

    failed_sql = state.get("sql_query", "")
    error_msg = state.get("error_message", "")
    retry_count = state.get("retry_count", 0)

    state["retry_count"] = retry_count + 1
    if state["retry_count"] > 3:
        return state

    healer_prompt = (
        "The following Spark SQL query failed with an error. Fix the query to be valid and executable in Databricks. "
        f"Original SQL: {failed_sql}\n"
        f"Spark Error: {error_msg}\n"
        "Respond with corrected SQL only."
    )

    llm_output = _llm_call(healer_prompt)
    corrected_sql = _extract_sql_from_text(llm_output)

    state["sql_query"] = corrected_sql
    state["messages"] = state.get("messages", []) + [f"[Healer generated corrected SQL after error: {error_msg}]"]
    state["error_message"] = ""
    return state


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("generate_sql", generate_sql)
    graph.add_node("run_sql", run_sql)
    graph.add_node("heal_sql", heal_sql)

    graph.set_entry_point("generate_sql")
    graph.add_edge("generate_sql", "run_sql")
    graph.add_edge("heal_sql", "run_sql")

    def decide_next(state: AgentState):
        if state.get("error_message") and state.get("retry_count", 0) < 3:
            return "heal_sql"
        return END

    graph.add_conditional_edges("run_sql", decide_next)
    return graph
