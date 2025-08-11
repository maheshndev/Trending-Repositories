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
index_html_filename = "index.html"  # Always current month
old_dir = "old"

os.makedirs(old_dir, exist_ok=True)

# --------------------------
# FETCH REPOS
# --------------------------
def fetch_trending_repos():
    url = "https://github.com/trending?since=daily"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch trending repos: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    repo_list = []

    for repo in soup.find_all("article", class_="Box-row"):
        # Repo name & URL
        repo_name_tag = repo.h2.a
        repo_name = repo_name_tag.get_text(strip=True).replace("\n", "").replace(" ", "")
        repo_url = "https://github.com" + repo_name_tag["href"]
        owner = repo_name.split("/")[0] if "/" in repo_name else ""
        
        # Stars
        star_tag = repo.find("a", href=re.compile(r"/stargazers"))
        stars = star_tag.get_text(strip=True).replace(",", "") if star_tag else "0"
        try:
            stars = int(stars)
        except ValueError:
            stars = 0
        
        # Language
        lang_tag = repo.find("span", itemprop="programmingLanguage")
        language = lang_tag.get_text(strip=True) if lang_tag else "Unknown"
        
        # Description
        desc_tag = repo.find("p", class_="col-9")
        description = desc_tag.get_text(strip=True) if desc_tag else "No description provided."
        
        # Topics
        topics = [t.get_text(strip=True) for t in repo.select(".topic-tag")]
        
        repo_list.append({
            "full_name": repo_name,
            "owner": owner,
            "html_url": repo_url,
            "stargazers_count": stars,
            "language": language,
            "description": description,
            "topics": topics
        })

    return repo_list

# --------------------------
# FETCH DEVELOPERS
# --------------------------
def fetch_trending_developers():
    url = "https://github.com/trending/developers?since=daily"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch trending developers: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    dev_list = []

    for dev in soup.find_all("article", class_="Box-row"):
        name_tag = dev.find("h1", class_="h3")
        username_tag = dev.find("p", class_="f4")
        profile_link = "https://github.com" + name_tag.a["href"] if name_tag and name_tag.a else ""
        fullname = name_tag.get_text(strip=True) if name_tag else ""
        username = username_tag.get_text(strip=True) if username_tag else ""
        
        # Repo info (highlighted repo)
        repo_name_tag = dev.find("h1", class_="h4")
        repo_name = repo_name_tag.get_text(strip=True) if repo_name_tag else ""
        repo_url = "https://github.com" + repo_name_tag.a["href"] if repo_name_tag and repo_name_tag.a else ""
        
        dev_list.append({
            "full_name": fullname,
            "username": username,
            "profile_url": profile_link,
            "repo_name": repo_name,
            "repo_url": repo_url
        })

    return dev_list

# --------------------------
# FORMAT MARKDOWN
# --------------------------
def format_repos_md(repos):
    md = f"{today_heading}\n\n"
    for repo in repos:
        md += f"- [{repo['full_name']}]({repo['html_url']}): ⭐ {repo['stargazers_count']} \n"
    md += "\n"
    return md

# --------------------------
# FORMAT HTML WITH TABS
# --------------------------
def format_html_with_tabs(repos, devs, date_str):
    repos_html = ""
    for repo in repos:
        topic_html = " ".join([f"<span class='bg-gray-200 text-gray-700 px-2 py-1 rounded text-xs'>{t}</span>" for t in repo['topics']])
        repos_html += f"""
        <div class="bg-white rounded-lg shadow hover:shadow-lg transition p-4">
            <a href="{repo['html_url']}" target="_blank" class="block text-lg font-semibold text-blue-600 hover:underline">
                {repo['full_name']}
            </a>
            <p class="text-gray-500 mt-1">{repo['description']}</p>
            <p class="text-sm text-gray-600 mt-1">Owner: {repo['owner']}</p>
            <p class="text-sm text-gray-600">Language: {repo['language']} | ⭐ {repo['stargazers_count']}</p>
            <div class="mt-2 flex flex-wrap gap-1">{topic_html}</div>
        </div>
        """

    devs_html = ""
    for dev in devs:
        devs_html += f"""
        <div class="bg-white rounded-lg shadow hover:shadow-lg transition p-4">
            <a href="{dev['profile_url']}" target="_blank" class="block text-lg font-semibold text-blue-600 hover:underline">
                {dev['full_name']} <span class="text-gray-500">({dev['username']})</span>
            </a>
            <p class="text-gray-600 mt-1">Highlighted Repo: <a href="{dev['repo_url']}" target="_blank" class="text-blue-500 hover:underline">{dev['repo_name']}</a></p>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GitHub Trending</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
        function openTab(evt, tabName) {{
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].style.display = "none";
            }}
            tablinks = document.getElementsByClassName("tablink");
            for (i = 0; i < tablinks.length; i++) {{
                tablinks[i].classList.remove("bg-blue-500","text-white");
            }}
            document.getElementById(tabName).style.display = "grid";
            evt.currentTarget.classList.add("bg-blue-500","text-white");
        }}
        </script>
    </head>
    <body class="bg-gray-100">
        <div class="max-w-6xl mx-auto py-8">
            <h1 class="text-3xl font-bold mb-8">GitHub Trending ({date_str})</h1>
            <div class="flex gap-4 mb-4">
                <button class="tablink px-4 py-2 rounded bg-blue-500 text-white" onclick="openTab(event, 'Repositories')">Repositories</button>
                <button class="tablink px-4 py-2 rounded bg-gray-200" onclick="openTab(event, 'Developers')">Developers</button>
            </div>
            <div id="Repositories" class="tabcontent grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {repos_html}
            </div>
            <div id="Developers" class="tabcontent grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" style="display:none;">
                {devs_html}
            </div>
        </div>
    </body>
    </html>
    """
    return html

# --------------------------
# ARCHIVE SYSTEM
# --------------------------
def archive_month():
    last_month = (today.replace(day=1) - timedelta(days=1))
    last_month_last_day = last_month.strftime("%d-%m-%Y")
    if os.path.exists(index_html_filename):
        archive_html_name = f"Trending-On-Month-{last_month_last_day}.html"
        os.rename(index_html_filename, os.path.join(old_dir, archive_html_name))

# --------------------------
# MAIN
# --------------------------
def main():
    trending_repos = fetch_trending_repos()
    trending_devs = fetch_trending_developers()
    today_md = format_repos_md(trending_repos)
    today_html = format_html_with_tabs(trending_repos, trending_devs, today_str)

    if today.day == 1:
        archive_month()

    with open(index_html_filename, "w", encoding="utf-8") as f:
        f.write(today_html)

if __name__ == "__main__":
    main()
