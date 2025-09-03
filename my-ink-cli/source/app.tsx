import React, { FC, useState, useMemo } from 'react';
import { Box, Text } from 'ink';
import TextInput from 'ink-text-input';
import { CommandParser } from './commands/parser.js';

const App: FC = () => {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState<string>('');
  const parser = useMemo(() => new CommandParser(), []);

  const handleSubmit = async (value: string) => {
    if (!value) return;
    try {
      const result = await parser.parse(value);
      setOutput(JSON.stringify(result, null, 2));
    } catch (error: any) {
      setOutput(`Error: ${error.message}`);
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
        <Box marginTop={1} borderStyle="round" padding={1}>
          <Text>{output}</Text>
        </Box>
      )}
    </Box>
  );
};

export default App;