import re
from typing import Dict, Any, List, Callable, Awaitable, TypedDict

from .tools import get_tools
from .models.jira_models import CreateJiraIssue


class Tool(TypedDict):
    """A dictionary representing a tool."""

    pattern: re.Pattern[str]
    function: Callable[..., Awaitable[Any]]
    # A function that extracts the arguments for the tool from the regex match.
    arg_extractor: Callable[[re.Match[str]], Dict[str, Any]]


def _extract_list_branches_args(match: re.Match[str]) -> Dict[str, Any]:
    """Extracts the owner and repo from the regex match."""
    return {"owner": match.group("owner"), "repo": match.group("repo")}

def _extract_create_branch_args(match: re.Match[str]) -> Dict[str, Any]:
    """Extracts the owner, repo, branch, and source from the regex match."""
    return {
        "owner": match.group("owner"),
        "repo": match.group("repo"),
        "branch_name": match.group("branch"),
        "source_branch": match.group("source"),
    }

def _extract_create_jira_issue_args(match: re.Match[str]) -> Dict[str, Any]:
    """Extracts the project, title, and description from the regex match."""
    return {
        "issue_data": CreateJiraIssue(
            project_key=match.group("project"),
            summary=match.group("title"),
            description=match.group("desc"),
        )
    }


async def process_prompt(prompt: str) -> Dict[str, Any]:
    """
    A functional AI agent that parses a prompt and executes the correct tool.
    """
    tools = get_tools()

    # --- Tool Matching Logic ---
    # The agent will try to match the prompt against a series of patterns.
    tool_patterns: List[Tool] = [
        {
            "pattern": re.compile(r"list (my |github )?repos", re.IGNORECASE),
            "function": tools["github_get_repos"]["function"],
            "arg_extractor": lambda match: {},
        },
        {
            "pattern": re.compile(
                r'list.*?branches in ["\\](?P<owner>[\w-]+)/(?P<repo>[\w-]+)["\\]',
                re.IGNORECASE,
            ),
            "function": tools["github_get_branches"]["function"],
            "arg_extractor": _extract_list_branches_args,
        },
        {
            "pattern": re.compile(
                r'create.*?branch ["\'](?P<branch>[\w/-]+)["\'] from ["\'](?P<source>[\w/-]+)["\'] in ["\'](?P<owner>[\w-]+)/(?P<repo>[\w-]+)["\']',
                re.IGNORECASE,
            ),
            "function": tools["github_create_branch"]["function"],
            "arg_extractor": _extract_create_branch_args,
        },
        {
            "pattern": re.compile(
                r'create.*?jira issue in project ["\\](?P<project>\w+)["\\] with title ["\\](?P<title>.*?)["\\] and description ["\\](?P<desc>.*?)["\\]',
                re.IGNORECASE,
            ),
            "function": tools["jira_create_issue"]["function"],
            "arg_extractor": _extract_create_jira_issue_args,
        },
    ]

    for tool in tool_patterns:
        match = tool["pattern"].search(prompt)
        if not match:
            continue

        try:
            kwargs = tool["arg_extractor"](match)
            result = await tool["function"](**kwargs)
            if tool["function"] == tools["github_create_branch"]["function"]:
                return {
                    "response": f"Successfully created branch '{result.name}' in '{match.group('owner')}/{match.group('repo')}'."
                }
            if tool["function"] == tools["jira_create_issue"]["function"]:
                return {"response": f"Successfully created Jira issue {result.get('key')}."}
            return {"response": result}
        except Exception as e:
            return {"error": f"Error executing tool: {e}"}

    # If no specific tool matches, return a helpful message
    return {
        "response": "I'm sorry, I couldn't understand that request. Please try phrasing it differently.",
        "example_prompts": [
            "list my github repos",
            'list branches in "shashank/project_automator"',
            'create branch "feature/test" from "main" in "shashank/project_automator"',
            'create a jira issue in project "TP" with title "New Bug" and description "Button is broken."',
        ],
    }