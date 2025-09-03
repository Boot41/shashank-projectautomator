
import { MCPClient, MCPClientFactory } from '../clients/mcp-clients.js';
import { defaultServers } from '../config/mcp-server.js';

export class CommandParser {
  private client: MCPClient;

  constructor() {
    // For now, let's use the default local server.
    // In the future, this could be made configurable.
    const serverConfig = defaultServers.find(s => s.name === 'local-mcp');
    if (!serverConfig) {
      throw new Error("Default local MCP server not found in configuration.");
    }
    this.client = MCPClientFactory.getClient(serverConfig);
  }

  async parse(command: string): Promise<any> {
    const parts = command.split(' ');
    const [entity, action, ...args] = parts;

    switch (entity) {
      case 'jira':
        return this.handleJira(action, args);
      case 'github':
        return this.handleGithub(action, args);
      case 'ai':
        return this.handleAi(action, args);
      default:
        // For natural language processing, we can send the whole command to the AI
        return this.client.processNaturalLanguage(command);
    }
  }

  private async handleJira(action: string, args: string[]): Promise<any> {
    switch (action) {
      case 'get':
        if (args[0] === '--id' && args[1]) {
          return this.client.getJiraIssue(args[1]);
        }
        break;
      case 'projects':
        return this.client.listJiraProjects();
      case 'list-issues':
        if (args[0] === '--project' && args[1]) {
          const status = args[2] === '--status' && args[3] ? args[3] : undefined;
          return this.client.listJiraIssues(args[1], status);
        }
        break;
    }
    return this.unrecognizedCommand('jira');
  }

  private async handleGithub(action: string, args: string[]): Promise<any> {
    if (action === 'commits' && args[0]) {
      const [owner, repo] = args[0].split('/');
      const limit = args[1] === '--limit' && args[2] ? parseInt(args[2], 10) : 10;
      return this.client.getGithubCommits(owner, repo, limit);
    }
    return this.unrecognizedCommand('github');
  }

  private async handleAi(action: string, args: string[]): Promise<any> {
    if (action === 'generate') {
      return this.client.generateAiResponse(args.join(' '));
    }
    return this.unrecognizedCommand('ai');
  }

  private unrecognizedCommand(tool: string) {
    return Promise.resolve(`Unrecognized command for ${tool}. Try 'help'.`);
  }
}
