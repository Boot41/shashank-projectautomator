import google.generativeai as genai
import importlib
from ..config.settings import settings
from ..adk_tools import ALL_TOOL_RUNNERS
from ..services.context_service import context_service


def _build_tool_declarations():
    # Define a practical subset of functions with JSON Schema parameters for Gemini tool calling
    fns = [
        {
            "name": "jira_fetch_issue",
            "description": "Fetch a single Jira issue by ticket ID",
            "parameters": {
                "type": "object",
                "properties": {"ticket_id": {"type": "string"}},
                "required": ["ticket_id"],
            },
        },
        {
            "name": "jira_create_issue",
            "description": "Create a new Jira issue",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_key": {"type": "string"},
                    "summary": {"type": "string"},
                    "description": {"type": "string"},
                    "issuetype_name": {"type": "string"},
                },
                "required": ["project_key", "summary", "description"],
            },
        },
        {
            "name": "jira_get_projects",
            "description": "List all available Jira projects",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "jira_get_issues_for_project",
            "description": "List issues for a specific Jira project",
            "parameters": {
                "type": "object",
                "properties": {"project_key": {"type": "string"}},
                "required": ["project_key"],
            },
        },
        {
            "name": "jira_comment_issue",
            "description": "Add a comment to a Jira issue",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string"},
                    "comment_text": {"type": "string"},
                },
                "required": ["issue_key", "comment_text"],
            },
        },
        {
            "name": "jira_get_issue_comments",
            "description": "Get all comments for a Jira issue",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string"},
                },
                "required": ["issue_key"],
            },
        },
        {
            "name": "jira_get_possible_transitions",
            "description": "Get possible workflow transitions for a Jira issue",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string"},
                },
                "required": ["issue_key"],
            },
        },
        {
            "name": "jira_transition_issue",
            "description": "Transition a Jira issue to a new status using transition ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string"},
                    "transition_id": {"type": "string"},
                },
                "required": ["issue_key", "transition_id"],
            },
        },
        {
            "name": "jira_summarize_and_email_issue",
            "description": "Summarize a Jira issue and send the summary via email with confirmation workflow",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string"},
                    "to_email": {"type": "string"},
                    "additional_context": {"type": "string", "description": "Additional context or notes to include in the summary"},
                },
                "required": ["issue_key", "to_email"],
            },
        },
        {
            "name": "github_get_repos",
            "description": "List repositories for the authenticated user",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "github_get_branches",
            "description": "List branches for a repository",
            "parameters": {
                "type": "object",
                "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}},
                "required": ["owner", "repo"],
            },
        },
        {
            "name": "github_create_branch",
            "description": "Create a new branch from a source branch",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "branch_name": {"type": "string"},
                    "source_branch": {"type": "string"},
                },
                "required": ["owner", "repo", "branch_name"],
            },
        },
        {
            "name": "github_get_issues",
            "description": "List issues for a repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                },
                "required": ["owner", "repo"],
            },
        },
        {
            "name": "github_get_pull_requests",
            "description": "List pull requests for a repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "state": {"type": "string", "description": "Pull request state (open, closed, all)", "enum": ["open", "closed", "all"]},
                },
                "required": ["owner", "repo"],
            },
        },
        {
            "name": "github_get_pr_files",
            "description": "Get the list of files changed in a pull request",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "pr_number": {"type": "integer"},
                },
                "required": ["owner", "repo", "pr_number"],
            },
        },
        {
            "name": "github_create_issue",
            "description": "Create a new issue in a repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["owner", "repo", "title"],
            },
        },
        {
            "name": "github_create_pull_request",
            "description": "Create a new pull request",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "title": {"type": "string"},
                    "head": {"type": "string"},
                    "base": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["owner", "repo", "title", "head", "base"],
            },
        },
        {
            "name": "github_merge_pull_request",
            "description": "Merge a pull request by number with optional commit message and merge method",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "pr_number": {"type": "integer"},
                    "commit_title": {"type": "string", "description": "Title for the merge commit"},
                    "commit_message": {"type": "string", "description": "Message for the merge commit"},
                    "merge_method": {"type": "string", "description": "Merge method: merge, squash, or rebase", "enum": ["merge", "squash", "rebase"]},
                },
                "required": ["owner", "repo", "pr_number"],
            },
        },
        {
            "name": "github_close_pull_request",
            "description": "Close a pull request without merging",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "pr_number": {"type": "integer"},
                },
                "required": ["owner", "repo", "pr_number"],
            },
        },
        {
            "name": "github_comment_issue",
            "description": "Add a comment to a GitHub issue",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "issue_number": {"type": "integer"},
                    "comment_body": {"type": "string"},
                },
                "required": ["owner", "repo", "issue_number", "comment_body"],
            },
        },
        {
            "name": "email_send",
            "description": "Send an email via configured SMTP",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to", "subject", "body"],
            },
        },
        {
            "name": "email_confirm_and_send",
            "description": "Show email preview and ask for user confirmation before sending",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                    "action_type": {"type": "string", "description": "Type of action (PR created, PR closed, etc.)"},
                },
                "required": ["to", "subject", "body", "action_type"],
            },
        },
        {
            "name": "regenerate_email_summary",
            "description": "Regenerate email summary with user feedback and key points",
            "parameters": {
                "type": "object",
                "properties": {
                    "initial_summary": {"type": "string"},
                    "user_feedback": {"type": "string"},
                    "key_points": {"type": "string"},
                    "pr_details": {"type": "object"},
                    "to_email": {"type": "string", "description": "Email recipient address"},
                    "issue_details": {"type": "object", "description": "Jira issue details for issue summary emails"},
                },
                "required": ["initial_summary", "user_feedback"],
            },
        },
        {
            "name": "finalize_email_summary",
            "description": "Finalize and send email summary after user approval",
            "parameters": {
                "type": "object",
                "properties": {
                    "final_summary": {"type": "string"},
                    "to_email": {"type": "string"},
                    "pr_details": {"type": "object"},
                },
                "required": ["final_summary", "to_email", "pr_details"],
            },
        },
    ]
    return [{"function_declarations": fns}]


class GeminiToolsAgent:
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise RuntimeError("Missing GEMINI_API_KEY")
        genai.configure(api_key=settings.gemini_api_key)
        self.tools = _build_tool_declarations()
        system_instruction = (
            "You are an automation agent with access to session context. When a user asks for an actionable task, ALWAYS call a function if one matches. "
            "Be proactive and infer context from user requests. Never ask for clarification unless absolutely necessary. "
            "PRIORITY: If a user mentions 'summarise' or 'summarize' along with 'send' or 'email' and provides an email address, this is a HIGH PRIORITY command that should trigger jira_summarize_and_email_issue function immediately. "
            "CONTEXT PRIORITY: Always use context from recent commands. If user says 'this pr', 'this issue', 'this project', etc., look at the most recent action in the session context to determine what they're referring to. "
            "IMPORTANT: You have access to session context that includes information about previous actions, current repository, recent branches, issues, PRs, Jira projects, Jira issues, and Jira sprints. "
            "Use this context to answer questions about previous work and provide relevant information. "
            "PR CREATION RULES: When creating a pull request, you MUST ensure both title and description are provided. If the user doesn't specify these, ask them to provide: 1) A clear, descriptive title for the PR, and 2) A detailed description explaining what changes were made and why. Only proceed with PR creation after both are provided. "
            "JIRA SUMMARY EMAIL RULES: When a user requests to 'summarise issue [ticket] and send it to [email]' or similar variations, you MUST call jira_summarize_and_email_issue function immediately. Do NOT just show the issue details - the user specifically wants to send an email summary. "
            "EXAMPLE: 'summarise issue tp-1 and send it to test@example.com' should call jira_summarize_and_email_issue with issue_key='tp-1' and to_email='test@example.com'. "
            "Common patterns to recognize: "
            "- 'show branches in my repo' or 'list my repositories' → call github_get_repos "
            "- 'show branches for [repo]' → call github_get_branches with the repo info "
            "- 'create PR' or 'pull request' → MANDATORY: Ask user for title and description if not provided, then call github_create_pull_request "
            "- 'list PRs', 'show PRs', 'pull requests', 'show pull requests' → call github_get_pull_requests "
            "- 'show files in PR #123', 'files changed in PR #123', 'what files changed in PR #123' → call github_get_pr_files "
            "- 'merge this pr', 'close this pr', 'files in this pr' → use the most recently viewed PR number from context "
            "- 'merge PR #123', 'merge pull request #123', 'merge this pr' → call github_merge_pull_request with sensible defaults (merge method='merge', commit_title from PR title, commit_message from PR description) "
            "- 'close PR #123', 'close pull request #123' → call github_close_pull_request "
            "- 'create issue' → call github_create_issue "
            "- 'create branch' → call github_create_branch "
            "- 'list jira projects' or 'show jira projects' → call jira_get_projects "
            "- 'list issues in [project]' or 'show issues for [project]' → call jira_get_issues_for_project and format the response with key, summary, assignee, due date, and status "
            "- 'get jira issue [ticket]' or 'fetch jira [ticket]' → call jira_fetch_issue "
            "- 'create jira issue' → call jira_create_issue "
            "- 'add comment to jira issue [ticket]' or 'comment on jira [ticket]' → call jira_comment_issue "
            "- 'get comments from jira issue [ticket]' or 'show comments for [ticket]' → call jira_get_issue_comments "
            "- 'change status of [ticket]' or 'transition [ticket]' → first call jira_get_possible_transitions to show available statuses, then call jira_transition_issue with the chosen transition ID "
            "- 'move [ticket] to [status]' or 'set [ticket] status to [status]' → first call jira_get_possible_transitions to find the transition ID for the desired status, then call jira_transition_issue "
            "- 'summarise [ticket] and send to [email]', 'summarize [ticket] and email [email]', 'summarise issue [ticket] and send it to [email]', 'summarize issue [ticket] and send this to [email]' → call jira_summarize_and_email_issue to fetch issue details, generate summary, and show email preview for confirmation "
            "- 'what was my previous project?' or 'which project was I on?' → use session context to provide information about recent repositories, Jira projects, and actions "
            "- 'what did I do last?' or 'show me my recent work' → use session context to summarize recent actions and conversations "
            "- 'what have I been working on?' → provide a comprehensive summary of recent GitHub and Jira activities "
            "- 'show me my conversation history' → list recent user inputs and their outcomes "
            "Infer reasonable defaults from context when missing. If a required field is missing, pick a sensible default (e.g., issuetype_name='Task', base='main'). "
            "For pull request operations: "
            "1. If user wants to CREATE a PR with email notification, create the PR first, then use email_confirm_and_send to show email preview and ask for user confirmation before sending. "
            "2. If user wants to CLOSE a PR with email notification, close the PR first, then use email_confirm_and_send to show email preview and ask for user confirmation before sending. "
            "3. EMAIL CONFIRMATION WORKFLOW: Always use email_confirm_and_send instead of email_send for user-requested email notifications. Show the generated email content and ask user to confirm or provide feedback for modifications. "
            "4. EMAIL RESPONSE HANDLING: When user responds to email preview with 'yes', 'confirm', 'send', 'looks good' → use email_send to actually send the email. When user provides feedback or asks for changes to an EMAIL PREVIEW → use regenerate_email_summary with their feedback, including the original email recipient and PR details from context. "
            "5. EMAIL FEEDBACK vs JIRA COMMENTS: If the user is responding to an EMAIL PREVIEW (showing email content with 'Please confirm if this email looks good to send'), their feedback should modify the EMAIL, not add a Jira comment. Only use jira_comment_issue when the user explicitly asks to 'add comment to [ticket]' or 'comment on [ticket]' without any email context. "
            "6. CONTEXT AWARENESS: When regenerating Jira issue summary emails, pass the original issue details to regenerate_email_summary so it can properly format the enhanced summary. The agent should maintain context about what type of email is being modified (PR vs Jira issue). "
            "3. Always extract email addresses from the user's request when they mention 'notify', 'email', or provide an email address. "
            "For email workflows: when a user provides feedback on email summaries, use regenerate_email_summary. When they approve a final summary, use finalize_email_summary. "
            "Return function calls promptly; avoid long natural-language replies unless no tool applies. "
            "If you can infer the user's intent, execute the appropriate function immediately. "
            "When users ask about previous work or context, use the session context information provided to give helpful answers about both GitHub and Jira activities. "
            "When users refer to 'this project', 'this repository', 'current project', 'this pr', 'this issue', or similar context references, use the most recently accessed repository, project, PR, or issue from the context. "
            "For example, if the context shows 'Repository: owner/repo-name' from a recent action, use that repository when the user asks about 'this project' or 'this repository'. "
            "If the user just viewed PR #4 and then says 'merge this pr', use PR #4. If they just viewed issue TP-1 and say 'comment on this issue', use TP-1. "
            "MERGE DEFAULTS: When merging PRs, use sensible defaults: merge_method='merge', commit_title from PR title, commit_message from PR description. Only ask for custom merge details if user specifically requests them (e.g., 'squash merge' or 'merge with custom message'). "
        )
        # Use Gemini 2.5 Flash Lite for tool calling support
        self.model = genai.GenerativeModel(
            "gemini-2.5-flash-lite",
            tools=self.tools,
            system_instruction=system_instruction,
        )

    async def run(self, prompt: str, session_id: str = None):
        print(f"DEBUG: Coordinator run called with session_id: {session_id}")
        # Get or create context for this session
        context = context_service.get_or_create_context(session_id)
        
        # Enhance prompt with context
        context_info = context_service.get_context_for_prompt(prompt)
        enhanced_prompt = f"{context_info}User request: {prompt}"
        
        history = []
        # First turn with enhanced prompt
        try:
            response = await self.model.generate_content_async(enhanced_prompt)
        except Exception:
            # Fallback: plain text generation without tools
            plain = genai.GenerativeModel("gemini-2.5-flash-lite")
            resp = await plain.generate_content_async(enhanced_prompt)
            return resp.text if getattr(resp, "text", None) else ""

        # Handle tool calls iteratively
        any_tool_called = False
        collected_tool_calls = []
        while True:
            parts = []
            try:
                parts = response.candidates[0].content.parts  # type: ignore[attr-defined]
            except Exception:
                break

            function_calls = [
                p.function_call for p in parts if getattr(p, "function_call", None) is not None
            ]
            if not function_calls:
                break

            # Execute each function call and send results back
            tool_results = []
            for fc in function_calls:
                # Skip malformed function calls
                if not fc.name or not fc.name.strip():
                    continue
                    
                name = fc.name.strip()
                args = dict(fc.args or {})
                # Normalize missing or vague args from NL prompts
                if name == "jira_create_issue":
                    if not args.get("project_key") and settings.jira_default_project_key:
                        args["project_key"] = settings.jira_default_project_key
                    # If only a title is given, map to summary and set a placeholder description
                    if "title" in args and "summary" not in args:
                        args["summary"] = args.pop("title")
                    if "description" not in args:
                        args["description"] = "Created via agent"
                    if "issuetype_name" not in args:
                        args["issuetype_name"] = "Task"
                if name == "github_create_branch":
                    # Fill source_branch default
                    if "source_branch" not in args or not args.get("source_branch"):
                        args["source_branch"] = "main"
                if name == "email_send":
                    # Require explicit recipient email. If missing, stop and ask the client to provide it.
                    if not args.get("to"):
                        collected_tool_calls.append({"name": name, "args": args})
                        return {
                            "error": "email_required",
                            "toolCalls": collected_tool_calls,
                            "model_summary": None,
                            "details": "Recipient email address is required. Please provide 'to' (e.g., david@example.com).",
                        }
                collected_tool_calls.append({"name": name, "args": args})
                runner = ALL_TOOL_RUNNERS.get(name)
                if runner is None:
                    tool_results.append({"function_response": {"name": name, "response": {"error": f"Unknown tool: {name}"}}})
                    continue
                try:
                    result = await runner(**args)
                    tool_results.append({"function_response": {"name": name, "response": result}})
                    any_tool_called = True
                    
                    # Enhanced email notification workflow for PR creation
                    if name == "github_create_pull_request" and hasattr(result, 'number'):
                        # Check if email was requested in the original prompt
                        if "email" in prompt.lower() or "notify" in prompt.lower():
                            try:
                                # Extract email address from prompt
                                import re
                                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', prompt)
                                if email_match:
                                    email_address = email_match.group()
                                    
                                    # Generate email content for new PR
                                    pr_number = result.number
                                    pr_title = result.title
                                    repo = f"{args.get('owner')}/{args.get('repo')}"
                                    
                                    subject = f"New Pull Request Created: #{pr_number} - {pr_title}"
                                    body = f"""
Hello,

A new pull request has been created in the repository {repo}:

• PR Number: #{pr_number}
• Title: {pr_title}
• Repository: {repo}
• Head Branch: {args.get('head', 'Unknown')}
• Base Branch: {args.get('base', 'main')}
• URL: {result.html_url}

{args.get('body', '')}

Please review the pull request and provide feedback when convenient.

Best regards,
Project Automator Agent
                                    """.strip()
                                    
                                    # Send email notification
                                    from ..services.email_service import send_email
                                    email_result = await send_email(to_email=email_address, subject=subject, body=body)
                                    
                                    # Convert result to dict and add email notification info
                                    result_dict = {
                                        "id": result.id,
                                        "number": result.number,
                                        "title": result.title,
                                        "state": result.state,
                                        "html_url": result.html_url
                                    }
                                    
                                    if email_result.get("status") == "sent":
                                        result_dict["email_notification"] = {
                                            "status": "sent",
                                            "recipient": email_address,
                                            "message": f"Email notification sent to {email_address}"
                                        }
                                    else:
                                        result_dict["email_notification"] = {
                                            "status": "failed",
                                            "error": email_result.get("error", "Unknown error"),
                                            "message": "Failed to send email notification"
                                        }
                                    
                                    # Replace the result with the enhanced version
                                    tool_results[-1]["function_response"]["response"] = result_dict
                                    
                                else:
                                    # Convert result to dict and add email notification info
                                    result_dict = {
                                        "id": result.id,
                                        "number": result.number,
                                        "title": result.title,
                                        "state": result.state,
                                        "html_url": result.html_url,
                                        "email_notification": {
                                            "status": "no_email_found",
                                            "message": "Email address not found in request. Please provide an email address to send notifications."
                                        }
                                    }
                                    tool_results[-1]["function_response"]["response"] = result_dict
                                    
                            except Exception as email_ex:
                                # Convert result to dict and add email error
                                result_dict = {
                                    "id": result.id,
                                    "number": result.number,
                                    "title": result.title,
                                    "state": result.state,
                                    "html_url": result.html_url,
                                    "email_error": str(email_ex)
                                }
                                tool_results[-1]["function_response"]["response"] = result_dict
                    
                    # Enhanced email notification workflow for PR closure
                    elif name == "github_close_pull_request" and result.get("state") == "closed":
                        # Check if email was requested in the original prompt
                        if "email" in prompt.lower() or "notify" in prompt.lower():
                            try:
                                # Generate initial AI summary of PR closure
                                pr_summary_prompt = f"""
Generate a professional email summary for a closed pull request with these details:
- Repository: {args.get('owner')}/{args.get('repo')}
- PR Number: #{args.get('pr_number')}
- Status: Closed
- Action: Pull request was closed

Create a concise, professional summary that includes:
1. What was closed
2. Repository context
3. Next steps or impact
4. Professional closing
user feedback required
Keep it under 100 words and make it suitable for team communication.
                                """.strip()
                                
                                # Generate initial summary using the model
                                summary_response = await self.model.generate_content_async(pr_summary_prompt)
                                initial_summary = getattr(summary_response, 'text', 'Pull request has been closed.')
                                
                                # Add email workflow to result
                                result["email_workflow"] = {
                                    "status": "initial_summary_generated",
                                    "initial_summary": initial_summary,
                                    "pr_details": {
                                        "repository": f"{args.get('owner')}/{args.get('repo')}",
                                        "pr_number": args.get('pr_number'),
                                        "status": "closed"
                                    },
                                    "next_step": "user_feedback_required",
                                    "message": "Initial email summary generated. Please review and provide feedback or key points to include."
                                }
                                
                            except Exception as email_ex:
                                result["email_error"] = str(email_ex)
                                
                except Exception as ex:
                    tool_results.append({"function_response": {"name": name, "response": {"error": str(ex)}}})
            # If we executed tools, return their raw responses immediately
            if any_tool_called and tool_results:
                if len(tool_results) == 1:
                    # Attempt to generate a concise model summary if model available
                    try:
                        tool_response = tool_results[0]['function_response']['response']
                        # Convert Pydantic models to dict for better serialization
                        if hasattr(tool_response, '__dict__'):
                            tool_response = tool_response.__dict__
                        elif hasattr(tool_response, 'model_dump'):
                            tool_response = tool_response.model_dump()
                        elif isinstance(tool_response, list) and tool_response and hasattr(tool_response[0], 'model_dump'):
                            tool_response = [item.model_dump() for item in tool_response]
                        
                        summary_prompt = f"Summarize the action result in one sentence: {tool_response}"
                        summary_resp = await self.model.generate_content_async(summary_prompt)
                        model_summary = getattr(summary_resp, 'text', None)
                    except Exception:
                        # Fallback: create a simple summary based on the tool name
                        tool_name = collected_tool_calls[0].get("name", "tool")
                        if "jira_get_projects" in tool_name:
                            model_summary = "Retrieved the list of available Jira projects."
                        elif "jira_get_issues" in tool_name:
                            model_summary = "Retrieved the list of Jira issues for the project."
                        else:
                            model_summary = f"Executed {tool_name} successfully."
                    result = {
                        "result": tool_results[0]["function_response"]["response"],
                        "toolCalls": collected_tool_calls,
                        "model_summary": model_summary,
                    }
                else:
                    result = {
                        "result": [tr["function_response"]["response"] for tr in tool_results],
                        "toolCalls": collected_tool_calls,
                        "model_summary": None,
                    }
                
                # Save context after tool execution
                context.add_conversation(prompt, result)
                context_service.save_context()
                
                return result

            # Otherwise, attempt to continue the loop by passing tool_results back to the model
            try:
                response = await self.model.generate_content_async(tool_results)
            except Exception:
                break

        # Return final text; do not fallback to regex agent (LLM-only mode)
        try:
            final_text = response.text  # type: ignore[attr-defined]
            if (not final_text or final_text.strip() == "") and not any_tool_called:
                result = {"error": "Model did not produce a final text and no tool was called.", "toolCalls": collected_tool_calls}
            else:
                # Include tool results if any tools were called
                tool_results_data = None
                if any_tool_called and tool_results:
                    # Extract the actual results from tool_results
                    tool_results_data = []
                    for tr in tool_results:
                        if "function_response" in tr:
                            tool_results_data.append(tr["function_response"]["response"])
                        else:
                            tool_results_data.append(tr)
                    # If only one result, return it directly
                    if len(tool_results_data) == 1:
                        tool_results_data = tool_results_data[0]
                
                result = {"result": tool_results_data, "toolCalls": collected_tool_calls, "model_summary": final_text}
            
            # Save context after processing
            context.add_conversation(prompt, result)
            context_service.save_context()
            
            return result
        except Exception:
            # Try to surface useful debugging info from the last response
            try:
                parts = response.candidates[0].content.parts  # type: ignore[attr-defined]
                function_calls = [
                    {"name": p.function_call.name, "args": dict(p.function_call.args or {})}
                    for p in parts if getattr(p, "function_call", None) is not None
                ]
                if function_calls:
                    result = {
                        "error": "Failed to read model text; model returned function_call parts.",
                        "toolCalls": function_calls,
                    }
                else:
                    result = {"error": "Failed to read model response."}
                
                # Save context even for errors
                context.add_conversation(prompt, result)
                context_service.save_context()
                
                return result
            except Exception:
                result = {"error": "Failed to read model response."}
                context.add_conversation(prompt, result)
                context_service.save_context()
                return result


def create_orchestrator_agent() -> GeminiToolsAgent:
    return GeminiToolsAgent()
