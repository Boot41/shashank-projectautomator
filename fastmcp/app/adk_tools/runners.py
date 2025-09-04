# Tool runner functions without ADK tool declarations
from ..services import github_service, jira_service
from ..services.email_service import send_email

# Jira runners
async def run_jira_fetch_issue(ticket_id: str):
    return await jira_service.fetch_issue(ticket_id)

async def run_jira_get_projects():
    return await jira_service.get_projects()

async def run_jira_get_issues_for_project(project_key: str):
    return await jira_service.get_issues_for_project(project_key)

async def run_jira_create_issue(project_key: str, summary: str, description: str, issuetype_name: str = "Task"):
    from ..models.jira_models import CreateJiraIssue
    payload = CreateJiraIssue(
        project_key=project_key,
        summary=summary,
        description=description,
        issuetype_name=issuetype_name
    )
    return await jira_service.create_issue(payload)

async def run_jira_assign_issue(ticket_id: str, assignee: str):
    return await jira_service.assign_issue(ticket_id, assignee)

async def run_jira_get_possible_transitions(ticket_id: str):
    return await jira_service.get_possible_transitions(ticket_id)

async def run_jira_transition_issue(ticket_id: str, transition_id: str):
    return await jira_service.transition_issue(ticket_id, transition_id)

async def run_jira_comment_issue(ticket_id: str, comment_body: str):
    return await jira_service.comment_issue(ticket_id, comment_body)

async def run_jira_get_sprints(project_key: str):
    return await jira_service.get_sprints(project_key)

async def run_jira_move_issue_to_sprint(ticket_id: str, sprint_id: int):
    return await jira_service.move_issue_to_sprint(ticket_id, sprint_id)

# GitHub runners
async def run_github_get_repos():
    return await github_service.get_repos()

async def run_github_get_branches(owner: str, repo: str):
    return await github_service.get_branches(owner, repo)

async def run_github_create_branch(owner: str, repo: str, branch_name: str, source_branch: str = "main"):
    from ..models.github_models import CreateGithubBranch
    payload = CreateGithubBranch(ref=f"refs/heads/{branch_name}", sha=source_branch)
    return await github_service.create_branch(owner, repo, payload)

async def run_github_create_pull_request(owner: str, repo: str, title: str, head: str, base: str, body: str = ""):
    from ..models.github_models import CreatePullRequest
    payload = CreatePullRequest(title=title, head=head, base=base, body=body)
    return await github_service.create_pull_request(owner, repo, payload)

async def run_github_merge_pull_request(owner: str, repo: str, pr_number: int):
    return await github_service.merge_pull_request(owner, repo, pr_number)

async def run_github_close_pull_request(owner: str, repo: str, pr_number: int):
    return await github_service.close_pull_request(owner, repo, pr_number)

async def run_github_get_issues(owner: str, repo: str):
    return await github_service.get_issues(owner, repo)

async def run_github_create_issue(owner: str, repo: str, title: str, body: str = ""):
    from ..models.github_models import CreateGithubIssue
    payload = CreateGithubIssue(title=title, body=body)
    return await github_service.create_issue(owner, repo, payload)

async def run_github_comment_issue(owner: str, repo: str, issue_number: int, comment_body: str):
    return await github_service.comment_issue(owner, repo, issue_number, comment_body)

# Email runner
async def run_email_send(to: str, subject: str, body: str):
    return await send_email(to_email=to, subject=subject, body=body)

# Enhanced email workflow runners
async def run_regenerate_email_summary(initial_summary: str, user_feedback: str, key_points: str = "", pr_details: dict = None):
    """Regenerate email summary with user feedback and key points"""
    try:
        # This would typically use the AI model to regenerate the summary
        # For now, we'll create a simple enhanced summary
        enhanced_summary = f"""
{initial_summary}

Additional Context:
{user_feedback}

Key Points to Highlight:
{key_points if key_points else "None specified"}

This summary has been enhanced based on your feedback.
        """.strip()
        
        return {
            "status": "summary_regenerated",
            "enhanced_summary": enhanced_summary,
            "pr_details": pr_details or {},
            "next_step": "final_approval_required",
            "message": "Email summary has been regenerated with your feedback. Please review and approve before sending."
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def run_finalize_email_summary(final_summary: str, to_email: str, pr_details: dict):
    """Finalize and send email summary after user approval"""
    try:
        # Create email subject and body
        pr_number = pr_details.get("pr_number", "Unknown")
        repo = pr_details.get("repository", "Unknown")
        
        subject = f"Pull Request #{pr_number} Closed - {repo}"
        body = f"""
Dear Team,

{final_summary}

Repository: {repo}
PR Number: #{pr_number}
Status: Closed

Best regards,
Project Automator Agent
        """.strip()
        
        # Send the email
        email_result = await send_email(to_email=to_email, subject=subject, body=body)
        
        if email_result.get("status") == "sent":
            return {
                "status": "email_sent_successfully",
                "email_result": email_result,
                "pr_details": pr_details,
                "message": f"Email notification has been sent to {to_email}"
            }
        else:
            return {
                "status": "email_failed",
                "error": email_result.get("error", "Unknown error"),
                "message": "Failed to send email notification"
            }
            
    except Exception as e:
        return {"status": "error", "error": str(e)}
