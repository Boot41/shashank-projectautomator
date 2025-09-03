export interface MCPServerConfig {
  name: string;
  url: string;
  type: 'github' | 'custom';
  apiKey?: string;
}

export const defaultServers: MCPServerConfig[] = [
  {
    name: 'github-official',
    url: 'https://github.com/github/github-mcp-server',
    type: 'github'
  },
  {
    name: 'local-mcp',
    url: 'http://localhost:8000',
    type: 'custom'
  }
];