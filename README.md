# Spark Sensei: Databricks LangGraph SQL Agent

> Professional, modular architecture for a self-healing Spark SQL agent on Databricks.
> Built for portfolio review: clean code, strong separation of concerns, and observability.

## ✅ What’s Included

- `agent.py`: runtime orchestration, LLM adapter, MLflow setup, experiment driver.
- `tools.py`: deterministic catalog inspection tool (`get_table_columns`).
- `graph_state.py`: typed LangGraph state machine (Planner, Executor, Healer), self-healing edges.
- `README.md`: architecture diagram, execution proof placeholders.

## 🧩 Repository Structure

- `graph_state.py`
- `tools.py`
- `agent.py`
- `README.md`
- `databricks_tool.py` (compat shim / original monolith)
- `requirements.txt`
- `work.md`

## 🧠 Architecture Diagram (Mermaid)

```mermaid
stateDiagram-v2
    [*] --> Planner
    Planner --> Executor
    Executor -->|success| [*]
    Executor -->|error + retry < 3| Healer
    Executor -->|error + retry >= 3| [*]
    Healer --> Executor

    state Planner {
      note right: generate_sql\nfrom user intent + schema_info
    }
    state Executor {
      note right: run_sql\nexecute spark.sql(query)
    }
    state Healer {
      note right: heal_sql\nLLM-based query repair
    }
```

## 🧪 Run Locally

1. Set environment variables:

```bash
export GROQ_API_KEY="<your-key>"
export MLFLOW_TRACKING_URI="file:///tmp/mlruns"
```

2. Install requirements:

```bash
pip install -r requirements.txt
```

3. Run self-healing demo:

```bash
python agent.py
```

## 📊 System in Action

### 1. Databricks Notebook Output

![Databricks notebook output](docs/screenshots/1-notebook-output.png)

### 2. MLflow Trace (Self-Healing Loop)

![MLflow trace screenshot](docs/screenshots/2-mlflow-trace.png)

> Note: These are placeholders. In a real pipeline, capture actual screenshots from Databricks UI and commit them.

## 📈 Senior Engineering Signals

- Clear single-responsibility modules
- Explicit typed state (`AgentState`) for correctness and better code review
- LLM call injection with `set_llm_call()` for testability
- Feature toggles and conditional transitions (self-healing control flow)
- MLflow telemetry + audit log
- Readme with architecture diagram + execution proof

---

## 📦 files to add after capture

- `docs/screenshots/1-notebook-output.png`
- `docs/screenshots/2-mlflow-trace.png`
