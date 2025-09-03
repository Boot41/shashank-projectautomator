import React, { FC } from 'react';
import { Box, Text } from 'ink';
import TextInput from 'ink-text-input';
import { parseCommand } from './commands/parser.js';

const App: FC = () => {
  const [input, setInput] = React.useState('');
  const [output, setOutput] = React.useState<string>('');
  const [error, setError] = React.useState<string | null>(null);

  const handleSubmit = async (value: string) => {
    setError(null);
    try {
      // Support format: [server-name:]command [args]
      // Example: github-official:jira get --id ABC-123
      // Example: jira get --id ABC-123 (uses default local-mcp)
      const result = await parseCommand(value);
      setOutput(JSON.stringify(result, null, 2));
    } catch (err) {
       const error = err as Error;
      setError(error.message || 'An unknown error occurred');
      setOutput('');
    }
    setInput('');
  };

  return (
    <Box flexDirection="column">
      <Box>
        <Text>{'> '}</Text>
        <TextInput value={input} onChange={setInput} onSubmit={handleSubmit} />
      </Box>
      {output && (
        <Box marginTop={1}>
          <Text>{output}</Text>
        </Box>
      )}
    </Box>
  );
};

export default App;