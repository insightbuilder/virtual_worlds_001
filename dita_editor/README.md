# DITA Authoring Tool

This is a simple Node.js application that provides a modern, easy-to-use Markdown authoring interface directly integrating with the **DITA Open Toolkit (DITA-OT)**.

### Why DITA-OT?
Adobe FrameMaker uses proprietary engines to stitch documents together and generate complex PDFs (TOC, cross-references, style catalogues). DITA-OT does exactly the same thing but is Open Source and allows you to write in Markdown!

## 1. Prerequisites (Installing DITA-OT)

To use the "Publish" buttons, you must have DITA-OT and Java installed on your machine.
1. Install Java (JRE or JDK 8+). [Download](https://www.java.com/)
2. Download DITA-OT from their official site: [dita-ot.org/download](https://www.dita-ot.org/download)
3. Extract the `.zip` file into a directory (e.g., `C:\dita-ot`).
4. **Important**: Add the `C:\dita-ot\bin` directory to your system's `PATH` environment variable.

## 2. Running The Editor

1. Open your terminal in this directory (`d:\gitFolders\mcp_filesystem\dita_editor`).
2. Run `npm run start` 
3. Open your browser to `http://localhost:3000`

## 3. How to Use

- The editor on the left is a standard Markdown editor.
- Click **Save** to save the contents to `src/concept.md`.
- Click **Publish to PDF** or **Publish to HTML**.
  - The Node.js server will trigger DITA-OT in the background.
  - It uses the `src/book.ditamap` (which acts like a FrameMaker `.book` file) to stitch everything together.
  - The output will be placed in the `out/` folder.
