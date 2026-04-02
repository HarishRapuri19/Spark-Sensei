Epic 1: Environment & Secure Connectivity
Goal: Establish a reproducible, secure workspace on Databricks Community Edition (CE) that can communicate with external LLM APIs without exposing credentials.

Story 1.1: Provision Workspace and Core Dependencies
Story AC: A Databricks CE notebook runs a validation script confirming all required third-party libraries are installed and the Groq/OpenAI API is reachable.

Task 1.1.1: Configure CE Cluster

Action: Spin up a Databricks CE cluster using a standard ML Runtime.

Task AC: Cluster is active. Notebook attached.

Task 1.1.2: Define requirements.txt / Pip Install

Action: Install core libraries using %pip install.

Task AC: langchain, langgraph, mlflow, and langchain-groq (or langchain-openai) install without dependency conflicts.

Task 1.1.3: Secure API Key Management

Action: Store the LLM API key securely. Since CE lacks full Secret Scopes, use dbutils.widgets for runtime input rather than hardcoding.

Task AC: API key is loaded via a secure text widget and is never printed in the notebook output.

🟡 Epic 2: The "Ground Truth" Tooling
Goal: Develop the deterministic Python tools the LLM will use to inspect the database, eliminating schema hallucination.

Story 2.1: Develop the PySpark Catalog Inspector Tool
Story AC: A LangChain @tool successfully receives a table name as a string and returns a formatted JSON or Markdown string of the exact column names and data types.

Task 2.1.1: Initialize Target Dataset

Action: Load samples.nyctaxi.trips (or similar) into a temporary view/table.

Task AC: spark.sql("SELECT * FROM samples.nyctaxi.trips LIMIT 5") executes successfully.

Task 2.1.2: Write the Schema Extraction Function

Action: Write a Python function using spark.catalog.listColumns().

Task AC: Function handles invalid table names gracefully by returning an error string (e.g., "Table not found"), rather than crashing.

Task 2.1.3: Wrap and Bind as an AI Tool

Action: Use LangChain's @tool decorator. Write a highly specific docstring (the LLM uses this to know how to use the tool).

Task AC: The tool is callable by the LLM, and the docstring explicitly instructs the LLM to "Always run this tool before generating SQL."

🔴 Epic 3: Agentic Orchestration (LangGraph)
Goal: Build the state machine that handles reasoning, execution, and self-healing.

Story 3.1: Define Graph State and Core Nodes
Story AC: The LangGraph successfully takes a natural language prompt, generates a valid Spark SQL query, and executes it against the Databricks cluster.

Task 3.1.1: Define the TypedDict State

Action: Define the variables passed between nodes.

Task AC: State includes messages (list), sql_query (str), error_message (str), and retry_count (int).

Task 3.1.2: Build the Planner Node

Action: Create the node that invokes the LLM with the user prompt and the Catalog Tool output.

Task AC: Outputs a clean, executable SQL string (stripping out markdown backticks like ```sql).

Task 3.1.3: Build the Executor Node

Action: Execute the SQL using PySpark.

Task AC: Uses a try/except block catching PySparkException. If successful, saves the DataFrame preview to State. If failed, saves the exact error string to State.

Story 3.2: Implement the Self-Healing Loop
Story AC: When forced to generate bad SQL (e.g., asking for a non-existent column), the graph automatically catches the error, rewrites the query, and executes successfully without human intervention.

Task 3.1.1: Build the Conditional Edge

Action: Write the routing logic after the Executor Node.

Task AC: If error_message exists AND retry_count < 3, route to Healer. If success, route to END. If retries maxed out, route to END.

Task 3.1.2: Build the Healer Node

Action: Construct a specific prompt injecting the failed SQL and the Spark error message.

Task AC: The Healer node appends a "HumanMessage" to the state asking the LLM to correct the specific syntax/schema error, incrementing retry_count by 1.

🟣 Epic 4: Observability & Evaluation
Goal: Instrument the code to prove the AI's reliability and internal logic to external reviewers.

Story 4.1: MLflow Tracing Integration
Story AC: Every full execution of the LangGraph generates a visual trace in the Databricks MLflow UI.

Task 4.1.1: Enable Autologging

Action: Implement mlflow.langchain.autolog().

Task AC: Code runs without throwing MLflow configuration errors.

Task 4.1.2: Trace Verification

Action: Run a deliberate "Self-Healing" test.

Task AC: The MLflow trace shows the exact latency, token usage, and the back-and-forth conversation during the error-recovery loop.

🔵 Epic 5: Portfolio Packaging
Goal: Transform the Databricks notebook into a professional GitHub repository that screams "Senior Engineer."

Story 5.1: Repository Structure and Documentation
Story AC: The GitHub repository contains modular code, an architecture diagram, and visual proof of the system working, easily understandable by a hiring manager or tech lead in under 3 minutes.

Task 5.1.1: Code Modularization

Action: Export the monolithic CE notebook. Separate the code into agent.py, tools.py, and graph_state.py.

Task AC: The root directory contains clean Python files, not just a single messy .ipynb.

Task 5.1.2: Visual Architecture

Action: Generate a Mermaid.js diagram mapping the LangGraph nodes (Planner -> Executor -> Healer).

Task AC: Diagram renders correctly in the GitHub README.md.

Task 5.1.3: Proof of Execution

Action: Capture screenshots of the Databricks notebook output and the MLflow Trace showing a successful recovery.

Task AC: Images are embedded in the README.md under a "System in Action" header.