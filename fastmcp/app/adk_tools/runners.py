# Tool runner functions without ADK tool declarations
from ..services import github_service, jira_service
from ..services.email_service import send_email

# Jira runners
async def run_jira_fetch_issue(ticket_id: str):
    return await jira_service.fetch_jira_issue(ticket_id)

async def run_jira_get_projects():
    return await jira_service.get_jira_projects()

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

async def run_jira_summarize_and_email_issue(issue_key: str, to_email: str, additional_context: str = ""):
    """Summarize a Jira issue and prepare email with confirmation workflow"""
    try:
        # First, fetch the issue details
        issue_details = await jira_service.fetch_jira_issue(issue_key)
        
        if not issue_details:
            return {"status": "error", "error": f"Issue {issue_key} not found"}
        
        # Generate a comprehensive summary
        summary = f"""
Jira Issue Summary: {issue_details.ticket}

Title: {issue_details.title}
Status: {issue_details.status}
Assignee: {issue_details.assignee}

Description:
{issue_details.description or 'No description provided'}

Additional Context:
{additional_context if additional_context else 'None provided'}
        """.strip()
        
        # Return in email preview format for confirmation
        return {
            "status": "preview",
            "action_type": "Jira Issue Summary",
            "email_preview": {
                "to": to_email,
                "subject": f"Jira Issue Summary: {issue_details.ticket} - {issue_details.title}",
                "body": summary
            },
            "message": f"📧 Jira Issue Summary Email Preview for {issue_key}:\n\nTo: {to_email}\nSubject: Jira Issue Summary: {issue_details.ticket} - {issue_details.title}\n\nBody:\n{summary}\n\nPlease confirm if this summary email looks good to send, or provide feedback for modifications."
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def run_jira_comment_issue(issue_key: str, comment_text: str):
    return await jira_service.comment_issue(issue_key, comment_text)

async def run_jira_get_issue_comments(issue_key: str):
    return await jira_service.get_issue_comments(issue_key)

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
    return await github_service.create_branch(owner, repo, branch_name, source_branch)

async def run_github_create_pull_request(owner: str, repo: str, title: str, head: str, base: str, body: str = ""):
    from ..models.github_models import CreatePullRequest
    payload = CreatePullRequest(title=title, head=head, base=base, body=body)
    return await github_service.create_pull_request(owner, repo, payload)

async def run_github_merge_pull_request(owner: str, repo: str, pr_number: int, commit_title: str = None, commit_message: str = None, merge_method: str = "merge"):
    return await github_service.merge_pull_request(owner, repo, pr_number, commit_title, commit_message, merge_method)

async def run_github_close_pull_request(owner: str, repo: str, pr_number: int):
    return await github_service.close_pull_request(owner, repo, pr_number)

async def run_github_get_issues(owner: str, repo: str):
    return await github_service.get_issues(owner, repo)

async def run_github_get_pull_requests(owner: str, repo: str, state: str = "open"):
    return await github_service.get_pull_requests(owner, repo, state)

async def run_github_get_pr_files(owner: str, repo: str, pr_number: int):
    return await github_service.get_pull_request_files(owner, repo, pr_number)

async def run_github_create_issue(owner: str, repo: str, title: str, body: str = ""):
    from ..models.github_models import CreateGithubIssue
    payload = CreateGithubIssue(title=title, body=body)
    return await github_service.create_issue(owner, repo, payload)

async def run_github_comment_issue(owner: str, repo: str, issue_number: int, comment_body: str):
    return await github_service.comment_issue(owner, repo, issue_number, comment_body)

# Email runner
async def run_email_send(to: str, subject: str, body: str):
    return await send_email(to_email=to, subject=subject, body=body)

async def run_email_confirm_and_send(to: str, subject: str, body: str, action_type: str):
    """Show email preview and ask for user confirmation before sending"""
    return {
        "status": "preview",
        "action_type": action_type,
        "email_preview": {
            "to": to,
            "subject": subject,
            "body": body
        },
        "message": f"📧 Email Preview for {action_type}:\n\nTo: {to}\nSubject: {subject}\n\nBody:\n{body}\n\nPlease confirm if this email looks good to send, or provide feedback for modifications."
    }

# Enhanced email workflow runners
async def run_regenerate_email_summary(initial_summary: str, user_feedback: str, key_points: str = "", pr_details: dict = None, to_email: str = "", issue_details: dict = None):
    """Regenerate email summary with user feedback and key points"""
    try:
        # Determine if this is a Jira issue or PR based on available details
        if issue_details:
            # This is a Jira issue summary
            issue_key = issue_details.get('ticket', 'unknown')
            issue_title = issue_details.get('title', 'Jira Issue')
            
            # Create enhanced summary with user feedback
            enhanced_summary = f"""
Jira Issue Summary: {issue_key}

Title: {issue_title}
Status: {issue_details.get('status', 'Unknown')}
Assignee: {issue_details.get('assignee', 'Unassigned')}

Description:
{issue_details.get('description', 'No description provided')}

Additional Details:
{user_feedback}

Key Points:
{key_points if key_points else "None specified"}

This summary has been enhanced based on your feedback.
            """.strip()
            
            # Return in preview format so CLI can display it properly
            return {
                "status": "preview",
                "action_type": "Jira Issue Summary (regenerated)",
                "email_preview": {
                    "to": to_email or "recipient@example.com",
                    "subject": f"Jira Issue Summary: {issue_key} - {issue_title}",
                    "body": enhanced_summary
                },
                "message": f"📧 Regenerated Email Preview for Jira Issue {issue_key}:\n\nTo: {to_email or '[recipient]'}\nSubject: Jira Issue Summary: {issue_key} - {issue_title}\n\nBody:\n{enhanced_summary}\n\nPlease confirm if this regenerated email looks good to send, or provide additional feedback for modifications."
            }
        else:
            # This is a PR summary (original logic)
            pr_number = pr_details.get('number', 'unknown') if pr_details else 'unknown'
            pr_title = pr_details.get('title', 'Pull Request') if pr_details else 'Pull Request'
            
            # Create enhanced summary with user feedback
            enhanced_summary = f"""
{initial_summary}

Additional Details:
{user_feedback}

Key Points:
{key_points if key_points else "None specified"}

This summary has been enhanced based on your feedback.
            """.strip()
            
            # Return in preview format so CLI can display it properly
            return {
                "status": "preview",
                "action_type": "PR created (regenerated)",
                "email_preview": {
                    "to": to_email or "recipient@example.com",
                    "subject": f"PR #{pr_number}: {pr_title}",
                    "body": enhanced_summary
                },
                "message": f"📧 Regenerated Email Preview for PR #{pr_number}:\n\nTo: {to_email or '[recipient]'}\nSubject: PR #{pr_number}: {pr_title}\n\nBody:\n{enhanced_summary}\n\nPlease confirm if this regenerated email looks good to send, or provide additional feedback for modifications."
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
