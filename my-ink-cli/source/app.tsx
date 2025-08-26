import React, {useCallback, useMemo, useState} from 'react';
import {Box, Text, useApp} from 'ink';
import Gradient from 'ink-gradient';
import BigText from 'ink-big-text';
import TextInput from 'ink-text-input';
import axios from 'axios';

type ResultKind = 'info' | 'error' | 'result';

const MCP_BASE_URL = 'http://localhost:8000';

export default function App() {
  const {exit} = useApp();
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [resultText, setResultText] = useState<string | null>(null);
  const [resultType, setResultType] = useState<ResultKind>('info');
  const [exiting, setExiting] = useState(false);

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

  const setResult = useCallback((type: ResultKind, text: string) => {
    setResultType(type);
    setResultText(text);
  }, []);

  const runCommand = useCallback(
    async (line: string) => {
      const trimmed = line.trim();
      if (!trimmed) return;

      if (trimmed === '/quit') {
        setExiting(true);
        setResult('info', 'Exiting...');
        // Let Ink unmount gracefully (prevents flicker)
        setTimeout(() => exit(), 10);
        return;
      }

      if (trimmed === '/help') {
        setResult('info', helpText);
        return;
      }

      // Simple parse: jira get --id <TICKET>
      const parts = trimmed.split(/\s+/);
      if (parts[0] === 'jira' && parts[1] === 'get') {
        const idFlagIdx = parts.findIndex(p => p === '--id' || p === '-i');
        const ticketId = idFlagIdx >= 0 ? parts[idFlagIdx + 1] : undefined;

        if (!ticketId) {
          setResult('error', 'Error: --id <TICKET_ID> is required');
          return;
        }

        try {
          setBusy(true);
          const url = `${MCP_BASE_URL}/jira/${encodeURIComponent(ticketId)}`;
          const res = await axios.get(url, {timeout: 10_000});
          setResult('result', JSON.stringify(res.data, null, 2));
        } catch (err: any) {
          const message =
            err?.response?.data ?? err?.message ?? String(err ?? 'Unknown error');
          setResult('error', `Request failed: ${message}`);
        } finally {
          setBusy(false);
        }
        return;
      }

      setResult('error', `Unknown command: ${trimmed}. Type /help`);
    },
    [exit, helpText, setResult]
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

      {resultText && (
        <Box
          flexDirection="column"
          borderStyle="round"
          borderColor={
            resultType === 'error' ? 'red' : resultType === 'result' ? 'green' : 'cyan'
          }
          paddingX={1}
          paddingY={0}
          marginBottom={1}
        >
          <Text
            color={
              resultType === 'error' ? 'red' : resultType === 'result' ? 'green' : undefined
            }
          >
            {resultText}
          </Text>
        </Box>
      )}

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
          />
          {busy && <Text color="yellow">  (working...)</Text>}
        </Box>
      )}
    </Box>
  );
}