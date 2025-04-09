#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema, McpError, ErrorCode, } from "@modelcontextprotocol/sdk/types.js";
import { NodeHtmlMarkdown } from 'node-html-markdown';
// Tool definitions
const WEB_SEARCH_TOOL = {
    name: "searxng_web_search",
    description: "Performs a web search using the SearXNG API. Supports pagination and multiple search engines.",
    inputSchema: {
        type: "object",
        properties: {
            query: {
                type: "string",
                description: "Search query",
            },
            count: {
                type: "number",
                description: "Number of results (default: 10)",
                default: 10,
            },
            offset: {
                type: "number",
                description: "Pagination offset (default: 0)",
                default: 0,
            },
        },
        required: ["query"],
    },
};
const URL_READER_TOOL = {
    name: "web_url_read",
    description: "Fetches content from a URL and converts it to Markdown format.",
    inputSchema: {
        type: "object",
        properties: {
            url: {
                type: "string",
                description: "URL to fetch content from",
            },
            timeout: {
                type: "number",
                description: "Timeout in milliseconds (default: 10000)",
                default: 10000,
            },
        },
        required: ["url"],
    },
};
// Type guards
function isWebSearchArgs(args) {
    return (typeof args === "object" &&
        args !== null &&
        typeof args.query === "string");
}
function isURLReaderArgs(args) {
    return (typeof args === "object" &&
        args !== null &&
        typeof args.url === "string");
}
// Server implementation
const server = new Server({
    name: "mcp-searxng",
    version: "0.1.0",
}, {
    capabilities: {
        resources: {},
        tools: {},
    },
});
// Helper functions
async function performWebSearch(query, count = 10, offset = 0) {
    console.error("[DEBUG] Starting web search...");
    const searxngUrl = process.env.SEARXNG_URL || "http://localhost:8888";
    const url = new URL(`${searxngUrl}/search`);
    console.error("[DEBUG] Search URL:", url.toString());
    url.searchParams.set("q", query);
    url.searchParams.set("format", "json");
    url.searchParams.set("start", offset.toString());
    url.searchParams.set("count", count.toString());
    try {
        console.error("[DEBUG] Sending request to SearXNG...");
        const response = await fetch(url.toString());
        console.error("[DEBUG] Response status:", response.status);
        if (!response.ok) {
            throw new McpError(ErrorCode.InternalError, `SearXNG API error: ${response.status} ${response.statusText}`);
        }
        const text = await response.text();
        console.error("[DEBUG] Raw response:", text);
        const data = JSON.parse(text);
        const results = data.results.map(result => ({
            title: result.title || "",
            content: result.content || "",
            url: result.url || "",
        }));
        return results
            .map(r => `Title: ${r.title}\nDescription: ${r.content}\nURL: ${r.url}`)
            .join("\n\n");
    }
    catch (error) {
        if (error instanceof McpError)
            throw error;
        throw new McpError(ErrorCode.InternalError, `Failed to perform search: ${error instanceof Error ? error.message : String(error)}`);
    }
}
async function fetchAndConvertToMarkdown(url, timeoutMs = 10000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const response = await fetch(url, {
            signal: controller.signal,
        });
        if (!response.ok) {
            throw new McpError(ErrorCode.InternalError, `Failed to fetch URL: ${response.status} ${response.statusText}`);
        }
        const htmlContent = await response.text();
        return NodeHtmlMarkdown.translate(htmlContent);
    }
    catch (error) {
        if (error instanceof McpError)
            throw error;
        if (error instanceof Error && error.name === "AbortError") {
            throw new McpError(ErrorCode.InternalError, `Request timed out after ${timeoutMs}ms`);
        }
        throw new McpError(ErrorCode.InternalError, `Failed to process URL: ${error instanceof Error ? error.message : String(error)}`);
    }
    finally {
        clearTimeout(timeoutId);
    }
}
// Request handlers
server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [WEB_SEARCH_TOOL, URL_READER_TOOL],
}));
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    try {
        const { name, arguments: args } = request.params;
        if (!args) {
            throw new McpError(ErrorCode.InvalidParams, "No arguments provided");
        }
        if (name === "searxng_web_search") {
            if (!isWebSearchArgs(args)) {
                throw new McpError(ErrorCode.InvalidParams, "Invalid arguments for web search");
            }
            const { query, count = 10, offset = 0 } = args;
            const results = await performWebSearch(query, count, offset);
            return {
                content: [{ type: "text", text: results }],
                isError: false,
            };
        }
        if (name === "web_url_read") {
            if (!isURLReaderArgs(args)) {
                throw new McpError(ErrorCode.InvalidParams, "Invalid arguments for URL reader");
            }
            const { url, timeout = 10000 } = args;
            const content = await fetchAndConvertToMarkdown(url, timeout);
            return {
                content: [{ type: "text", text: content }],
                isError: false,
            };
        }
        throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
    }
    catch (error) {
        if (error instanceof McpError) {
            return {
                content: [{ type: "text", text: error.message }],
                isError: true,
            };
        }
        return {
            content: [{ type: "text", text: `Error: ${String(error)}` }],
            isError: true,
        };
    }
});
// Server startup
async function runServer() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("SearXNG MCP server running on stdio");
}
runServer().catch((error) => {
    console.error("Fatal error running server:", error);
    process.exit(1);
});
