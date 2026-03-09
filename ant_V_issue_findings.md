# Findings: antv-charts MCP Server Build Issues on Windows

When attempting to build the `@antv/mcp-server-chart` repository on Windows, several process errors occur due to the use of POSIX (Linux/Mac) specific shell commands within the [package.json](file:///d:/bmad/mcp-server-chart/package.json) scripts. 

### 1. The `rm -rf` Error
As seen in the logs:
```
> @antv/mcp-server-chart@0.9.10 prebuild
> rm -rf build/*

'rm' is not recognized as an internal or external command
```
**Cause:** The `prebuild` script uses `rm -rf`, which is a Unix command and is not natively available in the standard Windows Command Prompt (CMD). 

**Solution:** Replace the `prebuild` script in [package.json](file:///d:/bmad/mcp-server-chart/package.json) with a cross-platform Node.js alternative:
```json
"prebuild": "node -e \"require('fs').rmSync('build', { recursive: true, force: true })\""
```

### 2. The `husky` and `prepare` Hook Error
**Cause:** When you run `npm install`, npm automatically triggers the `prepare` script lifecycle event. In this repository, `prepare` is mapped to `husky && npm run build`. Because the `build` script triggers `prebuild` (which throws the `rm` error), the entire installation process fails and aborts.

Additionally, the repository defines a `postbuild` step using the Unix command `chmod +x build/index.js`, which may also fail or behave unpredictably on standard Windows systems.

**Solution:** 
1. Remove or modify the Linux-specific commands from the `scripts` section in [package.json](file:///d:/bmad/mcp-server-chart/package.json).
2. To successfully install the dependencies without triggering the broken hooks, you can run:
   ```cmd
   npm install --ignore-scripts
   ```
3. After the scripts in [package.json](file:///d:/bmad/mcp-server-chart/package.json) are fixed to be cross-platform, you can manually run the build step:
   ```cmd
   npm run build
   ```

### Next Steps for `d:\bmad\mcp-server-chart`
The [package.json](file:///d:/bmad/mcp-server-chart/package.json) file in your cloned repository has already been modified to remove the Linux-specific `rm -rf`, `chmod`, and `husky` hooks. 

To complete the setup, open a terminal in `d:\bmad\mcp-server-chart` and run:
1. `npm install --ignore-scripts`
2. `npm run build`

Once built, update your [mcp_config.json](file:///c:/Users/uberdev/.gemini/antigravity/mcp_config.json) to point directly to the built file:
```json
"antv-charts": {
  "command": "node",
  "args": [
    "d:/bmad/mcp-server-chart/build/index.js"
  ]
}
```
