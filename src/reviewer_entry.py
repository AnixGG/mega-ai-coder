import os
import sys
from src.core.github_client import GithubClient
from src.agents.reviewer import ReviewerAgent
from src.logger import log


def get_ci_status(pr):
    log.info(f"Reviewer: getting CI Status for PR {pr.number}...")
    head_commit = pr.get_commits().reversed[0]
    check_runs = head_commit.get_check_runs()

    failed_logs = []
    for check in check_runs:
        if check.conclusion == "failure":
            failed_logs.append(f"Job '{check.name}' FAILED.")

    return failed_logs

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
        pr.create_review(event="REQUEST_CHANGES", body="CI Failed. Please fix tests.")
        sys.exit(1)

    task_description = f"{pr.title}\n{pr.body}"

    diff_text = ""
    for file in pr.get_files():
        diff_text += f"\n--- {file.filename} ---\n{file.patch}\n"

    reviewer = ReviewerAgent()
    result = reviewer.review_pr(task_description, diff_text)

    log.info(f"Verdict: {result.action}")
    log.info(f"Summary: {result.general_summary}")

    pr.create_issue_comment(f"## AI Review Result: {result.action}\n\n{result.general_summary}")
    last_commit = list(pr.get_commits())[-1]

    for comment in result.comments:
        try:
            pr.create_review_comment(
                body=comment.body,
                commit=last_commit,
                path=comment.path,
                line=comment.line
            )
        except Exception as e:
            log.error(f"Could not post comment on {comment.path}:{comment.line} - {e}")


    if result.action == "REQUEST_CHANGES":
        pr.create_review(event="REQUEST_CHANGES", body=result.general_summary)
        sys.exit(1)
    else:
        pr.create_review(event="APPROVE")


if __name__ == "__main__":
    main()