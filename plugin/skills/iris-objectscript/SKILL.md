---
name: iris-objectscript
description: Conventions and workflow for viewing and editing InterSystems IRIS code (ObjectScript classes, routines, includes) through the iris MCP tools. Use whenever reading, writing, compiling, or querying code on an IRIS server.
---

# Working with InterSystems IRIS code

This skill covers how to use the `iris` MCP tools effectively and the ObjectScript
conventions to follow. The code lives on the IRIS server, not on local disk.

## The core loop: read → edit → compile → verify

1. **Locate** — `iris_list_documents` (category `CLS` for classes, `RTN` for
   routines) with a `filter_pattern` like `MyApp.%`, or `iris_run_query` against
   `%Dictionary.ClassDefinition` for richer searches.
2. **Read** — `iris_read_document("MyApp.Service.cls")` returns the full source.
   Always read before editing.
3. **Edit** — build the *complete* new source text and send it with
   `iris_write_document`. The Atelier API replaces the whole document; there is no
   partial patch. Saving does **not** compile.
4. **Compile** — `iris_compile_documents(["MyApp.Service.cls"])`. Inspect the
   returned `console`. Anything other than a success message means it failed —
   fix and recompile.
5. **Verify** — re-read, or query, to confirm the result.

## Document names and types

Document names always include a type extension:

| Extension | Kind |
|-----------|------|
| `.cls` | Class definition |
| `.mac` | MAC routine (compiles to INT) |
| `.int` | Intermediate routine |
| `.inc` | Include file (macros) |

The package/class is dot-separated: `MyApp.Domain.Customer` → `MyApp.Domain.Customer.cls`.

## ObjectScript quick reference

```objectscript
Class MyApp.Greeter Extends %RegisteredObject
{

/// A class method returns a value with Quit.
ClassMethod Greet(name As %String = "world") As %String
{
    Quit "hello "_name
}

/// Instance method; properties declared with Property.
Property Count As %Integer [ InitialExpression = 0 ];

Method Increment() As %Status
{
    Set ..Count = ..Count + 1
    Quit $$$OK
}

}
```

- `Set` assigns, `_` concatenates strings, `..Name` accesses members, `$$$OK` is a
  success status macro.
- Class members are wrapped in `{ }`; each member (Method/Property/Parameter/Index)
  is its own block.

## Namespaces and safety

- Every tool takes an optional `namespace`; if omitted the server's configured
  default is used. Confirm the namespace for anything important.
- If the server runs read-only (`IRIS_MCP_READ_ONLY=true`), `iris_write_document`,
  `iris_delete_document`, and `iris_compile_documents` are not available. Don't
  attempt them — tell the user the server is view-only.
- Never delete documents or run destructive SQL without explicit confirmation.

## Editor / IntelliSense

Rich IntelliSense (hover, go-to-definition, completion) comes from the **official
InterSystems Language Server** in VS Code, not from these tools — see the
`.vscode/` configuration in the project README. The MCP tools are for programmatic
view/edit/compile/query; the Language Server is for interactive editing.
