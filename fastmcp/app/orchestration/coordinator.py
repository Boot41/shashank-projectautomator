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
    ]
    return [{"function_declarations": fns}]


class GeminiToolsAgent:
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise RuntimeError("Missing GEMINI_API_KEY")
        genai.configure(api_key=settings.gemini_api_key)
        self.tools = _build_tool_declarations()
        system_instruction = (
            "You are an automation agent. When the user requests an action that matches a tool, "
            "call the corresponding function with correct JSON arguments. Prefer calling tools over natural language responses."
        )
        # Prefer a 1.5 model for tool calling support
        self.model = genai.GenerativeModel(
            "gemini-1.5-flash",
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
                name = fc.name
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
                runner = ALL_TOOL_RUNNERS.get(name)
                if runner is None:
                    tool_results.append({"function_response": {"name": name, "response": {"error": "unknown tool"}}})
                    continue
                try:
                    result = await runner(**args)
                    tool_results.append({"function_response": {"name": name, "response": result}})
                    any_tool_called = True
                except Exception as ex:
                    tool_results.append({"function_response": {"name": name, "response": {"error": str(ex)}}})
            # If we executed tools, return their raw responses immediately
            if any_tool_called and tool_results:
                if len(tool_results) == 1:
                    return tool_results[0]["function_response"]["response"]
                return {"responses": [tr["function_response"]["response"] for tr in tool_results]}

            # Otherwise, attempt to continue the loop by passing tool_results back to the model
            try:
                response = await self.model.generate_content_async(tool_results)
            except Exception:
                break

        # Return final text; do not fallback to regex agent (LLM-only mode)
        try:
            final_text = response.text  # type: ignore[attr-defined]
            if (not final_text or final_text.strip() == "") and not any_tool_called:
                return {"error": "Model did not produce a final text and no tool was called."}
            return final_text
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
                        "function_calls": function_calls,
                    }
            except Exception:
                pass
            return {"error": "Failed to read model response."}


def create_orchestrator_agent() -> GeminiToolsAgent:
    return GeminiToolsAgent()
