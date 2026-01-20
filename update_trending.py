import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

# Setup
today = datetime.utcnow().date()
current_month = today.strftime("%B")
current_year = today.year
today_str = today.strftime("%Y-%m-%d")
today_heading = f"Trending On {today_str}"

readme_path = "README.md"
old_dir = "old"  # Directory for archived HTML files
os.makedirs(old_dir, exist_ok=True)

def fetch_trending_repos():
    url = "https://github.com/trending?since=daily"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch trending page: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    repos = []

    for repo in soup.find_all("article", class_="Box-row"):
        repo_name_tag = repo.h2.a
        repo_name = repo_name_tag.get_text(strip=True).replace("\n", "").replace(" ", "")
        repo_url = "https://github.com" + repo_name_tag["href"]
        star_tag = repo.find("a", href=re.compile(r"/stargazers"))
        stars = star_tag.get_text(strip=True).replace(",", "") if star_tag else "0"
        try:
            stars = int(stars)
        except ValueError:
            stars = 0
        repos.append({
            "full_name": repo_name,
            "html_url": repo_url,
            "stargazers_count": stars
        })
    return repos

def format_repos_html(repos):
    html = f"<h2 class='text-2xl font-bold mt-6 mb-4'>{today_heading}</h2>\n<ul class='list-disc ml-6 mb-6'>\n"
    for repo in repos:
        html += f"<li class='mb-2'><a href='{repo['html_url']}' class='text-blue-600 hover:underline'>{repo['full_name']}</a> ⭐ {repo['stargazers_count']}</li>\n"
    html += "</ul>\n"
    return html

def extract_month_sections(text, month, year):
    pattern = r"## Trending On Date (\d{4}-\d{2}-\d{2})"
    matches = list(re.finditer(pattern, text))
    sections = []
    for i in range(len(matches)):
        date_str = matches[i].group(1)
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        if date_obj.month == month and date_obj.year == year:
            start = matches[i].start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            sections.append(text[start:end])
    return sections

def update_readme_and_html(today_html):
    # Load existing README
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = ""

    # Append today’s markdown to README
    with open(readme_path, "a", encoding="utf-8") as f:
        f.write("\n" + today_html.replace("<h2", "##").replace("</h2>", "").replace("<ul>", "").replace("</ul>", ""))

    # Generate monthly archive links
    archive_links = [
        fname for fname in os.listdir(".")
        if re.match(r"Trending-On-Month-.*-\d{4}\.md", fname)
    ]
    archive_html = "<h2 class='text-2xl font-bold mt-8 mb-4'>Monthly Archives</h2>\n<ul class='list-disc ml-6 mb-6'>\n"
    for link in sorted(archive_links):
        archive_html += f"<li><a href='./{old_dir}/{link}' class='text-blue-600 hover:underline'>{link}</a></li>\n"
    archive_html += "</ul>\n"

    # Create final index.html
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trending GitHub Repos</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-800 p-6">
<div class="max-w-4xl mx-auto">
<h1 class="text-4xl font-bold mb-6">GitHub Daily Trending Repositories</h1>
{today_html}
{archive_html}
</div>
</body>
</html>"""

    # Save index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

    # Save a copy in old_dir with month-year
    month_filename = f"{current_month}-{current_year}.html"
    with open(os.path.join(old_dir, month_filename), "w", encoding="utf-8") as f:
        f.write(full_html)

def main():
    repos = fetch_trending_repos()
    today_html = format_repos_html(repos)
    update_readme_and_html(today_html)

if __name__ == "__main__":
    main()
