import os
import sys
from src.core.github_client import GithubClient
from src.agents.reviewer import ReviewerAgent
from src.logger import log


def get_ci_status(pr):
    log.info(f"Reviewer: getting CI Status for PR {pr.number}...")

    try:
        repo = pr.base.repo
        commit = repo.get_commit(pr.head.sha)
        status = commit.get_combined_status()

        if status.state == "success":
            return []
        elif status.state == "failure":
            failed_statuses = [s.context for s in status.statuses if s.state == "failure"]
            return [f"CI check failed: {ctx}" for ctx in failed_statuses]
        elif status.state == "pending":
            return ["CI checks are still pending."]
        else:
            return [f"CI status: {status.state}"]

    except Exception as e:
        log.warning(f"Could not fetch CI status: {e}")
        return []


def main():
    repo_name = os.getenv("REPO_NAME")
    pr_number = int(os.getenv("PR_NUMBER"))

    if not repo_name or not pr_number:
        log.error("Missing environment variables (REPO_NAME or PR_NUMBER)")
        sys.exit(1)

    log.debug(f"Reviewing PR #{pr_number} in {repo_name}...")
    gh = GithubClient()
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    failed_ci = get_ci_status(pr)
    if failed_ci:
        error_msg = "CI Checks Failed:\n" + "\n".join(failed_ci)
        pr.create_issue_comment(error_msg)
        sys.exit(1)

    task_description = f"{pr.title}\n{pr.body}"

    diff_text = ""
    for file in pr.get_files():
        diff_text += f"\n--- {file.filename} ---\n{file.patch}\n"

    reviewer = ReviewerAgent()
    result = reviewer.review_pr(task_description, diff_text)

    log.info(f"Verdict: {result.action}")
    log.info(f"Summary: {result.general_summary}")

    if result.action == "REQUEST_CHANGES":
        pr.create_issue_comment(f"## ❌ AI Review: Changes Requested\n\n{result.general_summary}")
        sys.exit(1)
    else:
        pr.create_issue_comment(f"## ✅ AI Review: Approved\n\n{result.general_summary}")


if __name__ == "__main__":
    main()