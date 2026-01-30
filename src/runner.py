import os
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

    def run(self, feedback=""):
        log.debug("--- Starting environment ---")

        token = work_dir_context.set(self.workspace_path)

        log.debug(f"Environment Started: {self.workspace_path}")

        try:
            issue, branch_name = self._setup()

            task_description = f"Title: {issue.title}\nBody: {issue.body}"

            self.agent.run(task_description, feedback=feedback)

            self._teardown(issue, branch_name)
        finally:
            work_dir_context.reset(token)
