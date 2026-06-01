---
description: Run an SQL query against an IRIS namespace
argument-hint: "<SQL query>"
---

Run the following SQL against InterSystems IRIS using the `iris_run_query` MCP tool:

```sql
$ARGUMENTS
```

Steps:
1. If the query is empty, ask the user what they want to query and stop.
2. Run it with `iris_run_query` in the default namespace (or one the user specified).
3. Render the rows as a Markdown table. If many rows return, show the first ~50
   and note the total count.
4. Never auto-run destructive DDL/DML (DROP/DELETE/UPDATE/INSERT) without
   confirming with the user first.
