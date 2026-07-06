import os
from github import Github
from dotenv import load_dotenv

load_dotenv()


class GitHubServer:
    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")
        self.github = Github(token)
        self.repo = self.github.get_repo(
            "siddheshpatil4534/agentsentinel"
        )

    def list_issues(self):
        issues = self.repo.get_issues(state="open")
        return [issue.title for issue in issues]

    def create_issue(self, title, body=""):
        issue = self.repo.create_issue(
            title=title,
            body=body,
        )
        return issue.html_url