import axios from 'axios';
import type { MCPServerConfig } from '../config/mcp-server.js';

export class MCPClient {
  private client;

  constructor(private config: MCPServerConfig) {
    this.client = axios.create({
      baseURL: this.config.url,
      headers: this.config.apiKey ? { 'Authorization': `Bearer ${this.config.apiKey}` } : {}
    });
  }

  // Jira Endpoints
  async getJiraIssue(ticketId: string) {
    const response = await this.client.get(`/jira/issue/${ticketId}`);
    return response.data;
  }

  async listJiraProjects() {
    const response = await this.client.get('/jira/projects');
    return response.data;
  }

  async listJiraIssues(projectKey: string, status?: string) {
    const params = status ? { status } : {};
    const response = await this.client.get(`/jira/issues/${projectKey}`, { params });
    return response.data;
  }

  // GitHub Endpoints
  async getGithubCommits(owner: string, repo: string, limit: number = 10) {
    const response = await this.client.get(`/github/commits/${owner}/${repo}`, {
      params: { limit }
    });
    return response.data;
  }

  // AI Endpoints
  async processNaturalLanguage(naturalLanguage: string) {
    const response = await this.client.post('/ai/process-nl', { natural_language: naturalLanguage });
    return response.data;
  }

  async generateAiResponse(prompt: string) {
    const response = await this.client.post('/ai/generate', { prompt });
    return response.data;
  }
}

export class MCPClientFactory {
  private static clients: Map<string, MCPClient> = new Map();

  static getClient(serverConfig: MCPServerConfig): MCPClient {
    if (!this.clients.has(serverConfig.name)) {
      this.clients.set(serverConfig.name, new MCPClient(serverConfig));
    }
    return this.clients.get(serverConfig.name)!;
  }
}
