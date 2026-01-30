import os
import time
from src.core.github_client import GithubClient
from src.core.local_git import LocalGit
from src.agents.coder import CoderAgent
from src.core.context import work_dir_context
from src.logger import log


class PipelineRunner:
    def __init__(self, repo_name: str, issue_number: int):
        self.repo_name = repo_name
        self.issue_number = issue_number
        self.workspace_path = os.path.abspath(f"./workspace/{repo_name.replace('/', '_')}_{issue_number}")
        self.gh = GithubClient()
        self.local_git = None
        self.agent = CoderAgent()

    def _setup(self):
        issue = self.gh.get_issue(self.repo_name, self.issue_number)

        self.local_git = LocalGit(issue.repository.clone_url, self.workspace_path)
        self.local_git.clone()

        branch_name = f"fix/issue-{self.issue_number}"
        self.local_git.create_branch(branch_name)

        return issue, branch_name

    def _teardown(self, issue, branch_name):
        log.debug("--- Tearing down environment ---")

        self.local_git.commit_all(f"Automated fix for #{self.issue_number}")
        self.local_git.push(branch_name)

        pr = self.gh.create_pull_request(
            repo_name=self.repo_name,
            title=f"Fix: {issue.title}",
            body=f"Fixes #{self.issue_number}",
            head=branch_name,
            base=self.local_git.default_branch,
        )
        log.info(f"PR Created: {pr.html_url}")
        return pr

    def run(self, feedback=""):
        log.debug("--- Starting environment ---")
        token = work_dir_context.set(self.workspace_path)
        log.debug(f"Environment Started: {self.workspace_path}")

        try:
            issue, branch_name = self._setup()
            task_description = f"Title: {issue.title}\nBody: {issue.body}"
            current_feedback = feedback

            for iteration in range(5):
                log.info(f"Iteration {iteration + 1} started")
                self.agent.run(task_description, feedback=current_feedback)

                # Push changes and get PR
                pr = self._teardown(issue, branch_name)

                # Polling for reviewer with 5 min timeout
                start_wait = time.time()
                review_received = False

                while time.time() - start_wait < 300:
                    pr.update()
                    reviews = list(pr.get_reviews())

                    if reviews:
                        last_review = reviews[-1]
                        if last_review.state == "APPROVED":
                            log.info("PR Approved by reviewer.")
                            return

                        if last_review.state == "CHANGES_REQUESTED":
                            log.info(f"Changes requested: {last_review.body}")
                            current_feedback = last_review.body
                            review_received = True
                            break

                    log.debug("Waiting for AI Reviewer...")
                    time.sleep(30)

                if not review_received:
                    log.error("Reviewer timeout (5 minutes reached). Shutting down.")
                    break

        finally:
            work_dir_context.reset(token)