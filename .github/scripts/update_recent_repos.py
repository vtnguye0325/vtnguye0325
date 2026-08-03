import os
import urllib.request
import json
from datetime import datetime, timezone

USERNAME = "vtnguye0325"
README_PATH = "README.md"
START_MARKER = "<!--START_RECENT_REPOS-->"
END_MARKER = "<!--END_RECENT_REPOS-->"
MAX_REPOS = 5


def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?sort=pushed&direction=desc&per_page=20"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def time_ago(iso_str):
    pushed = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - pushed
    days = delta.days
    if days == 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 30:
        return f"{days} days ago"
    months = days // 30
    return f"{months} month{'s' if months != 1 else ''} ago"


def build_section(repos):
    lines = [START_MARKER, "", "| Repo | Language | Last Pushed |", "| --- | --- | --- |"]
    count = 0
    for repo in repos:
        if repo.get("fork"):
            continue
        name = repo["name"]
        url = repo["html_url"]
        lang = repo.get("language") or "-"
        pushed = time_ago(repo["pushed_at"])
        lines.append(f"| [{name}]({url}) | {lang} | {pushed} |")
        count += 1
        if count >= MAX_REPOS:
            break
    lines.append("")
    lines.append(END_MARKER)
    return "\n".join(lines)


def main():
    repos = fetch_repos()
    section = build_section(repos)

    with open(README_PATH, "r") as f:
        content = f.read()

    start = content.find(START_MARKER)
    end = content.find(END_MARKER)
    if start == -1 or end == -1:
        raise SystemExit("Markers not found in README.md")
    end += len(END_MARKER)

    new_content = content[:start] + section + content[end:]

    with open(README_PATH, "w") as f:
        f.write(new_content)


if __name__ == "__main__":
    main()
