import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_trending_repos():
    url = "https://github.com/trending"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    repos = soup.find_all("article", class_="Box-row")

    trending = []
    for repo in repos[:10]:  # get top 10
        full_name = repo.h2.text.strip().replace("\n", "").replace(" ", "")
        link = "https://github.com/" + full_name
        trending.append((full_name, link))
    return trending

def update_readme(repos):
    today = datetime.today().strftime('%Y-%m-%d')
    header = f"\n\n## Trending Repositories {today}\n"
    lines = [header]
    for name, link in repos:
        lines.append(f"- [{name}]({link})")
    lines.append("\n")

    with open("README.md", "a", encoding="utf-8") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    trending_repos = fetch_trending_repos()
    update_readme(trending_repos)
