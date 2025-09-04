from google.ai.generativelanguage import Tool, FunctionDeclaration, Schema
from ..services import jira_service

# Example: wrap fetch_jira_issue
jira_fetch_issue_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="jira_fetch_issue",
            description="Fetch a single Jira issue by ticket ID",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "ticket_id": Schema(type=Schema.Type.STRING, description="The Jira ticket ID, e.g. PROJ-123")
                },
                required=["ticket_id"],
            ),
        )
    ]
)

async def run_jira_fetch_issue(ticket_id: str):
    return await jira_service.fetch_jira_issue(ticket_id)

# --- List Jira projects ---
jira_get_projects_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="jira_get_projects",
            description="List all available Jira projects",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={},
                required=[],
            ),
        )
    ]
)

async def run_jira_get_projects():
    return await jira_service.get_jira_projects()

# --- List issues for a project (optional status filter) ---
jira_get_issues_for_project_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="jira_get_issues_for_project",
            description="List issues for a Jira project, optionally filtered by status",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "project_key": Schema(type=Schema.Type.STRING, description="Jira project key, e.g. TP"),
                    "status": Schema(type=Schema.Type.STRING, description="Optional status filter, e.g. 'In Progress'"),
                },
                required=["project_key"],
            ),
        )
    ]
)

async def run_jira_get_issues_for_project(project_key: str, status: str | None = None):
    return await jira_service.get_issues_for_project(project_key, status)

# --- Create Jira issue ---
jira_create_issue_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="jira_create_issue",
            description="Create a new Jira issue",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "project_key": Schema(type=Schema.Type.STRING, description="Project key, e.g. TP"),
                    "summary": Schema(type=Schema.Type.STRING, description="Issue summary/title"),
                    "description": Schema(type=Schema.Type.STRING, description="Issue description"),
                    "issuetype_name": Schema(type=Schema.Type.STRING, description="Issue type name, e.g. Task, Bug"),
                },
                required=["project_key", "summary", "description"],
            ),
        )
    ]
)

async def run_jira_create_issue(project_key: str, summary: str, description: str, issuetype_name: str = "Task"):
    from ..models.jira_models import CreateJiraIssue

    payload = CreateJiraIssue(
        project_key=project_key,
        summary=summary,
        description=description,
        issuetype_name=issuetype_name,
    )
    return await jira_service.create_issue(payload)

# --- Assign Jira issue ---
jira_assign_issue_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="jira_assign_issue",
            description="Assign a Jira issue to a user by their name",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "issue_key": Schema(type=Schema.Type.STRING, description="Issue key, e.g. TP-123"),
                    "assignee_name": Schema(type=Schema.Type.STRING, description="Assignee display name or email"),
                },
                required=["issue_key", "assignee_name"],
            ),
        )
    ]
)

async def run_jira_assign_issue(issue_key: str, assignee_name: str):
    return await jira_service.assign_issue(issue_key, assignee_name)

# --- Get possible transitions ---
jira_get_possible_transitions_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="jira_get_possible_transitions",
            description="Get possible workflow transitions for an issue",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "issue_key": Schema(type=Schema.Type.STRING, description="Issue key, e.g. TP-123"),
                },
                required=["issue_key"],
            ),
        )
    ]
)

async def run_jira_get_possible_transitions(issue_key: str):
    return await jira_service.get_possible_transitions(issue_key)

# --- Transition issue ---
jira_transition_issue_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="jira_transition_issue",
            description="Transition an issue using a transition ID",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "issue_key": Schema(type=Schema.Type.STRING, description="Issue key, e.g. TP-123"),
                    "transition_id": Schema(type=Schema.Type.STRING, description="Transition ID"),
                },
                required=["issue_key", "transition_id"],
            ),
        )
    ]
)

async def run_jira_transition_issue(issue_key: str, transition_id: str):
    return await jira_service.transition_issue(issue_key, transition_id)

# --- Comment on issue ---
jira_comment_issue_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="jira_comment_issue",
            description="Add a comment to a Jira issue",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "issue_key": Schema(type=Schema.Type.STRING, description="Issue key, e.g. TP-123"),
                    "comment_text": Schema(type=Schema.Type.STRING, description="Comment body text"),
                },
                required=["issue_key", "comment_text"],
            ),
        )
    ]
)

async def run_jira_comment_issue(issue_key: str, comment_text: str):
    return await jira_service.comment_issue(issue_key, comment_text)

# --- Get sprints for project ---
jira_get_sprints_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="jira_get_sprints",
            description="List sprints for a project",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "project_key": Schema(type=Schema.Type.STRING, description="Project key, e.g. TP"),
                },
                required=["project_key"],
            ),
        )
    ]
)

async def run_jira_get_sprints(project_key: str):
    return await jira_service.get_sprints(project_key)

# --- Move issue to sprint ---
jira_move_issue_to_sprint_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="jira_move_issue_to_sprint",
            description="Move a Jira issue to a specific sprint",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "sprint_id": Schema(type=Schema.Type.INTEGER, description="Sprint ID"),
                    "issue_key": Schema(type=Schema.Type.STRING, description="Issue key, e.g. TP-123"),
                },
                required=["sprint_id", "issue_key"],
            ),
        )
    ]
)

async def run_jira_move_issue_to_sprint(sprint_id: int, issue_key: str):
    return await jira_service.move_issue_to_sprint(sprint_id, issue_key)
