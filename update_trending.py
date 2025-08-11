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
monthly_html_filename = f"Trending-On-Month-{current_month}-{current_year}.html"
readme_path = "README.md"
old_dir = "old"

os.makedirs(old_dir, exist_ok=True)


def fetch_trending_repos():
    url = "https://github.com/trending?since=daily"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch trending page: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    repo_list = []

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

        repo_list.append({
            "full_name": repo_name,
            "html_url": repo_url,
            "stargazers_count": stars
        })

    return repo_list


def format_repos_md(repos):
    md = f"{today_heading}\n\n"
    for repo in repos:
        md += f"- [{repo['full_name']}]({repo['html_url']}): ⭐ {repo['stargazers_count']} \n"
    md += "\n"
    return md


def format_repos_html(repos, date_str):
    html = f"""
    <div class="bg-gray-50 p-4 rounded-lg shadow mb-6">
        <h2 class="text-xl font-bold text-gray-800 mb-4">Trending on {date_str}</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    """
    for repo in repos:
        html += f"""
        <div class="bg-white rounded-lg shadow hover:shadow-lg transition p-4">
            <a href="{repo['html_url']}" target="_blank" class="block text-lg font-semibold text-blue-600 hover:underline">
                {repo['full_name']}
            </a>
            <p class="text-gray-500 mt-1">⭐ {repo['stargazers_count']} stars</p>
        </div>
        """
    html += "</div></div>\n"
    return html


def extract_month_section(text, month, year):
    pattern = r"## Trending On Date (\d{4}-\d{2}-\d{2})"
    matches = list(re.finditer(pattern, text))
    to_move = []
    for i in range(len(matches)):
        date_str = matches[i].group(1)
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        if date_obj.month == month and date_obj.year == year:
            start = matches[i].start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            to_move.append(text[start:end])
    return to_move


def update_readme(new_content, archive_link=None, all_archive_links=[]):
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            existing_content = f.read()
    except FileNotFoundError:
        existing_content = ""

    archive_links_md = ""
    existing_trending_md = ""

    archive_match = re.search(r"(## Monthly Archives.*?)(?=## Trending On Date |\Z)", existing_content, flags=re.DOTALL)
    if archive_match:
        archive_links_md = archive_match.group(1).strip() + "\n\n"
        existing_trending_md = existing_content.replace(archive_links_md, "").strip()
    else:
        existing_trending_md = existing_content.strip()

    if all_archive_links:
        archive_links_md = "## Monthly Archives\n\n"
        for link in sorted(all_archive_links):
            archive_links_md += f"- [{link}](./{link})\n"
        archive_links_md += "\n"

    final_readme = archive_links_md + new_content + existing_trending_md

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(final_readme)


def update_html(new_html):
    html_template_start = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Trending</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
<div class="max-w-6xl mx-auto py-8">
    <h1 class="text-3xl font-bold mb-8">GitHub Trending Repositories</h1>
"""
    html_template_end = """
</div>
</body>
</html>
"""

    if os.path.exists(monthly_html_filename):
        with open(monthly_html_filename, "r", encoding="utf-8") as f:
            existing_html = f.read()
        body_match = re.search(r"<div class=\"max-w-6xl.*?>(.*)</div>\s*</body>", existing_html, re.DOTALL)
        if body_match:
            body_content = body_match.group(1).strip()
        else:
            body_content = ""
        updated_body = new_html + body_content
    else:
        updated_body = new_html

    final_html = html_template_start + updated_body + html_template_end
    with open(monthly_html_filename, "w", encoding="utf-8") as f:
        f.write(final_html)


def archive_month():
    last_month = (today.replace(day=1) - timedelta(days=1))
    last_month_name = last_month.strftime("%B")
    last_month_year = last_month.year

    last_archive_md = f"Trending-On-Month-{last_month_name}-{last_month_year}.md"
    last_archive_html = f"Trending-On-Month-{last_month_name}-{last_month_year}.html"

    if os.path.exists(last_archive_html):
        os.rename(last_archive_html, os.path.join(old_dir, last_archive_html))


def main():
    trending_repos = fetch_trending_repos()
    today_md = format_repos_md(trending_repos)
    today_html = format_repos_html(trending_repos, today_str)

    if today.day == 1:
        archive_month()
        last_month = (today.replace(day=1) - timedelta(days=1))
        last_month_sections = extract_month_section(open(readme_path, "r", encoding="utf-8").read(), last_month.month, last_month.year)
        archive_content = "".join(last_month_sections)

        if archive_content:
            with open(f"Trending-On-Month-{last_month.strftime('%B')}-{last_month.year}.md", "w", encoding="utf-8") as f:
                f.write(archive_content)

    archive_links = [
        fname for fname in os.listdir(".")
        if re.match(r"Trending-On-Month-.*-\d{4}\.md", fname)
    ]

    update_readme(today_md, all_archive_links=archive_links)
    update_html(today_html)


if __name__ == "__main__":
    main()
