from langchain.tools import tool
from pyspark.sql.utils import AnalysisException

@tool
def get_table_columns(table_name: str) -> str:
    """Get the column names and data types for a Databricks table.

    Always run this tool before generating SQL to ensure accurate schema information and avoid hallucinations.

    Args:
        table_name (str): The name of the table to inspect.

    Returns:
        str: A comma-separated list of column names and data types, or an explicit error message.
    """
    try:
        columns = spark.catalog.listColumns(table_name)
        column_list = [f"{col.name}: {col.dataType}" for col in columns]
        return ", ".join(column_list)
    except AnalysisException:
        return "Table not found"
    except Exception as e:
        return f"Table inspection failed: {e}"
