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


def fetch_trending_repos():
    """Scrape trending repositories from GitHub trending page (daily)"""
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

    # Separate existing archive links and trending content
    archive_links_md = ""
    existing_trending_md = ""

    archive_match = re.search(r"(## Monthly Archives.*?)(?=## Trending On Date |\Z)", existing_content, flags=re.DOTALL)
    if archive_match:
        archive_links_md = archive_match.group(1).strip() + "\n\n"
        existing_trending_md = existing_content.replace(archive_links_md, "").strip()
    else:
        existing_trending_md = existing_content.strip()

    # Regenerate archive link block
    if all_archive_links:
        archive_links_md = "## Monthly Archives\n\n"
        for link in sorted(all_archive_links):
            archive_links_md += f"- [{link}](./{link})\n"
        archive_links_md += "\n"

    # Append new data at the top of existing trending content
    final_readme = archive_links_md + new_content + existing_trending_md

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(final_readme)


def main():
    trending_repos = fetch_trending_repos()
    today_md = format_repos_md(trending_repos)

    if today.day == 1:
        # Archive last month's content
        last_month = (today.replace(day=1) - timedelta(days=1))
        last_month_num = last_month.month
        last_month_year = last_month.year
        last_month_name = last_month.strftime("%B")
        last_archive_filename = f"Trending-On-Month-{last_month_name}-{last_month_year}.md"

        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract last month's sections
        last_month_sections = extract_month_section(content, last_month_num, last_month_year)
        archive_content = "".join(last_month_sections)

        if archive_content:
            # Save to archive file
            with open(last_archive_filename, "w", encoding="utf-8") as f:
                f.write(archive_content)

            # 💥 REMOVE previous month's sections from README
            for section in last_month_sections:
                content = content.replace(section, "")

            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(content.strip())

    # Collect archive links
    archive_links = [
        fname for fname in os.listdir(".")
        if re.match(r"Trending-On-Month-.*-\d{4}\.md", fname)
    ]

    # Append today’s data to the body
    readme_body = today_md

    # Write README (includes archive links + current month content only)
    update_readme(readme_body, all_archive_links=archive_links)



if __name__ == "__main__":
    main()
