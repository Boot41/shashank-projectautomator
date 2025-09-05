import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class SessionContext:
    def __init__(self):
        self.session_id: str = ""
        self.created_at: datetime = datetime.now()
        self.last_updated: datetime = datetime.now()
        self.conversation_history: List[Dict[str, Any]] = []
        
        # GitHub context
        self.current_repository: Optional[str] = None
        self.current_owner: Optional[str] = None
        self.active_branches: List[str] = []
        self.recent_issues: List[Dict[str, Any]] = []
        self.recent_prs: List[Dict[str, Any]] = []
        
        # Jira context
        self.current_jira_project: Optional[str] = None
        self.current_jira_project_key: Optional[str] = None
        self.recent_jira_issues: List[Dict[str, Any]] = []
        self.recent_jira_projects: List[Dict[str, Any]] = []
        self.recent_jira_sprints: List[Dict[str, Any]] = []
        self.current_jira_sprint: Optional[str] = None
        
        # General context
        self.recent_actions: List[Dict[str, Any]] = []
        self.user_preferences: Dict[str, Any] = {}
        
    def add_conversation(self, user_input: str, agent_response: Dict[str, Any], timestamp: datetime = None):
        """Add a conversation turn to the history"""
        if timestamp is None:
            timestamp = datetime.now()
            
        # Extract context from the response BEFORE adding to history
        self._extract_context_from_response(agent_response)
            
        conversation = {
            "timestamp": timestamp.isoformat(),
            "user_input": user_input,
            "agent_response": agent_response,
            "tools_used": agent_response.get("data", {}).get("toolCalls", []),
            "success": agent_response.get("success", False)
        }
        
        self.conversation_history.append(conversation)
        self.last_updated = timestamp
    
    def _make_serializable(self, obj):
        """Convert objects to JSON serializable format"""
        if obj is None:
            return None
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif hasattr(obj, '__dict__'):
            # Convert object to dict
            return {k: self._make_serializable(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
        else:
            # Fallback: convert to string
            return str(obj)
    
    def _extract_context_from_response(self, response: Dict[str, Any]):
        """Extract relevant context from agent responses"""
        # Handle both direct response and nested data structure
        if response.get("success") is False:
            return
            
        # Check if response has data field (from CLI) or direct fields (from API)
        if "data" in response:
            data = response.get("data", {})
            result = data.get("result")
            tool_calls = data.get("toolCalls", [])
        else:
            # Direct response structure
            result = response.get("result")
            tool_calls = response.get("toolCalls", [])
        
        # Debug: print what we're extracting
        print(f"DEBUG: Extracting context from response: result={result}, tool_calls={tool_calls}")
        
        # Extract repository context
        for tool_call in tool_calls:
            args = tool_call.get("args", {})
            tool_name = tool_call.get("name", "")
            
            # GitHub context extraction
            if "owner" in args and "repo" in args:
                self.current_owner = args["owner"]
                self.current_repository = args["repo"]
            
            # Jira context extraction
            if tool_name.startswith("jira_"):
                if "project_key" in args:
                    self.current_jira_project_key = args["project_key"]
                if "ticket_id" in args:
                    # Extract project key from ticket ID (e.g., "PROJ-123" -> "PROJ")
                    ticket_id = args["ticket_id"]
                    if "-" in ticket_id:
                        self.current_jira_project_key = ticket_id.split("-")[0]
                
            # Track recent actions (convert result to serializable format)
            serializable_result = self._make_serializable(result)
            action = {
                "timestamp": datetime.now().isoformat(),
                "tool": tool_call.get("name"),
                "args": args,
                "result": serializable_result
            }
            self.recent_actions.append(action)
            
            # Keep only last 10 actions
            if len(self.recent_actions) > 10:
                self.recent_actions = self.recent_actions[-10:]
        
        # Extract specific data based on tool used
        if result:
            if isinstance(result, list):
                # Handle repository lists
                if result and "name" in result[0] and "full_name" in result[0]:
                    # This is a repository list
                    pass
                # Handle branch lists
                elif result and len(result) > 0:
                    # Check if it's a branch list (either dict or object format)
                    first_item = result[0]
                    if (isinstance(first_item, dict) and "name" in first_item and "commit_sha" in first_item) or \
                       (hasattr(first_item, 'name') and hasattr(first_item, 'commit_sha')):
                        self.active_branches = []
                        for branch in result:
                            if isinstance(branch, dict):
                                self.active_branches.append(branch["name"])
                            elif hasattr(branch, 'name'):
                                self.active_branches.append(branch.name)
                # Handle issue lists
                elif result and "number" in result[0] and "title" in result[0]:
                    self.recent_issues = result[:5]  # Keep last 5 issues
                # Handle PR lists
                elif result and "id" in result[0] and "number" in result[0]:
                    self.recent_prs = result[:5]  # Keep last 5 PRs
                # Handle Jira project lists
                elif result and len(result) > 0 and "key" in result[0] and "name" in result[0]:
                    self.recent_jira_projects = result[:5]  # Keep last 5 projects
                # Handle Jira issue lists
                elif result and len(result) > 0 and "key" in result[0] and "fields" in result[0]:
                    self.recent_jira_issues = result[:5]  # Keep last 5 issues
                # Handle Jira sprint lists
                elif result and len(result) > 0 and "id" in result[0] and "name" in result[0]:
                    self.recent_jira_sprints = result[:5]  # Keep last 5 sprints
            elif isinstance(result, dict):
                # Handle single item results
                if "number" in result and "title" in result:
                    if "html_url" in result and "/issues/" in result["html_url"]:
                        # This is a GitHub issue
                        self.recent_issues.insert(0, result)
                        if len(self.recent_issues) > 5:
                            self.recent_issues = self.recent_issues[:5]
                    elif "html_url" in result and "/pull/" in result["html_url"]:
                        # This is a GitHub PR
                        self.recent_prs.insert(0, result)
                        if len(self.recent_prs) > 5:
                            self.recent_prs = self.recent_prs[:5]
                # Handle Jira single issue
                elif "key" in result and "fields" in result:
                    self.recent_jira_issues.insert(0, result)
                    if len(self.recent_jira_issues) > 5:
                        self.recent_jira_issues = self.recent_jira_issues[:5]
                # Handle Jira single project
                elif "key" in result and "name" in result and "fields" not in result:
                    self.recent_jira_projects.insert(0, result)
                    if len(self.recent_jira_projects) > 5:
                        self.recent_jira_projects = self.recent_jira_projects[:5]
    
    def get_context_summary(self) -> str:
        """Generate a context summary for the agent"""
        context_parts = []
        
        # GitHub context
        if self.current_owner and self.current_repository:
            context_parts.append(f"Current repository: {self.current_owner}/{self.current_repository}")
        
        if self.active_branches:
            context_parts.append(f"Available branches: {', '.join(self.active_branches)}")
        
        if self.recent_issues:
            issue_numbers = [f"#{issue.get('number', '?')}" for issue in self.recent_issues[:3]]
            context_parts.append(f"Recent GitHub issues: {', '.join(issue_numbers)}")
        
        if self.recent_prs:
            pr_numbers = [f"#{pr.get('number', '?')}" for pr in self.recent_prs[:3]]
            context_parts.append(f"Recent PRs: {', '.join(pr_numbers)}")
        
        # Jira context
        if self.current_jira_project_key:
            context_parts.append(f"Current Jira project: {self.current_jira_project_key}")
        
        if self.recent_jira_projects:
            project_keys = [proj.get('key', '?') for proj in self.recent_jira_projects[:3]]
            context_parts.append(f"Recent Jira projects: {', '.join(project_keys)}")
        
        if self.recent_jira_issues:
            issue_keys = [issue.get('key', '?') for issue in self.recent_jira_issues[:3]]
            context_parts.append(f"Recent Jira issues: {', '.join(issue_keys)}")
        
        if self.recent_jira_sprints:
            sprint_names = [sprint.get('name', '?') for sprint in self.recent_jira_sprints[:3]]
            context_parts.append(f"Recent Jira sprints: {', '.join(sprint_names)}")
        
        if self.recent_actions:
            recent_tools = [action["tool"] for action in self.recent_actions[-3:]]
            context_parts.append(f"Recent actions: {', '.join(recent_tools)}")
        
        return " | ".join(context_parts) if context_parts else "No previous context"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "conversation_history": self._make_serializable(self.conversation_history),
            
            # GitHub context
            "current_repository": self.current_repository,
            "current_owner": self.current_owner,
            "active_branches": self.active_branches,
            "recent_issues": self._make_serializable(self.recent_issues),
            "recent_prs": self._make_serializable(self.recent_prs),
            
            # Jira context
            "current_jira_project": self.current_jira_project,
            "current_jira_project_key": self.current_jira_project_key,
            "recent_jira_issues": self._make_serializable(self.recent_jira_issues),
            "recent_jira_projects": self._make_serializable(self.recent_jira_projects),
            "recent_jira_sprints": self._make_serializable(self.recent_jira_sprints),
            "current_jira_sprint": self.current_jira_sprint,
            
            # General context
            "recent_actions": self._make_serializable(self.recent_actions),
            "user_preferences": self._make_serializable(self.user_preferences)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionContext':
        """Create context from dictionary"""
        context = cls()
        context.session_id = data.get("session_id", "")
        context.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        context.last_updated = datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        context.conversation_history = data.get("conversation_history", [])
        
        # GitHub context
        context.current_repository = data.get("current_repository")
        context.current_owner = data.get("current_owner")
        context.active_branches = data.get("active_branches", [])
        context.recent_issues = data.get("recent_issues", [])
        context.recent_prs = data.get("recent_prs", [])
        
        # Jira context
        context.current_jira_project = data.get("current_jira_project")
        context.current_jira_project_key = data.get("current_jira_project_key")
        context.recent_jira_issues = data.get("recent_jira_issues", [])
        context.recent_jira_projects = data.get("recent_jira_projects", [])
        context.recent_jira_sprints = data.get("recent_jira_sprints", [])
        context.current_jira_sprint = data.get("current_jira_sprint")
        
        # General context
        context.recent_actions = data.get("recent_actions", [])
        context.user_preferences = data.get("user_preferences", {})
        return context

class ContextService:
    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            # Use current project directory for more reliable storage
            storage_dir = os.path.join(os.path.dirname(__file__), "..", "..")
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        # Use a single context file for all sessions
        self.context_file = self.storage_dir / "context.json"
        self.current_context: Optional[SessionContext] = None
        print(f"DEBUG: Context storage file: {self.context_file}")
    
    def get_or_create_context(self, session_id: str = None) -> SessionContext:
        """Get existing context or create new one"""
        print(f"DEBUG: get_or_create_context called with session_id: {session_id}")
        
        # Always use the same context file regardless of session_id
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r') as f:
                    data = json.load(f)
                
                # Check if the context file has meaningful content
                if data and (data.get("conversation_history") or data.get("current_repository") or data.get("recent_actions")):
                    context = SessionContext.from_dict(data)
                    self.current_context = context
                    print(f"DEBUG: Loaded existing context from {self.context_file}")
                    return context
                else:
                    print(f"DEBUG: Context file exists but is empty, creating new context")
            except Exception as e:
                print(f"Error loading context: {e}")
        
        # Create new context
        context = SessionContext()
        context.session_id = "global_context"
        self.current_context = context
        print(f"DEBUG: Created new context")
        return context
    
    def save_context(self):
        """Save current context to disk"""
        if self.current_context:
            try:
                with open(self.context_file, 'w') as f:
                    json.dump(self.current_context.to_dict(), f, indent=2)
                print(f"DEBUG: Saved context to {self.context_file}")
            except Exception as e:
                print(f"Error saving context: {e}")
                import traceback
                traceback.print_exc()
    
    def clear_context(self):
        """Clear current context and start fresh"""
        # Create new empty context
        self.current_context = SessionContext()
        self.current_context.session_id = "global_context"
        
        # Save the empty context to clear the file content
        try:
            with open(self.context_file, 'w') as f:
                json.dump(self.current_context.to_dict(), f, indent=2)
            print(f"DEBUG: Cleared context file content {self.context_file}")
        except Exception as e:
            print(f"Error clearing context: {e}")
        
        return self.current_context
    
    def get_context_for_prompt(self, user_input: str) -> str:
        """Get context information to include with the prompt"""
        if not self.current_context:
            return ""
        
        context_summary = self.current_context.get_context_summary()
        
        # Add recent conversation context if relevant
        recent_context = ""
        if self.current_context.conversation_history:
            recent_conversations = self.current_context.conversation_history[-5:]  # Last 5 conversations
            recent_context = "\nRecent conversation context:\n"
            for i, conv in enumerate(recent_conversations, 1):
                recent_context += f"{i}. User: {conv['user_input']}\n"
                
                # Extract tool calls and results
                agent_response = conv.get('agent_response', {})
                tool_calls = agent_response.get('toolCalls', [])
                result = agent_response.get('result')
                model_summary = agent_response.get('model_summary', '')
                
                if tool_calls:
                    tools_used = [tc.get('name', 'unknown') for tc in tool_calls]
                    recent_context += f"   Tools used: {', '.join(tools_used)}\n"
                    
                    # Extract repository/project info from tool call arguments
                    for tc in tool_calls:
                        args = tc.get('args', {})
                        if 'owner' in args and 'repo' in args:
                            recent_context += f"   Repository: {args['owner']}/{args['repo']}\n"
                        elif 'project_key' in args:
                            recent_context += f"   Jira Project: {args['project_key']}\n"
                
                if result:
                    if isinstance(result, list) and result:
                        # Extract repository/project info from list results
                        repo_info = []
                        project_info = []
                        for item in result:
                            if isinstance(item, dict):
                                if 'full_name' in item:  # GitHub repo
                                    repo_info.append(item['full_name'])
                                elif 'name' in item and 'commit_sha' in item:  # GitHub branch
                                    if 'owner' in conv.get('agent_response', {}).get('toolCalls', [{}])[0].get('args', {}):
                                        owner = conv['agent_response']['toolCalls'][0]['args']['owner']
                                        repo_info.append(f"{owner}/{conv['agent_response']['toolCalls'][0]['args'].get('repo', 'unknown')}")
                                elif 'key' in item and 'name' in item:  # Jira project
                                    project_info.append(f"{item['key']} ({item['name']})")
                                elif 'key' in item and 'id' in item:  # Jira issue
                                    project_info.append(f"issue {item['key']}")
                        
                        if repo_info:
                            recent_context += f"   Repository: {', '.join(set(repo_info))}\n"
                        if project_info:
                            recent_context += f"   Project: {', '.join(set(project_info))}\n"
                        if not repo_info and not project_info:
                            recent_context += f"   Result: Found {len(result)} items\n"
                    elif isinstance(result, dict):
                        if 'number' in result:
                            recent_context += f"   Result: Created/accessed #{result['number']}\n"
                        elif 'key' in result:
                            recent_context += f"   Result: Accessed {result['key']}\n"
                        elif 'full_name' in result:  # GitHub repo
                            recent_context += f"   Repository: {result['full_name']}\n"
                        elif 'name' in result and 'commit_sha' in result:  # GitHub branch
                            recent_context += f"   Branch: {result['name']}\n"
                
                if model_summary and len(model_summary) < 100:
                    recent_context += f"   Summary: {model_summary.strip()}\n"
                
                recent_context += "\n"
        
        return f"Session Context: {context_summary}{recent_context}\n\n"

# Global context service instance
context_service = ContextService()
