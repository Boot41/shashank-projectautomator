try:
    # Import runner functions from the clean runners module
    from .runners import (
        # Jira runners
        run_jira_fetch_issue,
        run_jira_get_projects,
        run_jira_get_issues_for_project,
        run_jira_create_issue,
        run_jira_assign_issue,
        run_jira_get_possible_transitions,
        run_jira_transition_issue,
        run_jira_comment_issue,
        run_jira_get_sprints,
        run_jira_move_issue_to_sprint,
        # GitHub runners
        run_github_get_repos,
        run_github_get_branches,
        run_github_create_branch,
        run_github_create_pull_request,
        run_github_merge_pull_request,
        run_github_close_pull_request,
        run_github_get_issues,
        run_github_create_issue,
        run_github_comment_issue,
        run_email_send,
        run_regenerate_email_summary,
        run_finalize_email_summary,
    )

    # We don't need ALL_TOOLS since we're using our own tool declarations in coordinator
    ALL_TOOLS = []

    ALL_TOOL_RUNNERS = {
        # Jira runners
        "jira_fetch_issue": run_jira_fetch_issue,
        "jira_get_projects": run_jira_get_projects,
        "jira_get_issues_for_project": run_jira_get_issues_for_project,
        "jira_create_issue": run_jira_create_issue,
        "jira_assign_issue": run_jira_assign_issue,
        "jira_get_possible_transitions": run_jira_get_possible_transitions,
        "jira_transition_issue": run_jira_transition_issue,
        "jira_comment_issue": run_jira_comment_issue,
        "jira_get_sprints": run_jira_get_sprints,
        "jira_move_issue_to_sprint": run_jira_move_issue_to_sprint,
        # GitHub runners
        "github_get_repos": run_github_get_repos,
        "github_get_branches": run_github_get_branches,
        "github_create_branch": run_github_create_branch,
        "github_create_pull_request": run_github_create_pull_request,
        "github_merge_pull_request": run_github_merge_pull_request,
        "github_close_pull_request": run_github_close_pull_request,
        "github_get_issues": run_github_get_issues,
        "github_create_issue": run_github_create_issue,
        "github_comment_issue": run_github_comment_issue,
        "email_send": run_email_send,
        "regenerate_email_summary": run_regenerate_email_summary,
        "finalize_email_summary": run_finalize_email_summary,
    }
except Exception:
    # Fail open: if ADK tool schemas aren't available, expose empty lists
    ALL_TOOLS = []
    ALL_TOOL_RUNNERS = {}
