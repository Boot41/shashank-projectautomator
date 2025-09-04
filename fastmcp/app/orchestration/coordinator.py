import google.generativeai as genai
import importlib
from ..config.settings import settings
from ..adk_tools import ALL_TOOL_RUNNERS


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
            "description": "Merge a pull request by number",
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
            "name": "regenerate_email_summary",
            "description": "Regenerate email summary with user feedback and key points",
            "parameters": {
                "type": "object",
                "properties": {
                    "initial_summary": {"type": "string"},
                    "user_feedback": {"type": "string"},
                    "key_points": {"type": "string"},
                    "pr_details": {"type": "object"},
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
            "You are an automation agent. When a user asks for an actionable task, ALWAYS call a function if one matches. "
            "Infer reasonable defaults from context when missing. Never guess IDs. If a required field is missing, pick a sensible default (e.g., issuetype_name='Task'). "
            "For pull request operations: if the user mentions email, notification, or sending updates, you can close the PR and prepare email notification. "
            "For email workflows: when a user provides feedback on email summaries, use regenerate_email_summary. When they approve a final summary, use finalize_email_summary. "
            "Return function calls promptly; avoid long natural-language replies unless no tool applies."
        )
        # Use Gemini 2.0 Flash Lite for tool calling support
        self.model = genai.GenerativeModel(
            "gemini-2.0-flash-lite",
            tools=self.tools,
            system_instruction=system_instruction,
        )

    async def run(self, prompt: str):
        history = []
        # First turn with user prompt
        try:
            response = await self.model.generate_content_async(prompt)
        except Exception:
            # Fallback: plain text generation without tools
            plain = genai.GenerativeModel("gemini-1.5-flash")
            resp = await plain.generate_content_async(prompt)
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
                    
                    # Enhanced email notification workflow for PR closure
                    if name == "github_close_pull_request" and result.get("state") == "closed":
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
                        summary_prompt = f"Summarize the action result in one sentence: {tool_results[0]['function_response']['response']}"
                        summary_resp = await self.model.generate_content_async(summary_prompt)
                        model_summary = getattr(summary_resp, 'text', None)
                    except Exception:
                        model_summary = None
                    return {
                        "result": tool_results[0]["function_response"]["response"],
                        "toolCalls": collected_tool_calls,
                        "model_summary": model_summary,
                    }
                return {
                    "result": [tr["function_response"]["response"] for tr in tool_results],
                    "toolCalls": collected_tool_calls,
                    "model_summary": None,
                }

            # Otherwise, attempt to continue the loop by passing tool_results back to the model
            try:
                response = await self.model.generate_content_async(tool_results)
            except Exception:
                break

        # Return final text; do not fallback to regex agent (LLM-only mode)
        try:
            final_text = response.text  # type: ignore[attr-defined]
            if (not final_text or final_text.strip() == "") and not any_tool_called:
                return {"error": "Model did not produce a final text and no tool was called.", "toolCalls": collected_tool_calls}
            return {"result": None, "toolCalls": collected_tool_calls, "model_summary": final_text}
        except Exception:
            # Try to surface useful debugging info from the last response
            try:
                parts = response.candidates[0].content.parts  # type: ignore[attr-defined]
                function_calls = [
                    {"name": p.function_call.name, "args": dict(p.function_call.args or {})}
                    for p in parts if getattr(p, "function_call", None) is not None
                ]
                if function_calls:
                    return {
                        "error": "Failed to read model text; model returned function_call parts.",
                        "toolCalls": function_calls,
                    }
            except Exception:
                pass
            return {"error": "Failed to read model response."}


def create_orchestrator_agent() -> GeminiToolsAgent:
    return GeminiToolsAgent()
