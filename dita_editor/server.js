const express = require('express');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static('public'));
app.use('/out', express.static('out')); // serve generated files

const SRC_DIR = path.join(__dirname, 'src');
const OUT_DIR = path.join(__dirname, 'out');
const DITA_CMD = process.env.DITA_HOME ? path.join(process.env.DITA_HOME, 'bin', 'dita') : 'dita';

// Ensure directories exist
if (!fs.existsSync(SRC_DIR)) fs.mkdirSync(SRC_DIR);
if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR);

// Ensure a default file exists
const defaultFile = path.join(SRC_DIR, 'concept.md');
if (!fs.existsSync(defaultFile)) {
    fs.writeFileSync(defaultFile, '# Welcome to Document Authoring\n\nStart typing your content here using Markdown.\n\n## Section 1\n\nSome text here.');
}

const mapFile = path.join(SRC_DIR, 'book.ditamap');
if (!fs.existsSync(mapFile)) {
    fs.writeFileSync(mapFile, `<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
<map>
    <title>My Documentation</title>
    <topicref href="concept.md" format="markdown"/>
</map>`);
}

// API: List files
app.get('/api/files', (req, res) => {
    try {
        const files = fs.readdirSync(SRC_DIR).filter(f => f.endsWith('.md'));
        res.json({ files });
    } catch (err) {
        res.status(500).json({ error: 'Failed to list files' });
    }
});

// API: Get content of a file
app.get('/api/content', (req, res) => {
    try {
        const filename = req.query.filename || 'concept.md';
        const filePath = path.join(SRC_DIR, filename);
        if (!fs.existsSync(filePath)) {
            return res.status(404).json({ error: 'File not found' });
        }
        const content = fs.readFileSync(filePath, 'utf8');
        res.json({ content });
    } catch (err) {
        res.status(500).json({ error: 'Failed to read file' });
    }
});

// API: Save content
app.post('/api/content', (req, res) => {
    try {
        const filename = req.body.filename || 'concept.md';
        const filePath = path.join(SRC_DIR, filename);
        fs.writeFileSync(filePath, req.body.content);
        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ error: 'Failed to save file' });
    }
});

function updateDitaMap() {
    const files = fs.readdirSync(SRC_DIR).filter(f => f.endsWith('.md'));
    let mapXml = `<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
<map>
    <title>My Documentation</title>\n`;
    for (const f of files) {
        mapXml += `    <topicref href="${f}" format="markdown"/>\n`;
    }
    mapXml += `</map>`;
    fs.writeFileSync(mapFile, mapXml);
}

// API: Publish using DITA-OT
app.get('/api/publish', (req, res) => {
    const format = req.query.format || 'pdf';
    console.log(`Publishing project to ${format} (Streaming)...`);
    
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    
    updateDitaMap();
    
    const cmdArgs = ['-i', mapFile, '-f', format, '-o', OUT_DIR];
    
    // Use res.flushHeaders() to start SSE stream immediately
    res.flushHeaders();
    res.write(`data: ${JSON.stringify({ type: 'stdout', text: '> Initializing DITA-OT Environment...\n' })}\n\n`);

    const ditaProcess = spawn(DITA_CMD, cmdArgs, { shell: true });
    
    ditaProcess.on('error', (err) => {
        res.write(`data: ${JSON.stringify({ type: 'error', message: 'Failed to start DITA-OT: ' + err.message })}\n\n`);
        res.end();
    });

    ditaProcess.stdout.on('data', (data) => {
        res.write(`data: ${JSON.stringify({ type: 'stdout', text: data.toString() })}\n\n`);
    });
    
    ditaProcess.stderr.on('data', (data) => {
        res.write(`data: ${JSON.stringify({ type: 'stderr', text: data.toString() })}\n\n`);
    });
    
    ditaProcess.on('close', (code) => {
        if (code === 0) {
            res.write(`data: ${JSON.stringify({ type: 'done', message: `Successfully published to ${format}` })}\n\n`);
        } else {
            res.write(`data: ${JSON.stringify({ type: 'error', message: `Publishing failed with code ${code}. Ensure DITA-OT is properly installed.` })}\n\n`);
        }
        res.end();
    });
});

const PORT = 3057;
app.listen(PORT, () => {
    console.log(`Authoring tool running on http://localhost:${PORT}`);
    console.log(`To publish successfully, ensure you have Java and DITA-OT installed.`);
});
