import os
import mlflow
from langchain.chat_models import GroqChat
from langchain.llms import Groq
from langchain.schema import SystemMessage, HumanMessage
from graph_state import set_llm_call, build_graph, AgentState
from tools import get_table_columns


def _get_groq_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY is required for Groq LLM calls")

    try:
        return GroqChat(api_key=api_key, temperature=0)
    except Exception:
        return Groq(api_key=api_key, temperature=0)


def _llm_call(prompt: str) -> str:
    llm = _get_groq_llm()
    if hasattr(llm, "__call__") and hasattr(llm, "response_format"):
        # GroqChat returns messages with content attr
        response = llm([
            SystemMessage(content="You are a Databricks Spark SQL planner. Generate valid Spark SQL based on the user request."),
            HumanMessage(content=prompt),
        ])
        return response.content
    else:
        return llm(prompt)


def configure_mlflow():
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'file:///tmp/mlruns'))
    mlflow.langchain.autolog()


def run_agent(initial_state: AgentState) -> AgentState:
    configure_mlflow()
    set_llm_call(_llm_call)
    graph = build_graph()

    return graph.run(initial_state)


def run_self_healing_test():
    initial_state = {
        "messages": ["Select non_existent_column from samples.nyctaxi.trips LIMIT 5"],
        "sql_query": "",
        "error_message": "",
        "retry_count": 0,
        "schema_info": get_table_columns("samples.nyctaxi.trips"),
    }

    final_state = run_agent(initial_state)

    with mlflow.start_run(run_name="self_healing_test") as run:
        mlflow.log_param("retry_count", final_state.get("retry_count", 0))
        mlflow.log_param("final_error_message", final_state.get("error_message", ""))
        mlflow.log_metric("results_preview_count", len(final_state.get("results_preview", [])))
        mlflow.log_text("\n".join(final_state.get("messages", [])), "conversation.txt")

    return final_state


if __name__ == "__main__":
    import pprint

    if not os.getenv("GROQ_API_KEY"):
        print("GROQ_API_KEY missing, skipping full LLM-driven execution. You can still run unit tests for static paths.")
    else:
        state = {
            "messages": ["Show me the 5 most recent rows from samples.nyctaxi.trips"],
            "sql_query": "",
            "error_message": "",
            "retry_count": 0,
            "schema_info": get_table_columns("samples.nyctaxi.trips"),
        }
        result = run_agent(state)
        pprint.pp(result)
