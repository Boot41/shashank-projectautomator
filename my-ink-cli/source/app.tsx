import React, {useCallback, useMemo, useState, useEffect} from 'react';
import {Box, Text, useApp} from 'ink';
import Gradient from 'ink-gradient';
import BigText from 'ink-big-text';
import TextInput from 'ink-text-input';
import axios from 'axios';

type ResultKind = 'info' | 'error' | 'result';


const MCP_BASE_URL = process.env['MCP_BASE_URL'] ?? 'http://localhost:8000';

type HistoryEntry = {
  cmd: string;
  type: ResultKind;
  text: string;
};

export default function App() {
  const {exit} = useApp();
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [exiting, setExiting] = useState(false);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [blinkVisible, setBlinkVisible] = useState(true);

  useEffect(() => {
	if (busy || exiting) return; // pause blinking when not interactive
	const id = setInterval(() => setBlinkVisible(v => !v), 500); // 500ms blink
	return () => clearInterval(id);
  }, [busy, exiting]);

  const helpText = useMemo(
    () =>
      [
        'Available Jira commands:',
        '  - jira get --id <TICKET_ID>  - Get Jira ticket details',
        '  - jira projects             - List all accessible Jira projects',
        '  - jira list-issues --project <KEY> [--status <STATUS>] - List issues in a project',
        '  - jira summarize --id <TICKET_ID> - Get AI summary of a ticket',
        '',
        'Available GitHub commands:',
        '  - github commits <owner>/<repo> [--branch <branch>] - Get commit history',
        '  - github commits <owner>/<repo> --limit <number>   - Limit number of commits',
        '  - github commits <owner>/<repo> --since <date>     - Commits since date',
        '  - github commits <owner>/<repo> --until <date>     - Commits until date',
        '',
        'General commands:',
        '  - /help                      - Show this help message',
        '  - /quit                      - Exit the application',
        '',
        'Natural Language Examples:',
        '  - "Show me ticket ABC-123"',
        '  - "Show commits from facebook/react"',
        '  - "Show last 5 commits from main branch"',
        '  - "Show commits from last week"',
        '  - "Show commits between Jan 1 and Feb 1"',
        '  - "List open issues in project ABC"',
        '  - "What\'s in progress in project XYZ?"',
      ].join('\n'),
    []
  );

  const append = useCallback((entry: HistoryEntry) => {
    setHistory(prev => [...prev, entry]);
  }, []);

  const processNaturalLanguage = useCallback(async (input: string) => {
    try {
      setBusy(true);
      const response = await axios.post(
        `${MCP_BASE_URL}/ai/process-command`,
        { natural_language: input },
        { 
          timeout: 30_000,
          headers: { 'Content-Type': 'application/json' }
        }
      );

      if (!response.data) {
        throw new Error('No response from server');
      }

      if (response.data.status !== 'success') {
        throw new Error(response.data.error || 'Failed to process command');
      }

      if (!response.data.command) {
        throw new Error('No command was generated');
      }

      return {
        success: true,
        command: response.data.command,
        explanation: response.data.explanation,
      };
    } catch (error: any) {
      console.error('Error processing command:', error);
      let errorMessage = 'Failed to process command';
      
      if (error.response) {
        // Server responded with error status code
        errorMessage = error.response.data?.error || 
                      error.response.statusText || 
                      `Server error: ${error.response.status}`;
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'No response from server. Is the MCP server running?';
      } else if (error.message) {
        // Other errors
        errorMessage = error.message;
      }
      
      return {
        success: false,
        error: errorMessage,
      };
    } finally {
      setBusy(false);
    }
  }, []);

  const runCommand = useCallback(
    async (line: string) => {
      const trimmed = line.trim();
      if (!trimmed) return;

      // Check if it's a natural language command (not starting with /, jira, or github)
      if (!trimmed.startsWith('/') && !trimmed.startsWith('jira ') && !trimmed.startsWith('github ')) {
        append({ cmd: trimmed, type: 'info', text: 'Processing natural language...' });
        
        const result = await processNaturalLanguage(trimmed);
        if (!result.success) {
          append({ 
            cmd: trimmed, 
            type: 'error', 
            text: `Failed to process command: ${result.error}` 
          });
          return;
        }

        // Show the interpreted command
        if (result.explanation) {
          append({ 
            cmd: '', 
            type: 'info', 
            text: `→ ${result.explanation}` 
          });
        }

        // Execute the generated command
        if (result.command) {
          await runCommand(result.command);
        }
        return;
      }

      // Handle built-ins
      if (trimmed === '/quit') {
        setExiting(true);
        append({cmd: trimmed, type: 'info', text: 'Exiting...'});
        setTimeout(() => exit(), 10);
        return;
      }

      // Handle github commands
      if (trimmed.startsWith('github commits ')) {
        try {
          setBusy(true);
          // Extract the repo path and any additional flags
          const repoPath = trimmed.replace('github commits ', '').split(' ')[0];
          
          if (!repoPath) {
            throw new Error('Repository path is required. Use: github commits owner/repo');
          }
          
          const repoParts = repoPath.split('/');
          
          if (repoParts.length !== 2) {
            throw new Error('Invalid repository format. Use: github commits owner/repo');
          }
          
          const [owner, repo] = repoParts;
          const params = new URLSearchParams();
          
          // Parse additional flags with type safety
          const parts = trimmed.split(/\s+/);
          
          const branchIdx = parts.findIndex(p => p === '--branch' || p === '-b');
          const branchValue = branchIdx > 0 ? parts[branchIdx + 1] : undefined;
          if (branchValue) {
            params.append('branch', branchValue);
          }
          
          const sinceIdx = parts.findIndex(p => p === '--since' || p === '-s');
          const sinceValue = sinceIdx > 0 ? parts[sinceIdx + 1] : undefined;
          if (sinceValue) {
            params.append('since', sinceValue);
          }
          
          const untilIdx = parts.findIndex(p => p === '--until' || p === '-u');
          const untilValue = untilIdx > 0 ? parts[untilIdx + 1] : undefined;
          if (untilValue) {
            params.append('until', untilValue);
          }
          
          const limitIdx = parts.findIndex(p => p === '--limit' || p === '-l');
          const limitValue = limitIdx > 0 ? parts[limitIdx + 1] : undefined;
          if (limitValue) {
            params.append('limit', limitValue);
          }
          
          const url = new URL(
            `${MCP_BASE_URL}/github/commits/${owner}/${repo}?${params.toString()}`
          );
          
          const res = await axios.get(url.toString(), {
            timeout: 15_000,
            validateStatus: () => true
          });
          
          if (res.status !== 200) {
            throw new Error(res.data?.error || `HTTP ${res.status} error`);
          }
          
          const commits = res.data;
          if (!Array.isArray(commits) || commits.length === 0) {
            append({cmd: trimmed, type: 'info', text: 'No commits found.'});
            return;
          }
          
          // Format commits as a readable list
          const result = [
            `=== Commits for ${owner}/${repo} ===`,
            `Branch: ${params.get('branch') || 'default'}`,
            ''
          ];
          
          commits.forEach((commit: any) => {
            const date = new Date(commit.author?.date || '').toLocaleString();
            result.push(`[${commit.sha?.slice(0, 7) || 'N/A'}] ${commit.message || 'No message'}`);
            result.push(`  Author: ${commit.author?.name || 'Unknown'} <${commit.author?.email || ''}>`);
            result.push(`  Date:   ${date}`);
            if (commit.url) {
              result.push(`  URL:    ${commit.url}`);
            }
            result.push('');
          });
          
          append({cmd: trimmed, type: 'result', text: result.join('\n')});
          
        } catch (err: any) {
          const message = err?.response?.data?.detail || err?.message || String(err || 'Unknown error');
          append({cmd: trimmed, type: 'error', text: `Failed to fetch commits: ${message}`});
        } finally {
          setBusy(false);
        }
        return;
      }
      
      // Handle projects command
      if (trimmed === 'jira projects' || trimmed === 'projects') {
        try {
          setBusy(true);
          const response = await axios.get(`${MCP_BASE_URL}/jira/projects`, {
            timeout: 15_000,
            validateStatus: () => true
          });

          if (response.status !== 200) {
            throw new Error(response.data?.error || `HTTP ${response.status} error`);
          }

          const projects = response.data;
          if (!Array.isArray(projects) || projects.length === 0) {
            append({cmd: trimmed, type: 'info', text: 'No projects found.'});
            return;
          }

          // Format projects as a table
          const maxKeyLength = Math.max(...projects.map((p: any) => p.key?.length || 0), 10);
          const maxNameLength = Math.max(...projects.map((p: any) => p.name?.length || 0), 20);
          
          let result = [
            'KEY'.padEnd(maxKeyLength) + '  ' + 'NAME'.padEnd(maxNameLength) + '  ' + 'TYPE',
            '-'.repeat(maxKeyLength) + '  ' + '-'.repeat(maxNameLength) + '  ' + '-'.repeat(10)
          ];
          
          projects.forEach((project: any) => {
            result.push(
              `${(project.key || '').padEnd(maxKeyLength)}  ${(project.name || '').padEnd(maxNameLength)}  ${project.projectTypeKey || 'N/A'}`
            );
          });
          
          append({cmd: trimmed, type: 'result', text: result.join('\n')});
        } catch (err: any) {
          const message = err?.response?.data?.error || err?.message || 'Unknown error';
          append({cmd: trimmed, type: 'error', text: `Failed to fetch projects: ${message}`});
        } finally {
          setBusy(false);
        }
        return;
      }

      if (trimmed === '/help') {
        append({cmd: trimmed, type: 'info', text: helpText});
        return;
      }

      // Simple parse: jira get --id <TICKET>
      const parts = trimmed.split(/\s+/);
      
      // Handle github commits command
      if (parts[0] === 'github' && parts[1] === 'commits' && parts[2]) {
        try {
          setBusy(true);
          const repoPath = parts[2];
          const repoParts = repoPath.split('/');
          
          if (repoParts.length !== 2) {
            throw new Error('Invalid repository format. Use: github commits owner/repo');
          }
          
          const [owner, repo] = repoParts;
          const params = new URLSearchParams();
          
          // Parse additional flags with type safety
          const branchIdx = parts.findIndex(p => p === '--branch' || p === '-b');
          const branchValue = branchIdx > 0 ? parts[branchIdx + 1] : undefined;
          if (branchValue) {
            params.append('branch', branchValue);
          }
          
          const sinceIdx = parts.findIndex(p => p === '--since' || p === '-s');
          const sinceValue = sinceIdx > 0 ? parts[sinceIdx + 1] : undefined;
          if (sinceValue) {
            params.append('since', sinceValue);
          }
          
          const untilIdx = parts.findIndex(p => p === '--until' || p === '-u');
          const untilValue = untilIdx > 0 ? parts[untilIdx + 1] : undefined;
          if (untilValue) {
            params.append('until', untilValue);
          }
          
          const limitIdx = parts.findIndex(p => p === '--limit' || p === '-l');
          const limitValue = limitIdx > 0 ? parts[limitIdx + 1] : undefined;
          if (limitValue) {
            params.append('limit', limitValue);
          }
          
          const url = new URL(
            `${MCP_BASE_URL}/github/commits/${owner}/${repo}?${params.toString()}`
          );
          
          const res = await axios.get(url.toString(), {
            timeout: 15_000,
            validateStatus: () => true
          });
          
          if (res.status !== 200) {
            throw new Error(res.data?.error || `HTTP ${res.status} error`);
          }
          
          const commits = res.data;
          if (!Array.isArray(commits) || commits.length === 0) {
            append({cmd: trimmed, type: 'info', text: 'No commits found.'});
            return;
          }
          
          // Format commits as a readable list
          const result = [
            `=== Commits for ${owner}/${repo} ===`,
            `Branch: ${params.get('branch') || 'default'}`,
            ''
          ];
          
          commits.forEach((commit: any) => {
            const date = new Date(commit.author?.date || '').toLocaleString();
            result.push(`[${commit.sha.slice(0, 7)}] ${commit.message}`);
            result.push(`  Author: ${commit.author?.name || 'Unknown'} <${commit.author?.email || ''}>`);
            result.push(`  Date:   ${date}`);
            if (commit.url) {
              result.push(`  URL:    ${commit.url}`);
            }
            result.push('');
          });
          
          append({cmd: trimmed, type: 'result', text: result.join('\n')});
          
        } catch (err: any) {
          const message = err?.response?.data?.detail || err?.message || String(err || 'Unknown error');
          append({cmd: trimmed, type: 'error', text: `Failed to fetch commits: ${message}`});
        } finally {
          setBusy(false);
        }
        return;
      }
      
      if (parts[0] === 'jira' && parts[1] === 'get') {
        const idFlagIdx = parts.findIndex(p => p === '--id' || p === '-i');
        const ticketId = idFlagIdx >= 0 ? parts[idFlagIdx + 1] : undefined;

        if (!ticketId) {
          append({cmd: trimmed, type: 'error', text: 'Error: --id <TICKET_ID> is required'});
          return;
        }

        try {
          setBusy(true);
          const url = new URL(`${MCP_BASE_URL}/jira/${encodeURIComponent(ticketId)}`);
          const res = await axios.get(url.toString(), {
            timeout: 15_000,
            validateStatus: () => true // Don't throw on HTTP error status
          });

          if (res.status !== 200) {
            const errorMsg = res.data?.error || res.statusText || `HTTP ${res.status} error`;
            throw new Error(`Failed to fetch Jira ticket: ${errorMsg}`);
          }

          const d = res.data as any;
          const readable = [
            `Ticket   : ${d.ticket ?? ''}`,
            `Title    : ${d.title ?? ''}`,
            `Status   : ${d.status ?? ''}`,
            `Assignee : ${d.assignee ?? '-'}`,
            `Description : ${d.description ?? "-"}`
          ].join('\n');

          append({cmd: trimmed, type: 'result', text: readable});
        } catch (err: any) {
          const message = err?.response?.data ?? err?.message ?? String(err ?? 'Unknown error');
          append({cmd: trimmed, type: 'error', text: `Request failed: ${message}`});
        } finally {
          setBusy(false);
        }
        return;
      }
      // Handle jira list-issues command
      else if (parts[0] === 'jira' && parts[1] === 'list-issues') {
        const projectFlagIdx = parts.findIndex(p => p === '--project');
        const projectKey = projectFlagIdx >= 0 ? parts[projectFlagIdx + 1] : undefined;
        
        if (!projectKey) {
          append({cmd: trimmed, type: 'error', text: 'Error: --project <PROJECT_KEY> is required'});
          return;
        }
        
        const statusFlagIdx = parts.findIndex(p => p === '--status');
        const status = statusFlagIdx >= 0 ? parts[statusFlagIdx + 1] : undefined;
        
        try {
          setBusy(true);
          const params = new URLSearchParams();
          if (status) {
            params.append('status', status);
          }
          
          const url = new URL(`${MCP_BASE_URL}/jira/projects/${encodeURIComponent(projectKey)}/issues?${params.toString()}`);
          const res = await axios.get(url.toString(), {
            timeout: 15_000,
            validateStatus: () => true
          });
          
          if (res.status !== 200) {
            const errorMsg = res.data?.error || res.statusText || `HTTP ${res.status} error`;
            throw new Error(`Failed to fetch project issues: ${errorMsg}`);
          }
          
          const issues = res.data as Array<{
            key: string;
            summary: string;
            status: string;
            assignee: string;
            priority?: string;
          }>;
          
          if (!Array.isArray(issues) || issues.length === 0) {
            append({cmd: trimmed, type: 'info', 
              text: `No issues found for project ${projectKey}${status ? ` with status "${status}"` : ''}.`
            });
            return;
          }
          
          // Format issues as a readable list
          const result = [
            `=== Issues for project ${projectKey}${status ? ` (Status: ${status})` : ''} ===`,
            ''
          ];
          
          issues.forEach(issue => {
            result.push(`[${issue.key}] ${issue.summary}`);
            result.push(`  Status: ${issue.status}${issue.priority ? ` | Priority: ${issue.priority}` : ''} | Assignee: ${issue.assignee || 'Unassigned'}\n`);
          });
          
          append({cmd: trimmed, type: 'result', text: result.join('\n')});
        } catch (err: any) {
          const message = err?.response?.data?.detail || err?.message || String(err || 'Unknown error');
          append({cmd: trimmed, type: 'error', text: `Request failed: ${message}`});
        } finally {
          setBusy(false);
        }
        return;
      }
      else if (parts[0] === 'jira' && parts[1] === 'summarize') {
        const idFlagIdx = parts.findIndex(p => p === '--id' || p === '-i');
        const ticketId = idFlagIdx >= 0 ? parts[idFlagIdx + 1] : undefined;
        
        if (!ticketId) {
          append({cmd: trimmed, type: 'error', text: 'Error: --id <TICKET_ID> is required'});
          return;
        }
      
        try {
          setBusy(true);
          // First get the ticket details
          const ticketRes = await axios.get(
            `${MCP_BASE_URL}/jira/${encodeURIComponent(ticketId)}`,
            { timeout: 10_000 }
          );
          
          // Then get the AI summary
          try {
            const summaryRes = await axios.post(
              `${MCP_BASE_URL}/ai/generate`,
              { 
                prompt: `Please provide a concise summary of this Jira ticket: ${JSON.stringify(ticketRes.data)}` 
              },
              { 
                timeout: 15_000,
                headers: { "Content-Type": "application/json" }
              }
            );

            const ticketData = ticketRes.data;
            const baseOutput = [
              '=== Jira Ticket ===',
              `Ticket   : ${ticketData.ticket || ''}`,
              `Title    : ${ticketData.title || ''}`,
              `Status   : ${ticketData.status || ''}`,
              `Assignee : ${ticketData.assignee || '-'}`
            ];

            if (summaryRes.data.status === "error") {
              // Show error but still display the ticket data
              const errorMsg = summaryRes.data.error || "Unknown error generating summary";
              append({
                cmd: trimmed, 
                type: 'error', 
                text: [...baseOutput, `\n=== AI Summary Generation Failed ===\n${errorMsg}\n`].join('\n')
              });
            } else {
              const summary = summaryRes.data.response || "No summary available";
              append({
                cmd: trimmed,
                type: 'result',
                text: [...baseOutput, `\n=== AI Summary ===\n${summary}\n`].join('\n')
              });
            }
          } catch (aiError: any) {
            // If AI fails, still show the ticket data
            const errorMsg = aiError?.response?.data?.error || aiError.message || "Unknown error";
            const readable = [
              '=== Jira Ticket ===',
              `Ticket   : ${ticketRes.data.ticket || ''}`,
              `Title    : ${ticketRes.data.title || ''}`,
              `Status   : ${ticketRes.data.status || ''}`,
              `Assignee : ${ticketRes.data.assignee || '-'}`,
              `\n=== AI Summary Generation Failed ===\n${errorMsg}\n`
            ].join('\n');
            
            append({cmd: trimmed, type: 'error', text: readable});
          }
        } catch (err: any) {
          const message = err?.response?.data?.detail ?? err?.message ?? String(err ?? 'Unknown error');
          append({cmd: trimmed, type: 'error', text: `Request failed: ${message}`});
        } finally {
          setBusy(false);
        }
        return;
      }

      // Unknown command
      append({cmd: trimmed, type: 'error', text: `Unknown command: ${trimmed}. Type /help`});
    },
    [append, exit, helpText]
  );

  const handleSubmit = useCallback(
    (value: string) => {
      const trimmed = value.trim();
      if (!trimmed) return;
      
      setInput('');
      runCommand(trimmed);
    },
    [runCommand]
    );

    return (
      <Box flexDirection="column" padding={1}>
        <Box marginBottom={1}>
          <Gradient name="rainbow">
            <BigText text="MY-CLI" />
          </Gradient>
        </Box>

        <Box flexDirection="column" marginBottom={1}>
          <Text>Tips for getting started:</Text>
          <Text>1. Run commands like: jira get --id PROJ-123</Text>
          <Text>2. Use /help for available commands</Text>
        <Text>3. Use /quit to exit</Text>
      </Box>

<Box flexDirection="column" marginBottom={1}>
        {history.map((entry, i) => (
          <Box key={i} flexDirection="column">
            {entry.cmd && !entry.cmd.startsWith('jira list') && (
              <Box>
                <Text color="gray">$ </Text>
                <Text bold>{entry.cmd}</Text>
              </Box>
            )}
            {entry.text && (
              <Box marginLeft={entry.cmd && !entry.cmd.startsWith('jira list') ? 2 : 0}>
                {entry.type === 'error' ? (
                  <Text color="red">{entry.text}</Text>
                ) : (
                  <Text>{entry.text}</Text>
                )}
              </Box>
            )}
          </Box>
        ))}
      </Box>

      {!exiting && (
        <Box>
          <Box marginRight={1}>
            <Text color="green">$</Text>
          </Box>
          <TextInput
            value={input}
            onChange={setInput}
            onSubmit={handleSubmit}
            placeholder={busy ? '' : 'Type a command...'}
            showCursor={!busy && blinkVisible}
          />
          {busy && <Text> Working...</Text>}
        </Box>
      )}
    </Box>
  );
}