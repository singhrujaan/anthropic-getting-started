# agent.py
#
# This is the brain of the system.
# It takes a plain English question,
# turns it into SQL, runs it, and explains the result.
#
# Flow:
# question → read schema → ask Claude for SQL
#          → run SQL → ask Claude to explain result
#          → return answer

import os
from dotenv import load_dotenv
from anthropic import Anthropic
from database import get_schema, execute_query

load_dotenv()
client = Anthropic()


def ask_database(question: str) -> dict:
    """
    Takes a plain English question.
    Returns the answer, the SQL used, and an explanation.
    """

    # ── Step 1: Get the database schema ──
    # This tells Claude what tables and columns exist
    schema = get_schema()

    # ── Step 2: Ask Claude to write SQL ──
    # We give Claude the schema + question
    # and ask it to write a SQL query
    sql_response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=512,
        system="""You are a SQL expert.
The user will give you a database schema and a question.
Write a single SQL query to answer the question.
Return ONLY the SQL query — no explanation, no markdown, no backticks.
Just the raw SQL query.""",
        messages=[{
            "role": "user",
            "content": f"""Database schema:
{schema}

Question: {question}

Write the SQL query:"""
        }]
    )

    # Get the SQL query Claude wrote
    sql_query = sql_response.content[0].text.strip()
    print(f"SQL generated: {sql_query}")

    # ── Step 3: Run the SQL query ──
    result = execute_query(sql_query)

    # ── Step 4: Handle errors ──
    # If SQL failed — ask Claude to fix it
    if not result["success"]:
        print(f"SQL failed: {result['error']}")
        print("Asking Claude to fix it...")

        # Tell Claude what went wrong
        fix_response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=512,
            system="""You are a SQL expert.
Fix the SQL query based on the error message.
Return ONLY the corrected SQL — no explanation.""",
            messages=[{
                "role": "user",
                "content": f"""Schema:
{schema}

Original question: {question}

SQL that failed: {sql_query}

Error: {result['error']}

Write the corrected SQL:"""
            }]
        )

        # Try the fixed SQL
        sql_query = fix_response.content[0].text.strip()
        print(f"Fixed SQL: {sql_query}")
        result = execute_query(sql_query)

    # ── Step 5: If still failing — return error ──
    if not result["success"]:
        return {
            "question": question,
            "sql":      sql_query,
            "answer":   "Sorry I could not answer that question.",
            "error":    result["error"]
        }

    # ── Step 6: Ask Claude to explain the results ──
    # Turn raw database rows into a plain English answer
    rows_text = str(result["rows"][:10])  # show max 10 rows

    explain_response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=256,
        system="""You are a helpful data analyst.
Explain database query results in plain English.
Be specific — use the actual numbers from the results.
Keep it short — 2-3 sentences maximum.
Plain text only, no markdown.""",
        messages=[{
            "role": "user",
            "content": f"""Question: {question}

Query results:
Columns: {result['columns']}
Rows: {rows_text}
Total rows: {result['row_count']}

Explain what these results mean:"""
        }]
    )

    answer = explain_response.content[0].text.strip()

    # ── Step 7: Return everything ──
    return {
        "question":  question,
        "sql":       sql_query,
        "columns":   result["columns"],
        "rows":      result["rows"],
        "row_count": result["row_count"],
        "answer":    answer
    }


# ── Test it ──
if __name__ == "__main__":

  # Test error recovery — intentionally vague question
    print("\n" + "=" * 55)
    print("Question: What are the top selling items?")
    print("=" * 55)
    result = ask_database("What are the top selling items?")
    print(f"SQL:    {result['sql']}")
    print(f"Answer: {result['answer']}")