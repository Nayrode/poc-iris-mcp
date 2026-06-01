---
description: Explore IRIS code — namespaces, classes, routines, and source
argument-hint: "[namespace] [name filter, e.g. MyApp.%]"
---

Explore the InterSystems IRIS server using the `iris` MCP tools.

Arguments (optional): `$ARGUMENTS`
- First word, if present, is the target namespace.
- Remaining text, if present, is a name filter (SQL-LIKE, e.g. `MyApp.%`).

Do this:
1. Call `iris_server_info` to confirm connectivity and report the version + namespaces.
2. If a namespace was given use it, otherwise use the server's default.
3. Call `iris_list_documents` for that namespace (category `CLS`), applying the filter if one was provided.
4. Present a concise tree of the classes/packages found. If the user named a
   specific document, also `iris_read_document` it and summarize its structure
   (class signature, key methods/properties).

Do not modify anything in this command — exploration only.
