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

# 🥋 Project Spark-Sensei: Self-Healing Agentic SQL Analyst

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Databricks](https://img.shields.io/badge/Databricks-Community_Edition-F37021.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_Orchestration-000000.svg)
![Groq](https://img.shields.io/badge/Groq-Llama_3-f55036.svg)
![MLflow](https://img.shields.io/badge/MLflow-Observability-0194E2.svg)

An enterprise-grade, agentic AI system designed specifically for the Databricks ecosystem. Spark-Sensei translates natural language into PySpark SQL, executes the queries against a live cluster, and—crucially—**autonomously catches and debugs Spark runtime errors (`PySparkException`) without human intervention.**

Built entirely on the Databricks Community Edition (CE) using open-source orchestration, proving that robust AI systems rely on strong engineering plumbing, not just expensive managed services.

---

## 🏗️ System Architecture

Spark-Sensei is orchestrated using a **LangGraph State Machine** that loops between planning, tool utilization, execution, and error healing.

```mermaid
graph TD
    User((User Prompt)) --> Planner
    
    subgraph Agentic Loop
        Planner[🧠 Planner Node <br/> Generates SQL]
        Tools[🛠️ Tool Node <br/> Inspects Hive Metastore]
        Executor[⚙️ Executor Node <br/> Runs spark.sql]
        Healer[🩹 Healer Node <br/> Analyzes Spark Exception]
        
        Planner -->|Needs Schema| Tools
        Tools -->|Returns Metadata| Planner
        Planner -->|Executes SQL| Executor
        Executor -->|Catches Error| Healer
        Healer -->|Rewrites SQL| Planner
    end
    
    Executor -->|Success| Output((Final DataFrame))