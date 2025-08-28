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
        'Available commands:',
        '  - jira get --id <TICKET_ID>',
        '  - /help',
        '  - /quit',
      ].join('\n'),
    []
  );

  const append = useCallback((entry: HistoryEntry) => {
    setHistory(prev => [...prev, entry]);
  }, []);

  const runCommand = useCallback(
    async (line: string) => {
      const trimmed = line.trim();
      if (!trimmed) return;

      // Handle built-ins
      if (trimmed === '/quit') {
        setExiting(true);
        append({cmd: trimmed, type: 'info', text: 'Exiting...'});
        setTimeout(() => exit(), 10);
        return;
      }

      if (trimmed === '/help') {
        append({cmd: trimmed, type: 'info', text: helpText});
        return;
      }

      // Simple parse: jira get --id <TICKET>
      const parts = trimmed.split(/\s+/);
      if (parts[0] === 'jira' && parts[1] === 'get') {
        const idFlagIdx = parts.findIndex(p => p === '--id' || p === '-i');
        const ticketId = idFlagIdx >= 0 ? parts[idFlagIdx + 1] : undefined;

        if (!ticketId) {
          append({cmd: trimmed, type: 'error', text: 'Error: --id <TICKET_ID> is required'});
          return;
        }

        try {
          setBusy(true);
          const url = `${MCP_BASE_URL}/jira/${encodeURIComponent(ticketId)}`;
          const res = await axios.get(url, {timeout: 10_000});

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
      
          const summary = summaryRes.data.response || "No summary available";
          append({cmd: trimmed, type: 'result', text: `\n=== Jira Ticket Summary ===\n\n${summary}\n\n====================\n`});
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

  const onSubmit = useCallback(
    async (line: string) => {
      await runCommand(line);
      setInput('');
    },
    [runCommand]
  );

  return (
    <Box flexDirection="column">
      <Gradient name="rainbow">
        <BigText text="MY-CLI" />
      </Gradient>

      <Box flexDirection="column" marginBottom={1}>
        <Text>Tips for getting started:</Text>
        <Text>1. Run commands like: jira get --id PROJ-123</Text>
        <Text>2. Use /help for available commands</Text>
        <Text>3. Use /quit to exit</Text>
      </Box>

      {/* History of commands and their responses */}
      {history.map((h, idx) => (
        <Box
          key={idx}
          flexDirection="column"
          borderStyle="round"
          borderColor={h.type === 'error' ? 'red' : h.type === 'result' ? 'green' : 'cyan'}
          paddingX={1}
          paddingY={0}
          marginBottom={1}
        >
          {/* Echo the command */}
          <Text color="cyan">{`> ${h.cmd}`}</Text>
          {/* Response text */}
          <Text color={h.type === 'error' ? 'red' : h.type === 'result' ? 'green' : undefined}>
            {h.text}
          </Text>
        </Box>
      ))}

      {!exiting && (
        <Box
          borderStyle="round"
          borderColor="cyan"
          paddingX={1}
          paddingY={0}
          alignItems="center"
        >
          <Text color="cyan">{'> '}</Text>
          <TextInput
            value={input}
            onChange={setInput}
            onSubmit={onSubmit}
            placeholder="Type your command..."
            focus={!busy}
			showCursor={blinkVisible}
          />
          {busy && <Text color="yellow">  (working...)</Text>}
        </Box>
      )}
    </Box>
  );
}