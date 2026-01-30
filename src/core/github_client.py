from github import Github
from src.core.config import settings


class GithubClient:
    def __init__(self):
        self.client = Github(settings.GITHUB_TOKEN)

    def get_repo(self, repo_name: str):
        return self.client.get_repo(repo_name)

    def get_issue(self, repo_name: str, issue_number: int):
        repo = self.client.get_repo(repo_name)
        return repo.get_issue(issue_number)

    def create_pull_request(self, repo_name: str, title: str, body: str, head: str, base: str):
        repo = self.client.get_repo(repo_name)
        return repo.create_pull(title=title, body=body, head=head, base=base)
