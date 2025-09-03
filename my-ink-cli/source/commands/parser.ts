import { MCPClientFactory, MCPClient } from '../clients/mcp-clients.js';
import { defaultServers } from '../config/mcp-server.js';

interface CommandResult {
  success: boolean;
  data?: any;
  error?: string;
}

function parseArgs(args: string[]): Record<string, any> {
  const params: Record<string, any> = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      const value = args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true;
      params[key] = value;
      if (typeof value === 'string') i++;
    }
  }
  return params;
}

export const parseCommand = async (input: string): Promise<CommandResult> => {
  try {
    const [serverName, ...parts] = input.split(':');
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

async function executeCommand(client: MCPClient, command: string) {
  const [tool, ...args] = command.split(' ');
  const params = parseArgs(args);
  return client.executeTool(tool, params);
}