// Dependencies are installed outside the checkout; pass their node_modules directory.
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const modules = process.argv[2];
if (!modules)
{
    throw new Error("Usage: node mydocs/smlib/tools/check_diagrams.mjs <node_modules-directory>");
}
const { JSDOM } = await import(pathToFileURL(path.join(modules, "jsdom/lib/api.js")));
const dom = new JSDOM("<!doctype html><html><body></body></html>");
globalThis.window = dom.window;
globalThis.document = dom.window.document;
const { default: mermaid } = await import(
    pathToFileURL(path.join(modules, "mermaid/dist/mermaid.esm.mjs")));
const { default: katex } = await import(
    pathToFileURL(path.join(modules, "katex/dist/katex.mjs")));
mermaid.initialize({ startOnLoad: false, securityLevel: "strict" });
const docs = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
let diagrams = 0;
let formulas = 0;
let errors = 0;

async function markdownFiles(directory)
{
    const files = [];
    const entries = await fs.readdir(directory, { withFileTypes: true });
    for (const entry of entries.sort((left, right) => left.name.localeCompare(right.name)))
    {
        const filename = path.join(directory, entry.name);
        if (entry.isDirectory())
        {
            files.push(...await markdownFiles(filename));
        }
        else if (entry.isFile() && entry.name.endsWith(".md"))
        {
            files.push(filename);
        }
    }
    return files;
}

for (const filename of await markdownFiles(docs))
{
    const name = path.relative(docs, filename);
    const content = await fs.readFile(filename, "utf8");
    for (const match of content.matchAll(/```mermaid\r?\n([\s\S]*?)```/g))
    {
        try
        {
            await mermaid.parse(match[1]);
            diagrams++;
        }
        catch (error)
        {
            console.error(`${name}: Mermaid: ${error.message}`);
            errors++;
        }
    }
    const prose = content.replace(/```[\s\S]*?```/g, "").replace(/`[^`]*`/g, "");
    for (const match of prose.matchAll(/\$\$([\s\S]*?)\$\$|(?<![\\$])\$([^$\n]+)\$/g))
    {
        try
        {
            katex.renderToString(match[1] ?? match[2], {
                displayMode: match[1] !== undefined,
                throwOnError: true,
                strict: "error"
            });
            formulas++;
        }
        catch (error)
        {
            console.error(`${name}: LaTeX: ${error.message}`);
            errors++;
        }
    }
}
console.log(`Parsed ${diagrams} Mermaid diagrams and rendered ${formulas} LaTeX expressions; ${errors} errors.`);
console.log("This verifies syntax, not browser layout or C++ examples.");
process.exitCode = errors > 0 ? 1 : 0;
