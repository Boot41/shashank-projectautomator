import React, {useCallback, useMemo, useState, useEffect} from 'react';
import {Box, Text, useApp} from 'ink';
import Spinner from 'ink-spinner';
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
        '  - jira get --id <TICKET_ID>  - Get Jira ticket details',
        '  - jira summarize --id <TICKET_ID> - Get AI summary of a ticket',
        '  - /help                      - Show this help message',
        '  - /quit                      - Exit the application',
        '',
        'Natural Language Examples:',
        '  - "Show me ticket ABC-123"',
        '  - "Summarize ticket ABC-123"',
        '  - "Get details for issue ABC-123"',
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
        { timeout: 30_000 }
      );

      if (response.data.status !== 'success') {
        return {
          success: false,
          error: response.data.error || 'Failed to process natural language',
        };
      }

      return {
        success: true,
        command: response.data.command,
        explanation: response.data.explanation,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Unknown error',
      };
    } finally {
      setBusy(false);
    }
  }, []);

  const runCommand = useCallback(
    async (line: string) => {
      const trimmed = line.trim();
      if (!trimmed) return;

      // Check if it's a natural language command (not starting with / or jira)
      if (!trimmed.startsWith('/') && !trimmed.startsWith('jira ')) {
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
          <BigText text="Jira CLI" font="simple3d" />
        </Gradient>
      </Box>

      <Box flexDirection="column" marginBottom={1}>
        {history.map((entry, i) => (
          <Box key={i} flexDirection="column">
            {entry.cmd && (
              <Box>
                <Text color="gray">$ </Text>
                <Text bold>{entry.cmd}</Text>
              </Box>
            )}
            <Box marginLeft={entry.cmd ? 2 : 0}>
              {entry.type === 'error' ? (
                <Text color="red">{entry.text}</Text>
              ) : entry.type === 'info' ? (
                <Text color="blue">{entry.text}</Text>
              ) : (
                <Text>{entry.text}</Text>
              )}
            </Box>
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
            placeholder={busy ? '' : 'Type a command or natural language...'}
            showCursor={!busy && blinkVisible}
          />
          {busy && (
            <Box marginLeft={1}>
              <Text><Spinner type="dots" /> Processing...</Text>
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
}