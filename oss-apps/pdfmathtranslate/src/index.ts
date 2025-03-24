#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';

const execAsync = promisify(exec);

class PDFTranslateServer {
  private server: Server;
  private cmdPath: string;
  private venvPath: string;

  constructor() {
    this.server = new Server(
      {
        name: 'pdf-translate-server',
        version: '0.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.cmdPath = '/home/coder/ml-samples/oss-apps/pdfmathtranslate';
    this.venvPath = '/home/coder/ml-samples/oss-apps/pdfmathtranslate/.venv';
    this.setupToolHandlers();
    
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'translate_pdf',
          description: 'Translate a PDF file using Ollama model',
          inputSchema: {
            type: 'object',
            properties: {
              input_path: {
                type: 'string',
                description: 'Path to input PDF file',
              },
              source_lang: {
                type: 'string',
                description: 'Source language code (e.g., "en" for English)',
              },
              target_lang: {
                type: 'string',
                description: 'Target language code (e.g., "ja" for Japanese)',
              },
              model: {
                type: 'string',
                description: 'Ollama model name to use for translation',
              },
              threads: {
                type: 'number',
                description: 'Number of threads to use',
                default: 1,
              }
            },
            required: ['input_path', 'source_lang', 'target_lang', 'model'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      if (request.params.name !== 'translate_pdf') {
        throw new McpError(
          ErrorCode.MethodNotFound,
          `Unknown tool: ${request.params.name}`
        );
      }

      const args = request.params.arguments as {
        input_path: string;
        source_lang: string;
        target_lang: string;
        model: string;
        threads?: number;
      };

      try {
        const activateCmd = `cd ${this.cmdPath} && source .venv/bin/activate`;
        const translateCmd = `uv run pdf2h -li ${args.source_lang} -lo ${args.target_lang} -t ${args.threads || 1} -s "ollama:${args.model}" "${args.input_path}"`;
        const fullCmd = `${activateCmd} && ${translateCmd}`;

        const { stdout, stderr } = await execAsync(fullCmd, { shell: '/bin/bash' });

        return {
          content: [
            {
              type: 'text',
              text: stdout + (stderr ? `\nErrors:\n${stderr}` : ''),
            },
          ],
        };
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error executing translation: ${error}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('PDF Translate MCP server running on stdio');
  }
}

const server = new PDFTranslateServer();
server.run().catch(console.error);
