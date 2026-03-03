# MCP Server Explanation: Resources, Prompts, and Tools

The code snippet from `server.py` defines the "capabilities" that this SQLite server exposes to any Model Context Protocol (MCP) client. In the MCP architecture, a server can provide three main things to an AI assistant: **Resources**, **Prompts**, and **Tools**.

## Here is what each block of code does:

### 1. Resources (`handle_list_resources`, `handle_read_resource`)

**Resources** are like files or static data that the server exposes to the client to read and use as context.

*   **`handle_list_resources()`**: Tells the client what resources are available. In this case, it advertises exactly one resource: a text document called "Business Insights Memo" located at the custom URI `memo://insights`.
*   **`handle_read_resource(uri)`**: When the client asks to actually *read* the `memo://insights` resource, this function gets called. It validates the URI, calls `db._synthesize_memo()` to generate the content (which stitches together all the business insights you've saved), and sends the resulting text back to the client.

```python
@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    logger.debug("Handling list_resources request")
    return [
        types.Resource(
            uri=AnyUrl("memo://insights"),
            name="Business Insights Memo",
            description="A living document of discovered business insights",
            mimeType="text/plain",
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    logger.debug(f"Handling read_resource request for URI: {uri}")
    if uri.scheme != "memo":
        logger.error(f"Unsupported URI scheme: {uri.scheme}")
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    path = str(uri).replace("memo://", "")
    if not path or path != "insights":
        logger.error(f"Unknown resource path: {path}")
        raise ValueError(f"Unknown resource path: {path}")

    return db._synthesize_memo()
```

### 2. Prompts (`handle_list_prompts`, `handle_get_prompt`)

**Prompts** are pre-configured conversational templates or instructions that the client can trigger.

*   **`handle_list_prompts()`**: Advertises the available prompts. Here, it lists one prompt named `mcp-demo`. It also specifies that this prompt requires a user argument called `topic` (e.g., "sales", "inventory").
*   **`handle_get_prompt(name, arguments)`**: When the user triggers the "mcp-demo" prompt in their client and provides a topic, this function executes. It injects the user's `topic` into a large pre-defined string template (`PROMPT_TEMPLATE`) and returns it. This acts as the initial system instructions to kick off an interactive database roleplay.

```python
@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    logger.debug("Handling list_prompts request")
    return [
        types.Prompt(
            name="mcp-demo",
            description="A prompt to seed the database with initial data and demonstrate what you can do with an SQLite MCP Server + Claude",
            arguments=[
                types.PromptArgument(
                    name="topic",
                    description="Topic to seed the database with initial data",
                    required=True,
                )
            ],
        )
    ]

@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
    logger.debug(f"Handling get_prompt request for {name} with args {arguments}")
    if name != "mcp-demo":
        logger.error(f"Unknown prompt: {name}")
        raise ValueError(f"Unknown prompt: {name}")

    if not arguments or "topic" not in arguments:
        logger.error("Missing required argument: topic")
        raise ValueError("Missing required argument: topic")

    topic = arguments["topic"]
    prompt = PROMPT_TEMPLATE.format(topic=topic)

    logger.debug(f"Generated prompt template for topic: {topic}")
    return types.GetPromptResult(
        description=f"Demo template for {topic}",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt.strip()),
            )
        ],
    )
```

### 3. Tools (`handle_list_tools`)

**Tools** are active functions the client can call to *do* things or fetch live data.

*   **`handle_list_tools()`**: This function simply returns a "menu" of all the tools the server supports. For each tool, it provides the name, a description of what it does, and a JSON Schema (`inputSchema`) dictating exactly what arguments the AI needs to provide when calling the tool.

```python
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="read_query",
            description="Execute a SELECT query on the SQLite database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SELECT SQL query to execute"},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="write_query",
            description="Execute an INSERT, UPDATE, or DELETE query on the SQLite database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query to execute"},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="create_table",
            description="Create a new table in the SQLite database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "CREATE TABLE SQL statement"},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="list_tables",
            description="List all tables in the SQLite database",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="describe_table",
            description="Get the schema information for a specific table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string", "description": "Name of the table to describe"},
                },
                "required": ["table_name"],
            },
        ),
        types.Tool(
            name="append_insight",
            description="Add a business insight to the memo",
            inputSchema={
                "type": "object",
                "properties": {
                    "insight": {"type": "string", "description": "Business insight discovered from data analysis"},
                },
                "required": ["insight"],
            },
        ),
    ]
```

*   **`handle_call_tool(name, arguments)`**: This function acts as the execution router. When the client decides to use one of the tools listed above, this function intercepts the request. It checks the `name` of the tool and routes the `arguments` (if any) to the underlying database connection. It has built-in safety checks, like making sure a `read_query` is actually a `SELECT` statement, or a `write_query` is not. After executing the respective action, it formats the result into a `TextContent` object and returns it to the client.

```python
@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests"""
    try:
        if name == "list_tables":
            results = db._execute_query(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            return [types.TextContent(type="text", text=str(results))]

        elif name == "describe_table":
            if not arguments or "table_name" not in arguments:
                raise ValueError("Missing table_name argument")
            results = db._execute_query(
                f"PRAGMA table_info({arguments['table_name']})"
            )
            return [types.TextContent(type="text", text=str(results))]

        elif name == "append_insight":
            if not arguments or "insight" not in arguments:
                raise ValueError("Missing insight argument")

            db.insights.append(arguments["insight"])
            _ = db._synthesize_memo()

            # Notify clients that the memo resource has changed
            await server.request_context.session.send_resource_updated(AnyUrl("memo://insights"))

            return [types.TextContent(type="text", text="Insight added to memo")]

        if not arguments:
            raise ValueError("Missing arguments")

        if name == "read_query":
            if not arguments["query"].strip().upper().startswith("SELECT"):
                raise ValueError("Only SELECT queries are allowed for read_query")
            results = db._execute_query(arguments["query"])
            return [types.TextContent(type="text", text=str(results))]

        elif name == "write_query":
            if arguments["query"].strip().upper().startswith("SELECT"):
                raise ValueError("SELECT queries are not allowed for write_query")
            results = db._execute_query(arguments["query"])
            return [types.TextContent(type="text", text=str(results))]

        elif name == "create_table":
            if not arguments["query"].strip().upper().startswith("CREATE TABLE"):
                raise ValueError("Only CREATE TABLE statements are allowed")
            db._execute_query(arguments["query"])
            return [types.TextContent(type="text", text="Table created successfully")]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except sqlite3.Error as e:
        return [types.TextContent(type="text", text=f"Database error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
```

---
**How it all fits together:** 
When the MCP client (like an IDE or chat interface) first connects to this SQLite server, it calls `list_resources`, `list_prompts`, and `list_tools` to understand what the server can do. When the model actually decides to take an action, it issues a tool call request which is captured and executed by `handle_call_tool`. The definitions provided in these functions are exactly what surfaces in the client's UI or to the AI model so it knows how to interact with your database.
