import React, { FC } from 'react';
import { Box, Text } from 'ink';
import TextInput from 'ink-text-input';
import { parseCommand } from './commands/parser.js';

interface CommandHistory {
  command: string;
  result: any;
  timestamp: Date;
  success: boolean;
}

const App: FC = () => {
  const [input, setInput] = React.useState('');
  const [history, setHistory] = React.useState<CommandHistory[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);
  const [sessionId] = React.useState(() => {
    // Generate a persistent session ID for this CLI session
    const now = new Date();
    return `cli_${now.getFullYear()}${(now.getMonth() + 1).toString().padStart(2, '0')}${now.getDate().toString().padStart(2, '0')}_${now.getHours().toString().padStart(2, '0')}${now.getMinutes().toString().padStart(2, '0')}`;
  });
  
  // Debug: log session ID
  React.useEffect(() => {
    console.log(`CLI Session ID: ${sessionId}`);
  }, [sessionId]);

  const formatOutput = (result: any): string => {
    if (!result) return 'No result';
    
    if (result.success === false) {
      return `❌ Error: ${result.error || 'Unknown error occurred'}`;
    }

    if (result.data) {
      const data = result.data;
      
      // Handle agent responses
      if (data.result !== null && data.result !== undefined) {
        if (Array.isArray(data.result)) {
          // Handle array results (like repositories, branches, etc.)
          if (data.result.length === 0) {
            return '📋 No items found';
          }
          
          const firstItem = data.result[0];
          if (firstItem && typeof firstItem === 'object') {
            if (firstItem.name && firstItem.full_name) {
              // GitHub repositories
              return `📁 Found ${data.result.length} repositories:\n${data.result.map((repo: any) => 
                `  • ${repo.name} (${repo.full_name}) - ${repo.private ? '🔒 Private' : '🌐 Public'}`
              ).join('\n')}`;
            } else if (firstItem.name && firstItem.commit_sha) {
              // GitHub branches
              return `🌿 Found ${data.result.length} branches:\n${data.result.map((branch: any) => 
                `  • ${branch.name} (${branch.commit_sha.substring(0, 8)})`
              ).join('\n')}`;
            } else if (firstItem.number && firstItem.title) {
              // GitHub issues
              return `🎫 Found ${data.result.length} issues:\n${data.result.map((issue: any) => 
                `  • #${issue.number}: ${issue.title} (${issue.state})`
              ).join('\n')}`;
            } else if (firstItem.number && firstItem.title && firstItem.head && firstItem.base) {
              // GitHub pull requests
              return `🔀 Found ${data.result.length} pull requests:\n${data.result.map((pr: any) => 
                `  • #${pr.number}: ${pr.title} (${pr.state}) - ${pr.head.ref} → ${pr.base.ref}`
              ).join('\n')}`;
            } else if (firstItem.key && firstItem.name && firstItem.projectTypeKey) {
              // Jira projects
              return `📁 Found ${data.result.length} Jira projects:\n${data.result.map((project: any) => 
                `  • ${project.key}: ${project.name} (${project.projectTypeKey})`
              ).join('\n')}`;
            } else if (firstItem.key && firstItem.summary && firstItem.status) {
              // Jira issues
              return `🎫 Found ${data.result.length} Jira issues:\n${data.result.map((issue: any) => {
                let issueText = `  • ${issue.key}: ${issue.summary} (${issue.status})`;
                if (issue.assignee && issue.assignee !== 'Unassigned') {
                  issueText += ` - Assigned to: ${issue.assignee}`;
                }
                if (issue.due_date) {
                  issueText += ` - Due: ${issue.due_date}`;
                }
                return issueText;
              }).join('\n')}`;
            } else if (firstItem.id && firstItem.name) {
              // Jira possible transitions
              return `🔄 Available transitions for this issue:\n${data.result.map((transition: any) => 
                `  • ${transition.id}: ${transition.name}`
              ).join('\n')}\n\nUse the transition ID to change the status.`;
            } else if (firstItem.filename && firstItem.status) {
              // GitHub PR files
              return `📁 Files changed in this PR:\n${data.result.map((file: any) => {
                const statusIcon = file.status === 'added' ? '➕' : file.status === 'modified' ? '📝' : file.status === 'deleted' ? '❌' : '📄';
                return `  ${statusIcon} ${file.filename} (${file.status}) - +${file.additions || 0} -${file.deletions || 0} (${file.changes || 0} changes)`;
              }).join('\n')}`;
            }
          }
        } else if (typeof data.result === 'object') {
          // Handle single object results
          if (data.result.name && data.result.commit_sha) {
            // Created branch
            return `✅ Branch created: ${data.result.name} (${data.result.commit_sha.substring(0, 8)})`;
          } else if (data.result.number && data.result.title) {
            // Created issue
            return `✅ Issue created: #${data.result.number} - ${data.result.title}\n🔗 ${data.result.html_url}`;
          } else if (data.result.merged === true) {
            // Merged PR
            let mergeMessage = `✅ Pull Request merged successfully`;
            if (data.result.commit_sha) {
              mergeMessage += ` (${data.result.commit_sha.substring(0, 8)})`;
            }
            if (data.result.merge_method) {
              mergeMessage += ` using ${data.result.merge_method} method`;
            }
            
            // Check for email notification status
            if (data.result.email_notification) {
              const emailStatus = data.result.email_notification;
              if (emailStatus.status === "sent") {
                mergeMessage += `\n📧 Email notification sent to ${emailStatus.recipient}`;
              } else if (emailStatus.status === "failed") {
                mergeMessage += `\n❌ Email notification failed: ${emailStatus.error}`;
              } else if (emailStatus.status === "no_email_found") {
                mergeMessage += `\n⚠️ ${emailStatus.message}`;
              }
            }
            
            return mergeMessage;
          } else if (data.result.closed === true || data.result.state === "closed") {
            // Closed PR
            let closeMessage = `❌ Pull Request closed`;
            if (data.result.message) {
              closeMessage += ` - ${data.result.message}`;
            }
            
            // Check for email notification status
            if (data.result.email_notification) {
              const emailStatus = data.result.email_notification;
              if (emailStatus.status === "sent") {
                closeMessage += `\n📧 Email notification sent to ${emailStatus.recipient}`;
              } else if (emailStatus.status === "failed") {
                closeMessage += `\n❌ Email notification failed: ${emailStatus.error}`;
              } else if (emailStatus.status === "no_email_found") {
                closeMessage += `\n⚠️ ${emailStatus.message}`;
              }
            }
            
            return closeMessage;
          } else if (data.result.id && data.result.number) {
            // Created PR
            let prMessage = `✅ Pull Request created: #${data.result.number} - ${data.result.title}\n🔗 ${data.result.html_url}`;
            
            // Check for email notification status
            if (data.result.email_notification) {
              const emailStatus = data.result.email_notification;
              if (emailStatus.status === "sent") {
                prMessage += `\n📧 Email notification sent to ${emailStatus.recipient}`;
              } else if (emailStatus.status === "failed") {
                prMessage += `\n❌ Email notification failed: ${emailStatus.error}`;
              } else if (emailStatus.status === "no_email_found") {
                prMessage += `\n⚠️ ${emailStatus.message}`;
              }
            }
            
            return prMessage;
          } else if (data.result.status === "preview" && data.result.email_preview) {
            // Email preview result
            const preview = data.result.email_preview;
            const isRegenerated = data.result.action_type && data.result.action_type.includes("regenerated");
            const isJiraSummary = data.result.action_type && data.result.action_type.includes("Jira Issue Summary");
            let prefix = "📧 Email Preview";
            if (isRegenerated) {
              prefix = "📧 Regenerated Email Preview";
            } else if (isJiraSummary) {
              prefix = "📧 Jira Issue Summary Email Preview";
            }
            return `${prefix} for ${data.result.action_type}:\n\nTo: ${preview.to}\nSubject: ${preview.subject}\n\nBody:\n${preview.body}\n\nPlease confirm if this email looks good to send, or provide feedback for modifications.`;
          } else if (data.result.status === "sent" && data.result.recipient) {
            // Email sent result
            return `📧 Email sent successfully to ${data.result.recipient}`;
          } else if (data.result.status === "error" && data.result.error) {
            // Email error result
            return `❌ Email failed: ${data.result.error}`;
          } else if (data.result.status === "success" && data.result.message && data.result.transition_id) {
            // Jira issue transitioned
            return `✅ ${data.result.message} (Transition ID: ${data.result.transition_id})`;
          } else if (Array.isArray(data.result) && data.result.length > 0 && data.result[0].id && data.result[0].name) {
            // Jira possible transitions
            return `🔄 Available transitions for this issue:\n${data.result.map((transition: any) => 
              `  • ${transition.id}: ${transition.name}`
            ).join('\n')}\n\nUse the transition ID to change the status.`;
          } else if (data.result.key && data.result.summary) {
            // Jira issue details
            let issueMessage = `🎫 Jira Issue: ${data.result.key} - ${data.result.summary}`;
            if (data.result.status) {
              issueMessage += ` (${data.result.status})`;
            }
            if (data.result.assignee && data.result.assignee !== 'Unassigned') {
              issueMessage += `\n👤 Assigned to: ${data.result.assignee}`;
            }
            if (data.result.due_date) {
              issueMessage += `\n📅 Due: ${data.result.due_date}`;
            }
            return issueMessage;
          }
        } else if (typeof data.result === 'string') {
          return `📝 ${data.result}`;
        } else if (Array.isArray(data.result) && data.result.length > 0) {
          // Handle mixed results from multiple tools
          const results = [];
          for (const item of data.result) {
            if (item && typeof item === 'object') {
              if (item.key && item.id && item.self) {
                // Jira issue created
                results.push(`✅ Jira Issue created: ${item.key} (ID: ${item.id})`);
              } else if (item.name && item.commit_sha) {
                // GitHub branch created
                results.push(`✅ Branch created: ${item.name} (${item.commit_sha.substring(0, 8)})`);
              } else if (item.number && item.title) {
                // GitHub issue created
                results.push(`✅ Issue created: #${item.number} - ${item.title}`);
              } else if (item.id && item.number) {
                // GitHub PR created
                results.push(`✅ Pull Request created: #${item.number} - ${item.title}`);
              } else if (item.merged === true) {
                // GitHub PR merged
                let mergeMessage = `✅ Pull Request #${item.pr_number || 'unknown'} merged successfully`;
                if (item.commit_sha) {
                  mergeMessage += ` (${item.commit_sha.substring(0, 8)})`;
                }
                if (item.merge_method) {
                  mergeMessage += ` using ${item.merge_method} method`;
                }
                
                // Check for email notification status
                if (item.email_notification) {
                  const emailStatus = item.email_notification;
                  if (emailStatus.status === "sent") {
                    mergeMessage += `\n📧 Email notification sent to ${emailStatus.recipient}`;
                  } else if (emailStatus.status === "failed") {
                    mergeMessage += `\n❌ Email notification failed: ${emailStatus.error}`;
                  } else if (emailStatus.status === "no_email_found") {
                    mergeMessage += `\n⚠️ ${emailStatus.message}`;
                  }
                }
                
                results.push(mergeMessage);
              } else if (item.closed === true || item.state === "closed") {
                // GitHub PR closed
                let closeMessage = `❌ Pull Request #${item.number || item.pr_number || 'unknown'} closed`;
                if (item.message) {
                  closeMessage += ` - ${item.message}`;
                }
                
                // Check for email notification status
                if (item.email_notification) {
                  const emailStatus = item.email_notification;
                  if (emailStatus.status === "sent") {
                    closeMessage += `\n📧 Email notification sent to ${emailStatus.recipient}`;
                  } else if (emailStatus.status === "failed") {
                    closeMessage += `\n❌ Email notification failed: ${emailStatus.error}`;
                  } else if (emailStatus.status === "no_email_found") {
                    closeMessage += `\n⚠️ ${emailStatus.message}`;
                  }
                }
                
                results.push(closeMessage);
              } else {
                // Generic object result
                results.push(`✅ ${JSON.stringify(item)}`);
              }
            } else if (typeof item === 'string') {
              results.push(`📝 ${item}`);
            }
          }
          return results.join('\n');
        }
      }
      
      // Handle model summary (fallback)
      if (data.model_summary) {
        return `🤖 ${data.model_summary}`;
      }
      
      // Handle tool calls (show what was executed) - only if no results
      if (data.toolCalls && data.toolCalls.length > 0) {
        const tools = data.toolCalls.map((call: any) => `🔧 ${call.name}`).join(', ');
        return `⚙️  Executed: ${tools}`;
      }
    }
    
    // Fallback to JSON for unknown formats
    return JSON.stringify(result, null, 2);
  };

  const handleSubmit = async (value: string) => {
    if (!value.trim()) return;
    
    // Handle special commands
    if (value === '/quit' || value === '/exit') {
      process.exit(0);
    }
    
    if (value === '/help') {
      const helpResult = {
        success: true,
        data: {
          result: `🚀 FastMCP CLI Help

Available Commands:
• /help - Show this help message
• /quit or /exit - Exit the CLI
• /clearcontext - Clear session context and start fresh
• Any other text - Send to AI agent automatically

Examples:
• List my GitHub repositories
• Create a new branch called feature/test
• Get issues for repository owner/repo
• Create a Jira issue with title "Bug fix"

The CLI automatically sends your input to the AI agent, so you don't need to type "agent:" anymore!
The CLI remembers your previous actions and context across sessions.`,
          toolCalls: [],
          model_summary: null
        }
      };
      
      const newEntry: CommandHistory = {
        command: value,
        result: helpResult,
        timestamp: new Date(),
        success: true
      };
      
      setHistory(prev => [...prev, newEntry]);
      setInput('');
      return;
    }
    
    if (value === '/clearcontext') {
      // This will be handled by the server
    }
    
    setIsLoading(true);
    const timestamp = new Date();
    
    try {
      // Automatically prepend "agent:" if not already present
      const command = value.startsWith('agent:') ? value : `agent: ${value}`;
      const result = await parseCommand(command, sessionId);
      const newEntry: CommandHistory = {
        command: value, // Store original input without "agent:" prefix
        result: result,
        timestamp,
        success: result.success !== false
      };
      
      setHistory(prev => [...prev, newEntry]);
    } catch (err) {
      const error = err as Error;
      const newEntry: CommandHistory = {
        command: value,
        result: { success: false, error: error.message },
        timestamp,
        success: false
      };
      
      setHistory(prev => [...prev, newEntry]);
    } finally {
      setIsLoading(false);
      setInput('');
    }
  };

  return (
    <Box flexDirection="column">
      {/* Welcome message */}
      {history.length === 0 && (
        <Box marginBottom={1}>
          <Text color="cyan">🚀 FastMCP CLI - Interactive Agent Session</Text>
          <Text color="green">\nSession ID: {sessionId}</Text>
          <Text color="gray">\nJust type your request - no need for 'agent:' prefix!</Text>
          <Text color="gray">\nType /help for commands, /quit to exit, /clearcontext to reset</Text>
          <Text color="gray">\nExample: List my GitHub repositories</Text>
        </Box>
      )}
      
      {/* Command history */}
      {history.map((entry, index) => (
        <Box key={index} flexDirection="column" marginBottom={1}>
          <Box>
            <Text color="green">{'> '}</Text>
            <Text color="white">{entry.command}</Text>
          </Box>
          <Box marginTop={1} marginLeft={2}>
            <Text>{formatOutput(entry.result)}</Text>
          </Box>
        </Box>
      ))}
      
      {/* Current input */}
      <Box>
        <Text color="green">{'> '}</Text>
        <TextInput 
          value={input} 
          onChange={setInput} 
          onSubmit={handleSubmit}
          placeholder={isLoading ? "Processing..." : "Type your request or /help for commands..."}
        />
      </Box>
      
      {/* Loading indicator */}
      {isLoading && (
        <Box marginTop={1}>
          <Text color="yellow">⏳ Processing...</Text>
        </Box>
      )}
    </Box>
  );
};

export default App;