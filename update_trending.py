import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

# Setup
today = datetime.utcnow().date()
yesterday = today - timedelta(days=1)
current_month = today.strftime("%B")
current_year = today.year
today_str = today.strftime("%Y-%m-%d")
today_heading = f"## Trending On Date {today_str}"
monthly_archive_filename = f"Trending-On-Month-{current_month}-{current_year}.md"
readme_path = "README.md"
index_html_filename = "index.html"
old_dir = "old"

os.makedirs(old_dir, exist_ok=True)


# ===================== DATA SCRAPERS =====================

def fetch_trending_repos():
    url = "https://github.com/trending?since=daily"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch trending repos: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    repo_list = []

    for repo in soup.find_all("article", class_="Box-row"):
        repo_name_tag = repo.h2.a
        repo_name = repo_name_tag.get_text(strip=True).replace("\n", "").replace(" ", "")
        repo_url = "https://github.com" + repo_name_tag["href"]

        description_tag = repo.p
        description = description_tag.get_text(strip=True) if description_tag else ""

        lang_tag = repo.find("span", itemprop="programmingLanguage")
        language = lang_tag.get_text(strip=True) if lang_tag else ""

        star_tag = repo.find("a", href=re.compile(r"/stargazers"))
        stars = int(star_tag.get_text(strip=True).replace(",", "")) if star_tag else 0

        owner = repo_name.split("/")[0]

        topics = [t.get_text(strip=True) for t in repo.find_all("a", class_="topic-tag")]

        repo_list.append({
            "full_name": repo_name,
            "html_url": repo_url,
            "description": description,
            "language": language,
            "owner": owner,
            "topics": topics,
            "stargazers_count": stars
        })

    return repo_list


def fetch_trending_developers():
    url = "https://github.com/trending/developers?since=daily"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch trending developers: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    dev_list = []

    for dev in soup.find_all("article", class_="Box-row"):
        name_tag = dev.find("h1", class_="h3")
        name = name_tag.get_text(strip=True) if name_tag else ""

        username_tag = dev.find("p", class_="f4")
        username = username_tag.get_text(strip=True) if username_tag else ""

        profile_url = "https://github.com" + dev.find("a")["href"]

        repo_tag = dev.find("article", class_="mt-2")
        repo_name = repo_tag.find("a").get_text(strip=True) if repo_tag else ""
        repo_url = "https://github.com" + repo_tag.find("a")["href"] if repo_tag else ""

        dev_list.append({
            "name": name,
            "username": username,
            "profile_url": profile_url,
            "repo_name": repo_name,
            "repo_url": repo_url
        })

    return dev_list


# ===================== MARKDOWN FORMATTING =====================

def format_repos_md(repos):
    md = f"{today_heading}\n\n### Repositories\n"
    for repo in repos:
        tags_str = ", ".join(repo["topics"]) if repo["topics"] else "No tags"
        md += (f"- [{repo['full_name']}]({repo['html_url']}): ⭐ {repo['stargazers_count']} | "
               f"Lang: {repo['language'] or 'N/A'} | Owner: {repo['owner']} | Tags: {tags_str}\n"
               f"  - {repo['description']}\n")
    md += "\n"
    return md


def format_devs_md(devs):
    md = "\n### Developers\n"
    for dev in devs:
        md += (f"- [{dev['name']}]({dev['profile_url']}) (@{dev['username']}): "
               f"[{dev['repo_name']}]({dev['repo_url']})\n")
    return md


# ===================== HTML FORMATTING =====================

def format_html(repos, devs, date_str):
    html_template_start = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="description" content="Daily GitHub trending repositories and developers on {date_str}">
    <meta name="keywords" content="GitHub, trending, repositories, developers, open-source, {current_month} {current_year}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Trending - {date_str}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
<div class="max-w-6xl mx-auto py-8">
    <h1 class="text-3xl font-bold mb-8">GitHub Trending ({date_str})</h1>
    <div class="tabs">
        <button onclick="showTab('repos')" class="tab-btn">Repositories</button>
        <button onclick="showTab('devs')" class="tab-btn">Developers</button>
    </div>
    <div id="repos" class="tab-content">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    """

    # Repositories section
    repo_html = ""
    for repo in repos:
        topics_html = "".join(f"<span class='bg-gray-200 rounded px-2 py-1 text-sm mr-1'>{t}</span>" for t in repo["topics"])
        repo_html += f"""
        <div class="bg-white rounded-lg shadow hover:shadow-lg transition p-4">
            <a href="{repo['html_url']}" target="_blank" class="block text-lg font-semibold text-blue-600 hover:underline">
                {repo['full_name']}
            </a>
            <p class="text-gray-700 mt-2">{repo['description']}</p>
            <p class="text-gray-500 mt-1">⭐ {repo['stargazers_count']} | Lang: {repo['language'] or 'N/A'} | Owner: {repo['owner']}</p>
            <div class="mt-2">{topics_html}</div>
        </div>
        """

    # Developers section
    dev_html = "</div></div><div id='devs' class='tab-content hidden'><div class='grid grid-cols-1 md:grid-cols-2 gap-4'>"
    for dev in devs:
        dev_html += f"""
        <div class="bg-white rounded-lg shadow hover:shadow-lg transition p-4">
            <a href="{dev['profile_url']}" target="_blank" class="block text-lg font-semibold text-blue-600 hover:underline">
                {dev['name']} (@{dev['username']})
            </a>
            <p class="text-gray-500 mt-1">
                <a href="{dev['repo_url']}" target="_blank" class="text-blue-500 hover:underline">
                    {dev['repo_name']}
                </a>
            </p>
        </div>
        """

    html_template_end = """</div></div>
</div>
<script>
function showTab(tab) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.getElementById(tab).classList.remove('hidden');
}
</script>
</body>
</html>"""

    return html_template_start + repo_html + dev_html + html_template_end


# ===================== ARCHIVING =====================

def archive_month():
    last_month = (today.replace(day=1) - timedelta(days=1))
    archive_html_name = f"trending-repositories-{last_month.strftime('%B-%Y')}.html"
    if os.path.exists(index_html_filename):
        os.rename(index_html_filename, os.path.join(old_dir, archive_html_name))


# ===================== MAIN =====================

def main():
    repos = fetch_trending_repos()
    devs = fetch_trending_developers()

    today_md = format_repos_md(repos) + format_devs_md(devs)
    today_html = format_html(repos, devs, today_str)

    if today.day == 1:
        archive_month()
        last_month = (today.replace(day=1) - timedelta(days=1))
        with open(f"Trending-On-Month-{last_month.strftime('%B')}-{last_month.year}.md", "w", encoding="utf-8") as f:
            f.write(today_md)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(today_md)

    with open(index_html_filename, "w", encoding="utf-8") as f:
        f.write(today_html)


if __name__ == "__main__":
    main()
