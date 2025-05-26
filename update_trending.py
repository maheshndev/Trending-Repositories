import os
import requests
from datetime import datetime, timedelta
import re

today = datetime.utcnow().date()
yesterday = today - timedelta(days=1)
current_month = today.strftime("%B")
current_year = today.year
today_str = today.strftime("%Y-%m-%d")
today_heading = f"## Trending On Date {today_str}"
monthly_archive_filename = f"Trending On Month {current_month}-{current_year}.md"
readme_path = "README.md"

def fetch_trending_repos():
    """Fetch trending repositories from the unofficial GitHub Trending API"""
    url = "https://github-trending-api.de.a9sapp.eu/repositories?since=daily"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Trending API error: {response.status_code} {response.text}")
    return response.json()

def format_repos_md(repos):
    md = f"{today_heading}\n\n"
    for repo in repos:
        name = repo["author"] + "/" + repo["name"]
        url = repo["url"]
        stars = repo["stars"]
        description = repo["description"] or "No description"
        md += f"- [{name}]({url}): ⭐ {stars} — {description}\n"
    md += "\n"
    return md

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
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = ""

    # Remove all trending sections
    content = re.sub(r"## Trending On Date \d{4}-\d{2}-\d{2}.*?(?=## Trending On Date |\Z)", "", content, flags=re.DOTALL)

    # Archive links block
    archive_links_md = ""
    if all_archive_links:
        archive_links_md += "## Monthly Archives\n\n"
        for link in sorted(all_archive_links):
            archive_links_md += f"- [{link}](./{link})\n"
        archive_links_md += "\n"

    # Final write
    new_readme = archive_links_md + new_content
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_readme)

def main():
    trending_repos = fetch_trending_repos()
    today_md = format_repos_md(trending_repos)

    if today.day == 1:
        # Archive last month's content
        last_month = (today.replace(day=1) - timedelta(days=1))
        last_month_num = last_month.month
        last_month_year = last_month.year
        last_month_name = last_month.strftime("%B")
        last_archive_filename = f"Trending On Month {last_month_name}-{last_month_year}.md"

        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
            last_month_sections = extract_month_section(content, last_month_num, last_month_year)
            archive_content = "".join(last_month_sections)

            if archive_content:
                with open(last_archive_filename, "w", encoding="utf-8") as f:
                    f.write(archive_content)

    # Collect archive links
    archive_links = [
        fname for fname in os.listdir(".")
        if re.match(r"Trending On Month .*-\d{4}\.md", fname)
    ]

    # Build README
    readme_body = today_md

    # Write README
    update_readme(readme_body, all_archive_links=archive_links)

if __name__ == "__main__":
    main()
