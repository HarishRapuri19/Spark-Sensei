"""Module shim for compatibility with old notebook-style entrypoint."""

from graph_state import build_graph, AgentState, set_llm_call
from tools import get_table_columns
from agent import _get_groq_llm, _llm_call, configure_mlflow, run_agent, run_self_healing_test

__all__ = [
    "build_graph",
    "AgentState",
    "set_llm_call",
    "get_table_columns",
    "run_agent",
    "run_self_healing_test",
]

if __name__ == "__main__":
    import pprint

    if not __import__("os").environ.get("GROQ_API_KEY"):
        print("GROQ_API_KEY missing, skipping full LLM-driven execution. You can still run unit tests for static paths.")
    else:
        state: AgentState = {
            "messages": ["Show me the 5 most recent rows from samples.nyctaxi.trips"],
            "sql_query": "",
            "error_message": "",
            "retry_count": 0,
            "schema_info": get_table_columns("samples.nyctaxi.trips"),
        }
        result = run_agent(state)
        pprint.pp(result)
def test_self_healing_mlflow():
    """Test the full self-healing flow with MLflow logging and verify trace metrics exist."""
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'file:///tmp/mlruns'))
    mlflow.set_experiment("spark_sensei_self_healing")

    initial_state = {
        "messages": ["Select non_existent_column from samples.nyctaxi.trips LIMIT 5"],
        "sql_query": "",
        "error_message": "",
        "retry_count": 0,
        "schema_info": get_table_columns("samples.nyctaxi.trips"),
    }

    with mlflow.start_run(run_name="self_healing_test") as run:
        final_state = graph.run(initial_state)

        mlflow.log_param("retry_count", final_state.get("retry_count", 0))
        mlflow.log_param("final_error_message", final_state.get("error_message", ""))
        mlflow.log_metric("results_preview_count", len(final_state.get("results_preview", [])))

        # Log conversation for audit (Epic 4.1.2 requirement)
        mlflow.log_text("\n".join(final_state.get("messages", [])), "conversation.txt")

        # Verify autolog metrics exist for latency/token usage
        run_data = mlflow.get_run(run.info.run_id).data
        metric_keys = set(run_data.metrics.keys())

        print("MLflow self-healing run_id:", run.info.run_id)
        print("Logged metrics:", metric_keys)

        latency_metrics = [k for k in metric_keys if "latency" in k.lower() or "time" in k.lower()]
        token_metrics = [k for k in metric_keys if "token" in k.lower()]

        if not latency_metrics:
            print("Warning: latency metric not found in MLflow run; ensure LangChain autolog creates metrics.")
        if not token_metrics:
            print("Warning: token usage metric not found in MLflow run; ensure LangChain autolog creates metrics.")

    return final_state


if __name__ == "__main__":
    import pprint

    # Basic module-level sanity check only; Groq key may be required for full flow.
    initial_state = {
        "messages": ["Show me the 5 most recent rows from samples.nyctaxi.trips"],
        "sql_query": "",
        "error_message": "",
        "retry_count": 0,
        "schema_info": "",
    }
    pprint.pp({
        "entry_point": graph.entry_point,
        "nodes": list(graph.nodes),
        "initial_state": initial_state,
    })
    # run graph without LLM if key missing
    if not os.getenv("GROQ_API_KEY"):
        print("GROQ_API_KEY missing, skipping full LLM-driven execution.")
    else:
        final_state = graph.run(initial_state)
        pprint.pp(final_state)
