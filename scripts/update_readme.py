import json
import re
import urllib.request

USER = "AjayBora002"
URL = f"https://api.github.com/users/{USER}/events/public?per_page=50"

req = urllib.request.Request(
    URL,
    headers={"Accept": "application/vnd.github+json", "User-Agent": "readme-bot"},
)
events = json.load(urllib.request.urlopen(req))


def clean(text, n=70):
    return text.splitlines()[0].replace("|", "/")[:n]


rows = []
for e in events:
    repo = e["repo"]["name"]
    link = f"[{repo}](https://github.com/{repo})"
    day = e["created_at"][:10]
    kind = e["type"]
    p = e["payload"]

    if kind == "PushEvent" and p.get("commits"):
        rows.append(f"| {day} | push | {link} | {clean(p['commits'][-1]['message'])} |")
    elif kind == "PullRequestEvent" and p["action"] in ("opened", "closed"):
        pr = p["pull_request"]
        state = "merged" if pr.get("merged") else p["action"]
        rows.append(f"| {day} | PR {state} | {link} | {clean(pr['title'])} |")

    if len(rows) == 6:
        break

if not rows:
    rows = ["| — | — | — | No recent public activity |"]

table = "| Date | Type | Repo | What |\n|---|---|---|---|\n" + "\n".join(rows)

with open("README.md", encoding="utf-8") as f:
    text = f.read()

new = re.sub(
    r"<!--START_ACTIVITY-->.*?<!--END_ACTIVITY-->",
    lambda m: f"<!--START_ACTIVITY-->\n{table}\n<!--END_ACTIVITY-->",
    text,
    flags=re.DOTALL,
)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new)
