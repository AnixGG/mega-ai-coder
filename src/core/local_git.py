import os
import shutil
from git import Repo


class LocalGit:
    def __init__(self, repo_url: str, work_dir: str = "./workspace"):
        self.repo_url = repo_url
        self.work_dir = work_dir
        self.repo = None
        self.default_branch = "main"

    def clone(self):
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
        self.repo = Repo.clone_from(self.repo_url, self.work_dir)

    def create_branch(self, name: str):
        if not self.repo:
            raise RuntimeError("Repository not cloned")
        current = self.repo.create_head(name)
        current.checkout()

    def commit_all(self, message: str):
        if not self.repo:
            raise RuntimeError("Repository not cloned")
        self.repo.git.add(A=True)
        self.repo.index.commit(message)

    def push(self, branch_name: str):
        if not self.repo:
            raise RuntimeError("Repository not cloned")
        origin = self.repo.remote(name='origin')
        origin.push(branch_name)
