---
description: Edit or create an IRIS class/routine, then compile it
argument-hint: "<document name, e.g. MyApp.Service.cls> [what to change]"
---

Edit (or create) an InterSystems IRIS document and compile it, using the `iris` MCP tools.

Request: `$ARGUMENTS`

Workflow:
1. Parse the document name (first token, with extension such as `.cls`/`.mac`/`.inc`).
   If none is given, ask which document to edit and stop.
2. Try `iris_read_document` to fetch the current source.
   - If it exists, this is an edit: show the relevant part and apply the requested change.
   - If it does not exist, this is a new document: scaffold sensible ObjectScript
     (e.g. `Class Pkg.Name Extends %RegisteredObject`).
3. Write the full, updated source with `iris_write_document`.
4. Compile with `iris_compile_documents` and report the compiler console output.
   - If compilation fails, read the errors, fix the source, and re-compile.
5. Summarize what changed. Do not delete documents in this command.

Follow the conventions in the `iris-objectscript` skill for ObjectScript syntax
and the read → edit → compile → verify loop.
