import { MCPClientFactory, MCPClient } from '../clients/mcp-clients.js';
import { defaultServers } from '../config/mcp-server.js';
import { callAgent } from '../clients/agent.js';

interface CommandResult {
  success: boolean;
  data?: any;
  error?: string;
}

function parseArgs(args: string[]): Record<string, any> {
  const params: Record<string, any> = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg && arg.startsWith('--')) {
      const key = arg.slice(2);
      const nextArg = args[i + 1];
      const value = nextArg && !nextArg.startsWith('--') ? nextArg : true;
      params[key] = value;
      if (typeof value === 'string') i++;
    }
  }
  return params;
}

// Generate a session ID based on current date and time
const generateSessionId = (): string => {
  const now = new Date();
  return `cli_${now.getFullYear()}${(now.getMonth() + 1).toString().padStart(2, '0')}${now.getDate().toString().padStart(2, '0')}_${now.getHours().toString().padStart(2, '0')}${now.getMinutes().toString().padStart(2, '0')}`;
};

export const parseCommand = async (input: string, sessionId?: string): Promise<CommandResult> => {
  try {
    // Support 'agent: <prompt>' path to call FastMCP agent microservice
    const [maybeAgent, ...rest] = input.split(':');
    if (maybeAgent && maybeAgent.trim() === 'agent') {
      const prompt = rest.join(':').trim();
      if (!prompt) return { success: false, error: 'No prompt provided.' };
      const baseUrl = process.env['FASTMCP_URL'] || 'http://127.0.0.1:8000';
      const finalSessionId = sessionId || generateSessionId();
      const data = await callAgent(baseUrl, { prompt, session_id: finalSessionId });
      return { success: true, data };
    }

    const [serverName, ...parts] = [maybeAgent, ...rest];
    const command = parts.join(':');

    if (!serverName) {
      return { success: false, error: 'No server name provided in input.' };
    }

    const targetServer = serverName.includes(':') 
      ? defaultServers.find(s => s.name === serverName)
      : defaultServers.find(s => s.name === 'local-mcp');

    if (!targetServer) {
      return { success: false, error: `Unknown MCP server: ${serverName}` };
    }

    const client = MCPClientFactory.getClient(targetServer);
    const result = await executeCommand(client, command);
    return { success: true, data: result };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' };
  }
};

async function executeCommand(_client: MCPClient, command: string) {
  const [tool, ...args] = command.split(' ');
  const params = parseArgs(args);
  // Note: executeTool method needs to be implemented in MCPClient
  return { tool, params, message: "MCP client execution not yet implemented" };
}