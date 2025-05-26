import requests
from datetime import datetime, timedelta
import calendar
import os
import re

README_FILE = "README.md"

def get_trending_repositories():
    url = "https://api.github.com/search/repositories?q=stars:>1000&sort=stars&order=desc"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["items"][:5]  # Top 5 trending repos
    else:
        print(f"Failed to fetch trending repos: {response.status_code}")
        return []

def format_trending_section(date_str, repos):
    section = f"\n## Trending On Date {date_str}\n\n"
    for repo in repos:
        name = repo["name"]
        url = repo["html_url"]
        section += f"- [{name}]({url})\n"
    return section

def archive_previous_month_sections(readme_content, today):
    # Calculate previous month and year
    first_day_this_month = today.replace(day=1)
    prev_month_last_day = first_day_this_month - timedelta(days=1)
    prev_month = prev_month_last_day.month
    prev_year = prev_month_last_day.year

    # Regex to find all "Trending On Date YYYY-MM-DD" sections
    pattern = r"(## Trending On Date (\d{4}-\d{2}-\d{2})\n(?:- \[.*?\]\(.*?\)\n)+)"
    matches = re.findall(pattern, readme_content, flags=re.MULTILINE)

    # Sections belonging to previous month
    prev_month_sections = []
    keep_sections = []

    for full_section, date_str in matches:
        section_date = datetime.strptime(date_str, "%Y-%m-%d")
        if section_date.month == prev_month and section_date.year == prev_year:
            prev_month_sections.append(full_section)
        else:
            keep_sections.append(full_section)

    # Remove all previous month sections from readme_content
    for sec in prev_month_sections:
        readme_content = readme_content.replace(sec, "")

    # Build monthly archive content
    if prev_month_sections:
        month_name = calendar.month_name[prev_month]
        archive_filename = f"Trending On Month {month_name}-{prev_year}.md"
        archive_content = f"# Trending Repositories for {month_name} {prev_year}\n\n"
        archive_content += "\n".join(prev_month_sections)

        # Write archive file
        with open(archive_filename, "w", encoding="utf-8") as f:
            f.write(archive_content)
        print(f"Archived previous month trending to {archive_filename}")

        # Add link to archive file at the top or bottom of README.md
        link_text = f"\n[View Previous Month → {archive_filename}](./{archive_filename})\n"

        # Remove any existing monthly archive links first
        readme_content = re.sub(r"\n\[View Previous Month → Trending On Month .*?\.md\]\(.*?\)\n", "\n", readme_content)

        # Insert link at the top after title or at start
        if readme_content.startswith("#"):
            # Insert link after first line (title)
            lines = readme_content.splitlines()
            lines.insert(1, link_text.strip())
            readme_content = "\n".join(lines)
        else:
            # Just prepend
            readme_content = link_text + readme_content

        return readme_content, archive_filename
    else:
        # No previous month sections to archive
        return readme_content, None

def update_readme():
    today = datetime.today()
    today_str = today.strftime("%Y-%m-%d")

    # Read README.md
    if os.path.exists(README_FILE):
        with open(README_FILE, "r", encoding="utf-8") as f:
            readme_content = f.read()
    else:
        # If README doesn't exist, create a default one with title
        readme_content = "# Trending GitHub Repositories\n"

    # If first day of month, archive previous month's sections
    if today.day == 1:
        readme_content, archive_file = archive_previous_month_sections(readme_content, today)
    else:
        archive_file = None

    # Remove today's existing section if any (to avoid duplicates)
    readme_content = re.sub(
        rf"\n## Trending On Date {today_str}\n(?:- \[.*?\]\(.*?\)\n)+",
        "",
        readme_content,
        flags=re.MULTILINE,
    )

    # Fetch today's trending repos
    trending_repos = get_trending_repositories()
    if not trending_repos:
        print("No trending repositories fetched, README not updated.")
        return False

    # Create today's section and append
    today_section = format_trending_section(today_str, trending_repos)
    readme_content += today_section

    # Write updated README.md
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"README.md updated with trending repositories for {today_str}")
    return True

if __name__ == "__main__":
    update_readme()
