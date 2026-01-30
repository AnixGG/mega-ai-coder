import os
from fastapi import FastAPI, Request, BackgroundTasks

from src.agents.coder import CoderAgent
from src.core.github_client import GithubClient
from src.core.local_git import LocalGit

app = FastAPI()


def run_agent_job(repo_full_name: str, issue_number: int, feedback: str = ""):
    print(f"Worker started for {repo_full_name}#{issue_number}")

    gh = GithubClient()
    issue = gh.get_issue(repo_full_name, issue_number)
    repo_url = issue.repository.clone_url
    branch_name = f"fix/issue-{issue_number}"

    local = LocalGit(repo_url)
    local.clone()
    local.create_branch(branch_name)

    agent = CoderAgent()
    task_text = f"{issue.title}\n{issue.body}"
    agent.run(task_text, feedback=feedback)

    local.commit_all("AI Fixes")
    local.push(branch_name)


@app.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")

    if event == "issues" and payload["action"] == "opened":
        repo_name = payload["repository"]["full_name"]
        issue_num = payload["issue"]["number"]

        background_tasks.add_task(run_agent_job, repo_name, issue_num)
        return {"status": "accepted", "msg": "Agent started for new issue"}

    if event == "issue_comment" and payload["action"] == "created":
        if "pull_request" in payload["issue"]:
            repo_name = payload["repository"]["full_name"]
            issue_num = payload["issue"]["number"]
            comment_body = payload["comment"]["body"]

            if payload["sender"]["type"] != "Bot":
                background_tasks.add_task(run_agent_job, repo_name, issue_num, feedback=comment_body)
                return {"status": "accepted", "msg": "Agent started for feedback"}

    return {"status": "ignored"}
