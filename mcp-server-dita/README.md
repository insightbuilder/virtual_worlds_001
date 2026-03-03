# DITA MCP Server
Converts Markdown to PDF using the DITA Open Toolkit.

**Project Path:** `d:\gitFolders\virtual_worlds_001\mcp-server-dita`

## Overview
This MCP server exposes a `md_to_pdf` tool that utilizes the DITA Open Toolkit (`dita` executable) to convert input Markdown files directly into PDF format.

## Setup & Implementation
- **Dependencies**: Uses `hatchling` as the build system and the official `mcp` SDK.
- **Server Logic**: Implemented using `FastMCP` (named "dita"). 
- **Tool Details**: The `@mcp.tool()` `md_to_pdf` takes an `input_path` and `output_path`. It runs `dita --input <input_path> --format pdf --output <temp_dir>`, handles DITA's behavior of saving to a temporary directory, and then moves the generated PDF to the requested `output_path`.

## How to Configure in MCP Clients
You can add this to your `mcp_config.json` (for clients like Claude Desktop or Cursor):

```json
{
  "dita-server": {
    "command": "uv",
    "args": [
      "--directory",
      "d:/gitFolders/virtual_worlds_001/mcp-server-dita",
      "run",
      "mcp-server-dita"
    ]
  }
}
```
*(Ensure you modify the `uv` execution path or add the absolute project path if necessary depending on your environment).*

When asked in chat, the AI agent can call `md_to_pdf` with your specific markdown paths to generate PDFs seamlessly!

