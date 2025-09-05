# 🧠 Context System - Complete Guide

## 📋 **Overview**

The context system stores **every command** executed from user input and uses this context to provide intelligent responses to history questions. It maintains a persistent memory across CLI sessions.

## 🗄️ **What Gets Stored**

### **1. Conversation History (`conversation_history`)**
Every user input and agent response is stored with:
- **Timestamp**: When the interaction occurred
- **User Input**: Exact command/prompt from user
- **Agent Response**: Complete response including tool calls and results
- **Tools Used**: Which tools were called
- **Success Status**: Whether the operation succeeded

### **2. Recent Actions (`recent_actions`)**
Last 10 tool calls with:
- **Tool Name**: Which function was called
- **Arguments**: Parameters passed to the tool
- **Result**: What the tool returned
- **Timestamp**: When the action occurred

### **3. Current State**
- **GitHub Context**: Current repository, owner, active branches, recent issues/PRs
- **Jira Context**: Current project, recent issues, projects, sprints
- **User Preferences**: Any saved preferences

## 🎯 **How History Questions Are Answered**

### **Context Enhancement Process:**
1. **User asks history question** → No tool call needed
2. **System loads context** → From persistent `context.json` file
3. **Context summary generated** → `get_context_summary()` creates summary
4. **Conversation context added** → Last 5 conversations with details
5. **Enhanced prompt sent to agent** → Context + user question
6. **Agent responds intelligently** → Using context without calling tools

### **Example Context Provided to Agent:**
```
Session Context: Current repository: shashanks41/private-project | Available branches: feat/new, feature/test-branch, main | Recent actions: jira_get_projects, github_get_branches, jira_get_projects

Recent conversation context:
1. User: list jira projects
   Tools used: jira_get_projects
   Summary: I am sorry, I encountered an error when trying to retrieve your Jira projects.

2. User: what was my previous project?
   Summary: You last listed Jira projects.

3. User: show branches for shashanks41/private-project
   Tools used: github_get_branches
   Result: Found 3 items
   Summary: The available branches in the repository are feat/new, feature/test-branch, and main.
```

## 🔍 **Types of History Questions & Responses**

### **1. "What did I do last?" / "What was my previous project?"**
- **Context Used**: `recent_actions` (last tool called)
- **Response**: "You last listed Jira projects." or "You last worked on shashanks41/private-project"

### **2. "Show me my recent work" / "What have I been working on?"**
- **Context Used**: `recent_actions` + `conversation_history`
- **Response**: "You recently: 1) Listed Jira projects, 2) Checked branches for shashanks41/private-project, 3) Listed Jira projects again"

### **3. "What repositories have I worked with?"**
- **Context Used**: `current_repository` + `current_owner`
- **Response**: "You're currently working with shashanks41/private-project"

### **4. "What branches are available in my current project?"**
- **Context Used**: `active_branches` + `current_repository`
- **Response**: "In shashanks41/private-project, you have branches: feat/new, feature/test-branch, main"

### **5. "What Jira projects have I accessed?"**
- **Context Used**: `recent_jira_projects` + `current_jira_project_key`
- **Response**: "You recently accessed Jira projects: [list of projects]"

### **6. "Show me my conversation history"**
- **Context Used**: `conversation_history` (last 5 conversations)
- **Response**: "Recent conversations: 1) 'list jira projects' - tried to list projects, 2) 'show branches' - found 3 branches, etc."

## 🚀 **Key Features**

### **✅ Complete Command Storage**
- Every command executed is stored
- Both successful and failed attempts
- Tool results and responses preserved

### **✅ Cross-Session Persistence**
- Context survives CLI restarts
- Single `context.json` file for all sessions
- Automatic context loading on startup

### **✅ Smart Context Summarization**
- Only relevant context provided to agent
- Prevents information overload
- Focuses on recent and relevant activities

### **✅ Multi-Platform Tracking**
- GitHub activities (repos, branches, issues, PRs)
- Jira activities (projects, issues, sprints)
- Email notifications and workflows

### **✅ Intelligent History Responses**
- No tool calls needed for history questions
- Context-aware responses
- Detailed conversation summaries

## 🛠️ **Technical Implementation**

### **Context File Location:**
```
/home/shashank/Documents/project_automator/fastmcp/context.json
```

### **Context Service Methods:**
- `get_or_create_context()` - Load or create context
- `save_context()` - Persist context to disk
- `clear_context()` - Reset context (clears content, keeps file)
- `get_context_for_prompt()` - Generate context summary for agent

### **Context Enhancement:**
- Context is prepended to every user prompt
- Agent receives rich context information
- Enables intelligent responses without tool calls

## 🧪 **Testing History Responses**

Use the demo script to test different history questions:
```bash
./demo_history_responses.sh
```

Or test individual questions:
```bash
curl -X POST http://localhost:8000/adk/agent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "what did I do last?", "session_id": "test"}'
```

## 📊 **Context File Structure**

```json
{
  "session_id": "global_context",
  "created_at": "2025-09-05T01:36:51.225666",
  "last_updated": "2025-09-05T09:28:18.739774",
  "conversation_history": [
    {
      "timestamp": "2025-09-05T01:36:54.686736",
      "user_input": "list jira projects",
      "agent_response": {
        "result": null,
        "toolCalls": [{"name": "jira_get_projects", "args": {}}],
        "model_summary": "I am sorry, I encountered an error..."
      },
      "tools_used": [],
      "success": false
    }
  ],
  "current_repository": "private-project",
  "current_owner": "shashanks41",
  "active_branches": ["feat/new", "feature/test-branch", "main"],
  "recent_actions": [
    {
      "timestamp": "2025-09-05T01:36:54.686786",
      "tool": "jira_get_projects",
      "args": {},
      "result": null
    }
  ]
}
```

## 🎉 **Benefits**

1. **🧠 Intelligent Memory**: Agent remembers all previous work
2. **🔄 Seamless Continuity**: Pick up where you left off
3. **📈 Better Productivity**: No need to re-explain context
4. **🎯 Context-Aware Responses**: Relevant answers based on history
5. **💾 Persistent Storage**: Memory survives sessions and restarts
6. **🔍 Rich History**: Detailed conversation and action tracking
